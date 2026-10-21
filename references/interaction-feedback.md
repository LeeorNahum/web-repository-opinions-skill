# Interaction Feedback

Make action feedback coherent across every control representing the same operation.

## Shared State

Key feedback by entity identity and action kind. Individual controls and aggregate controls read the same state instead of running isolated animations.

Use a small state model:

```text
idle -> loading -> success
idle -> loading -> error
```

## Presentation

- Keep loading, success, and failure inside the existing control footprint.
- Preserve text labels when they carry action meaning.
- Use accessible labels or live announcements for complete, partial, and failed results.
- Keep routine action feedback to a word or a short phrase.
- Prevent duplicate submission while an action is in flight.

Transient feedback, such as a copy button's confirmation, a saved or sent notice, or a toast, must not reflow the surrounding interface. Reserve its space, replace content within a stable footprint, or use an overlay surface whose appearance does not move nearby controls. Persistent validation and user-authored content may change layout when that change is part of the lasting page state.

Choose reset timing by how the state was produced. Pointer feedback may reset when the pointer leaves if that is an established immediate interaction. Keyboard-triggered and remotely coordinated feedback stays visible for about two seconds, then resets on a timer.

## Compact Counts

Use locale-aware short compact decimal notation for social and aggregate counts when the full value would compete with the action label.

- Show exact localized integers below 1,000.
- At 1,000 and above, use the runtime's ECMA-402 `Intl.NumberFormat` with `notation: 'compact'` and its default rounding, which gives `1.2K`, `12K`, `123K`, and `1.2M` and takes its suffixes from Unicode CLDR locale data.
- Keep the full localized value in the accessible label and, when useful, a tooltip.
- Reserve enough width for the longest supported compact form so count changes do not resize the control.
- Keep the action label and its loading or success state in a separate stable column so wording changes do not move the count.

## Selection Surfaces

A row or card that toggles selection on click suppresses text selection only for primary-pointer drags that start on its non-interactive area.

Preserve:

- Links, buttons, inputs, editable content, and copy actions.
- Native text selection that begins outside the selection surface.
- Keyboard selection.
- Range selection.
- Native browser shortcuts such as select all and find.

Selection survives pagination and unrelated controls. Clear it when the filter, search, or scope changes, when the user explicitly clears it, or on Escape.

## Search Shortcuts

For a search-centered collection, `/` focuses the search input. `Ctrl/Cmd+K` does too, unless the product has a command palette, which then owns it.

- Focus the existing search input.
- Select its current value without clearing it.
- Ignore shortcuts inside editable controls, dialogs, menus, and listboxes.
- Preserve native find and select-all behavior.
- Keep shortcut text out of the search placeholder.
