# Legal Pages

A public product needs trust pages, and several providers require them before they will approve sign-in, payments, or listings. Treat them as required surface, not optional content.

Default routes, served at the site origin:

```text
/privacy
/terms
```

- Always provide a privacy policy at `/privacy` and terms of service at `/terms` on the public site.
- Link both from the homepage, usually in the footer, so they are reachable without login.
- Keep them publicly accessible with no auth wall, since verifiers and crawlers must reach them.
- Host them on the same domain as the homepage they describe.

Some providers, such as a Google OAuth consent screen, will not verify an app until a publicly reachable home page, privacy policy, and terms page exist and are linked. Create the routes early so sign-in works in testing, and fill real content before requesting verification.

The privacy policy must describe what user data is accessed, how it is used, stored, and shared, and must state that use is limited to what is described.

Both pages carry the product's contact alias in a Contact section; `references/contact-email.md` owns what that address is.
