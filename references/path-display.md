# Path Display

## Shortening Must Have A Floor

A shortener that can return a bare ellipsis has failed at its one job. Give it a ladder with a floor: drop interior segments first, then shorten them, and keep the first and last segments whole to the end. If even that does not fit, the honest move is to give the path its own full-width line rather than to shred it, because a readable owner and leaf beat an unreadable full path.

Never let an element's available width be derived from a box that the element's own content shrank. That measurement is circular: each pass hands back what the last pass gave up, and it converges on the element getting nothing, which is exactly how a path collapses to a single ellipsis while the same component elsewhere on the page renders fine. Measure siblings at their natural width, and decide the layout from that.

When one surface shortens a path correctly and another does not, the difference is almost always that the working one gives the path a row to itself. Suspect the measurement, not the shortener.

How a product shows remote or hierarchical file paths to a person. The location of an item is expressed in exactly one place; everything else names the item alone.

## One Location, Expressed Once

- The breadcrumb (or path bar) above a listing is the sole expression of where the user is. Every parent segment is clickable; the final segment is the current location and is not a link.
- A listing row shows only the entry's own name: one segment, never its parents, never a leading slash. The row's location is already told by the breadcrumb above it.
- A file viewer or editor names its file the same way: the breadcrumb carries the parents, the header carries the bare filename. Never a raw joined path in a heading.

## The Root Is a Word

- The root of the browsable tree renders as a word, `home`, never as a bare `/` or the provider's mount path. A non-technical operator reads "home / projects / notes.txt" without knowing what a root slash is.
- The underlying remote root (a jail directory, a mount) is configuration, shown in settings where it is edited, not repeated as a prefix on every path in the browsing surface.

## Data Contract Behind the Display

- A directory-listing entry carries two fields with fixed meanings: `name` is the entry's own leaf (one path segment, no slashes), and `path` is the entry's full path from the product root. Clients navigate and act with `path` and display `name`; no client ever joins a parent onto a name.
- Every path a tool returns is a product path a caller can pass straight back to another verb. Jailed absolute paths, provider mount prefixes, and doubled slashes never leak into results, errors, or URLs.
- Search and recursive matches are the exception where a full path IS the display: a match list is location-first by nature, so it shows `path` (with line and column when relevant), like a code-search tool does.

## Never Restyle The Case Of A Name

The case a person sees on a name, filename, path segment, or identifier must be the case that is stored. A case transform applied to a value is a lie the reader cannot detect, and they may type back what they saw: `SKILL.md` styled uppercase reads as `SKILL.MD`, which a case-sensitive system then rejects.

Whatever case styling a product uses on its own labels, it stops at the boundary of data. This is easy to introduce and hard to see, because one rule usually styles a label and the value beside it together.

## Failure Smells

- A doubled segment or double slash anywhere (`//files//files/x`) means a client joined a path onto a path; fix the contract, not the string.
- A row that repeats its parent directory on every line is noise the breadcrumb already carries.
- A heading that starts with `/` or the remote mount path is speaking the implementation's frame, not the operator's.
