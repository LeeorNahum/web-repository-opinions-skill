I've written the plan to `docs/architecture.md`. It's a plan only: nothing is built and nothing is committed. Each call I made without you is tagged **[Assumed]**, and the doc ends with a numbered list of assumptions and open questions.

**What I decided:**
- **No workspace or team layer.** Your brief rules out sharing and teams permanently, so each account is the boundary around its own entries. Organizations are turned off in the auth provider (Clerk), and URLs carry no account segment.
- **Auth:** Clerk with Google plus an emailed one-time code, and no passwords. There's a single `/auth` page that sends people back to where they were. The account record is created the first time someone signs in, not only when a webhook arrives.
- **One access check for all private data.** The backend works out the account from the verified sign-in and never accepts an account ID from the browser. Opening someone else's entry looks exactly like opening one that doesn't exist.
- **Who owns what:** Clerk holds identity and email (I don't store email in our database). Stripe holds the subscription, and we keep only a copy updated by its webhooks. Convex holds accounts and entries, one entry per calendar day.
- **Search:** search covers full entry text, always limited to the signed-in account.
- **Lapsed subscriptions:** people can still read, search, export and delete their own entries. Only writing and editing are paid features.
- **Deleting an account** removes the data in stages, cancels the subscription, and then deletes the Clerk user.
- **URLs:** the app's home page `/` is Today. `/entries` is the calendar (with `?month=` to pick a month), `/entries/[id]` is a single entry, `/search?q=` is search, `/settings/{preferences,account,billing,data}` is settings, and `/auth` is sign-in. There are no public or share links, and none are planned.

**Questions for you, most important first:**
1. **Access control or end-to-end encryption.** As planned, the hosting platform and anyone with the production keys could technically read entries. If "visible only to the person who wrote them" has to hold even against you as the operator, entries need encrypting in the browser. That would move search into the browser and mean a lost key is a lost journal. This needs deciding before anything is built, and your marketing and privacy-policy wording should match the choice.
2. **Free tier or trial**, and prices.
3. **Apple sign-in at launch?**
4. **Smaller calls that are easy to change now:**
   - one entry per day
   - rich text rather than plain text or markdown
   - deleting an entry is permanent, with a short undo and no trash
   - export is included even though the brief doesn't list it
   - no images in v1
   - search terms in the URL: they would show up in hosting logs unless logging and analytics strip query strings
5. **Domain:** `marrowjournal.com` is a placeholder.

One thing outside this task: your working branch is `master`, while the repo's main branch is `main`. I left the branches alone.