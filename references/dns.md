# DNS

Treat DNS as part of the runtime contract. Records, proxy mode, and comments are all intentional.

Proxy mode:

- Keep third-party service records DNS only (unproxied) by default: hosting platform CNAMEs, auth provider frontend and portal CNAMEs, and email authentication records. Proxy one only where its provider documents support for proxying.
- Keep domain-verification CNAMEs, DKIM records, and any record a provider validates by DNS lookup DNS only in every case, because a proxied record answers with the proxy's addresses instead of the target that check reads.
- Proxying is fine for A and AAAA records pointing at your own origin servers.

Email authentication record names are literal, including underscores and dots. Enter them exactly as the provider shows them.

Every record carries a comment in one format:

```text
Provider - Product Purpose (Scope)
```

- Provider is the service the record points at or is verified by.
- Product Purpose is the product plus what this specific record is for: the surface it serves, the connection it enables, or the verification it proves.
- Scope is the deployment stage in parentheses. Include it on any record that serves a single stage, production included. Leave it off only when one shared record is reused unchanged across every stage.
- Keep each comment within 100 characters.

So a single record reads as one phrase that says who owns it, what it does, and which stage it belongs to. Apply the comment to every record created during domain, verification, or provider setup, so the zone stays self-documenting.

Ask before changing any production DNS record.
