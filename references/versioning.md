# Versioning

Version anything that ships: apps, packages, and downloadable artifacts. Use semantic versioning.

Bump the version in the same change that alters behavior, never in a separate commit after it.

When a version changes, keep every mention of it in sync in the same change: package metadata, README badges or version lines, and any release notes. A version stated in two places that disagree is a bug.

Calibrate the bump to the full delta since the last released state, not to the size of the latest edit alone. A run of small additions since the last release can warrant one honest minor bump rather than many micro bumps.
