# Font Loading

The goal on every surface is zero FOUT (Flash of Unstyled Text), when a browser renders fallback text before the custom font downloads, then flashes to the brand font. The right strategy is determined by when and how the environment renders text.

A server-rendered surface gets self-hosted files and preloads from the framework font utility. A client SPA, the default for the signed-in app, self-hosts the same woff2 files the site uses and preloads each above-the-fold face in `index.html` with `rel="preload"`, `as="font"`, `type="font/woff2"`, and `crossorigin`. Both use the display rule below. This reference matters most for the other surfaces a web-technology repo can include: static HTML, browser extensions, injected scripts, email, and native runtimes.

## By Environment

| Environment | FOUT risk | Notes |
| --- | --- | --- |
| Next.js SSR | None with the framework font module and `optional` display | Fetches at build time, self-hosts, preloads before first paint. Custom fonts safe. |
| Nuxt SSR | None with the framework font module and `optional` display | Same build-time model. Custom fonts safe. |
| Astro | None with the framework Fonts API and `optional` display | Self-hosts at build and preloads through its Font component. |
| Remix or React Router | Low if handled | No font module. Self-host and preload manually via route links. |
| Other static generators | Manageable | Static output. Self-host and preload in the head. |
| Vite or plain SPA | None when preloaded with `optional` display | Fonts otherwise load after first paint. Self-host, preload, and use a metric-matched fallback. |
| Static HTML | Risk unless preloaded | Self-host and preload in the head. |
| Browser extension popup or options | None | Fonts bundle as local assets and load instantly. Custom fonts safe. |
| Injected content script | High | Runs in an unknown host page, and host CSP may block fonts. System fonts only. |
| Electron renderer | None | Assets are local to the bundle. Custom fonts safe. |
| Email clients | Fragmented | Some clients support font-face, and many strip it. Treat custom fonts as progressive enhancement. |
| React Native or Expo | Different model | Embed fonts at build time through the platform's font config plugin so they exist at launch. When a font must load at runtime, hold the splash screen until it has loaded. |

## Font Sources

- Build-time fetch through a framework font utility fetches at build and self-hosts the result.
- Self-host the font files when no framework font utility exists.

## Text Stays Visible

Use `font-display: optional` wherever a web font loads over the network, and set it in the framework font utility's display option, since Next.js, Nuxt, and Astro default to `swap`. Text is visible from first paint, and the brand font is used only when it is ready within the brief block period, otherwise the fallback stays for that page view, so text never changes face in front of the reader. A first visit on a slow connection may show only the fallback, and later views use the cached font. Give the fallback the brand font's metrics through `size-adjust` and the `ascent-override`, `descent-override`, and `line-gap-override` descriptors, so a view that keeps it lays out as the brand font would.
