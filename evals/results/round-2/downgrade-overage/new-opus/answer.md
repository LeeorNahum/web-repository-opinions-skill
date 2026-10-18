I've written `docs/downgrade-policy.md`. I didn't commit it, and I left `docs/brief.md` untouched since that's your record. There's no backend code in the repo yet, so the enforcement section is a contract for whoever builds it, not a description of existing code.

**The rules once the paid period ends:**
- **Nothing is deleted or shrunk.** Every book and photo is kept at full size, and Trash keeps its normal 14-day schedule.
- **Books (Free allows 25):** the 25 oldest books stay fully editable. The rest become read-only: they can still be viewed, downloaded, printed and moved to Trash, but not edited. No new or restored books while 25 or more are active. Moving a book to Trash frees a slot right away.
- **Storage (Free allows 1.5 GB, Trash included):** while over, all uploads are refused. Edits that don't add bytes still work, and viewing, downloading, printing and deleting always do.
- **Photo size (Free allows 40 MB):** existing larger photos are kept and still print. New uploads must be 40 MB or less.
- **Resubscribing** restores everything instantly. Editability is worked out from the current plan each time rather than stored as a lock on each book, so there's nothing to undo.

**The typical case from the brief:** the 15 newest books become read-only and all uploads stop, since 2.6 GB is 1.1 GB over. The 15 large photos stay as they are. Trash purges on its own within 14 days, leaving 2.3 GB, still 0.8 GB over. The 15 large photos alone take 0.9–1.65 GB, so the user can get back under by their own choices. Their whole account fits within Pro again (40 of 60 books, 2.6 of 4 GB, largest photo 110 MB under 120 MB), so resubscribing fully reverses the downgrade.

**How the backend enforces it:** the plan comes from the billing provider, with a local copy kept current by its notifications. Plan limits are constants in a shared code package. One set of checks covers the browser, the API, MCP and background jobs. Refusals return one of four error codes with the measured value and the limit, and each error suggests only fixes that actually clear it.

**Calls I made that you should confirm (all listed at the end of the doc):**
1. Read-only books can still be printed.
2. The oldest books are the ones that stay editable; users don't pick.
3. Books in Trash count toward storage but not the 25-book limit.
4. I read "40 books" as 40 outside Trash, with the 300 MB in Trash coming from other books.
5. Removing a photo from a book deletes it permanently, since the brief only defines Trash for whole books.
6. A photo used on several pages is stored only once.
7. GB and MB are decimal units.
8. There's no grace period after the paid period, and how to handle failed payments is still undecided.
9. No email goes out when the plan ends.