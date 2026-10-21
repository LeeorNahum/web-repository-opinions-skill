# Provider Setup

Provider dashboards are part of the product. A setting that can break the app is product work, not a chore buried in chat history.

Provider resources should be understandable from the dashboard alone. Fill optional descriptions, labels, and tags with the product, operational purpose, and environment or shared scope. Use canonical names from the repo, and prefer concise metadata that helps both people and automation distinguish similar resources across stages. Resource-specific formats, such as DNS record comments, remain authoritative where defined.

Keep a committed setup document beside each deployable app's `.env.example` that lists, per stage and never with secret values:

- CORS policies
- Webhook URLs and the store holding each signing secret
- Allowed origins
- OAuth redirect URLs
- Env variables per stage
- Branch and custom domains
- Storage lifecycle rules
- Deployment branch settings
- Deferred items with their blockers

When onboarding providers, work one provider or one small sub-step at a time: make the change, write values into the correct store, confirm, then move on. Where the user takes a step, give it to them one step at a time rather than as a full checklist in one message.

Some steps need a public URL that does not exist yet, such as a webhook target before the first staging deploy. Defer those explicitly, note what will unblock them, and keep them in the setup document rather than guessing a value.

Every provider resource exists once per stage. A dev-tier app, key, or install pointing at production, or a production one reusing dev credentials, is not a shortcut, it is a wrong webhook target and a shared blast radius. Create the production resource when the stage exists rather than borrowing the development one and planning to fix it later.

Provider branding is part of setup, not decoration. Fill the logo, name, support contact, and links on every consent screen, app listing, and connector entry, so a user granting access sees the product rather than an unnamed client.

Consent-screen and app-listing branding is reviewed against the live page, and passing it is quick once the page agrees with the registration. Saving anything on a branding form usually invalidates an existing verified result, so a later logo upload silently undoes an earlier verification. A verified result often has to be published separately before users see it, and expires if it is not. Finish by re-reading the status and confirming it says the branding is being shown, not merely that it verified.

## Provider Shape

Map the product's stages onto each provider's own isolation model before creating anything. Prefer the provider's native environments, modes, sandboxes, deployments, or credential scopes inside one canonical project when they keep stages independently configurable and safe. Create separate projects or accounts only when the provider requires them. Record the mapping before filling values.

Name the provider project, application, workspace, or account with the product's canonical name, keeping its capitalization and spaces where the provider accepts them. Adapt only as far as the provider forces, and check availability before falling back to a less canonical name.

## Order Of Operations

Wire each provider as completely as its known dependencies allow, across dev/test and production, while its dashboard is open.

- Configure the dev/test tier first, then production. Complete production provisioning whenever its values are known, even when end-to-end production verification comes later.
- Order by dependency truth. Establish canonical projects, deployments, domains, and origins before credentials, allowlists, callbacks, webhooks, or redirect URIs that refer to them. Defer a dependent setting until its upstream value exists rather than entering a temporary value that needs repair later.
- Finish every actionable setting of one provider before moving to the next, and record each remaining deferral with its blocker.
- Fill local env and push the dev backend deployment as soon as dev/test values are ready, so local verification proceeds while production waits.
- Push the repo to its remote before wiring a host that deploys from it.
- For each hosted stage, provision credentials, fill env, then add its domain and DNS records once the stage has an origin.
- Count a stage as done only when its dashboard state, such as allowed origins, callbacks, webhooks, and branch deploys, is set alongside its keys.
- When a later step changes an earlier value, update every store that holds it in the same pass.
- When one provider, key, or surface is added, rotated, or removed on an onboarded product, diff the contracts against the stores and fill only the delta, across every existing stage.

Adapt the order when a provider forces a different sequence.

## Verify By Completing The Real Flow

A provider integration is verified when the real client completes the real flow against the real deployment, and it does something afterwards. Discovery endpoints returning 200, a registration returning 201, and a well-formed metadata document prove nothing about whether a user can connect. Sign in through the actual host, then exercise the integration.

When a host bakes a setting in at creation time and offers no way to edit it afterwards, a misconfigured connection cannot be repaired. Recreate it, and say so plainly rather than leaving a broken entry that looks configured.

Ask before a production deploy, switching a provider to a live mode, or any provider change that costs money or is visible outside the team, such as a paid plan, a public listing, or a first publish.
