# Domain Mail

Every product gets addresses on its own domain, hosted where its owner lives. A person's own products share that person's one hosted mailbox seat, each product domain added as a secondary domain on it. A company, project, or legal entity gets its own workspace on its own domain, so it can be handed over, staffed, or closed without touching anyone's personal mail. Either way the service receives each domain's mail through its own MX records and sends as any alias natively, so a reply from a product address needs no relay and no per-alias credential.

- One general alias per product on the product's domain. Add a second alias only when a distinct purpose needs a distinct address, such as a test or reviewer identity.
- A product address sends under the product's name alone, set as the display name on its send-as entry. Where the provider requires a first and last name on an account that is not a person, use the product name and `Team`.
- The person's own mailbox stays the place a product alias is read and answered. Route the product aliases into it, or forward them from the hosted seat, and send as the alias from there. A relay that lets a personal webmail send as third-party addresses is not a durable path, because webmail providers restrict and retire it, so the aliases must be hosted addresses the mailbox provider recognizes as its own.
- Adding a product is two steps: add the domain to its owner's seat or workspace and publish its MX, SPF, and DKIM records in DNS and turn DKIM signing on at the provider, then add the alias. Where the provider offers the DKIM key only later, add the alias without waiting, then publish DKIM and turn signing on. Retire an alias when its product ends.
- Filtering: one filter per alias in the reading mailbox, labeled with the full address, never sent to spam, so product mail is visible and separable.
- Application mail, the messages a product sends by itself, goes through a sending relay with the domain verified and DKIM published, with credentials only in that product's server environment. It never uses the person's mailbox or a person's alias as its sender.
- No mail credential of any kind enters a repository. The seat's credentials, the relay's credentials, and DNS access live where the environment contract says secrets live.

## Finish The Setup At The Provider

Mail that sends and receives is the midpoint of setting up a domain. In the same pass, finish these at the mailbox provider, wherever it offers them:

- **Account picture.** An account that stands for the product rather than a named person shows the product's square icon. Where the organization manages pictures, set it from the admin console.
- **Workspace logo.** The workspace shows the product's wide wordmark.
- **Footer.** Mail from the address closes with the product's name, the one line that says what it does, its contact address, and its site. Read a footer the provider suggests before accepting it, and replace whatever it could not fill or guessed wrong.
- **A verified send.** A message sent as the address, from the mailbox that answers it, reaches an outside mailbox and shows the product's name as its sender, with the footer beneath it.

A workspace of its own is the product's throughout, so all four apply. On a seat that serves several products, the picture, the logo, and an organization-wide footer are the owner's, so leave them. Where the workspace is the product's alone and the provider has an organization footer, set the footer there. Otherwise it is the signature on the address's send-as entry.

Fill what is empty and leave what somebody already set, export each image from the product's canonical brand asset, and have the person enter every password the console asks for.
