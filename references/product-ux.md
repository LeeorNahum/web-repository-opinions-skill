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

Use product-owned dialogs, sheets, menus, and inline forms for user input and destructive confirmation. Browser-native prompt, confirmation, and alert dialogs are not product interfaces and must not ship.

## One Word, One Meaning

A product word means exactly one thing across the whole surface. The moment a single word names both a kind of thing and a state that thing can be in, every sentence containing it becomes ambiguous, and the ambiguity is invisible to the person who wrote it because they know which sense they meant.

This is harder to catch than jargon, because each individual sentence reads fine. Find it by listing the product's nouns and asking what each one names, exactly once. If a word answers two questions, rename one of the senses, and prefer renaming the state, because a kind of thing is usually the older and more load-bearing meaning.

## Name The Field That Decides

When the system chooses something on a user's behalf by reading a field the user wrote, say so where they write it. A description that looks like documentation but is actually the input a matcher runs on is a trap: the user writes prose for a human, and the behavior they get is decided by prose they were never told was load-bearing.

One plain sentence at the field is enough. It changes what people write, which is the whole point.

The same applies to how a capability is reached at all. If something is fetched on demand rather than always present, the surface that shows it should say so quietly, because a user cannot reason about why it did or did not apply otherwise.

## Never Silently Rewrite Input

A field that quietly transforms what a user typed, lowercasing it, replacing characters, or cutting it at a limit, teaches them nothing and hides its own rules. Character-by-character substitution is the worst version, because it produces artifacts the user did not intend and cannot explain.

Show the constraint before the entry, show the transformed value as a preview the user can see, and say when a limit was reached. Silent coercion is not forgiving, it is unexplained.

## A Reversible State Stays Findable

Turning something off must not remove it from the surface that lists it. When the off state is rendered as absence, it becomes indistinguishable from never having existed, and the only way back is remembering the name. Off and gone are different states and must look different.

## Numbers The User Cannot Act On

Do not show a count, a size, or an identifier because it was easy to compute. Every number on a surface should change what the viewer does next. A file count in a header, a byte size beside a name, and a commit hash on a row are all facts, and none of them answer a question the viewer was asking.

The exception is a number that stands in for something hidden: a collapsed directory's file count says how much is behind the row, so it earns its place. Where a measure genuinely helps, choose the unit the user thinks in rather than the one the system stores.
