# Query State

Put shareable collection state in the URL so a reload, copied link, browser navigation, and server render restore the same view.

## Parameter Contract

- Use `q` for the primary free-text search query.
- Use readable enum values and `true` or `false` for booleans.
- Omit empty values and state the user has not chosen.
- Preserve an explicitly selected default when that choice must survive sharing or reload.
- Give an explicit all-value to a control only when selecting all is meaningful state rather than the absence of a filter.
- Address pagination in the URL when a position is a distinct, linkable destination, such as a page number or a cursor into a large result set. Treat an incremental "load more" that only deepens the current view as view depth the base view already restores, and leave it out of the URL.
- Reject unknown formats instead of silently maintaining an unreleased contract.

Centralize parsing, validation, normalization, and serialization in shared domain logic. UI components consume typed state rather than interpreting query strings independently.

## Canonical Order

Serialize parameters in one fixed order. Interaction history never changes the resulting URL.

Put the primary intent first. For a searchable collection, `q` comes first. After that, mirror the product's stable visible control hierarchy so the URL reads in the same order as the interface. Append non-visible scopes, presentation state, and pagination after the visible controls.

Use semantic grouping only when there is no stable visible hierarchy:

```text
primary intent -> scopes and filters -> sort -> view -> pagination
```

The fixed order is the durable requirement. No HTTP or browser standard gives query parameters semantic priority. Matching a deliberate interface hierarchy makes the order explainable instead of arbitrary.

## Defaults And History

An untouched default may stay absent. Once the user explicitly selects that default, preserve it when the product promises that copied URLs represent the chosen state.

Use history replacement for debounced search and rapid control changes that refine one view. Use history pushes when each state is a meaningful navigation destination the user should step through with Back.

Keep transient selection, hover, open menus, loading, and feedback out of the URL unless sharing or restoring them is a real product capability.

## Verification

Add contract tests when URL state is part of the product:

- Parse each supported value into the intended typed state.
- Serialize state into the exact canonical URL.
- Restore explicit defaults and all-values.
- Omit untouched and empty state.
- Reject unsupported formats.
- Prove equivalent interaction sequences serialize identically.

These are automated parser and serializer tests, not a visual checklist.

## URL-Openable Creation

Make a creation or "adder" modal a URL-addressable view like any other, openable by a query parameter or a route, so it can be linked, shared, and deep-linked into from an onboarding step or a partner's setup link. Restoring the URL reopens the same modal.

Pre-fill only non-sensitive fields, and only as a convenience for the shape of the form. Never put a secret, or any value that confers access or reveals private data, in a URL: URLs are logged, shared, and kept in history, and what a user may see is decided by their authenticated session, never by a query parameter. A sensitive value is always supplied behind auth, not through the link.
