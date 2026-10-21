# Grader protocol

You grade finished clean-room builds of one eval prompt against the assertions of a web-development skill. The builds are in blind folders named by letter. You do not know which build had which instructions, and you must not try to guess. Grade each build only on what it produced. Never ask questions.

Keep the work bounded, because a grader that waits on something that never returns leaves no grades at all. Start every server as a background process, never in the foreground. Wait on no single step longer than five minutes; record a step that hangs and move on. Run a subagent only in the foreground, and leave none running when you finish. When half the time you were given is gone, write `grading.json` with what you have, then improve it.

Inputs, under the run folder `$EVAL_ROOT` and this harness folder:

- The prompt every builder received: `judge/<round>-<eval>/prompt.txt`.
- The builds: `judge/<round>-<eval>/<letter>/work`, and beside each `builder-final-message.txt`, what the builder said at the end (lines naming instructions it followed were removed). Never open `key.json`.
- The assertions: `judge/<round>-<eval>/rules.json`, a list of rules, each with an id, the rule, and a suggested check.
- The scripts in this harness folder: `prepare.py` (install, build, lint, typecheck, layout record), `serve.mjs` (static server with single-page fallback), `capture.mjs` (captures and measures every page at 1440, 2560, 390, and 320 CSS pixels), `sheets.py` (contact sheets). Read their headers for usage. Run `npm install` and `npx playwright install chromium` in this folder once, then run `capture.mjs` from here.

For each build:

1. Run `python prepare.py $EVAL_ROOT/judge/<round>-<eval>/<letter>` and read `prepare.json`.
2. Start the product the way its README or final message says, on a free port, preferring the production build (a static output folder through `serve.mjs`, `next start`, `vite preview`, or the server's start script). If the build failed, try the dev server and record that you did. For an HTTP API, start it and exercise it with real requests. For a repository with several surfaces, start each one.
3. Run the skill's own layout check with every output under the build's judge folder, `node <skill>/scripts/check-layout.mjs <url> --paths=<routes> --out=$EVAL_ROOT/judge/<round>-<eval>/<letter>/check-<surface> > $EVAL_ROOT/judge/<round>-<eval>/<letter>/check-<surface>.txt`, where `<skill>` is the snapshot the new builds used, adding `--app` for a signed-in app shell. Its failures are evidence for the matching assertions. Then run `capture.mjs` against every served surface into `judge/<round>-<eval>/<letter>/capture-<surface>`, adding `--paths=` for routes a crawl from the start page would not reach (detail pages, settings, legal pages, pricing), then `sheets.py` on that folder. When `capture.mjs` prints a TRUNCATED line, capture again with higher `--max-pages` or `--max-slices`, or with the missing routes in `--paths`, until it prints none. Never grade from a truncated capture. Look at the contact sheets yourself, at least the home page and the main view at 1440 and 320, before judging any visual rule.
4. Exercise the interactions the prompt asks for (filters, bulk actions, copy buttons, status changes, votes, API calls) with Playwright or requests, and measure what a rule asks (for example a button's box before and after its confirmation). Reload the page after changing a filter to see whether the view restores.
5. Stop every server you started.

Then grade every assertion for every build, as one of:

- `pass`: the build shows the rule, with concrete evidence (a file and line, a measurement, a screenshot name, a response).
- `fail`: the build had occasion to show the rule and did not, with the evidence.
- `na`: the build never had occasion (for example a billing rule in a build with no billing). Say why in a few words.

Require concrete evidence for a pass. A label present without the substance is a fail. Where a rule's suggested check is impractical, use the closest check that decides it and say what you did.

Write `judge/<round>-<eval>/grading.json`:

```json
{
  "eval": "<eval>",
  "builds": {
    "<letter>": {
      "prepare": [["<command from prepare.json>", 0]],
      "served": "<how it was served, or why it could not be>",
      "summary": "<three sentences on what this build is and its biggest defects>",
      "rules": {"<rule id>": {"v": "pass|fail|na", "e": "<evidence, one line>"}}
    }
  },
  "rule_notes": {"<rule id>": "<only when the rule itself is ambiguous, untestable, or wrong as written>"}
}
```

Validate that it parses. Reply with only the path, a one-line summary per build, and the rules that failed in every build.
