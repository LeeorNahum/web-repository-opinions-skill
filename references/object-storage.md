# Object Storage

Large user files belong in object storage, not the database. Cloudflare R2 is the default; any S3-compatible store fills the role.

The database is the source of truth for metadata, ownership, status, and permissions. It stores the object key and references the bytes. Object storage holds only the bytes.

- Keep large media in object storage and store only its key and metadata in the database.
- Treat the bucket as the byte layer; keep app state and relationships in the database.
- Charge usage against durable database state, not against what happens to sit in a bucket.

## Buckets

Use a dedicated bucket per asset class and a separate bucket per stage, matching the two provider stages, so dev/test bytes never mix with production bytes. One asset class, such as video, is one bucket pair (dev and prod). Split into more buckets only when a distinct asset class needs different access, lifecycle, or region, not by default.

## Keys

The database owns the mapping from a row to its object key, so the key itself carries no meaning the app depends on.

- Use an opaque, non-guessable, collision-resistant key for each object. Random IDs prevent enumeration and keep the namespace flat and simple.
- Keep user content out of the key: no filenames, titles, emails, or other identifying or renameable text. The original filename, if needed, is metadata in the database.
- A flat key at the bucket root is a sound default when one bucket holds one asset class and the database holds the mapping.
- Reach for a key prefix only when it earns its keep, such as per-owner lifecycle rules, expiry policies, or operator debugging. A prefix is a storage convention for those needs, not app structure, and the database stays the source of truth either way.

## Delivery

Ownership and delivery are separate decisions. The database owns the mapping and the bucket owns the bytes, and neither changes when delivery changes.

Serve bytes straight from the bucket while callers are the product's own authenticated surfaces. Put a CDN or provider edge in front once delivery turns public, high-volume, or reachable by a caller the product did not choose. Egress from an origin bucket to an arbitrary public caller is metered per byte and can be driven arbitrarily high by anyone who can generate a request, while an edge built for that traffic absorbs the spike and flattens the cost. The edge in front is additive, never a replacement for the bucket's ownership.

## Triggering A Download

A download is a navigation, and a browser only reliably permits one that the user started. A control that first awaits a round trip to mint a signed URL and then synthesizes a click has already spent its transient activation, so the browser may drop the download with no error anywhere: the object is built, the URL is valid, the request never happens, and the product looks broken while every server-side check passes.

Make the download a plain link the user clicks. Point it at a same-origin route that authorizes the caller, produces or fetches the signed URL, and redirects to it. The click is then a real user navigation, the URL is addressable and restorable like every other view, and no client-side timing is involved.

Do not verify a download by confirming the action returned a URL or that the object appeared in the bucket. Both can be true while nothing reaches the user. Verify that the file lands.

## Orphans, And Why Deletion Needs A Write-Ahead Ledger

Bytes travel outside any transaction, and that is the whole problem. An upload computes its key,
begins its put, and lands whenever the network says so. Deletion, meanwhile, lists a prefix,
removes what it saw, and removes the owning row. A put still in flight then lands as an object no
row references, and no sweep can ever rediscover it, because every sweep finds its keys through
the row that is gone. Logical access ends, physical erasure silently fails, and whatever the
privacy policy promises about deletion is now false for that object. "Plan for orphans" is not a
plan; this section is the plan.

**No stored byte may exist before the record that can destroy it.** Keep a write-ahead ledger of
object writes, and hold these properties, each of which exists because a race defeats the version
without it:

- **Register, then write, without exception.** Every writer records the keys it is about to put,
  in a database transaction, before the first byte moves. That transaction also rechecks that the
  write is still allowed, the owner still open and the row still present, so a caller whose
  account died mid-action is refused before the upload instead of stranding one.
- **The ledger outlives everything it anchors.** Key the ledger by the object key alone, never by
  the row or account being deleted, so cleanup can still find the byte after both are gone. The
  anchor row then no longer has to be the last thing deleted, because it is no longer the only
  thing that knows the byte exists.
- **Drain by age, never by optimism.** Only rows older than the longest legitimate write are
  candidates: by then the write landed or never will. Skip an object fresher than the window, since
  every writer re-registers first and a fresh byte under an old row means a concurrent writer the
  sweep outran. Clear a row only when its registration timestamp is unchanged, so a row a new
  writer touched survives to anchor that writer's own write.
- **Wire the drain into the scheduled sweep**, so the worst-case orphan life is the age window plus
  one sweep interval, and check the deletion copy in the privacy policy against that bound rather
  than assuming it.

**Lifecycle rules are for prefixes that are short-lived by construction**, staging areas and
export downloads, where every object is garbage after a known age. Never put one on a prefix of
content-addressed served objects: lifecycle conditions are age-since-upload, and age cannot tell a
stranded byte from a served one, because a content-addressed object is uploaded once and then
served unchanged for the life of its owner. A rule at any age eventually destroys live content,
and a rule set long enough never to fire is not defense in depth, it is a delayed defect. The
ledger is the mechanism; a lifecycle rule is only correct where age genuinely implies garbage.
