# Auth

Use a managed auth provider so identity, sessions, and social sign-in are never hand-rolled. Clerk is the default. You never store or handle raw passwords or emails yourself. The provider owns credential security.

Hold three postures throughout: least privilege, granting each caller the minimum scope it needs; defense in depth, re-verifying on the server even when the UI already hides an unavailable action; and zero trust, never trusting a request for where it came from, so every token is validated and every webhook signature is checked before its payload is believed.

## One Auth Route

Authentication lives at a single route, `/auth`, handled by the provider's integration. Keep it as one route rather than separate sign-in, sign-up, and callback paths with redirect-back juggling. Use the provider's combined sign-in-or-up component so the same surface serves a returning and a new user, deciding between them from the identifier entered. A single integrated route avoids the redirect dance and the post-login bounce, and it returns the user straight into the product.

Auth route structure is a product decision and lives in code, not env. Do not add sign-in and sign-up env keys out of habit.

## Signing In Returns The Person To Where They Were

Every surface that can offer a sign-in carries the destination through it, so the person lands back on the page they were reading rather than on the product's default home. Someone who followed a link to a specific thing, met a sign-in, and arrived at a generic dashboard has lost what they came for and has to go find it again.

Derive the destination once, from the request being interrupted, rather than plumbing it per call site, and validate it as a same-origin relative path before honoring it, since an unvalidated return destination is an open redirect. Test it signed out at each entry point, because it fails silently: the page still works, and only the person who wanted something specific pays.

## Sign-In Methods

Default to social sign-in plus email as an enabled identifier. The provider owns credential security, so you never store a password or verify an email yourself, and a password is an acceptable method when you want one, carrying no credential surface of your own. Keep the email identifier on regardless of whether a password is enabled, because it is what lets the product invite teammates by email, send sign-in links, and resolve a social sign-in and a verified email to one account.

When a product's core function depends on every user holding one provider's account, make that provider the only identity and turn the others off, including email when no feature needs it, such as invitations or sign-in links. The product's own requirement wins over the open default.

## Social Sign-In With Account Selection

Use custom OAuth credentials for each social provider, and enable the account-selector prompt so a user can switch accounts after signing out instead of being locked into the last session.

Some providers gate this behavior behind custom credentials. In Clerk specifically, the account-selector prompt can only be enabled once you supply your own OAuth client ID and secret. The shared development credentials do not expose it. Always create custom credentials so account switching works, even in development.

## Stage Separation

Use separate OAuth credentials per stage. Each auth instance issues a different redirect URI, and a credential validates the exact redirect URI on every login, so sharing one credential across dev and production widens the blast radius of a leak. Keep dev/test and production credentials separate, matching the two provider stages.

Integration contract names, such as a JWT template name, can be code conventions. Make them env only if deployments truly need different names.

## Identity And Deletion

Store the provider's stable subject identifier on the application user. Provider webhooks and account cleanup resolve by that subject, not mutable email, handle, or profile data.

Account deletion webhooks follow a strict contract:

- Verify the signature before trusting the payload.
- Deduplicate delivery by the provider event ID.
- Treat repeated delivery as successful completion.
- Enqueue bounded cleanup instead of deleting an account graph inside the HTTP request.
- Remove only user-owned relationships, deduplication rows, and private metadata.
- Delete the application user record last.
- Preserve shared objects the user referenced but did not own.

## Verify A Token Against What The Provider Actually Mints

Read a real token from your own provider before writing the check. Decode one, list its claims, and build the rule from that. The specification says what a token ought to carry; the provider decides what it does carry, and the gap between them is where a confident, wrong check gets written.

Two failures come from skipping that step, and they fail in opposite directions.

Enforcing a claim that is never issued rejects every legitimate request on the first call. An audience check is the usual example: if the provider mints no audience, comparing one to your resource denies everybody, and it looks like a broken deployment rather than a bad rule. Enforce the issuer unconditionally, since that is always present, and enforce an audience only when the token actually names a resource, refusing one that names a different resource. Say plainly in the code why the check is conditional, or the next reader will "fix" it into the version that rejects everyone.

Advertising a requirement and then not checking it is the other direction, and it is worse because nothing visibly breaks. If a resource publishes required scopes in its metadata and its challenge, it must require them. Decide the minimum set the resource genuinely consumes, require every member, and answer a refusal with the status and challenge the protocol defines for insufficient scope rather than a generic denial. Beware the truthiness trap in whatever language you use: an empty list of scopes is not the absence of a scopes field, and a check for presence will wave it through.

When a provider cannot express something you need, such as binding a token to one resource among several it issues for, record the residual exposure where the next person will find it rather than implying the check is complete.

## Validate Origin By Shape, Not By Roster

A defence against a browser being tricked into calling a local or private endpoint needs to reject the shapes that attack uses, not enumerate the hosts you happen to know. A roster is wrong the day a legitimate client ships from a host nobody added, and it fails closed and silently, which is the worst way to be wrong.

Define what a request must look like instead: a secure origin, loopback where that is meaningful, whatever scheme the platform's own extensions use. Refuse a null origin, plaintext off loopback, and malformed values. Serve a request that carries no origin at all, because a server-to-server caller is not a browser and has nothing to forge. A shape-based rule keeps serving clients that do not exist yet, which is the whole point.

## One Authorization Gate

Enforce authorization once, at the boundary every client crosses, so the MCP, the CLI, the raw API, and the UI all inherit the same rules instead of each re-implementing them. One gate keeps policy in one place and gives every surface the same answer. The gate is capability-granular: every action maps to a named capability, and access is the intersection of the caller's role, their per-resource allowlist, and, for a token or key, the token's own scope.

Capabilities are assignable to roles and to individual members, so an admin can grant one verb while denying another on the same resource. Re-verify on the server even when the UI already hides an unavailable action, and fail closed when a capability is unknown or absent.

The gate scopes what a member or token may do. Keep it separate from what a plan sells. Whether any capability is also a paid feature is a billing decision, not a job for this gate.

## Gates Compose, Or They Leak

Two gates that each hold on their own can still leak at their seam. A product grows one gate for
who is acting and another for how an expensive read or write proceeds, and the defect class that
survives both is a capability issued under one gate crossing a transaction or process boundary
without the fact the other gate needed. A plan authorized while an account was open drains after
it closes. A background job fetches a private resource for an owner whose account died between
scheduling and running. The proof of each gate stays true while the product leaks.

- **Whatever crosses a boundary carries its principal.** A plan, job, or capability consumed in
  later transactions has who it was issued for frozen inside it, and every consumer re-establishes
  that principal's liveness in its own transaction, by stable ID. Serialization strips runtime
  identity, so the recheck is what carries the guarantee across the wire.
- **Background work has no caller, but it always has an owner**, and the owner check belongs in
  every transaction that acts. A check at scheduling time is an optimization, never the guarantee,
  because a closure can commit between scheduling and running.
- **The last gate is where the result lands**, and some results land without a landing mutation: a
  presigned URL, a sent message, a minted credential. Recheck the principal immediately before
  releasing one, because nothing downstream will get another chance.
- **Enumerating call sites fails.** A list of places to add the check is stale the day it is
  written; the fix that holds is structural: one constructor or one module every path must cross,
  with the alternatives deleted rather than deprecated so an unconverted caller is a compile error.
- **Lint rules and type brands are hygiene, not the boundary**, and must say so where they are
  written. A lint rule cannot see a property name computed at runtime or an object reached through
  a parameter, and a type brand is erased and forgeable. Runtime identity for issued objects (a
  module-private WeakSet) plus the per-transaction recheck are the boundary; everything else keeps
  honest people honest.

## Closure Is Permanent, And Retention Depends On Who Closed It

When an account closes, keep a small record that outlives every row it owned: a one-way hash of
the provider subject and when it closed. It exists because credentials issued before the closure
verify by signature, not by asking the provider, so without it a lingering token quietly recreates
an account that was just deleted. How long to keep it depends on who ended the account, and the
two answers differ because the safety assumption differs:

- The provider deleted the identity and said so: the subject can never issue or refresh a
  credential again, so the record is a tombstone kept comfortably past the longest credential
  life, then dropped so this never becomes a permanent list of everyone who left.
- The product closed the account while the provider identity still exists: that subject can still
  sign in and still refresh, so the record must never expire, or the closure quietly ends on a
  date. Retention only ever lengthens; a later provider event never puts an expiry back.

Make the origin a required argument with no default, because the safe answer differs and a default
silently picks the unsafe one for the caller that most needs the other. And when permanence is
encoded as an absent expiry field, every expiry scan must range only over records that have the
field, because an absent value sorts before every real one in a typical index, and an unbounded
range deletes exactly the refusals that must never be forgotten.

Ask before changing OAuth callback hosts or production auth settings.
