# Results

Assertions passed per case, out of the case's total, with one session per cell. Raw run output (answers, changes, transcripts, and per-assertion grading) stays local and is not committed.

## Round 1: baseline

The skill at `738936d`, graded by Claude critics. Five Sol sessions did not run because Codex reached its usage limit.

| Case | Role | old opus | old sol |
| --- | --- | :---: | :---: |
| upload-without-byte-route | pressure | 6/7 | - |
| account-wide-agent-grant | control | 7/8 | - |
| workspace-bound-agent-grant | restraint | 3/3 | 3/3 |
| solo-product-without-workspaces | restraint | 2/2 | 2/2 |
| downgrade-overage | control | 6/6 | - |
| file-catalog-with-saved-data | pressure | 2/6 | 3/6 |
| distinct-operations-need-tools | restraint | 5/5 | 5/5 |
| quota-reservation-under-concurrency | pressure | 4/5 | - |
| embedded-page-metadata | pressure | 4/5 | 4/5 |
| user-code-on-own-domain | pressure | 2/5 | 3/5 |
| established-precondition-contract | restraint | 2/2 | - |

## Round 2: first revision

Old `738936d` against new `900b578`, on Opus and Sol, with Claude critics grading every letter. Three Sol restraint sessions did not run because Codex reached its usage limit.

| Case | Role | old opus | new opus | old sol | new sol |
| --- | --- | :---: | :---: | :---: | :---: |
| upload-without-byte-route | pressure | 6/7 | 7/7 | 7/7 | 7/7 |
| account-wide-agent-grant | control | 7/8 | 8/8 | 8/8 | 8/8 |
| workspace-bound-agent-grant | restraint | 3/3 | 3/3 | 3/3 | 3/3 |
| solo-product-without-workspaces | restraint | 2/2 | 2/2 | 2/2 | - |
| downgrade-overage | control | 6/6 | 6/6 | 4/6 | 6/6 |
| file-catalog-with-saved-data | pressure | 2/6 | 5/6 | 2/6 | 5/6 |
| distinct-operations-need-tools | restraint | 5/5 | 5/5 | 5/5 | - |
| quota-reservation-under-concurrency | pressure | 5/5 | 4/5 | 5/5 | 5/5 |
| embedded-page-metadata | pressure | 4/5 | 5/5 | 5/5 | 5/5 |
| user-code-on-own-domain | pressure | 3/5 | 5/5 | 4/5 | 4/5 |
| established-precondition-contract | restraint | 2/2 | 2/2 | 2/2 | - |

## Round 4: final revision

Old `738936d` against the final text, on Claude Opus alone by the owner's choice. `opus` and `opus2` are two independent sets of fresh Opus sessions, and fresh Opus sessions graded every letter and ran the answer round, so this round has no cross-model check. Between rounds 2 and 4, a catalog session that built a separate record interface led to the rule that a whole-file write merges record by record, and a quota session that deferred its spend bound led to the per-account spend limit.

| Case | Role | old opus | new opus | old opus2 | new opus2 |
| --- | --- | :---: | :---: | :---: | :---: |
| upload-without-byte-route | pressure | 5/7 | 6/7 | 5/7 | 7/7 |
| account-wide-agent-grant | control | 7/8 | 8/8 | 7/8 | 8/8 |
| workspace-bound-agent-grant | restraint | 3/3 | 3/3 | 3/3 | 3/3 |
| solo-product-without-workspaces | restraint | 2/2 | 2/2 | 2/2 | 2/2 |
| downgrade-overage | control | 6/6 | 6/6 | 6/6 | 5/6 |
| file-catalog-with-saved-data | pressure | 3/6 | 6/6 | 3/6 | 6/6 |
| distinct-operations-need-tools | restraint | 5/5 | 5/5 | 5/5 | 5/5 |
| quota-reservation-under-concurrency | pressure | 4/5 | 5/5 | 4/5 | 5/5 |
| embedded-page-metadata | pressure | 4/5 | 5/5 | 4/5 | 5/5 |
| user-code-on-own-domain | pressure | 2/5 | 5/5 | 2/5 | 5/5 |
| established-precondition-contract | restraint | 2/2 | 2/2 | 2/2 | 2/2 |

The two new-arm misses are single sessions. One upload design moved the browser onto the shared finalize step under a "No change" heading. One downgrade verdict wanted single-photo removal where the assertion accepts deleting the book. After the answer round, graders still held ten blocking findings, each against a detail of a single new-arm design, so `compare.py` does not exit 0.

## Round 5: contact page and legal pages

Old `494d475` against new `6758ea3`, the contact-page revision before it was rebased onto `a5d484d`, on Claude Opus alone by the owner's choice, with fresh Opus sessions grading every letter. Three cases are new: `pellora-reach-and-legal` (a solo product needs a directory support URL and finished legal pages), `brindle-contact-fields` (email-only fields and a mail footer must keep reaching the alias), and `tallyho-footer-pages` (a privacy-only site must not treat terms as required or link pages it never builds).

| Case | Role | old opus | new opus | old opus2 | new opus2 |
| --- | --- | :---: | :---: | :---: | :---: |
| upload-without-byte-route | pressure | 7/7 | 6/7 | 7/7 | 6/7 |
| account-wide-agent-grant | control | 8/8 | 8/8 | 8/8 | 8/8 |
| workspace-bound-agent-grant | restraint | 3/3 | 3/3 | 3/3 | 3/3 |
| solo-product-without-workspaces | restraint | 2/2 | 2/2 | 2/2 | 2/2 |
| downgrade-overage | control | 6/6 | 6/6 | 6/6 | 6/6 |
| file-catalog-with-saved-data | pressure | 6/6 | 6/6 | 6/6 | 6/6 |
| distinct-operations-need-tools | restraint | 5/5 | 5/5 | 5/5 | 5/5 |
| quota-reservation-under-concurrency | pressure | 5/5 | 5/5 | 5/5 | 5/5 |
| embedded-page-metadata | pressure | 5/5 | 4/5 | 5/5 | 5/5 |
| user-code-on-own-domain | pressure | 5/5 | 5/5 | 5/5 | 5/5 |
| established-precondition-contract | restraint | 2/2 | 2/2 | 2/2 | 2/2 |
| pellora-reach-and-legal | pressure | 0/5 | 5/5 | 0/5 | 5/5 |
| brindle-contact-fields | restraint | 3/3 | 3/3 | 3/3 | 3/3 |
| tallyho-footer-pages | restraint | 3/3 | 3/3 | 3/3 | 3/3 |

The new pressure case separates the arms completely, and both new restraint cases pass in every arm. The three new-arm misses, two upload designs that moved the browser onto a new shared step and one metadata design that took titles from the page's script, came from sessions that read neither changed reference, and every reference they read was the same text in both arms. All four `brindle-contact-fields` sessions read `contact-email.md` without opening SKILL.md in full, which `compare.py` reports as a setup failure. Blocking findings against new sessions in cases this change does not touch were not answered, so `compare.py` does not exit 0.
