# Round 1

Skill commit `738936d01659448e19e26243f5257f7e92a23041`. One session per eval and column. P is a pass, F a fail, and a dash a missing verdict.

Sessions in the round that did not finish, and are not recorded:

- `1-upload-without-byte-route-old-sol`: not run yet
- `1-account-wide-agent-grant-old-sol`: not run yet
- `1-downgrade-overage-old-sol`: not run yet
- `1-quota-reservation-under-concurrency-old-sol`: not run yet
- `1-established-precondition-contract-old-sol`: not run yet

Claude critics graded 11 Claude-built sessions because Codex was unreachable. They need a Codex verdict before any comparison.

| Assertion | old opus | old sol |
| --- | :---: | :---: |
| `upload-without-byte-route-01` | P | - |
| `upload-without-byte-route-02` | P | - |
| `upload-without-byte-route-03` | P | - |
| `upload-without-byte-route-04` | P | - |
| `upload-without-byte-route-05` | P | - |
| `upload-without-byte-route-06` | P | - |
| `upload-without-byte-route-07` | F | - |
| `account-wide-agent-grant-01` | F | - |
| `account-wide-agent-grant-02` | P | - |
| `account-wide-agent-grant-03` | P | - |
| `account-wide-agent-grant-04` | P | - |
| `account-wide-agent-grant-05` | P | - |
| `account-wide-agent-grant-06` | P | - |
| `account-wide-agent-grant-07` | P | - |
| `workspace-bound-agent-grant-01` | P | P |
| `workspace-bound-agent-grant-02` | P | P |
| `workspace-bound-agent-grant-03` | P | P |
| `solo-product-without-workspaces-01` | P | P |
| `solo-product-without-workspaces-02` | P | P |
| `downgrade-overage-01` | P | - |
| `downgrade-overage-02` | F | - |
| `downgrade-overage-03` | P | - |
| `downgrade-overage-04` | P | - |
| `downgrade-overage-05` | P | - |
| `downgrade-overage-06` | P | - |
| `file-catalog-with-saved-data-01` | F | F |
| `file-catalog-with-saved-data-02` | F | F |
| `file-catalog-with-saved-data-03` | F | P |
| `file-catalog-with-saved-data-04` | P | P |
| `file-catalog-with-saved-data-05` | F | F |
| `file-catalog-with-saved-data-06` | P | P |
| `distinct-operations-need-tools-01` | P | P |
| `distinct-operations-need-tools-02` | P | P |
| `distinct-operations-need-tools-03` | P | P |
| `distinct-operations-need-tools-04` | P | P |
| `distinct-operations-need-tools-05` | P | P |
| `quota-reservation-under-concurrency-01` | P | - |
| `quota-reservation-under-concurrency-02` | P | - |
| `quota-reservation-under-concurrency-03` | P | - |
| `quota-reservation-under-concurrency-04` | F | - |
| `quota-reservation-under-concurrency-05` | P | - |
| `embedded-page-metadata-01` | P | P |
| `embedded-page-metadata-02` | P | P |
| `embedded-page-metadata-03` | P | P |
| `embedded-page-metadata-04` | F | F |
| `embedded-page-metadata-05` | P | P |
| `user-code-on-own-domain-01` | F | P |
| `user-code-on-own-domain-02` | P | P |
| `user-code-on-own-domain-03` | F | F |
| `user-code-on-own-domain-04` | P | P |
| `user-code-on-own-domain-05` | F | F |
| `established-precondition-contract-01` | P | - |
| `established-precondition-contract-02` | P | - |

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
