# Origins

Every surface is URL-addressable. Any meaningful state has a path that can be linked, shared, bookmarked, and restored. Build navigation and deep state around real URLs, never around hidden in-memory state that cannot be linked back to.

Origin resolution is deciding which scheme, host, and port a link or callback should use. Centralize it in one shared module so every surface and the backend resolve origins the same way. Never scatter hardcoded origins through app code.

A canonical origin is the locked production origin for a surface, such as `https://example.com` or `https://app.example.com`, held as a code constant.

## Resolution Order

When building an absolute URL, resolve in this order:

1. An explicit env override, when targeting a different surface or deployment.
2. The current request origin, when generating an absolute URL for the current surface.
3. The local development default, when running locally.
4. The canonical production origin constant.

Same-surface navigation uses relative paths (`/pricing`, `/settings/billing`). Cross-surface navigation goes through the shared resolvers, never a hardcoded host.

## Stage Awareness

A resolver must know which deployment stage it is serving, not only which surface. When no explicit override or current request origin is available, fall back to the platform's stage signal, such as a build or runtime environment indicator, before the canonical production origin, so a preview deployment resolves to the preview origin instead of production.

Any UI that displays an origin, endpoint, base URL, example request, or copyable command builds it from the resolver. A page served from preview shows preview URLs, a page served from production shows production URLs. Never print a hardcoded production origin on a non-production stage, because users copy what they see and will hit the wrong or non-existent host.

## Shape

The shared module exposes a canonical origin and a resolver per surface, plus an absolute-URL helper. One resolver exists for each surface the product actually has, named by the surface role, not hardcoded to a fixed pair. A product with only a site has one resolver; a product with site, app, and dashboard has three.

```text
CANONICAL_<SURFACE>_ORIGIN   one constant per real surface
LOCAL_<SURFACE>_ORIGIN       one local default per real surface
resolve<Surface>Origin()     one resolver per real surface
absoluteUrl(path, origin)    join a path to a resolved origin
```

Env overrides use the same key names across stages; only the value changes by store. Staging differs from local mainly by these origin values.

## Local Ports

Local ports follow a stable ladder so links are predictable across surfaces. The primary site takes the default browser port; each additional surface takes the next port in role order:

```text
site      -> 3000
app       -> 3001   (the first signed-in surface, whatever its role name)
dashboard -> 3002
admin     -> 3003
```

The first signed-in surface gets 3001 whether it is named `app`, `portal`, or another role. Keep the ladder dense and ordered so any developer can guess a surface's local origin.
