# Cobblebook

Cobblebook is a hosted photo-book maker. A book holds pages and the photos placed on them. People edit books in the browser, through the public API, and through an MCP connection, and they order printed copies.

## Plans

| Allowance | Free | Pro ($8/month) |
| --- | ---: | ---: |
| Books | 25 | 60 |
| One uploaded photo | 40 MB | 120 MB |
| Total storage | 1.5 GB | 4 GB |

Deleted books go to Trash for 14 days, then are removed permanently.

## Decided

- Billing provider owns subscription truth. Plan limits are constants in code.

## The case that prompted this

Pro cancellations take effect at the end of the paid period. A typical cancelling user has 40 books, 2.6 GB stored (300 MB of it in Trash), and fifteen photos between 60 and 110 MB each.
