# Naming

Name by paradigm, not by provider. A thing is named for what it does so the name survives a tool swap.

| Identifier | Convention | Example |
| --- | --- | --- |
| Repo and canonical folder | Title-Dash-Case | `Product-Web` |
| Deployable code slug, package name, import path | kebab-case | `product-web`, `@product/domain` |
| Source folders | lowercase | `apps/`, `src/`, `auth/` |
| App surface in `apps/` | role word | `site`, `app`, `admin`, `studio` |

## Surface Names

`site` is the default name for the primary web surface. Most web-technology repos either are a `site` or at least include one, so `site` is the safe default that stays accurate once a signed-in surface joins it.

Use `app` for the signed-in product. Name additional surfaces by their role: `admin`, `dashboard`, `console`, `portal`, `studio`. The role word is the name; there is no need for generic suffixes.

## Package Names

Package names state purpose. Use names like `backend`, `domain`, `config`, `ui`. Keep each package's name describing the one job it owns.

## Integration Names

Name a module, function, or folder after the capability it provides, not the vendor behind it. Pick the most accurate word for what it does in this product rather than the provider's name or a vague catch-all. The vendor lives inside the adapter; the name stays true when the vendor changes.

## Env Keys

Env keys keep the same name across every stage. The value changes by store, never the key. The stage is not encoded into the key name.

Avoid names that describe a temporary process or a moment in time. A name should still read true a year later.
