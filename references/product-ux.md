# Product UX

Design every screen around a real human path, not a template average of nearby patterns. For each page, decide what the viewer should notice first, next, and last, then build to that order.

- Give each view one primary action, styled as the only primary button in its main region.
- Give every view, including empty, not-found, and error states, at least one link or action onward.
- Hide actions a user cannot take instead of showing disabled or error-producing controls.
- Write every visible label, status, and message in product words, free of internal, debug, provider, and job terminology. A privacy policy still names the processors it must disclose. Provider job IDs, raw webhook states, model names, and storage keys appear only in admin.

Use product-owned dialogs, sheets, menus, and inline forms for user input and destructive confirmation. Browser-native prompt, confirmation, and alert dialogs are not product interfaces and must not ship.

## One Word, One Meaning

A product word means exactly one thing across the whole surface. The moment a single word names both a kind of thing and a state that thing can be in, every sentence containing it becomes ambiguous, and the ambiguity is invisible to the person who wrote it because they know which sense they meant.

This is harder to catch than jargon, because each individual sentence reads fine. Find it by listing the product's nouns and asking what each one names, exactly once. If a word answers two questions, rename one of the senses, and prefer renaming the state, because a kind of thing is usually the older and more load-bearing meaning.

## Name The Field That Decides

When the system chooses something on a user's behalf by reading a field the user wrote, say so where they write it. A description that looks like documentation but is actually the input a matcher runs on is a trap: the user writes prose for a human, and the behavior they get is decided by prose they were never told was load-bearing.

One plain sentence at the field is enough. It changes what people write, which is the whole point.

The same applies to a capability that takes effect only under a condition. Show that condition, quietly, where the capability appears, because a user cannot reason about why it did or did not apply otherwise.

## Preview Every Transformation

A field that quietly transforms what a user typed, lowercasing it, replacing characters, or cutting it at a limit, teaches them nothing and hides its own rules. Character-by-character substitution is the worst version, because it produces artifacts the user did not intend and cannot explain.

Show the constraint before the entry, show the transformed value as a preview the user can see, and say when a limit was reached. Silent coercion is not forgiving, it is unexplained.

Display follows the same rule. Show every name, filename, and identifier in exactly its stored case, and apply case styling to the product's own labels only, stopping at the boundary of data. A case transform on a value is a lie the reader cannot detect, and they may type back what they saw, which a case-sensitive system then rejects.

## A Reversible State Stays Findable

Turning something off must not remove it from the surface that lists it. When the off state is rendered as absence, it becomes indistinguishable from never having existed, and the only way back is remembering the name. Off and gone are different states and must look different.

## Show Numbers That Drive A Decision

Show a count, a size, or an identifier only when it changes what the viewer does next, never because it was easy to compute. An internal ID on a list row or a raw byte count beside a name is a fact that answers no question the viewer was asking.

The exception is a number that stands in for something hidden: a collapsed group's item count says how much is behind the row, so it earns its place. Where a measure genuinely helps, choose the unit the user thinks in rather than the one the system stores.
