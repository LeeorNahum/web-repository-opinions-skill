I added two tools to `docs/mcp-tools.md`, one for each new request in the brief. That brings the catalog from five tools to seven. I didn't commit anything, and I didn't touch `docs/brief.md`.

**The new tools**
- **`search_pages`** `{ query, folder?, cursor?, limit? }`: finds pages by their title and content and returns each match's path, title and a few short snippets. It pages through results like `list_pages` does (20 per page, at most 50) and doesn't return the full page, so the agent calls `read_page` on the matches it wants. This replaces listing folders and reading pages one at a time.
- **`order_prints`** `{ request_id, paths[], copies, ship_to }`: orders one bound volume of the listed pages, in the given order, makes the requested number of copies, charges the card once and ships one package.
  - **Duplicate calls:** `request_id` is required. If a host resends the same call after a timeout, it gets back the original order (`already_placed`) and isn't charged again. Reusing an ID with different arguments is refused.
  - **Unconfirmed charges:** if the server can't confirm whether the charge went through, the result says the outcome is unknown and tells the agent to call again with the same `request_id`. That call either returns the existing order or places it once.
  - **All or nothing:** if any listed page doesn't exist, nothing is ordered and the refusal lists the bad paths.
  - **Viewers:** every caller sees the same tool list. A Viewer who calls `order_prints` gets a `not_permitted` refusal, and the doc lists the other refusals too, each with a next step.

I also added an annotations column (read-only, destructive, and so on) to all seven tools, including the existing five, which is a small change beyond what you asked for.

**Calls I made**, also listed at the end of the doc under "Assumptions pending owner review":
- **No price quote before ordering.** The per-copy price and total come back with the order. If agents need to show a price first, the fix is a separate read-only `quote_prints` tool rather than a dry-run option on `order_prints`.
- **No status, history or cancel tools.** Agents can't check shipping or cancel through MCP. Repeating the call with the same `request_id` is enough to settle an uncertain charge.
- **Shipping and tax** are either included in the per-copy price or charged with it as one total.
- **Limits:** up to 200 pages per volume and 100 copies per order. These are placeholders until we know the print partner's real limits.
- **Search scope:** search covers full page content as well as titles, skips pages in Trash, and updates on every write, edit and delete.
- **Search matching:** a page matches when it contains every word in the query, and text in double quotes matches as an exact phrase. Results are ranked with title matches above body matches.
- **Request IDs** are kept with the order indefinitely and are separate for each workspace.
- **Pages are named by path**, like the existing tools. The order result echoes each page's path and title so the agent can check what was printed.