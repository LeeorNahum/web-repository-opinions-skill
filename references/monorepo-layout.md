# Monorepo Layout

Use `apps/` for deployable entry points and `packages/` for shared libraries. Nothing else earns a top-level slot by default.

```text
Product-Name/
  apps/
    site/      public marketing, SEO, docs, pricing, legal, help
    app/       signed-in product, private routes, account, billing
    admin/     internal admin surface, once the product needs one
  packages/
    backend/   backend functions, jobs, provider adapters, schema
    domain/    pure product rules, route builders, permissions, limits, origins
    config/    shared TypeScript and tooling config
    tokens/    shared design tokens and theme, created with the first app
    ui/        shared UI primitives, only once real ones exist
  package.json
```

Apps are thin. They compose routes, layouts, runtime adapters, and env wiring. Shared product logic lives in packages.

Dependency direction is one way. Apps import packages. Packages never import apps. Backend packages never depend on UI packages.

Each package has one clear purpose, so none becomes a junk drawer. Create `packages/ui` once two apps share a real primitive. Keep types in the package that owns their concept.

Declare workspace dependencies explicitly:

```json
{
  "dependencies": {
    "@product/domain": "workspace:*"
  }
}
```

Backend placement: keep the backend in the package graph while preserving its native folder shape.

```text
packages/backend/
  package.json
  .env.example
  convex/
    schema.ts
    _generated/
```

One backend serves the whole product. Public site, signed-in app, future mobile, and admin share it when they are one product. Split the backend only when the products are genuinely separate.

Future mobile or desktop clients become new apps under `apps/` that reuse the same packages and backend, never a fork of product logic. A native mobile client is one cross-platform project for Android and iOS.

## Package Hygiene

Keep apps thin and put each piece of shared code in the package that owns its concept.

- When the same helper, type, or constant is copied across two apps, move it into the package whose concept it belongs to.
- When a route handler holds a product rule that clients, jobs, or another surface also need, lift the rule into the shared package and have the handler call it.
- When code crosses a boundary the layout forbids, move the code, do not relax the boundary.

Keep each surface its own deployable. Combine the public site and a signed-in app into one deployable only when they truly share one audience, one deployment, one auth model, and one routing concern. Ask before merging surfaces that currently stand apart.
