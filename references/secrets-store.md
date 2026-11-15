# Secrets Store

A repository whose runtimes read env, and that has a remote or a production stage, keeps every value in one secrets store, its permanent home, because its keys have to reach a second place: another clone, a cloud agent, CI, a host, or a shipped build. Doppler is the default. A hosting platform, a backend deployment, a CI system, or a provider dashboard holds a synced or pasted copy, never the only one, because several of them cannot give a value back: a hosting platform's secret variables are write-only once saved, and a provider shows a new key once. Some values exist in no provider at all, such as an API token an agent uses, a private key, or a test identity's password. They live in the store from the moment they are created.

A repository that reads no env, such as a static site that calls no keyed service, or that has neither a remote nor a production stage, has no store and no store file. A store a repository already keeps stays, as a deliberate choice, even where the repository has neither, and everything below applies to it.

## Shape

- One project per product, named for the product, in the workplace (Doppler's top-level account) the product belongs to, never a workplace of its own. Ask which workplace when the product's own docs do not say.
- One environment per stage the repository has, and no others, named for the branch roles in place of the store's default names: `dev`, `production` when the repository has a production stage, and `preview` when it deploys.
- One config per runtime that reads env, in every environment, holding exactly the keys its `.env.example` lists. Doppler calls these branch configs and prefixes them with the environment, so each runtime has one config per stage. Keep the environment's root config to values every runtime shares, since each branch config inherits it. Values no runtime reads, such as a token an agent uses or a test identity's password, go in a config of their own in the stage they belong to, or in `dev` where that is the only stage.
- A committed `doppler.yaml` at the repository root mapping each runtime folder to the product's project and that runtime's `dev` config, so one setup command links every folder on a fresh clone:

```yaml
setup:
  - project: product-name
    config: dev_<runtime>
    path: <runtime folder>/
```

## Syncs

A sync copies one whole config into one destination, so a destination's config is what decides which keys it receives.

- Sync each hosted runtime's `preview` and `production` configs to its hosting project's staging and production scopes. Keep the default sync type, which stores each value by its visibility in the store, and leave unmasked only the values the browser may read, so they arrive as viewable configuration and every other value as a secret.
- Sync the CI secrets a workflow needs, such as a publish or release workflow's token, into the repository's Actions secrets from a config of their own, whether or not the repository deploys.
- In a repository with a production stage, have a release build that ships, such as an installer, read its runtime's `production` config through a CI sync or the store's CLI.
- Sync every other provider the store has an integration for. Set a provider without one, such as the backend deployment, from its runtime's config through the provider's CLI, as one bulk set per stage, and set it again whenever a value in that config changes.

## Setup

Set the store up one step at a time, each stage's config filled before anything reads from it.

Write every value into the store first, under its stage, then fill `.env.local` from its runtime's `dev` config and each deployed store through a sync or the provider's CLI. After a fresh clone, link the folders from `doppler.yaml` and fill each runtime's `.env.local` the same way. `.env.local` stays gitignored and is a copy the store fills, so a new or changed value goes into the store too, or the next fill loses it. Deleting the clone deletes the copy and loses nothing, because the store holds every value. Each machine signs in to the store once through its CLI, the one credential the store cannot hold for itself, and a cloud agent reads with a read-only token scoped to the configs its work needs.

Ask before rotating a value, deleting one from the store, or changing which config a sync reads.
