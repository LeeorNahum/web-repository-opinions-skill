# Domain Mail

Every product gets addresses on its own domain, hosted where its owner lives. A person's own products share that person's one hosted mailbox seat, each product domain added as a secondary domain on it. A company, project, or legal entity gets its own workspace on its own domain, so it can be handed over, staffed, or closed without touching anyone's personal mail. Either way the service receives each domain's mail through its own MX records and sends as any alias natively, so a reply from a product address needs no relay and no per-alias credential.

- One general alias per product on the product's domain. Add a second alias only when a distinct purpose needs a distinct address, such as a test or reviewer identity.
- A product address sends under the product's name alone, set as the display name on its send-as entry. Where the provider requires a first and last name on an account that is not a person, use the product name and `Team`.
- The person's own mailbox stays the place a product alias is read and answered. Route the product aliases into it, or forward them from the hosted seat, and send as the alias from there. A relay that lets a personal webmail send as third-party addresses is not a durable path, because webmail providers restrict and retire it, so the aliases must be hosted addresses the mailbox provider recognizes as its own.
- Adding a product is two steps: add the domain to its owner's seat or workspace and publish its MX, SPF, and DKIM records in DNS, then add the alias. Retire an alias when its product ends.
- Filtering: one filter per alias in the reading mailbox, labeled with the full address, never sent to spam, so product mail is visible and separable.
- Application mail, the messages a product sends by itself, goes through a sending relay with the domain verified and DKIM published, with credentials only in that product's server environment. It never uses the person's mailbox or a person's alias as its sender.
- No mail credential of any kind enters a repository. The seat's credentials, the relay's credentials, and DNS access live where the environment contract says secrets live.
