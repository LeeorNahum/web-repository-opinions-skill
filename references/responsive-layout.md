# Responsive Layout

Design for available space and input capabilities, not a mobile or desktop label. A narrow desktop window and a narrow phone should receive the layout their containers can support. A large touch display should gain useful space without being trapped in a reduced phone layout.

Every page and view must remain fully usable and intentional from its smallest supported container to its largest. Responsiveness is a requirement of done, not a later polish pass.

Web-derived means any environment whose layout model descends from HTML and CSS: browser apps, SPAs, server-rendered frameworks, browser extensions, React Native, Expo, cross-platform hybrids, and web-adjacent rendering layers. If the environment understands a box model, relative units, or viewport dimensions, this applies.

## Smallest Viable Space First

Design from the smallest viable container outward. Each increase in available space is an opportunity to reveal labels, increase density, or change composition. Device identity does not determine which state is active. This is mobile-first generalized: start from the smallest viable container rather than a device class, and treat each gain in space as a chance to enhance.

## Fluid By Default

Prefer continuous, fluid sizing over a few hard breakpoints. Layout should adapt at every width, not jump between two or three fixed designs.

- Use intrinsic and proportional sizing, fractional grids, and flexible wrapping so layout flexes continuously.
- Use fluid type and spacing that scale smoothly with the viewport between sensible minimums and maximums, rather than fixed sizes swapped at breakpoints.
- Reach for container-based responsiveness so a component adapts to the space it occupies, not only to the global viewport. This keeps a component correct when reused in a sidebar, a modal, or a full page.
- Collapse labels and controls from measured container fit. Preserve text while the actual space supports it.
- Treat breakpoints as a coarse tool for genuine layout changes, such as moving from a stacked to a side-by-side structure, not as the primary mechanism for every size adjustment.

Fixed values belong only where size must never vary: icon assets at a declared size, hairline borders, and minimum touch-target sizes.

Use viewport media queries for page-level composition and container queries or measured fit for reusable components. Use input media features such as `hover` and `pointer` only for interaction capabilities, never as a proxy for a device category.

## Typography And Reading

Type stays readable at every viewport. Scale heading hierarchy gracefully on small screens, and constrain body line length to a comfortable reading measure on wide screens so text does not stretch across the full width.

## Touch And Pointer

Interactive elements are large enough to activate reliably by touch, and remain comfortable with a mouse. This holds for browser apps, extension popups, React Native, Expo, and any touch-capable surface.

## Media

Images and media stay bounded by their containers, never overflowing and never distorting. Serve appropriately sized assets when the environment supports it.

## Content Priority

When space is constrained, decide what to show, defer, or hide, not only how to reflow. A wide navigation model may need a different constrained-space composition instead of a squeezed copy.

### Structured Text

Treat paths, breadcrumbs, namespaced identifiers, and other separator-delimited values as ordered semantic units, not ordinary prose. Define which units matter before implementing truncation.

When both the origin and destination matter, use an outside-in priority by default: first unit, last unit, next unit from the left, next unit from the right, continuing inward. Keep every accepted unit in its original order and collapse each omitted run to one ellipsis. Use a different order only when the product has a clearer semantic priority.

Measure the final candidate against the real available width when font metrics, sibling controls, or container size affect the result. Continue evaluating later units after one candidate fails to fit. A later, shorter unit may still fit and carry more useful context.

If the highest-priority endpoint units cannot both fit in full, abbreviate within those endpoints while preserving both sides for as long as the available width allows. Keep the complete value available through an accessible name and, when useful, a pointer tooltip.

Put the selection and compaction policy in a deterministic formatter that can be tested independently from rendering. Reserve CSS text overflow for final containment after the semantic truncation algorithm runs.

### Dense Controls

Allocate horizontal space by information priority before styling a dense control. Protect the control identity, required status, count, or primary action. Let placeholder text, hints, and secondary copy yield first.

When an icon, input text, and trailing status share one control:

- Reserve the trailing element's footprint in the flexible text area at every viewport where they share a row.
- Keep the text area shrinkable with an explicit minimum width of zero and clip or truncate it before it can collide with protected content.
- Center leading and trailing adornments against the full control box with flex or grid alignment rather than text-line offsets.
- Keep overlays non-interactive when the underlying control owns input and focus.
- Verify the longest real status and loading label, not only the shortest steady state.

## Overflow

Horizontal scroll caused by layout is always a failure. Any element that can escape its container at any width must be fixed.

Test hostile content, not only normal examples:

- Long unbroken paths, URLs, identifiers, and filenames
- Dialogs with scrollable result lists
- Fixed or sticky action bars
- Dense multi-action controls
- Loading, success, and error icons in light and dark themes

Keep keyboard focus visible through every responsive rearrangement.

## Scrolling And Scrollbars

Decide, per surface, which single box scrolls. Everything else follows from that.

**An app shell must not scroll the viewport.** A signed-in app with persistent chrome is exactly one viewport tall: the header, sidebar, and any status bar sit outside the scroll container, and exactly one region under them scrolls. That is not a stylistic preference. It is what makes the rest possible:

- Full-bleed chrome only reaches the screen edge when the document reserves no scrollbar gutter, because `body` and every fixed layer are sized to the viewport minus that gutter.
- The viewport cannot gain or lose a scrollbar, so nothing a dialog, dropdown, filter, or late-loading content does to the page's height can move it sideways.
- The scrollbar sits with the content it scrolls, instead of running the full height of the window past chrome it has nothing to do with.

The cost is that the browser no longer restores scroll position on back or forward for that region, since it only restores the viewport's. Accept it, or restore it yourself, knowing that the one-line version does not work.

**Restoring scroll in a region the browser will not restore.**

- **Learn about the back before the router does.** A router that intercepts traversals through the Navigation API has already committed the new view by the time `popstate` fires, so a `popstate` listener decides too late and mis-attributes one navigation to the next. Take the traversal from the `navigate` event filtered to a traversal type, and keep `popstate` only as the fallback where that API does not exist. Inside `navigate` the location is still the old URL, so read the destination from the event.
- **Restore only on a back or a forward.** A fresh navigation starts at the top, and a view entered any other way must also forget what an earlier visit to that URL left, or a position from two visits ago gets applied to this one. A reload starts at the top unless the browser itself says the navigation was a traversal.
- **Wait for the height, do not assume it.** A region can only hold an offset once its content is that tall; assigning earlier clamps silently and lands at the top, which looks exactly like no restoration at all. Retry per animation frame until the region can reach the offset, then apply it once. Bound the wait from the user's keypress, not from the mount, since the route commit, the data, and the region existing at all have to fit inside it. Check that deadline only on a frame that found the region still too short, so a restore that becomes possible is taken and only a stalled wait is abandoned. That also makes a tab nobody is watching wait rather than give up, since a frame that is never painted cannot be late.
- **Yield to the user immediately.** A wheel, a touch move, a pointer press on the region, or a scrolling key ends the attempt for good. A restore that arrives after the user has started scrolling is worse than no restore.
- **Never animate it, and never restore part of the way.** An instant jump to a position the user already had is the only honest answer, and it owes nothing to reduced-motion preferences because nothing about it moves.
- **Key it by the region and the path, not by the query, unless the query can be navigated back to.** Filter and dialog state written with a replace never creates a history entry, so including it only creates keys nothing can return to, and makes a closing dialog look like a new view.
- **Capture continuously, and drop events that belong to the next view.** A scroll event is dispatched a frame or more after the scroll, so the router resetting the outgoing region to the top can arrive while the old view's listener is still attached and overwrite the position the user left. Ignore any event whose current path is no longer the view the listener was attached for.

A definite height is not a minimum height. A minimum leaves every percentage basis inside it resolving against content, so a flex child that was supposed to fill the shell silently grows instead and the surface scrolls the document after all, while still looking correct until something inside it gets tall.

**A document scrolls the document.** Long prose, marketing pages, articles, legal text, and generated docs are documents. Let the viewport own their scrollbar: they print correctly, restore scroll position for free, and let a mobile URL bar collapse. Do not put them in an app shell.

**Reserve the gutter on the region that scrolls. Never at the root.**

- An app shell's scrolling region keeps its gutter reserved permanently. It is invisible there, because the region's background is the page, so the reserved strip looks like page whether or not a bar is in it.
- The root reserves nothing. A root gutter is carved out of the viewport before `body` exists, so no page background, no fixed texture or backdrop, and no full-bleed header can ever paint into it. Reserved but empty, it is a dead, slightly discolored strip down the edge of the screen, and it is the single most common way this goes wrong.
- Never toggle a gutter on and off. Reserving it only when it is needed moves every centered column by half a scrollbar and every full-width row by a whole one, every time content grows or shrinks, while the user is reading or typing.

**Chrome that must align with scrolled content has to account for the gutter.** A full-bleed bar above a gutter-reserving region is wider than the content below it by exactly one scrollbar, so its trailing controls land closer to the screen edge than the content does. Do not hardcode the width: it varies by platform and zoom and is zero where scrollbars are overlays. An empty scroll container's own used width is exactly one scrollbar, which measures it in CSS alone.

**Do not let a scroll lock compensate a gutter that is already reserved.** Dialog libraries that add padding or a negative margin when they lock the body will double-compensate. A native modal dialog element blocks document scroll without removing the scrollbar and needs no compensation at all. In an app shell there is nothing to lock, which is one more reason to prefer one.

**Size overlays from their containing block, not from viewport units.** A viewport width unit counts the root scrollbar gutter as available space, so anything sized that way overhangs by exactly one scrollbar wherever the page behind it has a bar.

**Style native scrollbars, never replace them.** Use the standard properties rather than a scripted scroller that reimplements wheel, touch, keyboard, and assistive behavior. Any engine that honors `scrollbar-color` ignores the vendor-prefixed scrollbar pseudo-elements entirely, so treat those rules as a fallback for engines that do not, and never depend on a width stated only there. A transparent track only reads as page inside a region whose background is the page, which is another reason the scrollbar belongs to the content region rather than the window. Keep the primary scrollbar at the platform width and reserve thin scrollbars for compact nested panes.

**Verification.** On every surface, at wide and narrow widths, in light and dark: confirm the header, the page background, and every fixed layer reach the real screen edge with no reserved-but-empty strip beside them, and confirm a known element's x position is identical before and after opening a dialog, opening a dropdown, and filtering content down to nothing and back. Zero pixels, not close enough. A layout that only holds still when nothing is happening has not been tested.

## Surface Considerations

| Surface | Key constraint |
| --- | --- |
| Browser or web app | Full continuous range from the narrowest supported window upward |
| Browser extension popup | Fixed-width container; overflow, scroll, and padding still apply |
| React Native or Expo | No CSS breakpoints; mobile-first and fluid principles apply through platform layout APIs |
| Server-rendered framework | Responsiveness is a layout concern, not a server concern; same rules apply |
| Electron | Resizable window with an explicit minimum size and continuous behavior above it |

## Verification

Before a layout is complete, confirm no horizontal overflow and no broken hierarchy at the smallest target viewport, the largest, and a sweep of widths between. Resize continuously and watch for any width where the layout breaks, not just at named breakpoints. Exercise real interaction states, including selection, partial failure, dialogs, and long content.

For structured truncation, test the full value, several intermediate widths, a width where one candidate fails but a later candidate fits, and a width narrower than both endpoint units. Assert both the semantic order and the measured width.

For dense controls, test the longest placeholder or entered value beside the widest protected status. Confirm the protected content stays inside the control, adornments remain visually centered, and flexible text yields without overlap.
