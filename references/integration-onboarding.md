# Integration Onboarding

When a user connects one of their own external systems through the product UI, make the connection flow guided, validated, and safe before anything is saved.

- Offer a picker of the providers you support, shown as recognizable logos. Selecting one presets the connection fields to that provider's known shape, so the common case is a click rather than a hand-built form. Keep the list to providers you have verified.
- Always offer a sanitized custom option for an unlisted provider. Normalize what the user enters (enforce the expected scheme, repair common mistakes, strip stray characters) rather than rejecting a nearly-correct value.
- Validate the connection before saving it. Make a real, read-only check with the supplied credentials and surface a clear pass or fail, so a wrong credential is caught at connect time, not on first use. Store what the check learns about the connection so the product offers only what it actually supports.
- When a protocol authenticates a peer by a key pinned on first use, present the observed key for the user to confirm, then pin it, so a later mismatch fails closed instead of connecting elsewhere silently.
- Keep the credential out of the client and out of any URL. It is entered once, held server-side, and used only to open the connection.
