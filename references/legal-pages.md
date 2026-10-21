# Legal Pages

A public product's legal pages follow from what it does, and several providers require them before they will approve sign-in, payments, or listings. Treat a page whose trigger is met as required surface, not optional content. The triggers below are defaults. Whether the law of a given place requires a page, and what the page must say, is a lawyer's question.

Default routes, served at the site origin:

```text
/privacy
/terms
```

- Provide a privacy policy at `/privacy` when the product, or a service acting for it, collects anything that can be tied to a person, or when a provider it uses requires one. Analytics, forms, cookies, third-party embeds, and the host's request logs all count, so leave the page out only after confirming that nothing is collected.
- Provide terms of service at `/terms` when the product has accounts, payments, user content, or a public API, or when a provider it uses requires them. At sign-up and checkout, have the person agree to the linked terms, through the provider's own consent step where a provider renders that surface, because a footer link alone does not show agreement.
- Link each page the product has from the homepage, usually in the footer, so it is reachable without login. In the footer, order the legal links and the contact link Terms, Privacy, then any other legal page, then Contact, keeping only the pages the product has.
- Keep them publicly accessible with no auth wall, since verifiers and crawlers must reach them.
- Host them on the same domain as the homepage they describe.

Some providers, such as a Google OAuth consent screen, will not verify an app until a publicly reachable home page and a privacy policy exist and are linked, and they show a terms link when one is given. Create the needed routes early so sign-in works in testing, and fill real content before requesting verification.

For that verification, the privacy policy must describe what user data is accessed, how it is used, stored, and shared, and must state that use is limited to what is described.

Each legal page names who runs the product, a person or a legal entity, and carries a "Last updated" date that moves whenever its text changes in a way that matters to a reader. Privacy laws commonly require a notice to name who controls the data, some require the date it last changed, and terms need an identifiable party to bind.

Write each page for the visitor, in short sections under plain headings, with the "Last updated" date at the top. Say what happens to the visitor's data rather than how the code handles it. Name third parties by role, so swapping a vendor does not make the page false, and by name only where a law or a provider's policy requires it. Publish only statements the shipped code backs, and keep the legal text in the site's source alone, so no second copy drifts from what is published.
