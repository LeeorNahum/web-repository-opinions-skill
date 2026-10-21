# App Surface

The signed-in app owns the core workflow and private state. It serves its routes `noindex` and publishes no sitemap. A page meant to be found through search belongs to the public site.

Responsibilities:

- Authentication and session
- Private data and product workflows
- Account and billing
- Provider-backed actions
- Private routing

The app surface feels like its core object first. Its home route opens the primary object's list or workspace, with the create action on the first screen when users create that object. Summary numbers sit above or beside that list and take less than half of the first screen.
