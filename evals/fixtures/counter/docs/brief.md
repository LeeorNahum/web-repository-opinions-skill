# Quillstack

Quillstack is a documentation workspace for teams. Pages are Markdown files in folders. Agents already maintain pages through the MCP tools listed in `docs/mcp-tools.md`.

## New requests

1. Agents need to find pages by their content. A workspace can hold up to 50,000 pages. Today an agent has to list folders and read pages one at a time to find where a term is used.
2. Teams want their agent to order printed, bound copies of a set of pages for workshops. An order charges the workspace's card on file and ships a physical package. Agent hosts retry tool calls after network timeouts, and we have seen duplicate calls.

## Decided

- Printing is fulfilled by a print partner's API, priced per copy.
- Editors may order prints, Viewers may not.
