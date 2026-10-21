# Domain Mail

Every product gets addresses on its own domain. When one owner runs several products, host all of them in one hosted mailbox service under one seat, never one mailbox, one relay, or one workspace per product. The service holds each product domain as a secondary domain on the one account, receives that domain's mail through its own MX records, and sends as any alias natively, so a reply from a product address needs no relay and no per-alias credential. A product shared with a cofounder, or meant to become its own company, gets its own workspace instead, with one shared login for the company address until each person needs their own, so its mail and accounts belong to the product rather than to one person's seat.

- Route each person-facing alias into the person's own mailbox, or forward it from the hosted seat, and read, answer, and send as the alias from there. An identity that a test reads gets its own inbox on the seat.
- Host each alias as an address the mailbox provider recognizes as its own, so reading and sending as it need no external relay.
- When the person reads mail in a personal mailbox at the same provider, add each alias there as a send-as address that sends through the provider's own SMTP server, signed in as the seat with an app password. Mail then leaves signed with the product domain's DKIM and passes DMARC, with no third-party relay.
- Adding a product is two steps: add the domain to the seat and publish its MX, SPF, DKIM, and DMARC records in DNS, with DMARC at `p=quarantine`, then add the alias. Retire an alias when its product ends.
- An alias is ready once a message from outside reaches it and a message from it reaches an outside mailbox with DKIM signed by the product domain and SPF and DMARC passing.
- Filtering: one filter per alias in the reading mailbox, labeled with the full address, never sent to spam, so product mail is visible and separable.
- Application mail, the messages a product sends by itself, goes through a sending relay with the domain verified and DKIM published, with credentials only in that product's server environment. It never uses the person's mailbox or a person's alias as its sender.
- No mail credential of any kind enters a repository. The seat's credentials, the relay's credentials, and DNS access live where the environment contract says secrets live.
