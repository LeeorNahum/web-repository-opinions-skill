# Physical Commerce

A web product that sells physical goods keeps its own site and hands the commerce to a commerce platform. The platform is a back office and a checkout, never the thing that renders pages.

Default: Shopify, reached through its Storefront API from the product's own app. Swap the platform, keep the paradigm.

## Split

- The site owns every page a visitor reads: home, product pages, collections, about, policies, the cart drawer. It is the product's own code, deployed like any other public surface.
- The platform owns the catalog, prices, inventory, the cart's line items, checkout, payments, tax, shipping, discounts, order records, and order email. Merchants edit there and the site reflects it.
- The only navigation off the site is the checkout button, which sends the buyer to the platform's hosted checkout on a subdomain of the site's domain. Nothing else lives on that subdomain.

Do not build the site inside the platform's theme system. A theme repo has to be the root of its own repository to deploy, it renders in the platform's template language, and every visual change routes through the platform. That couples the whole site to the one piece that should stay a black box.

Do not link out to a platform-hosted storefront for the shop pages either. Two apps mean two sessions, and the cart and any sign-in break at the seam.

## Wiring

- Access is a headless storefront token pair issued by the platform, public for the browser, private for the server, with permissions scoped to what the site reads.
- Products and collections are read through the storefront API at build or on revalidation, never copied into the site's own database.
- Every line of editable copy on the site lives in the platform's custom content objects, which the merchant edits as plain fields. The site reads them through the same API. This is what makes "edit it yourself and the site updates" true without building an admin surface.
- Legal pages come from the platform's own policy templates and render on the site's domain at its own legal-page routes.
- The cart is created and updated through the platform's cart API, its id kept in a cookie. Fetch the checkout URL only when the buyer clicks checkout, and redirect.
- Freshness is time-based revalidation, or the platform's product and collection webhooks hitting a secret-guarded revalidate route. Never a manual redeploy.
- Guest checkout by default. Customer accounts, if ever wanted, are the platform's hosted pages on the checkout subdomain, not a sign-in built into the site.

## Domains

The site is the apex, with `www` redirecting to it. The platform's primary domain is the checkout subdomain, pointed at the platform by CNAME, so its checkout URLs carry the site's domain rather than the platform's. Verify the host of the first real checkout URL the day the domain connects.

## Hosting

A store is commercial. Never place it on a hosting plan whose terms exclude commercial use.

Ask before connecting a live domain, changing the platform's primary domain, or touching payment settings.
