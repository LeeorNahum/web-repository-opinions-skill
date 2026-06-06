# App Surface

The signed-in app owns the core workflow and private state. It should not carry public SEO routes without a deliberate reason.

Responsibilities:

- Authentication and session
- Private data and product workflows
- Account and billing
- Admin
- Provider-backed actions
- Private routing

The app surface feels like its core object first. Secondary features attach to that object; they do not turn the home screen into a generic dashboard of panels.

Hide actions a user cannot take instead of showing disabled or error-producing controls. Keep the primary path on every screen obvious and unblocked.
