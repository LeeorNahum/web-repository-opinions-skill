# Catch-Up

A repository built under an earlier version of these opinions drifts behind them, because an agent applies the skill only to what it is building. Catching up is a whole-repository pass the owner asks for, in words such as "is anything from these opinions missing in our repo?", and it ends with the gaps implemented, not with a list.

1. Read every reference in full, since this pass is the one case that loads all of them, and the whole repository: its apps and packages, workflows, env contracts, setup documents, and the docs that record its decisions.
2. For each reference, decide first whether its trigger is met in this product. A reference about a part the product does not have, such as payments, a signed-in app, or an agent plugin, finds nothing to add.
3. Sort what applies into missing, mismatched, and improvable, across architecture, runtime, data, UX, operations, and release readiness.
4. Keep every deliberate alternative. A different framework or tool, or a decision recorded in the repository's own docs, stands, and the opinions apply around it in that tool's terms. When a choice looks accidental but could be deliberate, ask.
5. Implement the rest, one category at a time, verifying each the way its owning reference says it is done, and honor every "Ask before" line on the way.
6. Report what was implemented, what was kept as a deliberate alternative, and what is deferred with its blocker, in the conversation rather than in a file in the repository.
