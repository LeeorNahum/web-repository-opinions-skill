# Round 1

Skill commit `738936d01659448e19e26243f5257f7e92a23041`. One session per eval and column. P is a pass, F a fail, and a dash a missing verdict.

Sessions in the round's jobs file that are not recorded:

- `1-upload-without-byte-route-old-sol`: not run yet
- `1-account-wide-agent-grant-old-sol`: not run yet
- `1-downgrade-overage-old-sol`: not run yet
- `1-quota-reservation-under-concurrency-old-sol`: not run yet
- `1-established-precondition-contract-old-sol`: not run yet

Claude critics graded 11 Claude-built sessions because Codex had reached its usage limit. They need a Codex verdict before any comparison.

Sessions in this round ran under more than one version of `evals.json`, and some before the case hash was recorded. Treat the round as a reference record: a before-and-after comparison reruns the old arm in the same round as the new one.

| Assertion | Role | old opus | old sol |
| --- | --- | :---: | :---: |
| `upload-without-byte-route-01` | pressure | P | - |
| `upload-without-byte-route-02` | pressure | P | - |
| `upload-without-byte-route-03` | pressure | P | - |
| `upload-without-byte-route-04` | pressure | P | - |
| `upload-without-byte-route-05` | pressure | P | - |
| `upload-without-byte-route-06` | pressure | P | - |
| `upload-without-byte-route-07` | pressure | F | - |
| `account-wide-agent-grant-01` | control | P | - |
| `account-wide-agent-grant-02` | control | P | - |
| `account-wide-agent-grant-03` | control | P | - |
| `account-wide-agent-grant-04` | control | P | - |
| `account-wide-agent-grant-05` | control | P | - |
| `account-wide-agent-grant-06` | control | P | - |
| `account-wide-agent-grant-07` | control | P | - |
| `account-wide-agent-grant-08` | control | F | - |
| `workspace-bound-agent-grant-01` | restraint | P | P |
| `workspace-bound-agent-grant-02` | restraint | P | P |
| `workspace-bound-agent-grant-03` | restraint | P | P |
| `solo-product-without-workspaces-01` | restraint | P | P |
| `solo-product-without-workspaces-02` | restraint | P | P |
| `downgrade-overage-01` | control | P | - |
| `downgrade-overage-02` | control | P | - |
| `downgrade-overage-03` | control | P | - |
| `downgrade-overage-04` | control | P | - |
| `downgrade-overage-05` | control | P | - |
| `downgrade-overage-06` | control | P | - |
| `file-catalog-with-saved-data-01` | pressure | F | F |
| `file-catalog-with-saved-data-02` | pressure | F | F |
| `file-catalog-with-saved-data-03` | pressure | F | P |
| `file-catalog-with-saved-data-04` | pressure | P | P |
| `file-catalog-with-saved-data-05` | pressure | F | F |
| `file-catalog-with-saved-data-06` | pressure | P | P |
| `distinct-operations-need-tools-01` | restraint | P | P |
| `distinct-operations-need-tools-02` | restraint | P | P |
| `distinct-operations-need-tools-03` | restraint | P | P |
| `distinct-operations-need-tools-04` | restraint | P | P |
| `distinct-operations-need-tools-05` | restraint | P | P |
| `quota-reservation-under-concurrency-01` | pressure | P | - |
| `quota-reservation-under-concurrency-02` | pressure | P | - |
| `quota-reservation-under-concurrency-03` | pressure | P | - |
| `quota-reservation-under-concurrency-04` | pressure | F | - |
| `quota-reservation-under-concurrency-05` | pressure | P | - |
| `embedded-page-metadata-01` | pressure | P | P |
| `embedded-page-metadata-02` | pressure | P | P |
| `embedded-page-metadata-03` | pressure | P | P |
| `embedded-page-metadata-04` | pressure | F | F |
| `embedded-page-metadata-05` | pressure | P | P |
| `user-code-on-own-domain-01` | pressure | F | P |
| `user-code-on-own-domain-02` | pressure | P | P |
| `user-code-on-own-domain-03` | pressure | F | F |
| `user-code-on-own-domain-04` | pressure | P | P |
| `user-code-on-own-domain-05` | pressure | F | F |
| `established-precondition-contract-01` | restraint | P | - |
| `established-precondition-contract-02` | restraint | P | - |

References read counts files whose opening and closing lines came back to the model. For Codex sessions it counts command output, which Codex may shorten before the model sees it, so treat those counts as an upper bound.

| Session | Finished | Skill read | References read | Seconds |
| --- | :---: | :---: | ---: | ---: |
| `1-upload-without-byte-route-old-opus` | yes | yes | 9 | 470.1 |
| `1-account-wide-agent-grant-old-opus` | yes | yes | 14 | 160.0 |
| `1-workspace-bound-agent-grant-old-opus` | yes | yes | 6 | 110.1 |
| `1-workspace-bound-agent-grant-old-sol` | yes | yes | 13 | 100.0 |
| `1-solo-product-without-workspaces-old-opus` | yes | yes | 25 | 145.1 |
| `1-solo-product-without-workspaces-old-sol` | yes | yes | 22 | 125.0 |
| `1-downgrade-overage-old-opus` | yes | yes | 7 | 125.0 |
| `1-file-catalog-with-saved-data-old-opus` | yes | yes | 17 | 240.2 |
| `1-file-catalog-with-saved-data-old-sol` | yes | yes | 16 | 170.1 |
| `1-distinct-operations-need-tools-old-opus` | yes | yes | 9 | 75.1 |
| `1-distinct-operations-need-tools-old-sol` | yes | yes | 9 | 75.1 |
| `1-quota-reservation-under-concurrency-old-opus` | yes | yes | 13 | 175.0 |
| `1-embedded-page-metadata-old-opus` | yes | yes | 12 | 180.1 |
| `1-embedded-page-metadata-old-sol` | yes | yes | 20 | 190.1 |
| `1-user-code-on-own-domain-old-opus` | yes | yes | 5 | 385.1 |
| `1-user-code-on-own-domain-old-sol` | yes | yes | 14 | 255.1 |
| `1-established-precondition-contract-old-opus` | yes | yes | 10 | 280.1 |
