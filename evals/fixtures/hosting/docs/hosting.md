# How apps are served today

- A request to `<name>.plinth.example` is answered by our edge, which looks up the app and streams its files from object storage. The person's `index.html` is the top-level document.
- `app.plinth.example` serves the signed-in product.
- Private apps check the auth provider's session cookie at the edge before serving.

## Constraint

Beta opens next week. Infrastructure is in a change freeze until the beta ends in about two months: no new domains, DNS zones, or certificates before then.
