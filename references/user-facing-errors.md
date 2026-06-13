# User-Facing Errors

Treat every provider, framework, transport, database, and backend error as internal data. Convert failures into product-owned outcomes before they reach visible UI.

## Boundary

- Return typed outcome codes for expected failures.
- Map outcome codes to concise, actionable copy at a shared presentation boundary.
- Use one context-specific fallback for unexpected failures.
- Keep raw messages available only to approved logs and diagnostics.

Never render an exception message directly. Framework wrappers often combine safe wording with request IDs, function names, stack locations, provider payloads, and deployment details.

## Classification

Classify failures by what the user can do next:

- Correct the input.
- Sign in or request access.
- Choose a supported source or format.
- Reduce the size or scope.
- Retry a transient operation.
- Return later when a source is unavailable.
- Contact support when the product cannot recover.

Provider status codes and internal failure names may choose the classification, but they do not become visible copy.

## Presentation

- Name the failed user action, not the subsystem.
- Give one realistic next step.
- Keep routine feedback inside the existing control or validation area.
- Reserve full-page error states for failures that prevent the page from serving its purpose.
- Keep the same failure class worded consistently across dialogs, toasts, forms, and pages.

## Verification

- Search the UI for direct rendering of `error.message`, serialized exceptions, request IDs, stack traces, provider responses, and framework names.
- Test known failure classes plus an unknown fallback.
- Confirm production error boundaries show product copy while diagnostics still receive the original error through the approved logging path.
