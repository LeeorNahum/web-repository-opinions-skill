# Interaction Feedback

Make action feedback coherent across every control representing the same operation.

## Shared State

Key feedback by entity identity and action kind. Individual controls and aggregate controls read the same state instead of running isolated animations.

Use a small state model:

```text
idle -> loading -> success
idle -> loading -> error
```

An aggregate action reports partial failure when any included item fails, even if useful partial output succeeds. Individual controls retain their own outcomes.

## Presentation

- Keep loading, success, and failure inside the existing control footprint.
- Preserve text labels when they carry action meaning.
- Use accessible labels or live announcements for complete, partial, and failed results.
- Keep raw provider errors and large status paragraphs out of routine action feedback.
- Prevent duplicate submission while an action is in flight.

Transient feedback must not reflow the surrounding interface. Reserve its space, replace content within a stable footprint, or use an overlay surface whose appearance does not move nearby controls. Persistent validation and user-authored content may change layout when that change is part of the lasting page state.

Choose reset timing by how the state was produced. Pointer feedback may reset when the pointer leaves if that is an established immediate interaction. Keyboard-triggered and remotely coordinated feedback stays visible long enough to perceive, then resets on a timer.

## Compact Counts

Use locale-aware short compact decimal notation for social and aggregate counts when the full value would compete with the action label. Build on the runtime's ECMA-402 `Intl.NumberFormat` compact notation so suffixes follow Unicode CLDR locale data.

- Show exact localized integers below 1,000.
- At 1,000 and above, use short compact notation with at most two significant digits, such as `1K`, `1.2K`, `12K`, `1.2M`, and `25M`.
- Keep the full localized value in the accessible label and, when useful, a tooltip.
- Reserve enough width for the longest supported compact form so count changes do not resize the control.
- Keep the action label and its loading or success state in a separate stable column so wording changes do not move the count.

## Selection Surfaces

Suppress accidental text selection only when a primary-pointer gesture begins on the non-interactive selection surface.

Preserve:

- Links, buttons, inputs, editable content, and copy actions.
- Native text selection that begins outside the selection surface.
- Keyboard selection.
- Range selection.
- Native browser shortcuts such as select all and find.

Selection survives pagination and unrelated controls. Clear it when the result set meaningfully changes, the user explicitly clears it, or the standard escape action applies.

## Search Shortcuts

For a search-centered collection, support `/` and `Ctrl/Cmd+K` when they fit the host platform.

- Focus the existing search input.
- Select its current value without clearing it.
- Ignore shortcuts inside editable controls, dialogs, menus, and listboxes.
- Preserve native find and select-all behavior.
- Keep shortcut text out of placeholders unless user research shows it improves discovery.
