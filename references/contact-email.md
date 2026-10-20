# Contact Email

The public contact address is an alias on the product domain, never a personal mailbox.

- Default the alias to `contact@` on a product domain, one general alias per product rather than a spread of role addresses that all reach the same person. A personal domain uses the owner's first name instead.
- A personal Gmail or other private mailbox never appears in page copy, code, manifests, committed config, or public profiles.
- The alias lives in one code constant per repository, and every surface that shows an address reads that constant. Where the alias delivers is a mail-layer routing decision that can change without touching the site.
- A contact address is not optional for a public product: a privacy policy with no way to reach its owner is defective, and provider verifications check for one.
- On the site, its one home is a contact page at `/contact`: the alias as a `mailto:` link, and a short line naming what this product's readers write about. Any other page that would show the address, a legal page or a page in the signed-in app included, links to `/contact` instead.
- Give a field that asks for a support URL, such as a directory or marketplace listing's, the `/contact` URL, a route the product owns and keeps serving. Where the address itself is what the reader needs, such as a field that accepts only an email address, use the alias itself.

Put the alias on any surface, the contact page included, only after it receives mail from outside. A dead contact address is worse than none.
