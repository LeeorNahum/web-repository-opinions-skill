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

## Orphans

Plan for orphans. When a database row is created before bytes arrive, or bytes arrive before a row is finalized, define how unreferenced objects are detected and cleaned up. An object with no owning row is garbage; a row with a missing object is a failure to surface, not to hide.
