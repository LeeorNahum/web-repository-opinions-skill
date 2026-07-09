# Path Display

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

## Failure Smells

- A doubled segment or double slash anywhere (`//files//files/x`) means a client joined a path onto a path; fix the contract, not the string.
- A row that repeats its parent directory on every line is noise the breadcrumb already carries.
- A heading that starts with `/` or the remote mount path is speaking the implementation's frame, not the operator's.
