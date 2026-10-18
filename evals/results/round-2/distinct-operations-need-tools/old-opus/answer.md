I added two tools to `docs/mcp-tools.md`, so the catalog goes from five tools to seven, one for each of the two requests. Each new tool has a short section underneath that spells out how it behaves. This only changes the document; I didn't commit it.

- **`search_pages { query, folder?, cursor?, limit? }`**: finds pages by their content, across the whole workspace or under one folder. It returns a ranked list of paths, titles and short snippets showing the matches, not whole pages. The agent then uses `read_page` on the pages it wants. It changes nothing.
- **`order_prints { idempotency_key, paths[], copies, ship_to }`**: places one print order, charges the card on file and ships one package. Only Editors can use it.

**Decisions I made:**
- **Search is its own tool, not an option on `list_pages`.** It needs a different scope (all subfolders), different ordering (by relevance) and a different result (snippets). Bolting it onto `list_pages` would make that tool do two different jobs depending on one optional argument, which agents get wrong more often than choosing between two tools.
- **No price-quote or order-status tool.** The order result already reports the amount charged and an order ID. If teams need a price before ordering, or shipping tracking, `quote_prints` or `get_print_order` can be added later.
- **Duplicate orders are prevented with a required `idempotency_key`.** A retry with the same key returns the original order and never charges or ships twice. Reusing a key with different arguments is refused. I didn't dedupe on order contents instead, because that would block a team that deliberately orders the same set twice.
- **An order is all or nothing.** If any page is missing, the address is invalid, or there's no card on file, nothing is charged. The card is charged only after the print partner accepts the order.
- **Viewers can see the tool but are refused when they call it.** The error tells them an Editor has to place the order. Many agent hosts cache the tool list when they first connect, so it's better to show everyone the same list and check the role on each call.

**Numbers and details I assumed (please check):**
- Search matches every word, ignoring case, and treats a double-quoted part as an exact phrase. Title matches rank above body matches. Each result has up to 3 snippets, with 20 results per page by default and 50 at most. Pages in Trash are never returned.
- An order allows 1–200 pages and 1–500 copies. Pages print in the order listed, as they read when the order is placed.
- The shipping address is passed with each order; I assumed workspaces have no saved address. The country is a two-letter code (e.g. US). Each order ships to a single address.
- Searching the full text of all 50,000 pages means storing a search index. The index has to stay current as pages are edited and drop pages when they're deleted.