# Domain Mail

Every product gets addresses on its own domain, hosted where its owner lives. A person's own products share that person's one hosted mailbox seat, each product domain added as a secondary domain on it. A company, project, or legal entity gets its own workspace on its own domain, so it can be handed over, staffed, or closed without touching anyone's personal mail. Either way the service receives each domain's mail through its own MX records and sends as any alias natively, so a reply from a product address needs no relay and no per-alias credential.

- Route each person-facing alias into the person's own mailbox, or forward it from the hosted seat, and read, answer, and send as the alias from there, through the mailbox provider's own servers rather than a third-party relay, so mail leaves signed with the product domain's DKIM and passes DMARC.
- A product address sends under the product's name alone, set as the display name on its send-as entry. Where the provider requires a first and last name on an account that is not a person, use the product name and `Team`.
- To add a product, add the domain to its owner's seat or workspace, publish its MX, SPF, DKIM, and DMARC records in DNS, with DMARC at `p=quarantine`, turn DKIM signing on at the provider, and then add the alias. Where the provider offers the DKIM key only later, add the alias without waiting, then publish DKIM and turn signing on.
- Retire an alias when its product ends.
- An alias is ready once a message from outside reaches it and a message from it reaches an outside mailbox with DKIM signed by the product domain and SPF and DMARC passing.
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
