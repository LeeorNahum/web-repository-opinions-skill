# Badges

A badge is a small image with a link behind it, the one object that survives in a README and in every other Markdown surface that strips scripts, frames, and styling and keeps only images and links. It is how a public resource appears on a page the product does not control, so it carries the product's mark and takes its colors and type from the product's design tokens.

## What A Badge Shows

Two sizes, chosen by the caller, drawn from the same data as the resource's link preview card:

- Compact: the product mark and the resource's name.
- Large: the compact content plus the product name and the resource's one-line description.

What travels is the resource's name, its one-line description, the product mark, and the canonical public URL. Body content and the identity of the person who shared the resource stay on the page, because a badge in a README reaches a wider audience than the page it links to.

Text inside an SVG served through an image tag loads no web font. Name the product's face with a system fallback stack, size the badge from measured text widths so a long name cannot overflow it, and render a raster with the face embedded only when the type itself has to be exact.

## Endpoint

The badge lives one segment under the resource's canonical public URL, as a file with its format in its name:

```text
/[prefix]/[id]/badge.svg
```

The extension names the format, because a badge is a file that Markdown renderers and image proxies must recognize as an image without fetching it, the same reason a published OpenAPI document carries `.json`. Answer that URL with the image itself rather than redirecting to wherever the bytes live, because a redirect on an image URL breaks caching proxies. It is a credential-free public read and carries that posture.

Presentation is chosen by query parameter, in the product's fixed order, with defaults omitted:

- Size, through `size`: `compact` when omitted, or `large`.
- Theme, through `theme`: `light` when omitted, or `dark`. There is no system value, because an image cannot follow the host page's theme. The picture snippet below is how the host chooses.

Those two are the whole contract. The badge has no caller-chosen color, label, logo, or style, because a badge whose look the caller decides stops being the product. An unrecognized value renders the default rather than an error, because the reader of a broken image cannot see an error.

## Caching

Two audiences cache a badge, and they get different headers:

- Image proxies in front of Markdown renderers hold an image indefinitely unless told otherwise. Send `Cache-Control: no-cache` plus a validator, an entity tag derived from everything the badge shows, so the proxy revalidates on each view and gets a cheap not-modified answer while nothing changed.
- The product's own edge caches the badge briefly with stale revalidation through the edge-scoped cache header, so README traffic is absorbed before it reaches the origin.

Re-check the resource's public state on every origin hit. A cache hit is never an authorization.

## A Dead Or Unshared Link

A resource that is not public, whether it was never shared, has been unshared, or never existed, answers with one neutral badge that shows the product mark and names nothing, so the badge cannot be used to probe which identifiers exist and a stale badge cannot keep announcing what it pointed at. Serve it as a successful response, because a non-success status behind an image proxy turns into a broken-image glyph, and the neutral image is the refusal. Give it the same validator treatment, so a resource shared again repairs its badges on the next view.

## Snippets

Offer the badge where the share link is copied, beside the link, each snippet with its own copy control and a live preview. Build every URL in them from the same origin resolver as the share link. Two shapes:

Markdown, for READMEs and package pages:

```text
[![<resource name> on <Product>](<public URL>/badge.svg)](<public URL>)
```

HTML, for Markdown hosts that honor the picture element, so the host's theme picks the variant:

```html
<a href="<public URL>">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="<public URL>/badge.svg?theme=dark">
    <img alt="<resource name> on <Product>" src="<public URL>/badge.svg">
  </picture>
</a>
```

The alt text names the resource and the product, because it is what remains when the image does not load. The public resource schema carries the public URL once the resource is public, so a client building a snippet outside the product never guesses it.

## Boundaries

This opinion ends at the image. A framed embed, and an oEmbed answer that wraps one, are separate decisions this skill does not take, so shipping a badge implies neither.

Verify a badge by putting the snippet in a real README and viewing it in light and dark, then unsharing the resource and confirming the badge goes neutral on the next view.

Ask before widening what a shared resource reveals off-site.
