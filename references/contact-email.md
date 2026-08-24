# Contact Email

The public contact address is an alias on the product domain, never a personal mailbox.

- Default the alias to `contact@` on a product domain. A personal domain uses the owner's first name instead.
- A personal Gmail or other private mailbox never appears in page copy, code, manifests, committed config, or public profiles. A page that needs a reachable human shows the alias.
- The alias lives in one code constant per repository, and every surface that shows an address reads that constant. Where the alias delivers is a mail-layer routing decision that can change without touching the site.
- A contact address is not optional for a public product: a privacy policy with no way to reach its owner is defective, provider verifications check for one, and a product without a public issue tracker has no other support surface.
- Its home is the two required trust pages: a Contact section on the privacy and terms pages, linking the alias as `mailto:`. That placement is sufficient. No dedicated contact page and no address scattered across other surfaces unless the product genuinely outgrows it.

Creating the alias, routing it to a monitored inbox, filtering it there, and enabling reply-from-alias sending are owned by the `email-setup-opinions` skill. This file owns only what the repository shows.

Verify from outside before shipping a page that carries the alias: mail sent to it from an unrelated account must arrive at the monitored inbox. A dead contact address on a trust page is worse than none.
