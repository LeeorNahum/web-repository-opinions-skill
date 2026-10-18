Updated [docs/mcp-tools.md](docs/mcp-tools.md) with three tools:

- `search_pages`: indexed content search with bounded, paginated results.
- `order_prints`: Editor-only ordering with a spending ceiling and durable duplicate protection.
- `read_print_order`: read-only status lookup after timeouts.

Documented assumptions about search matching, print format, limits, and order visibility, plus why three tools suffice.

Only the catalog changed. `git diff --check` passed.