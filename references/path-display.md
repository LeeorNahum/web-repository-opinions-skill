# Path Display

How a product shows file paths and other browsable hierarchies to a person. The location of an item is expressed in exactly one place. Everything else names the item alone.

## One Location, Expressed Once

- The breadcrumb (or path bar) above a listing is the sole expression of where the user is. Every parent segment is clickable. The final segment is the current location and is not a link.
- A listing row shows only the entry's own name, one segment with no parents and no leading slash. The row's location is already told by the breadcrumb above it.
- A file viewer or editor names its file the same way: the breadcrumb carries the parents, the header carries the bare filename.

## The Root Is a Word

- The root of a browsable hierarchy renders as a product word the user recognizes, so a non-technical reader follows the breadcrumb without knowing what a root slash or a mount is.
- The underlying storage root is configuration, shown only in the settings where it is edited.

## Data Contract Behind the Display

- A directory-listing entry carries two fields with fixed meanings: `name` is the entry's own leaf (one path segment, no slashes), and `path` is the entry's full path from the product root. Clients navigate and act with `path` and display `name`. No client ever joins a parent onto a name.
- Every path an interface returns is a product path the caller can pass back unchanged, with no storage prefix or doubled slash, in results, errors, and URLs alike.
- Search and recursive matches are the exception where a full path IS the display: a match list is location-first by nature, so it shows `path`, with line and column when relevant.

## Structured Text

Treat paths, breadcrumbs, namespaced identifiers, and other separator-delimited values as ordered semantic units, not ordinary prose. Define which units matter before implementing truncation.

When both the origin and destination matter, use an outside-in priority by default: first unit, last unit, next unit from the left, next unit from the right, continuing inward. Keep every accepted unit in its original order and collapse each omitted run to one ellipsis. Use a different order only when the product has a clearer semantic priority.

Measure the final candidate against the real available width when font metrics, sibling controls, or container size affect the result. Continue evaluating later units after one candidate fails to fit. A later, shorter unit may still fit and carry more useful context.

If the highest-priority endpoint units cannot both fit in full, abbreviate within those endpoints while preserving both sides for as long as the available width allows. Keep the complete value available through an accessible name and, when useful, a pointer tooltip. A shortener always returns at least one readable unit. If even the abbreviated endpoints do not fit, give the value its own full-width line rather than shred it, because a readable owner and leaf beat an unreadable full value.

Measure an element's available width from its siblings at their natural width, never from a box the element's own content shrank. That measurement is circular: each pass hands back what the last pass gave up, and it converges on the element getting nothing.

Put the selection and compaction policy in a deterministic formatter that can be tested independently from rendering. Reserve CSS text overflow for final containment after the semantic truncation algorithm runs.

Test the full value, several intermediate widths, a width where one candidate fails but a later candidate fits, and a width narrower than both endpoint units. Assert both the semantic order and the measured width.
