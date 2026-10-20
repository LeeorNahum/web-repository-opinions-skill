# Workspace Tenancy

Give a product workspaces when it needs shared ownership, membership, or policy now or its owner says it will, because retrofitting an ownership boundary costs far more than carrying one early. A product whose data will only ever belong to one person keeps that data on the user account, with no organization layer.

When a product's collaboration model is workspaces, back every workspace with the auth provider's organization object, the user's first workspace included. One organization per workspace gives every workspace the same membership, invitation, role, and token contract from day one, and the provider's verified organization context becomes the one workspace authority every surface shares. Clerk Organizations are the default pick, and the paradigm holds for any provider tenant object.

## Every Workspace Is The Same Kind Of Thing

- Auto-create each user's first workspace at sign-up as a real provider organization, with a personalized name and a plain fallback name, and give it no special product status afterward: one workspace kind, one set of rules, so no flag exists for the first one to drift stale.
- Turn the provider's personal-account (no-organization) mode off and require organization membership, so no session ever acts without a verified organization context.
- Keep the provider's organization roles to its built-in administrator and member, with the workspace owner as administrator, and hold every finer product role in the app's own authorization gate, which owns capabilities whichever provider holds membership.
- Key per-user facts to ownership, not to a designated workspace: the subscription is managed from any workspace the user owns. How many members a plan admits is a plan fact whose enforcement lives at the product's seat gate. The provider's per-organization membership cap is kept as a mirror of that fact, never as a second source of truth.
- Make account deletion member-based: an owned workspace with no other active member is removed outright with its provider organization, while one that other members use is retained behind an anonymized owner, so nothing anyone depends on dies with an account and nothing orphaned lingers.

## Verified Access And Grant Scope

- Resolve identity and memberships from the provider's verified contracts: verified session or access-token claims, or the provider's userinfo endpoint for opaque tokens. A readable, unverified token body never selects a workspace.
- Choose an agent grant's workspace scope from the product's need, independently of the workspace the UI is showing. A workspace-bound grant has consent select one workspace, and another workspace is a new authorization of the same canonical OAuth resource, never a second resource or a per-workspace path. An account-wide grant covers every current and future membership plus individually shared resources, and consent says so.
- Under either scope, verify every call's target on the server against a live membership or a share of that resource, with its role, intersected with the token's scope. A single organization claim proves nothing about another workspace. A client may name its target workspace for the server to verify. A filter that only narrows what a view lists never selects the workspace a call acts on. Revocation reaches existing credentials, because every call rechecks.
- An individual share grants that resource alone, never its workspace's other resources or its member list.
- Fail closed when verified identity is absent, or when neither a live membership nor a share covers the target, with one clear product error.

## The Provider's UI Speaks The Product's Vocabulary

When the provider's own prebuilt components, an organization switcher, an organization or account management panel, become a primary surface for renaming, membership, or settings, they still carry the provider's own words in their labels by default: `organization`, `member`, `personal account`. Override those strings to the product's own tenancy term everywhere the provider renders, not only in the app's own copy. A component that still says the provider's word is a leak, not an accepted exception. Most providers expose a localization or strings-override mechanism for exactly this.

Override the provider's complete default string resource rather than a hand-maintained list of keys: profile subpages, confirmation dialogs, and error states hide strings a partial override misses. Start from the resource version matched to the installed SDK, transform every string to the product's term, and keep interpolation placeholders exactly as the provider names them, because its templating resolves them by name. Providers typically stamp each rendered string with its key, so a word that still leaks traces straight to the entry that needs fixing. Pin the transform with a test over the whole resource, proving no provider term survives and every placeholder does.

## Creation Limits And Seat Coherence

- Put the paywall where the value appears, not on the container. A workspace without other people in it is an empty wrapper, so workspace creation stays free, bounded by a generous fixed provider limit as anti-abuse rather than as the paywall.
- When sign-up must create the first organization, creation stays enabled for every user. Send a real limit value. When the provider treats zero as unlimited, zero is never a valid product limit.
- When plans price on seats, derive every workspace's seats live from its owner's current plan at the gate. The owner holds the first seat by reservation so they can never be locked out of a workspace they own. Members hold the remaining seats by admission order. When a plan shrinks, the newest members cleanly stop passing the gate, keep every row of data, and pass again the instant a plan covers them.
- Block an invitation the plan has no seat for at the moment of sending, by mirroring the seat count onto the provider's per-organization membership cap (providers enforce it server-side and count pending invitations). Push the mirror whenever the owner fact or the owner's plan changes, re-derived from the plan on each push and never stored, and set the instance default cap to one seat so an unsynced workspace fails closed. Shrinking the cap below current occupancy must keep existing members (the live gate unseats the newest) and only stop new invitations. The gate stays the access authority throughout.

## Migrating Existing Workspaces Onto Organizations

- Re-key an existing workspace row to its real organization only on verified facts read from the provider: the user is currently a member and the provider names them creator, with exactly one qualifying organization. Refuse ambiguity and report it. Never select an organization by display name, list position, or age.
- Run the reconciliation as a dry run first and report exact counts before writing.
- Patch the workspace row in place so its stable public id and every child row survive. A migration that moves children has the wrong shape.
- Let webhook redelivery converge event ordering: answer non-2xx when a prerequisite mirror has not landed, keep every mirror idempotent under redelivery, and rebind only where the creator fact is verified rather than compensating with writes from a caller's own token claims.
