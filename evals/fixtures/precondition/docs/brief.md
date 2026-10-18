# Ledgerline

Ledgerline keeps shared price lists for wholesale suppliers. A price list is a JSON document of a few hundred rows.

## Public HTTP API v1

Partners' own systems integrate with `api.ledgerline.example/v1`, and many of them sync price lists unattended every few minutes. Our published contract, which partners have built against for two years:

- `GET /v1/price-lists/{id}` returns the document with an `ETag` header.
- `PUT /v1/price-lists/{id}` replaces the whole document and requires `If-Match` with that ETag. A stale ETag gets `412 Precondition Failed`.

Several partners, and our own staff in the browser app, often edit the same list during the same hour.

## Request

Partners keep asking for a way to change one row without sending the whole document.
