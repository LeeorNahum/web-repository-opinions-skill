Wrote [docs/upload-design.md](docs/upload-design.md) with transport contracts and assumptions: signed direct uploads for HTTP/CLI, fetchable HTTPS URLs for MCP, and no inline base64.

Updated the MCP tool to reject inaccessible paths and require confirmed completion before reporting success. Added regression tests; all six subtests and strict TypeScript checking pass.

URL imports return `upload_unavailable` until the product API adapter is implemented.

Execution policy blocked cleanup; temporary `.upload-verification` dependencies and the `node_modules` junction remain inside the workspace.