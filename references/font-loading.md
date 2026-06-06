# Font Loading

The goal on every surface is zero FOUT (Flash of Unstyled Text), when a browser renders fallback text before the custom font downloads, then flashes to the brand font. The right strategy is determined by when and how the environment renders text.

With the default server-rendered framework, the framework font utility handles this for you, so a standard site or app rarely needs more than picking that utility. This reference matters most for the other surfaces a web-technology repo can include: client-only SPAs, static HTML, browser extensions, injected scripts, email, and native runtimes.

## By Environment

| Environment | FOUT risk | Notes |
| --- | --- | --- |
| Next.js SSR | None with the framework font module | Fetches at build time, self-hosts, preloads before first paint. Custom fonts safe. |
| Nuxt SSR | None with the framework font module | Same build-time model. Custom fonts safe. |
| Remix or React Router | Low if handled | No font module; self-host and preload manually via route links. Avoid CDN. |
| Astro or Gatsby SSG | Manageable | Static output; preload in the head. Self-hosting beats CDN. |
| Vite, CRA, plain SPA | High | Fonts load after hydration, after first paint. System fonts unless FOUT is explicitly handled. |
| Static HTML | Risk unless preloaded | Preload hints help. Self-hosted loads faster than CDN. |
| Server-rendered PHP | Low if enqueued correctly | Preloading in the head template removes most risk. |
| Browser extension popup or options | None | Fonts bundle as local assets and load instantly. Custom fonts safe. |
| Injected content script | High | Runs in an unknown host page; host CSP may block fonts. System fonts only. |
| Electron renderer | None | Assets are local to the bundle. Custom fonts safe. |
| Email clients | Fragmented | Some clients support font-face; many strip it. Treat custom fonts as progressive enhancement. |
| React Native or Expo | Different model | Async load must complete before text renders; unloaded fonts block render rather than flashing. |

## Font Sources

- Raw CDN link is a runtime network request, so it risks FOUT on any surface, plus cross-origin latency and a third-party dependency.
- Build-time fetch through a framework font utility fetches at build and self-hosts the result, so there is no runtime CDN call. Safe.
- Self-hosted is fastest, with no cross-origin and no third-party dependency. Best when no framework font utility exists.

## FOIT

FOIT (Flash of Invisible Text) hides text while the font loads, then shows it. No layout flash, but content is invisible during load, which is generally worse for perceived performance. Controlled by font-display behavior.
