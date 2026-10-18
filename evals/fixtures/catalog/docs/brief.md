# Fernpage

Fernpage hosts small interactive static sites that people's AI agents write for them: a wedding RSVP page, a team checklist, a recipe box. A site is HTML, CSS, JavaScript, and assets, served at its own URL.

## Saved data

Sites can keep small saved data, such as RSVP entries, checklist state, and site settings. It is a few kilobytes to a few megabytes per site, stored in our reactive database. Visitors' browsers read and write it through a small runtime SDK, one entry at a time, and every open page updates live.

Rules a site declares in its settings decide who may write what. For example, anyone may tick a shared checklist item, while an RSVP entry can be edited only by the visitor who created it or by the site owner.

## What agents need to do

- Create a site in one of the user's workspaces and fill in its files.
- Change files later, often one small edit.
- Read and occasionally fix saved data: seed a checklist, correct a misspelled RSVP name, clear test entries before launch, change a setting.
- Remove a file, or remove a whole site.

Visitors may be writing saved data at the same moment an agent edits it.

## Decided

- A site's title, description, and favicon come from its `index.html`.
- One `index.html` is enough to publish a site.
- Deleting a site moves it to Trash for 30 days. Restoring is done in the browser app only.
