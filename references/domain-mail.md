# Domain Mail

The alias on the product domain receives and sends through a free router and relay, delivering into a monitored Gmail. The repository shows only the alias. Everything here is mail-layer setup that can change without touching the site.

Default picks, each swappable: Cloudflare Email Routing receives, a Gmail filter sorts, and SMTP2GO on its free plan relays outbound mail.

## Phase Order

1. Receiving: route the alias to Gmail.
2. Filtering: label routed mail and keep it out of Spam.
3. Sending: send and reply as the alias from Gmail.

Receiving and filtering complete a receiving-only setup. Add sending when replying as the alias matters. The order is load-bearing: the relay emails its account activation and later sign-in verifications to the alias, and Gmail's send-as confirmation goes there too, so routing must be live before sending starts and must stay live after.

## Receiving

- Check the zone first. Existing MX records mean the domain already receives somewhere, and enabling routing would break that.
- Deliver to a monitored Gmail. A dedicated per-product Gmail works, and so does the owner's main Gmail, because the filter keeps routed mail labeled and separated.
- Verify the Gmail as a destination address. Destinations are account-scoped, so one already verified for another domain is usable at once.
- Create a rule for the alias local part that sends to the verified Gmail.
- Apply the DNS records the router provides and enable routing. The rule alone delivers nothing until this step runs. Expect three MX records, an SPF TXT, and a DKIM TXT, managed and locked by the router.
- Leave the catch-all disabled with action Drop. Only named aliases deliver.

Receiving is done when a test email from an unrelated account shows as Forwarded in the routing overview and arrives in the Gmail inbox, labeled once filtering exists.

## Filtering

Gmail treats routed mail as ordinary inbound, so without a filter it can land in Spam and blends into the inbox. Create one filter per alias: match `to:` the alias, apply a label named exactly the full alias address, and check Never send it to Spam. The label list then reads as an inventory of live aliases. The filter does not reach conversations already in Spam or Trash.

## Sending

Gmail cannot send as a custom-domain address on its own. Its From menu offers only addresses added through Send mail as, and adding one requires SMTP server credentials. Without a relay, every reply comes from the personal Gmail.

- Give each product its own relay account, with the product alias as its login. The alias inbox then receives that account's activation and sign-in mail, and no product shares another's quota or credentials.
- Add the domain as a verified sender domain with the manual DNS setup. The automatic setup grants the relay write access to the zone. Manual is three CNAME records.
- Verify the domain once the records resolve on a public resolver, and expect the sender list to read Verified.
- Create an SMTP user under the account, accepting the suggested username. Gmail holds only this SMTP user's credentials, never the account login. The settings are server `mail.smtp2go.com`, port 587, TLS.
- In Gmail, add the alias under Accounts and Import with Treat as alias checked. Gmail prefills the inbound mail host and the alias local part as SMTP server and username, and both are wrong. Replace them with the SMTP user's values.
- Confirm the address through the link Gmail sends to the alias.
- Set the default address for new mail, and set replies to come from the address the message was sent to, so a sender always sees the address they wrote to. Reply behavior is account-wide, not per alias.
