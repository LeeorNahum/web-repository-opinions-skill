# DNS

Treat DNS as part of the runtime contract. Records, proxy mode, and comments are all intentional.

Proxy mode:

- Keep third-party service records as DNS only (unproxied): hosting platform CNAMEs, auth provider frontend and portal CNAMEs, and email authentication records. Proxying breaks certificate issuance and email signature verification for these services.
- Proxying is fine for A and AAAA records pointing at your own origin servers.

Email authentication record names are literal, including underscores and dots. Enter them exactly as the provider shows them.

Every record carries a comment in one format:

```text
Provider - Product Purpose (Scope)
```

- Provider is the service the record points at or is verified by.
- Product Purpose is the product plus what this specific record is for: the surface it serves, the connection it enables, or the verification it proves.
- Scope is the deployment stage in parentheses, omitted for production.

So a single record reads as one phrase that says who owns it, what it does, and which stage it belongs to. Apply the comment to every record created during domain, verification, or provider setup, so the zone stays self-documenting.

Ask before changing any production DNS record.
