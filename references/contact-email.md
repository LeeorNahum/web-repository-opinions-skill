# Contact Email

The public contact address is on the product domain, never a personal mailbox.

- Default the address to `contact@` on a product domain, one general address per product rather than a spread of role addresses that all reach the same person. A personal domain uses the owner's first name instead, which is the owner's own account and so also fits a consent screen.
- A personal Gmail or other private mailbox never appears in page copy, code, manifests, committed config, public profiles, consent screens, or provider support fields.
- Where a consent screen accepts as its support address only the editor's own address or a group the editor owns, make the contact address a group: owned by the person who fills in that screen, delivering to the owner's mailbox, with outside senders allowed to post. Create it as a group from the start, because an address cannot be both an alias and a group and converting a live alias pauses its delivery. The same address fills each provider's support field.
- A purpose address, such as a reviewer or testing identity, is a plain alias, since no public surface shows it.
- The address lives in one code constant per repository, and every surface that shows an address reads that constant. Where it delivers is a mail-layer routing decision that can change without touching the site.
- A contact address is not optional for a public product: a privacy policy with no way to reach its owner is defective, and provider verifications check for one.
- On the site, its one home is a contact page at `/contact`: the address as a `mailto:` link, and a short line naming what this product's readers write about. Any other page that would show the address, a legal page or a page in the signed-in app included, links to `/contact` instead.
- Give a field that asks for a support URL, such as a directory or marketplace listing's, the `/contact` URL, a route the product owns and keeps serving. Where the address itself is what the reader needs, such as a field that accepts only an email address, use the address itself.

Put the address on any surface, the contact page included, only after it receives mail from an outside account. A dead contact address is worse than none.
