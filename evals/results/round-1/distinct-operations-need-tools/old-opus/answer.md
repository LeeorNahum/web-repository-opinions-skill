I added two tools to `docs/mcp-tools.md`, `search_pages` and `order_prints`, plus a short section for each covering how it behaves. The other five tools are unchanged. Nothing is committed and I didn't touch `docs/brief.md`.

## Why two tools and not fewer
- **Search is its own tool.** I could have added a `query?` argument to `list_pages`, but that would make one tool do two different jobs. Listing walks one folder in order; search covers the whole workspace, ranks results and returns snippets. Agents choose the wrong argument more often than the wrong tool. Search returns short snippets rather than full pages, so it doesn't flood the agent's context; `read_page` stays the way to get content.
- **Printing is one tool.** Its result includes the order's status and total. A retry with the same key returns the current state of the original order, which also covers the timeout case. So I left out a separate price-quote tool, an order-status tool and a confirmation flag.

## Calls I made (please check)
1. **Duplicate orders:** `order_prints` requires an `idempotency_key`. When a host retries a call it resends the same key, so the workspace isn't charged twice. Reusing a key with a different order is refused.
   - I made it required rather than optional, because an optional key would still let duplicates through.
   - I didn't try to spot duplicates by matching arguments, because that would block a team that really wants the same order twice.
2. **What counts as "placed":** the tool returns `placed` once the card is charged and the print partner has accepted the order, or `processing` until then. Shipping and tracking status after that aren't exposed, since the brief doesn't ask for them.
3. **Shipping address is an argument.** The brief doesn't say where it comes from. If there should be a saved workspace address, `ship_to` could become optional, or be dropped.
4. **No price check before ordering.** Agents learn the cost from `total` after the order goes through, and the host's own approval step is the human check. If you want agents to see the price first, a read-only `quote_prints` would be the one tool to add.
5. **Pages are identified by path**, like every other tool in the catalog. An order is all or nothing: if any path is missing, nothing is charged. Pages print as they read when the order is placed, bound in the order listed.
6. **Limits are left open.** The most pages and copies per order should come from the print partner's limits. The refusal will name the limit once it's set.
7. **Roles:** every caller sees the same list of tools, and the server checks the Editor role on each call. A Viewer can see `order_prints` but gets a clear refusal, rather than having it hidden.
8. **Search matching:** case-insensitive, every word must appear, `"quoted phrases"` match exactly, best match first, 20 per page. Pages in Trash are excluded, and results include only pages the caller can read.
   - This means indexing the full text of up to 50,000 pages and keeping that index up to date on every write, edit and delete.