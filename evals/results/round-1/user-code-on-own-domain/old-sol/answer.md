Wrote [docs/hosting-plan.md](docs/hosting-plan.md).

Recommends a restricted sandboxed beta that preserves short URLs during the freeze. Native `localStorage` apps must wait because restoring it would reopen the shared-cookie risk.

Includes private-access rules, release gates, post-freeze options and assumptions. Checked whitespace and local links. No infrastructure changed.