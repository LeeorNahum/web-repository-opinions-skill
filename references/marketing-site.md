# Marketing Site

The public site owns reach, not product complexity. It should not inherit signed-in app weight.

Responsibilities:

- SEO and discovery
- Marketing and product education
- Pricing
- Docs and help
- Legal pages
- Public links into the app

The public site should not carry private data, auth-gated workflows, or provider-backed actions, apart from a storefront's cart and its handoff to checkout. It links into the app. It does not become the app.

Keep public copy product-native and simple. Never expose internal, provider, or implementation language on a public page.

Separating the public site from the signed-in app improves build size, security posture, routing clarity, and future deployment flexibility.

## Header Link

The logo or wordmark in the header links to the site root path, `/`, rather than an in-page anchor. The root is the top of the page, it is the same destination from every page and every scroll depth, and it leaves no stray fragment in the address bar. Anchors are for sections, not for home.
