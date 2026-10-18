I added two tools to `docs/mcp-tools.md`, which brings the catalog to 7. I haven't committed the change.

- **`search_pages { query, folder?, cursor?, limit? }`**: a read-only search over page content and titles. Each result gives the page's path, title, match count and up to 3 matching lines with line numbers, so an agent can go straight to `read_page` or `edit_page`. It pages through results the same way `list_pages` does (default 20, maximum 100), which keeps results manageable across 50,000 pages.
- **`order_prints { paths[], copies, ship_to, idempotency_key }`**: charges the card on file and ships the printed copies. Only Editors can use it. Ordering is a separate tool because it costs real money, ships something physical and has its own permission. The idempotency key is required: if a host retries with the same key, the agent gets back the original order and nothing is charged again. Reusing a key with different arguments is refused. If anything is wrong (a missing page, a missing or declined card, or a caller who isn't an Editor), nothing is charged and the error says why.

**Left out to keep the catalog small:** a price-quote tool, an order status tool, cancellation, and a separate tool for saving a shipping address. The order result already reports the total charged.

**What I assumed** (also listed in a short "Assumptions to confirm" section at the end of the doc):
1. Search matches the exact phrase, ignoring case. It doesn't support regular expressions or meaning-based search.
2. Search covers every page's full text and skips pages in Trash. That means keeping a content index up to date on every write, edit and delete.
3. One copy is one bound book of all the listed pages, in the order given. An order either goes through completely or not at all.
4. Pages are printed as they are when the order is placed.
5. The agent supplies the shipping address on every order, because there's no saved workspace address yet.
6. Idempotency keys are kept separately for each workspace and last at least 24 hours.
7. The limits of 200 pages and 100 copies per order are placeholders until we know the print partner's limits.