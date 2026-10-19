I added two tools to `docs/mcp-tools.md`, one for each request in the brief, and wrote out the full behavior for each. Nothing is committed, and there's no code yet; the repo only has the docs.

## The two tools

**`search_pages { query, folder?, cursor?, limit? }`** lets agents find pages by their content.
- It's read-only and pages through results the same way `list_pages` does (20 per page, up to 50).
- It searches page titles and text, ignoring case. A word search needs every word to appear; a quoted search matches the exact phrase.
- Each result is `{ path, title, snippet }`, ranked by relevance, so agents don't pull whole pages into their context. They call `read_page` for the pages they actually need.
- Pages in Trash, or pages the caller can't read, never show up. A page becomes searchable as soon as its write returns.

**`order_prints { paths[], copies, ship_to, idempotency_key }`** orders the bound copies.
- **Duplicate calls:** `idempotency_key` is required. When a host retries after a timeout it resends the same arguments, so it sends the same key. A retry gets back the original order marked `replayed: true`, with no second charge or shipment. Reusing a key with different arguments is refused, and a retry that arrives while the first call is still running waits for that call instead of starting another order.
- **Who can order:** only Editors. The server enforces this on each call and refuses Viewers with a clear message. The tool isn't hidden from them.
- **Missing pages:** the order is all-or-nothing. If any page is missing, it fails before anything is charged and lists every bad path.
- **Payment:** the card is held first, the order goes to the print partner, and the charge goes through only once the partner accepts it. If anything fails, the card isn't charged, and the agent gets a plain message rather than raw payment or partner errors.
- **Result:** the order ID, price per copy, total and status.

I kept the catalog to these two. Instead of a confirmation flag or a separate "check the outcome" tool, an agent that's unsure whether an order went through repeats the call with the same key, and the answer it gets is the true outcome.

## What I assumed

These are also listed at the bottom of the doc under "Assumptions pending owner review":
1. Each copy is one bound book with the listed pages in the order given, printed as they are when the order is placed.
2. **The limits are placeholders:** up to 200 pages per order, 1–500 copies, and keys kept for 30 days. They should change once we know the print partner's limits and how much we're willing to let one order spend.
3. **No price quote before ordering.** The price comes back with the order. If you want agents to show a price before charging, the clean way is to add a read-only `quote_prints` tool.
4. **No tools to check status, track or cancel an order.** A `get_print_order` tool can be added later if agents need to follow shipping.
5. One shipping address per order, typed into the call. There's no saved workspace address.
6. **Pages are identified by path**, like the rest of the catalog. If a page is moved between finding it and ordering it, the order could fail or print the wrong page. If pages ever get permanent IDs, `order_prints` should use those instead.
7. **Search indexes the full text of every page**, as the brief asks, for up to 50,000 pages per workspace. That means storing and updating that index, and removing pages from it when they're deleted.