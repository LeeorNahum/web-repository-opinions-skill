# Round 4

Skill commit `old 738936d. New ce6eb1d for nine cases, with embedded-page-metadata on 14de7bf (opus) and 1a9ecd8 (opus2), and user-code-on-own-domain on 2b30f15 (opus) and 1a9ecd8 (opus2)`. One session per eval and column. P is a pass, F a fail, and a dash a missing verdict.

Both subject arms are Claude Opus: `opus` and `opus2` are two independent sets of fresh Opus sessions, not two models. Every grader and every answer round also ran on fresh Claude Opus sessions, by the owner's choice, so this round measures the skill change on one model and gives no cross-model check.

| Assertion | Role | old opus | new opus | old opus2 | new opus2 |
| --- | --- | :---: | :---: | :---: | :---: |
| `upload-without-byte-route-01` | pressure | P | P | P | P |
| `upload-without-byte-route-02` | pressure | P | P | P | P |
| `upload-without-byte-route-03` | pressure | F | P | F | P |
| `upload-without-byte-route-04` | pressure | P | P | P | P |
| `upload-without-byte-route-05` | pressure | P | P | P | P |
| `upload-without-byte-route-06` | pressure | P | F | P | P |
| `upload-without-byte-route-07` | pressure | F | P | F | P |
| `account-wide-agent-grant-01` | control | P | P | P | P |
| `account-wide-agent-grant-02` | control | P | P | P | P |
| `account-wide-agent-grant-03` | control | P | P | P | P |
| `account-wide-agent-grant-04` | control | P | P | P | P |
| `account-wide-agent-grant-05` | control | P | P | P | P |
| `account-wide-agent-grant-06` | control | P | P | P | P |
| `account-wide-agent-grant-07` | control | P | P | P | P |
| `account-wide-agent-grant-08` | control | F | P | F | P |
| `workspace-bound-agent-grant-01` | restraint | P | P | P | P |
| `workspace-bound-agent-grant-02` | restraint | P | P | P | P |
| `workspace-bound-agent-grant-03` | restraint | P | P | P | P |
| `solo-product-without-workspaces-01` | restraint | P | P | P | P |
| `solo-product-without-workspaces-02` | restraint | P | P | P | P |
| `downgrade-overage-01` | control | P | P | P | P |
| `downgrade-overage-02` | control | P | P | P | F |
| `downgrade-overage-03` | control | P | P | P | P |
| `downgrade-overage-04` | control | P | P | P | P |
| `downgrade-overage-05` | control | P | P | P | P |
| `downgrade-overage-06` | control | P | P | P | P |
| `file-catalog-with-saved-data-01` | pressure | F | P | F | P |
| `file-catalog-with-saved-data-02` | pressure | F | P | F | P |
| `file-catalog-with-saved-data-03` | pressure | P | P | P | P |
| `file-catalog-with-saved-data-04` | pressure | P | P | P | P |
| `file-catalog-with-saved-data-05` | pressure | F | P | F | P |
| `file-catalog-with-saved-data-06` | pressure | P | P | P | P |
| `distinct-operations-need-tools-01` | restraint | P | P | P | P |
| `distinct-operations-need-tools-02` | restraint | P | P | P | P |
| `distinct-operations-need-tools-03` | restraint | P | P | P | P |
| `distinct-operations-need-tools-04` | restraint | P | P | P | P |
| `distinct-operations-need-tools-05` | restraint | P | P | P | P |
| `quota-reservation-under-concurrency-01` | pressure | P | P | P | P |
| `quota-reservation-under-concurrency-02` | pressure | P | P | P | P |
| `quota-reservation-under-concurrency-03` | pressure | P | P | P | P |
| `quota-reservation-under-concurrency-04` | pressure | F | P | F | P |
| `quota-reservation-under-concurrency-05` | pressure | P | P | P | P |
| `embedded-page-metadata-01` | pressure | P | P | P | P |
| `embedded-page-metadata-02` | pressure | P | P | P | P |
| `embedded-page-metadata-03` | pressure | P | P | P | P |
| `embedded-page-metadata-04` | pressure | F | P | F | P |
| `embedded-page-metadata-05` | pressure | P | P | P | P |
| `user-code-on-own-domain-01` | pressure | F | P | F | P |
| `user-code-on-own-domain-02` | pressure | P | P | P | P |
| `user-code-on-own-domain-03` | pressure | F | P | F | P |
| `user-code-on-own-domain-04` | pressure | P | P | P | P |
| `user-code-on-own-domain-05` | pressure | F | P | F | P |
| `established-precondition-contract-01` | restraint | P | P | P | P |
| `established-precondition-contract-02` | restraint | P | P | P | P |

References read counts files whose opening and closing lines came back to the model. For Codex sessions it counts command output, which Codex may shorten before the model sees it, so treat those counts as an upper bound.

| Session | Finished | Skill read | References read | Seconds |
| --- | :---: | :---: | ---: | ---: |
| `4-upload-without-byte-route-old-opus` | yes | yes | 15 | 225.1 |
| `4-upload-without-byte-route-new-opus` | yes | yes | 9 | 125.0 |
| `4-upload-without-byte-route-old-opus2` | yes | yes | 10 | 175.0 |
| `4-upload-without-byte-route-new-opus2` | yes | yes | 9 | 120.0 |
| `4-file-catalog-with-saved-data-old-opus` | yes | yes | 18 | 190.0 |
| `4-file-catalog-with-saved-data-new-opus` | yes | yes | 19 | 215.0 |
| `4-file-catalog-with-saved-data-old-opus2` | yes | yes | 22 | 195.0 |
| `4-file-catalog-with-saved-data-new-opus2` | yes | yes | 20 | 195.0 |
| `4-quota-reservation-under-concurrency-old-opus` | yes | yes | 12 | 155.0 |
| `4-quota-reservation-under-concurrency-new-opus` | yes | yes | 13 | 190.0 |
| `4-quota-reservation-under-concurrency-old-opus2` | yes | yes | 10 | 190.0 |
| `4-quota-reservation-under-concurrency-new-opus2` | yes | yes | 7 | 180.0 |
| `4-embedded-page-metadata-old-opus` | yes | yes | 13 | 200.0 |
| `4-embedded-page-metadata-new-opus` | yes | yes | 11 | 175.0 |
| `4-embedded-page-metadata-old-opus2` | yes | yes | 12 | 190.0 |
| `4-embedded-page-metadata-new-opus2` | yes | yes | 11 | 185.8 |
| `4-user-code-on-own-domain-old-opus` | yes | yes | 6 | 185.2 |
| `4-user-code-on-own-domain-new-opus` | yes | yes | 4 | 155.0 |
| `4-user-code-on-own-domain-old-opus2` | yes | yes | 5 | 155.0 |
| `4-user-code-on-own-domain-new-opus2` | yes | yes | 7 | 130.0 |
| `4-account-wide-agent-grant-old-opus` | yes | yes | 13 | 180.1 |
| `4-account-wide-agent-grant-new-opus` | yes | yes | 19 | 180.0 |
| `4-account-wide-agent-grant-old-opus2` | yes | yes | 20 | 185.0 |
| `4-account-wide-agent-grant-new-opus2` | yes | yes | 10 | 140.0 |
| `4-downgrade-overage-old-opus` | yes | yes | 6 | 105.0 |
| `4-downgrade-overage-new-opus` | yes | yes | 6 | 105.0 |
| `4-downgrade-overage-old-opus2` | yes | yes | 5 | 135.7 |
| `4-downgrade-overage-new-opus2` | yes | yes | 8 | 110.0 |
| `4-workspace-bound-agent-grant-old-opus` | yes | yes | 8 | 95.0 |
| `4-workspace-bound-agent-grant-new-opus` | yes | yes | 10 | 115.0 |
| `4-workspace-bound-agent-grant-old-opus2` | yes | yes | 10 | 110.0 |
| `4-workspace-bound-agent-grant-new-opus2` | yes | yes | 8 | 135.0 |
| `4-solo-product-without-workspaces-old-opus` | yes | yes | 23 | 150.0 |
| `4-solo-product-without-workspaces-new-opus` | yes | yes | 20 | 125.0 |
| `4-solo-product-without-workspaces-old-opus2` | yes | yes | 24 | 190.0 |
| `4-solo-product-without-workspaces-new-opus2` | yes | yes | 24 | 165.0 |
| `4-distinct-operations-need-tools-old-opus` | yes | yes | 11 | 90.0 |
| `4-distinct-operations-need-tools-new-opus` | yes | yes | 7 | 60.1 |
| `4-distinct-operations-need-tools-old-opus2` | yes | yes | 11 | 75.0 |
| `4-distinct-operations-need-tools-new-opus2` | yes | yes | 6 | 60.0 |
| `4-established-precondition-contract-old-opus` | yes | yes | 9 | 90.0 |
| `4-established-precondition-contract-new-opus` | yes | yes | 9 | 110.0 |
| `4-established-precondition-contract-old-opus2` | yes | yes | 6 | 90.0 |
| `4-established-precondition-contract-new-opus2` | yes | yes | 7 | 85.0 |
