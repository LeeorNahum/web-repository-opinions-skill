# Query State

Put shareable collection state in the URL so a reload, copied link, browser navigation, and server render restore the same view.

## Parameter Contract

- Use `q` for the primary free-text search query.
- Use readable enum values and `true` or `false` for booleans.
- Omit empty values and state the user has not chosen.
- Give an explicit all-value to a control only when selecting all is meaningful state rather than the absence of a filter.
- Address pagination in the URL when a position is a distinct, linkable destination, such as a page number or a cursor into a large result set. Treat an incremental "load more" that only deepens the current view as view depth the base view already restores, and leave it out of the URL.
- Treat an unknown key or value as invalid: drop it and replace the URL with the canonical serialization of the valid state that remains, instead of silently maintaining an unreleased contract.

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

An untouched default stays out of the URL. A default the user explicitly selects is written to the URL, so a copied link reproduces the choice.

Use history replacement for debounced search and rapid control changes that refine one view. Use history pushes when each state is a meaningful navigation destination the user should step through with Back.

Keep transient selection, hover, open menus, loading, and feedback out of the URL unless sharing or restoring them is a real product capability.

## Verification

Add contract tests when URL state is part of the product:

- Parse each supported value into the intended typed state.
- Serialize state into the exact canonical URL.
- Restore explicit defaults and all-values.
- Omit untouched and empty state.
- Drop unsupported values and replace the URL with the canonical form.
- Prove equivalent interaction sequences serialize identically.

These are automated parser and serializer tests, not a visual checklist.

## URL-Openable Creation

Make a creation or "adder" modal a URL-addressable view like any other, openable by a query parameter or a route, so it can be linked, shared, and deep-linked into from an onboarding step or a partner's setup link. Restoring the URL reopens the same modal.

Pre-fill only non-sensitive fields from the URL, and only as a convenience for the shape of the form. URLs are logged, shared, and kept in history, so a creation form reads secrets and access-granting values from the authenticated session, and what a user may see is decided by that session, never by a query parameter. A URL carries access only as a purpose-built, expiring token, such as a signed download URL or an invitation link.

## Third-Party And Embedded Views

The same rule extends past your own dialogs. When a workflow's step is a meaningful destination, a payment portal step, an embedded settings surface someone would reload, bookmark, or land on directly, give it a real route instead of leaving it an anonymous popover, even when a third-party SDK owns its rendering. When a provider component offers both a page mode and a modal mode, choose by the rules below.

Weigh what page mode actually mounts before choosing it. A provider panel with internal tabs brings its own sub-routes, in the provider's vocabulary, under whatever URL it is mounted at, and needs a routing adapter the SDK supports. When those provider-owned segments have no place in the product's URL contract, or the panel is a control someone opens, acts in, and closes rather than a destination anyone shares, use the provider's modal mode over the current view: its internal tab state stays virtual, and the product URL underneath stays unchanged and restorable. A transient menu, popover, or tooltip stays out of the URL. A panel that is a real destination gets one.
