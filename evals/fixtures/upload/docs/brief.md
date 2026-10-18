# Kitepost

Kitepost is a hosted image board. A board holds images and short captions, and has a public share link.

## Surfaces

- Browser app at `app.kitepost.example`. Drag-and-drop upload signs a direct PUT to object storage, the browser uploads the bytes, then calls finalize. This works and customers like it.
- Public HTTP API at `api.kitepost.example/v1`, used by scripts and integrations, authenticated with personal API keys.
- A small CLI, `npx kitepost`, that people run on their own machines and in CI.
- A remote MCP server at `mcp.kitepost.example/mcp`, connected from hosted chat assistants and from coding agents. Most of these agents run in a hosted sandbox or a chat app, not on the user's machine.

## Limits

- One image: 20 MB. Accepted types: PNG, JPEG, WebP, GIF.
- Storage per account: 2 GB on the free plan.

## Decided

- Original bytes are stored as uploaded, never recompressed.
- Every surface goes through the same product API and the same authorization.
