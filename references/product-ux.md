# Product UX

Design every screen around a real human path, not a template average of nearby patterns. A product surface can be locally correct and globally incoherent; judge the whole, not just the parts.

For each page, decide what the viewer should notice first, next, and last, then build to that order.

- Give every page one clear primary path or action. No dead-end screens.
- Hide actions a user cannot take instead of showing disabled or error-producing controls.
- Avoid duplicate concepts and parallel route schemes that say the same thing twice.
- Keep internal, debug, provider, and job terminology out of user-facing copy.
- Never expose provider job IDs, raw webhook states, model names, or storage keys to users.
- Keep public copy separate from internal implementation language.

Fix structure before style. If the skeleton of a page is wrong, do not decorate it; reset the path first, then polish.

Simulate the real interaction, not the static screenshot. A page that survives a skim can still break the moment someone tries to use it.

Use product-owned dialogs, sheets, menus, and inline forms for user input and destructive confirmation. Browser-native `prompt`, `confirm`, and `alert` UI is not a product interface and must not ship.
