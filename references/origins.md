# Origins

Origin resolution is deciding which scheme, host, and port a link or callback should use. Centralize it in one shared module so every surface and the backend resolve origins the same way. Never scatter hardcoded origins through app code.

A canonical origin is the locked production origin for a surface, such as `https://example.com` or `https://app.example.com`, held as a code constant.

## Resolution Order

When building an absolute URL, resolve in this order:

1. An explicit env override, when targeting a different surface or deployment.
2. The current request origin, when generating an absolute URL for the current surface.
3. The local development default, when running locally.
4. The stage origin, when the platform's stage signal names a hosted non-production stage.
5. The canonical production origin constant.

Same-surface navigation uses relative paths (`/pricing`, `/settings/billing`). Cross-surface navigation goes through the shared resolvers, never a hardcoded host.

## Stage Awareness

A resolver must know which deployment stage it is serving, not only which surface, so a preview deployment resolves to the preview origin instead of production.

Any UI that displays an origin, endpoint, base URL, example request, or copyable command builds it from the resolver. A page served from preview shows preview URLs, a page served from production shows production URLs. Never print a hardcoded production origin on a non-production stage, because users copy what they see and will hit the wrong or non-existent host.

## Shape

The shared module exposes a canonical origin and a resolver per surface, plus an absolute-URL helper. One resolver exists for each surface the product actually has, named by the surface role, not hardcoded to a fixed pair. A product with only a site has one resolver, and a product with site, app, and admin has three.

```text
CANONICAL_<SURFACE>_ORIGIN   one constant per real surface
LOCAL_<SURFACE>_ORIGIN       one local default per real surface
PREVIEW_<SURFACE>_ORIGIN     one staging origin per real surface
resolve<Surface>Origin()     one resolver per real surface
absoluteUrl(path, origin)    join a path to a resolved origin
```

## Local Ports

Local ports follow a stable ladder so links are predictable across surfaces. The primary public surface takes `3000`, the rendered-surface framework's development default, and every additional surface takes the next free port up.

Order the ladder by two rules, applied in that order:

1. Canonical appearance: place each surface in the order a person first meets it in the product's own journey.
2. Dependency necessity: when one surface must be running for another to function, the depended-on surface takes the earlier port.

A site, an app, and an API the app cannot start without take `3000` for the site, `3001` for the API, and `3002` for the app, since a person never meets the API and dependency alone places it.

The same two-rule ordering governs any ordered enumeration the product defines, not only ports, such as the surfaces listed in docs and env files. Keep the ladder dense, and keep every store, doc, and code default that names a port consistent with it, so a developer can guess a surface's local origin without consulting a list that may have drifted.
