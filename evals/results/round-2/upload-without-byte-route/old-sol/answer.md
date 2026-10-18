Wrote [docs/upload-design.md](docs/upload-design.md) with decisions and assumptions: MCP uses downloadable HTTPS URLs; HTTP API accepts multipart files; CLI streams local files; browser keeps signed PUT uploads.

Updated the MCP tool to reject paths/base64, delegate to the product API, and require finalized image metadata before reporting success.

Strict TypeScript compilation and 20 mocked checks passed. API/CLI implementation and runtime wiring remain documented follow-up work; this repository contains only adapter stubs.