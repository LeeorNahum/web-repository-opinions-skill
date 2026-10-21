# Physical Commerce

A web product that sells physical goods keeps its own site and hands the commerce to a commerce platform. The platform is a back office and a checkout, never the thing that renders pages.

Default: Shopify, reached through its Storefront API from the product's own app. Swap the platform, keep the paradigm.

## Split

- The site owns every page a visitor reads: home, product pages, collections, about, policies, the cart drawer. It is the product's own code, deployed like any other public surface.
- The platform owns the catalog, prices, inventory, the cart's line items, checkout, payments, tax, shipping, discounts, order records, and order email. Merchants edit there and the site reflects it.
- The only navigation off the site is the checkout button, which sends the buyer to the platform's hosted checkout on a subdomain of the site's domain. Nothing else lives on that subdomain.

Build the site as the product's own app, outside the platform's theme system. A theme renders in the platform's template language, and every visual change routes through the platform. That couples the whole site to the one piece that should stay a black box.

Serve the shop pages from the site too, so the cart and any sign-in stay in one app instead of breaking at the seam between two sessions.

## Wiring

- Access is a headless storefront token pair issued by the platform, public for the browser, private for the server, with permissions scoped to what the site reads.
- Products and collections are read through the storefront API at build or on revalidation, with the platform as their only store.
- Merchant-facing copy (page headlines, section text, announcements, and about content) lives in the platform's custom content objects, which the merchant edits as plain fields. The site reads them through the same API. Interface labels and error copy stay in code. This is what makes "edit it yourself and the site updates" true without building an admin surface.
- Legal pages come from the platform's own policy templates and render on the site's domain at its own legal-page routes.
- The cart is created and updated through the platform's cart API, its id kept in a cookie. Fetch the checkout URL only when the buyer clicks checkout, and redirect.
- Freshness is time-based revalidation, or the platform's product and collection webhooks hitting a secret-guarded revalidate route.
- Guest checkout by default. Customer accounts, if ever wanted, are the platform's hosted account pages on their own subdomain of the site's domain, and the site links to them rather than building sign-in.

## Domains

The platform's primary domain is the checkout subdomain, pointed at the platform by CNAME, so its checkout URLs carry the site's domain rather than the platform's. Verify the host of the first real checkout URL the day the domain connects.

Ask before connecting a live domain, changing the platform's primary domain, or touching payment settings.
