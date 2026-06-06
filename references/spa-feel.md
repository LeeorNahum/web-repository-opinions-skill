# SPA Feel

A signed-in app should feel like one continuous application, not a series of full page loads, while keeping real URLs.

Achieve the feel with:

- Persistent layouts and shells that survive navigation
- Client-side navigation between routes
- Drawers, sheets, and modals for secondary flows instead of new pages
- A persistent element where it fits the product, such as a mini-player or active-object bar
- Optimistic and live updates so state feels immediate

Keep stable, shareable, deep-linkable URLs underneath. App feel is a navigation and state concern, not a reason to abandon addressable routes.

Do not fake the feel by hiding the URL or trapping the user in one route. Every meaningful view still has its own path.
