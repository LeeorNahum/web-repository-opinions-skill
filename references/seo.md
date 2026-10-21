# SEO

SEO is a property of public pages only. Apply it to the marketing site. The tab title rule below applies to every page, public or signed-in.

Set a unique title and description on every public page.

## The Homepage Names The Product

The public homepage carries exactly one `h1`, and the product's name is in it, because automated reviewers read the `h1` as the app's name, and a mismatch against the registered name fails checks the product needs to pass. Providers' OAuth consent branding review does exactly this. So does anything else that has to identify a site without a human reading it.

Follow the heading with one server-rendered sentence, the first paragraph after the `h1` and visible in the first viewport at phone width, that names the product and says what it does, so a cold reviewer or a crawler understands the site without scrolling and without JavaScript. Neither line is keyword filler: write what a person would read aloud.

## The Tab Title Leads With The Page

A tab title is read from the left. Tab strips, window switchers, and phone browsers truncate from the right, and the more tabs a person has open the fewer leading characters survive. So the page's own subject goes first and the site name goes last, with one separator chosen once and used everywhere. On the homepage the subject is the product itself, so its title is the product name, optionally followed by the separator and the product's one-line promise.

Take the subject from the page's own main heading. A tab that says something the page never says is a second name for the same page, and the reader cannot tell which one the site means.

A page about one object leads with that object's own name, not with the name of its type. A detail route titled by its type gives every one of its pages an identical tab, so a person who opened six of them has six tabs that read the same and must visit each to find the one they wanted. The object's name is already on their screen, so the generic title conceals nothing and spends the only signal a tab strip can carry.

Within one object's routes the object keeps leading and the view inside it follows, so tabs group by object and the part after the name is what tells them apart. Name the file or section on screen, and add a word only for a mode that changes what the page does. The default reading view needs no word.

Private pages follow the same rule, with the client setting the object's name as the tab title once its data loads, because the name in a tab is something the reader is already looking at.

When the object's name is not known to the server, because the URL addresses it by opaque ID or the view reads live data, the title still leads with it. Give the route a static title that names the type, as the value that stands until the data lands, then write the real title from the data the view already loaded rather than fetching it a second time. Two things have to hold and both are easy to miss. Reset to the placeholder whenever the identity changes, or the previous object's name stays in the tab while the next one loads. And treat the framework's own title as a competitor, because a router that re-renders the document head can supersede a title written imperatively: reassert the title when the head changes, and verify a tab after a client-side navigation rather than only after a reload.
