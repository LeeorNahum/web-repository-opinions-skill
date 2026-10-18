# Round 2

Skill commit `old 738936d, new 900b578 (file-catalog and quota Sol new on 1160137)`. One session per eval and column. P is a pass, F a fail, and a dash a missing verdict.

Sessions in the round's jobs file that are not recorded:

- `2-solo-product-without-workspaces-new-sol`: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 5:58 AM.
- `2-distinct-operations-need-tools-new-sol`: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 5:58 AM.
- `2-established-precondition-contract-new-sol`: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 5:58 AM.

Claude critics graded 22 Claude-built sessions because Codex had reached its usage limit. They need a Codex verdict before any comparison.

| Assertion | Role | old opus | new opus | old sol | new sol |
| --- | --- | :---: | :---: | :---: | :---: |
| `upload-without-byte-route-01` | pressure | P | P | P | P |
| `upload-without-byte-route-02` | pressure | P | P | P | P |
| `upload-without-byte-route-03` | pressure | P | P | P | P |
| `upload-without-byte-route-04` | pressure | P | P | P | P |
| `upload-without-byte-route-05` | pressure | P | P | P | P |
| `upload-without-byte-route-06` | pressure | P | P | P | P |
| `upload-without-byte-route-07` | pressure | F | P | P | P |
| `account-wide-agent-grant-01` | control | P | P | P | P |
| `account-wide-agent-grant-02` | control | P | P | P | P |
| `account-wide-agent-grant-03` | control | P | P | P | P |
| `account-wide-agent-grant-04` | control | P | P | P | P |
| `account-wide-agent-grant-05` | control | P | P | P | P |
| `account-wide-agent-grant-06` | control | P | P | P | P |
| `account-wide-agent-grant-07` | control | P | P | P | P |
| `account-wide-agent-grant-08` | control | F | P | P | P |
| `workspace-bound-agent-grant-01` | restraint | P | P | P | P |
| `workspace-bound-agent-grant-02` | restraint | P | P | P | P |
| `workspace-bound-agent-grant-03` | restraint | P | P | P | P |
| `solo-product-without-workspaces-01` | restraint | P | P | P | - |
| `solo-product-without-workspaces-02` | restraint | P | P | P | - |
| `downgrade-overage-01` | control | P | P | P | P |
| `downgrade-overage-02` | control | P | P | F | P |
| `downgrade-overage-03` | control | P | P | F | P |
| `downgrade-overage-04` | control | P | P | P | P |
| `downgrade-overage-05` | control | P | P | P | P |
| `downgrade-overage-06` | control | P | P | P | P |
| `file-catalog-with-saved-data-01` | pressure | F | F | F | P |
| `file-catalog-with-saved-data-02` | pressure | F | P | F | P |
| `file-catalog-with-saved-data-03` | pressure | P | P | P | P |
| `file-catalog-with-saved-data-04` | pressure | F | P | F | F |
| `file-catalog-with-saved-data-05` | pressure | F | P | F | P |
| `file-catalog-with-saved-data-06` | pressure | P | P | P | P |
| `distinct-operations-need-tools-01` | restraint | P | P | P | - |
| `distinct-operations-need-tools-02` | restraint | P | P | P | - |
| `distinct-operations-need-tools-03` | restraint | P | P | P | - |
| `distinct-operations-need-tools-04` | restraint | P | P | P | - |
| `distinct-operations-need-tools-05` | restraint | P | P | P | - |
| `quota-reservation-under-concurrency-01` | pressure | P | P | P | P |
| `quota-reservation-under-concurrency-02` | pressure | P | P | P | P |
| `quota-reservation-under-concurrency-03` | pressure | P | P | P | P |
| `quota-reservation-under-concurrency-04` | pressure | P | F | P | P |
| `quota-reservation-under-concurrency-05` | pressure | P | P | P | P |
| `embedded-page-metadata-01` | pressure | P | P | P | P |
| `embedded-page-metadata-02` | pressure | P | P | P | P |
| `embedded-page-metadata-03` | pressure | P | P | P | P |
| `embedded-page-metadata-04` | pressure | F | P | P | P |
| `embedded-page-metadata-05` | pressure | P | P | P | P |
| `user-code-on-own-domain-01` | pressure | P | P | P | P |
| `user-code-on-own-domain-02` | pressure | P | P | P | P |
| `user-code-on-own-domain-03` | pressure | F | P | P | P |
| `user-code-on-own-domain-04` | pressure | P | P | P | P |
| `user-code-on-own-domain-05` | pressure | F | P | F | F |
| `established-precondition-contract-01` | restraint | P | P | P | - |
| `established-precondition-contract-02` | restraint | P | P | P | - |

References read counts files whose opening and closing lines came back to the model. For Codex sessions it counts command output, which Codex may shorten before the model sees it, so treat those counts as an upper bound.

| Session | Finished | Skill read | References read | Seconds |
| --- | :---: | :---: | ---: | ---: |
| `2-upload-without-byte-route-old-opus` | yes | yes | 11 | 210.1 |
| `2-upload-without-byte-route-new-opus` | yes | yes | 8 | 150.1 |
| `2-file-catalog-with-saved-data-old-opus` | yes | yes | 23 | 205.1 |
| `2-file-catalog-with-saved-data-new-opus` | yes | yes | 21 | 240.1 |
| `2-quota-reservation-under-concurrency-old-opus` | yes | yes | 10 | 205.0 |
| `2-quota-reservation-under-concurrency-new-opus` | yes | yes | 11 | 230.1 |
| `2-embedded-page-metadata-old-opus` | yes | yes | 5 | 145.0 |
| `2-embedded-page-metadata-new-opus` | yes | yes | 13 | 195.0 |
| `2-user-code-on-own-domain-old-opus` | yes | yes | 5 | 180.0 |
| `2-user-code-on-own-domain-new-opus` | yes | yes | 4 | 170.1 |
| `2-account-wide-agent-grant-old-opus` | yes | yes | 16 | 165.0 |
| `2-account-wide-agent-grant-new-opus` | yes | yes | 11 | 135.0 |
| `2-downgrade-overage-old-opus` | yes | yes | 5 | 105.0 |
| `2-downgrade-overage-new-opus` | yes | yes | 6 | 145.1 |
| `2-workspace-bound-agent-grant-old-opus` | yes | yes | 10 | 120.0 |
| `2-workspace-bound-agent-grant-new-opus` | yes | yes | 5 | 115.1 |
| `2-solo-product-without-workspaces-old-opus` | yes | yes | 32 | 180.1 |
| `2-solo-product-without-workspaces-new-opus` | yes | yes | 27 | 190.1 |
| `2-distinct-operations-need-tools-old-opus` | yes | yes | 11 | 65.0 |
| `2-distinct-operations-need-tools-new-opus` | yes | yes | 5 | 75.1 |
| `2-established-precondition-contract-old-opus` | yes | yes | 8 | 95.0 |
| `2-established-precondition-contract-new-opus` | yes | yes | 5 | 105.1 |
| `2-upload-without-byte-route-old-sol` | yes | yes | 16 | 240.1 |
| `2-upload-without-byte-route-new-sol` | yes | yes | 16 | 270.1 |
| `2-file-catalog-with-saved-data-old-sol` | yes | yes | 17 | 160.1 |
| `2-file-catalog-with-saved-data-new-sol` | yes | yes | 14 | 240.1 |
| `2-quota-reservation-under-concurrency-old-sol` | yes | yes | 16 | 310.1 |
| `2-quota-reservation-under-concurrency-new-sol` | yes | yes | 13 | 225.1 |
| `2-embedded-page-metadata-old-sol` | yes | yes | 16 | 135.1 |
| `2-embedded-page-metadata-new-sol` | yes | yes | 18 | 150.0 |
| `2-user-code-on-own-domain-old-sol` | yes | yes | 20 | 150.1 |
| `2-user-code-on-own-domain-new-sol` | yes | yes | 15 | 150.1 |
| `2-account-wide-agent-grant-old-sol` | yes | yes | 15 | 130.1 |
| `2-account-wide-agent-grant-new-sol` | yes | yes | 17 | 150.1 |
| `2-downgrade-overage-old-sol` | yes | yes | 9 | 120.1 |
| `2-downgrade-overage-new-sol` | yes | yes | 10 | 115.1 |
| `2-workspace-bound-agent-grant-old-sol` | yes | yes | 13 | 105.0 |
| `2-workspace-bound-agent-grant-new-sol` | yes | yes | 16 | 160.0 |
| `2-solo-product-without-workspaces-old-sol` | yes | yes | 24 | 135.0 |
| `2-distinct-operations-need-tools-old-sol` | yes | yes | 10 | 105.0 |
| `2-established-precondition-contract-old-sol` | yes | yes | 10 | 95.0 |
