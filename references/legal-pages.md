# Legal Pages

A public product's legal pages follow from what it does, and several providers require them before they will approve sign-in, payments, or listings. Treat a page whose trigger is met as required surface, not optional content. The triggers below are defaults. Whether the law of a given place requires a page, and what the page must say, is a lawyer's question.

Default routes, served at the site origin:

```text
/privacy
/terms
```

- Provide a privacy policy at `/privacy` when the product, or a service acting for it, collects anything that can be tied to a person, or when a provider it uses requires one. Analytics, forms, cookies, third-party embeds, and the host's request logs all count, so leave the page out only after confirming that nothing is collected.
- Provide terms of service at `/terms` when the product has accounts, payments, user content, or a public API, or when a provider it uses requires them. At sign-up and checkout, have the person agree to the linked terms, through the provider's own consent step where a provider renders that surface, because a footer link alone does not show agreement.
- Link each page the product has from the homepage, usually in the footer, so it is reachable without login.
- Keep them publicly accessible with no auth wall, since verifiers and crawlers must reach them.
- Host them on the same domain as the homepage they describe.

Some providers, such as a Google OAuth consent screen, will not verify an app until a publicly reachable home page and a privacy policy exist and are linked, and they show a terms link when one is given. Create the needed routes early so sign-in works in testing, and fill real content before requesting verification.

For that verification, the privacy policy must describe what user data is accessed, how it is used, stored, and shared, and must state that use is limited to what is described.

Each page carries the same product-domain contact alias in a Contact section.
