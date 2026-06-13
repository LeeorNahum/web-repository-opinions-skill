# Responsive Layout

Design for available space and input capabilities, not a mobile or desktop label. A narrow desktop window and a narrow phone should receive the layout their containers can support. A large touch display should gain useful space without being trapped in a reduced phone layout.

Every page and view must remain fully usable and intentional from its smallest supported container to its largest. Responsiveness is a requirement of done, not a later polish pass.

Web-derived means any environment whose layout model descends from HTML and CSS: browser apps, SPAs, server-rendered frameworks, browser extensions, React Native, Expo, cross-platform hybrids, and web-adjacent rendering layers. If the environment understands a box model, relative units, or viewport dimensions, this applies.

## Smallest Viable Space First

Design from the smallest viable container outward. Each increase in available space is an opportunity to reveal labels, increase density, or change composition. Device identity does not determine which state is active.

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

## Scrollbars And Scroll Lock

Keep native scrolling. Style native scrollbars with standard scrollbar properties and a browser fallback rather than replacing wheel, touch, keyboard, or assistive behavior with a custom JavaScript scroller.

Reserve the root scrollbar gutter so content does not shift when page overflow appears, disappears, or is locked by a dialog. When a dialog library adds scrollbar-width compensation, verify it does not double-compensate after a stable gutter is reserved.

Use a visually intentional thumb and track that remain legible in light and dark themes. Preserve comfortable pointer targeting on the page scrollbar; reserve thin scrollbars for compact nested panes where space is constrained.

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
