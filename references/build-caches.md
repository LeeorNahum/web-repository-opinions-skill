# Build Caches

Build caches grow until something evicts them. Gitignoring a cache keeps it out of Git and does nothing for the disk, so give each cache an age bound. Configure it once in the repo where the tool supports it, and otherwise run a prune after each approved commit to `main`.

- Gitignore `.turbo`, `.next`, `node_modules`, and Rust `target/`.
- Exclude the framework's own cache from every task's build outputs (the `outputs` list in `turbo.json`, with `"!.next/cache/**"` beside `".next/**"`), so the task runner does not store it again inside each entry.

## Task Runner Cache

Set `"cacheMaxAge": "14d"` in the root `turbo.json`. Turborepo 2.10 and later evicts entries older than that in a background thread at the start of every `turbo run`, so the repo needs no prune script. Add `cacheMaxSize` as a second bound only when the cache still outgrows the disk.

An entry is reused only when its inputs hash to exactly its key, so old entries mostly sit unused until someone returns to those exact inputs. Fourteen days keeps recent branches fast. Age counts from when an entry was written, not from its last hit, so a busy entry is rebuilt once per window.

## Rust Target Folders

Cargo never prunes a project's `target` folder. Its automatic cleanup covers only the global cache in `CARGO_HOME`. Every dependency, feature, and profile change leaves artifacts behind, and every dev build adds incremental data, so a Rust crate such as a desktop app's backend grows without bound.

- Set `[profile.dev] debug = "line-tables-only"` in the crate's `Cargo.toml` (Rust 1.71 or later). Backtraces keep file and line numbers while debug info shrinks. A debugger no longer shows local variables.
- Prune with `cargo sweep --time 14` from the crate folder, installed once with `cargo install cargo-sweep`. It reads Cargo's fingerprints, so it removes whole stale units that a rebuild regenerates.
- Keep last-access-time updates enabled on the volume, because cargo-sweep measures age by last access. On Windows, `fsutil behavior query disablelastaccess` reports it.
- Delete `target/debug/incremental` in the same prune, because cargo-sweep leaves it alone. It is a cache the next build recreates, and that build recompiles the crate's own workspace code but not its dependencies.
- Run both steps after each approved commit to `main`. The cargo-sweep README calls the tool unmaintained, so look for an active replacement when installing it.
