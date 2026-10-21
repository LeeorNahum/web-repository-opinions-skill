# Loading States

A loading state's job is to hold the exact shape of the page that is coming, so nothing visibly changes when the real content lands.

## Reserve The Final Geometry

- A loading placeholder occupies the same size, position, and structure as the content it stands in for. A skeleton row is the height of a real row. A skeleton card grid has the same column count as the real grid. While content resolves, cumulative layout shift stays below 0.01 and no element outside the loading region moves.
- Prefer skeletons over spinners for content people are used to scanning: lists, tables, cards. A spinner is acceptable for a single, small, isolated action, a button's own pending state. It is not a substitute for a skeleton over a whole content region.
- A full-page splash shares the frame, chrome, and proportions of the shell it precedes. A splash shaped differently from its shell makes the boot do two layouts, and the visitor watches the seam.

## The Shell Boots First, Regions Fill Independently

Render the app's persistent frame, navigation, header, page chrome, as soon as the route resolves, before any data is known. Let each content region inside that frame carry its own loading state and resolve independently, so the slowest query holds back only its own region. A page that waits for every region to be ready before showing any of it is a single, slower spinner wearing a page-shaped costume.

## Resolve Destinations In Place

A route whose only job is to decide where a visitor actually belongs, an unauthenticated root sending a signed-in visitor into their default workspace, a locale root choosing a language, is a dispatcher, not a page. While it resolves, it shows the shell and nothing of its own. Put the decision in one shared resolver. Every route that legitimately ends in it, the entry root, the post-auth return, a switcher's landing route, renders that resolver in place and navigates to its result with a history replace, so Back skips it and no visitor passes through another route's URL to borrow its redirect logic.

## Diagnose Before Changing Rendering

A rendering posture change, client to server or the reverse, relocates a bad loading sequence rather than repairing it. Diagnose whether the defect is geometry (content reflows), sequencing (the shell waits on data it does not need), or routing (a visitor passes through a page with an unrelated meaning) before reaching for a different rendering tool.
