# Provider Setup

Provider dashboards are part of the product. A setting that can break the app is product work, not a chore buried in chat history.

Provider resources should be understandable from the dashboard alone. Fill optional descriptions, labels, and tags with the product, operational purpose, and environment or shared scope. Use canonical names from the repo, and prefer concise metadata that helps both people and automation distinguish similar resources across stages. Resource-specific formats, such as DNS record comments, remain authoritative where defined.

Track near the runtime contract:

- CORS policies
- Webhook URLs and signing secrets
- Allowed origins
- OAuth redirect URLs
- Env variables per stage
- Branch and custom domains
- Storage lifecycle rules
- Deployment branch settings

When onboarding providers, work one provider or one small sub-step at a time. Explain what to click, write values into the correct store, confirm, then move on. Do not dump a full checklist into one message.

Report missing or pasted values by key name and store location only. Never echo a secret value back after it is provided.

Some steps need a public URL that does not exist yet, such as a webhook target before the first staging deploy. Defer those explicitly, note what will unblock them, and keep a running list of deferred items rather than guessing a value.

Do not run production deploys, change production DNS, or touch live provider modes unless explicitly asked.
