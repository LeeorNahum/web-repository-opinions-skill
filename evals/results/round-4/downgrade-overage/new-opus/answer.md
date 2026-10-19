I've written `docs/downgrade-policy.md`. I didn't commit it. There's no code in the repo yet, so it describes how the backend should enforce the rules, not code that exists.

**The rules:**
- **Nothing is deleted or made worse because someone stopped paying.** Once the paid period ends, a user can still view, download and remove everything they have.
- **Over a limit, users can shrink but not grow.** Anything that adds a book or adds stored space is refused until they're back under the Free limit.
- **Book limit (25 on Free):** the 25 oldest books not in Trash stay fully editable. Newer books can be viewed, downloaded, have photos or pages removed, or be moved to Trash. Nothing else is allowed on them. Which books are editable is worked out on each request, never saved on the book, so resubscribing restores everything at once.
- **Storage limit (1.5 GB on Free):** books in Trash still count toward storage until they're permanently removed. Edits that don't add space (rearranging, captions, layout) stay allowed in the editable books. Uploads are refused until the new photo fits under the limit.
- **Photo size limit (40 MB on Free):** existing larger photos stay at full size and print unchanged. New uploads must be 40 MB or less.
- **Enforcement:** the limits are fixed values in code, and one set of backend checks is used by the browser app, the public API, the MCP connection and background jobs. Each refusal returns a clear error naming the limit hit. There's no site-wide warning banner; limits show up where they're hit and in billing settings.

**Against the typical case in the brief** (40 books, 2.6 GB, fifteen photos of 60–110 MB): the 25 oldest books stay editable and the 15 newest become view-only. All 15 big photos are kept. Uploads are blocked because the user is 1.1 GB over. Emptying Trash only gets them to 2.3 GB, so they'd need to permanently remove about another 0.8 GB. Trashing 16 books lets them create new ones. If they resubscribe, everything works again immediately because they're within all Pro limits.

**Calls I made that you should confirm** (each is listed in the doc, and each can be changed in one place):
1. **Which books stay editable:** the oldest 25. Letting the user pick would mean storing their choice.
2. **Print orders:** refused for books that aren't editable. Allowing them would be reasonable, since printing earns money and uses no plan allowance. It's a one-line change.
3. **Books in Trash:** they don't count toward the 25-book limit, but their space does count toward storage.
4. **Emptying Trash early:** users can permanently delete from Trash before the 14 days are up. Otherwise freeing space could take up to two weeks.
5. **What counts as storage:** only uploaded photos. Thumbnails and print files don't count.
6. **Reusing photos and editing them:** placing a photo again reuses the stored file, and crops or rotations don't save a new copy. If either is wrong, those actions count toward storage and photo size.
7. **No grace period:** Free limits apply the moment the billing provider says the period has ended.
8. **Uploads in progress at that moment:** they must meet Free limits when they complete.