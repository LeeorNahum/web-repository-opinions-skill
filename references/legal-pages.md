# Legal Pages

A public product needs trust pages, and several providers require them before they will approve sign-in, payments, or listings. Treat them as required surface, not optional content.

Default routes, served at the site origin:

```text
/privacy
/terms
```

- Always provide a privacy policy at `/privacy` and terms of service at `/terms` on the public site, on the same origin as the homepage they describe and with no auth wall, since verifiers and crawlers must reach them.
- Link both from the homepage, usually in the footer, so they are reachable without login.

Some providers, such as a Google OAuth consent screen, will not verify an app until a publicly reachable home page, privacy policy, and terms page exist and are linked. Create the routes early so sign-in works in testing, and fill real content before requesting verification.

The privacy policy must describe what user data is accessed, how it is used, stored, and shared, and must state that use is limited to what is described.

Write both pages as a consumer product's own website pages: short sections under plain headings, addressed to the visitor, with no tables and a "Last updated" date at the top. The product is the operator, named on its own. Say what happens to the visitor's data rather than how the code handles it, and name third parties by role, except an AI model provider, which is named outright.

Before writing, read two or three comparable products' published pages, shape the draft on them, and hold the draft against them as the check. Publish only statements the shipped code backs. The site's source is the pages' only copy.

Both pages carry a Contact section.
