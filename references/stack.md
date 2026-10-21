# Stack

Pick the role first, then the tool. Do not let a tool dictate architecture: the same product rules must hold if the tool changes. A framework choice never decides a protocol's design.

TypeScript is the floor, not a choice. Prefer one language across apps, packages, and backend so types and helpers cross boundaries cleanly.

Prefer the latest stable release of each tool, and follow its current conventions rather than an older major's. Look up each dependency's current version with the package manager, such as `npm view <package> version`, before adding it. Keep the parts of the toolchain that must agree on the same major, so the config, build, types, and rendered runtime stay consistent.

## Components

In a React surface, set up shadcn/ui with its CLI (`shadcn init`, then `shadcn add` for each control) and take buttons, inputs, dialogs, menus, and tables from it before writing one by hand. Its components read the token layer, so the product's look stays in tokens, and lucide-react supplies their icons.

## Serve Dependencies From Your Own Origin

Serve every script, style, font, and worker bundle the product itself ships from its own origin. Load a provider script from the provider's host only when the provider requires it, such as a payment or auth SDK, and only on the surfaces that use it. Everything else is a real dependency in the manifest, bundled or self-hosted.

The cost of a runtime CDN is not only latency and an availability dependency you do not control. It hands a third party a request, and therefore an IP address and a referrer, from every user on every session that touches that feature. It also silently defeats version pinning: a loader with a default CDN URL will fetch whatever version that URL names, so the version in the lockfile can be a version that never runs.

Heavy editors and viewers are where this hides, because their loaders default to a CDN and work perfectly in development, so nothing ever fails. Check them specifically. Add the package as a real dependency, configure the loader at the product's own path, and verify in a browser's network panel that no third-party host is contacted beyond the provider scripts the product requires. A dependency that is not in the manifest but appears in the network panel is the bug.
