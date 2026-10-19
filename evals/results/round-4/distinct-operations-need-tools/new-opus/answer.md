I added two tools to `docs/mcp-tools.md`, which brings the catalog from five tools to seven. I didn't commit anything.

**`search_pages { query, folder?, cursor?, limit? }`**
- **Why a new tool:** listing folders and reading pages one at a time can't work across 50,000 pages. Search is something agents already know how to use.
- **What it returns:** each matching page's path, title, and up to three short snippets with line numbers, so the agent can go straight to `read_page` or `edit_page`. It never returns whole pages.
- **Paging:** it pages the same way as `list_pages`, at most 100 results per page.
- **Who and what:** it doesn't change anything, it skips Trash, and any member who can read the workspace can use it, Viewers included.

**`order_prints { paths[], copies, ship_to, idempotency_key }`**
- **Why a separate tool:** an order charges a card and ships a package, so it needs its own tool and its own permission. Only Editors can use it; anyone else gets a `forbidden` error.
- **`idempotency_key` is required:** the brief says agent hosts retry after timeouts, and the server can't otherwise tell a retry from a second real order.
- **How the key works:** the server claims the key before charging. A repeat or simultaneous call with the same key gets the first call's result, so there's never a second charge or shipment. Reusing a key for a different order is refused.
- **Uncertain outcomes:** if the server can't confirm the payment, it returns `unknown` and doesn't retry by itself. Calling again with the same key reports what actually happened.
- **Errors:** it returns clear errors for missing pages, limits, a bad address, no card on file or a declined card, and a reused key. None of these charge anything.
- **No confirmation step:** there's no "are you sure" argument. Permission is checked on the server for every call.

**What I assumed** (also listed in an "Assumptions pending owner review" section at the end of the doc):
1. **Search matching:** search looks for the query as one exact phrase in page content and titles, ignoring case. It doesn't support patterns (regular expressions), relevance ranking or meaning-based search.
2. **No price check:** there's no tool to get a quote before ordering. The price comes back with the order. If agents need to show the cost first, a read-only quote tool is the obvious next addition.
3. **No tracking or cancel:** the brief doesn't ask for order status or cancellation, so I didn't add tools for them.
4. **Address per order:** the agent gives the shipping address with each order. There's no saved workspace address.
5. **What gets printed:** each order is one bound volume, with pages in the order listed and their content as it is when the order is placed. `copies` is how many volumes to print.
6. **Limits:** 200 pages and 500 copies per order, and the server remembers idempotency keys for 7 days. I picked these numbers; nothing in the brief sets them.
7. **Roles:** I assumed Owners and Admins can also order, along with Editors.