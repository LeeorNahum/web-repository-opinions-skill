I added two tools to `docs/mcp-tools.md`, so the catalog goes from five tools to seven. Nothing is committed; the change is in the working tree.

**`search_pages { query, folder?, cursor?, limit? }`** (read-only)
- Finds pages whose title or text contains the query, across the whole workspace or within one folder.
- Each result has the page's path, its title and up to 3 matching lines.
- It's paged like `list_pages` (20 per page, maximum 50), so 50,000 pages never flood the agent.
- I made this its own tool rather than adding a `query` option to `list_pages`. Searching content is a different job from browsing a folder, and agents pick the wrong option more often than the wrong tool.

**`order_prints { paths[], copies, ship_to, idempotency_key }`**
- It gets its own tool because it charges the card and ships a package.
- **Duplicate calls:** `idempotency_key` is required. A repeated call with the same key never charges or ships again; it returns the first call's order. The tool description tells agents to retry with the same key after a timeout. This is the one place a key is worth its cost, because only the caller can tell a retry from a new order.
- **Who can order:** Editors only, checked on the server for every call. Viewers get a clear refusal. Every agent sees the same tool list whatever its role.
- It returns the order ID, the pages it included, the amount charged and the order status.
- There's no confirmation argument. The host's approval step already covers that, and the tool has to work in unattended runs.

**What I assumed (please check):**
1. **Search matching:** search matches the exact phrase, ignoring case, with no wildcards or patterns. That's what "find where a term is used" needs. It means storing and indexing full page text and keeping it current on every write. Pages in Trash never match.
2. **What gets printed:** the pages are bound in the order listed, and their content is fixed at the moment the order is placed.
3. **Limits:** I picked 200 pages per order and 1–100 copies. These are placeholders; I don't know the print partner's real limits.
4. **Price:** I read "priced per copy" as a price per bound set, possibly depending on page count. There's no tool to get a price first; the order just reports what was charged. If you want agents to see the price before buying, the next step would be a `quote_prints` tool or an optional spending cap on `order_prints`.
5. **Order status:** there's no tool to look up an order later. To check on an order, an agent repeats the call with the same key. If agents need to track shipping, a read-only `get_print_order` would be the addition.
6. **Shipping address:** the shape is my guess (name, address lines, city, region, postal code, country). It should match whatever the print partner requires.
7. **Pages are named by path,** like the existing tools, since pages don't expose any other ID today.