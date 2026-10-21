# Responsive Layout

Design for available space and input capabilities, not a mobile or desktop label. A narrow desktop window and a narrow phone should receive the layout their containers can support. A large touch display should gain useful space without being trapped in a reduced phone layout.

Every page and view must remain fully usable and intentional from its smallest supported container to its largest. Responsiveness is a requirement of done, not a later polish pass.

These rules apply to every surface whose layout uses boxes, relative units, or viewport dimensions, native ones such as React Native and Expo included.

## Smallest Viable Space First

Design from the smallest viable container outward. Each increase in available space is an opportunity to reveal labels, increase density, or change composition. Device identity does not determine which state is active.

## One Design At Every Scale

A very narrow or very wide viewport shows the same page at a different scale: the same identity, sections, order, arrangements, and actions, with about the same amount of content on each screen. Adapt an arrangement only where its content measurably cannot fit at a usable size.

- Scale type, controls, illustrations, padding, and gaps together by one proportion, each with a readable or operable floor. On a phone, supporting copy sits around 13 to 15 CSS pixels, form inputs stay at 16 so focus does not zoom, headings step down until they wrap at most one more line than on desktop, buttons and their padding shrink with the type, and section spacing shrinks by the same proportion.
- Keep a document page's length in screens, measured at 390 by 844 and at 320 by 700 CSS pixels, within about 1.3 times its length at 1440 by 900. Long reading pages such as legal text follow their reading measure instead. When it runs longer, shrink type and spacing and restore side-by-side arrangements before accepting it.
- Keep pairs and short groups side by side on a phone: paired actions, peer tiles, and short link groups. Give them an explicit column count, such as `repeat(2, minmax(0, 1fr))`, with compact padding, and let labels wrap inside each column. Use auto-fit grids with a minimum track width for open-ended collections only, and take that minimum from the smallest usable item.
- Stack a row that pairs copy with an illustration when the illustration beside the copy would render its internal text below 9 CSS pixels, and give the stacked illustration the full column width.
- For a full-screen hero, size the first-screen region, including navigation, to fill the initial visible viewport. On CSS surfaces, use the small viewport height as its minimum and let content grow. On native surfaces, use the available window height.
- Scale each illustration, product mockup, or diagram as one unit inside a box that reserves its rendered dimensions. Use container-relative sizing or an SVG viewBox so the whole subject stays in frame.
- Bound reading and marketing content with maximum widths, capping body text at about 45 to 75 characters per line, and cap type and spacing. Let task workspaces use extra width when it reveals useful work.

## Fluid By Default

Prefer continuous, fluid sizing over a few hard breakpoints. Layout should adapt at every width, not jump between two or three fixed designs.

- Use intrinsic and proportional sizing, fractional grids, and flexible wrapping so layout flexes continuously.
- Use fluid type and spacing that scale smoothly with the viewport between sensible minimums and maximums, rather than fixed sizes swapped at breakpoints.
- Reach for container-based responsiveness so a component adapts to the space it occupies, not only to the global viewport. This keeps a component correct when reused in a sidebar, a modal, or a full page.
- Collapse labels and controls from measured container fit. Preserve text while the actual space supports it.
- Treat breakpoints as a coarse tool for genuine layout changes, such as moving from a stacked to a side-by-side structure, not as the primary mechanism for every size adjustment.

Fixed values belong where size must never vary: icon assets at a declared size, hairline borders, touch-target minimums, the 16 pixel input text floor, and content maximum widths.

Use viewport media queries for page-level composition and container queries or measured fit for reusable components. Use input media features such as `hover` and `pointer` only for interaction capabilities, never as a proxy for a device category.

## Display Scale

Display scale is a runtime variable, not a build-time constant. Treat every scale the platform offers as reachable, and treat the current scale as changeable while the app is running: a settings change, a window dragged to a different monitor, a laptop display switching resolution modes.

- Lay out in logical units and derive physical pixels from the current scale at the moment of use. A scale factor cached at startup, or a physical size computed once, is stale the first time the setting moves.
- Re-derive everything that renders in physical pixels when the scale changes: canvas backing stores sized from `devicePixelRatio`, native window dimensions in desktop shells, and any coordinate math bridging native and web layers.
- Watch `devicePixelRatio` through a `(resolution: <current>dppx)` media query listener that re-arms itself after each change, since the value has no change event of its own.
- Treat scale-change notifications as an optimization, with the current scale queried at the point of use as the source of truth. Notification delivery varies by platform, window style, and framework, and a missed notification is silent: the only symptom is one layer still rendering at the old scale. In a desktop shell, reconcile the web content and the native window explicitly, and size the native window from the monitor's current scale every time it is shown rather than from a cached factor.

Verify at more than one scale by exercising a real scale change, in both directions, while the app is running. In a browser, change the emulated device scale factor without reloading. In a desktop shell, change the operating system's display scale, watch the running UI, and restore it afterwards. A layout that was only ever seen at one scale has not been verified.

## Touch And Pointer

Interactive elements are large enough to activate reliably by touch, and remain comfortable with a mouse. This holds for browser apps, extension popups, React Native, Expo, and any touch-capable surface.

On CSS surfaces, make every standalone target at least 24 by 24 CSS pixels. A link inside a sentence takes the sentence's line height. On native surfaces, follow the platform's target sizes.

## Media

Images and media stay bounded by their containers, never overflowing and never distorting. Serve appropriately sized assets when the environment supports it.

## Content Priority

When space is constrained, shrink first, reflow second, and keep every piece of content and every action reachable. Move persistent navigation into a drawer or disclosure when that gives the primary task usable space.

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

Let long text wrap instead of widening its box. Give body text `overflow-wrap: anywhere`, and give every flex or grid child that holds text `min-width: 0`. A value the reader must see whole, such as a command beside its copy button, wraps inside its box or moves the button to its own line, and never scrolls or hides behind it.

Test hostile content, not only normal examples:

- Long unbroken paths, URLs, identifiers, and filenames
- Dialogs with scrollable result lists
- Fixed or sticky action bars
- Dense multi-action controls

Keep keyboard focus visible through every responsive rearrangement.

## Scrolling And Scrollbars

Decide, per surface, which single box scrolls. Everything else follows from that.

**An app shell scrolls one region, never the viewport.** A signed-in app with persistent chrome is exactly one viewport tall: the header, sidebar, and any status bar sit outside the scroll container, and exactly one region under them scrolls. That is what makes the rest possible:

- Full-bleed chrome only reaches the screen edge when the document reserves no scrollbar gutter, because `body` and every fixed layer are sized to the viewport minus that gutter.
- The viewport cannot gain or lose a scrollbar, so nothing a dialog, dropdown, filter, or late-loading content does to the page's height can move it sideways.
- The scrollbar sits with the content it scrolls, instead of running the full height of the window past chrome it has nothing to do with.

The cost is that the browser no longer restores scroll position on back or forward for that region, since it only restores the viewport's. Accept it, or restore it yourself by the rules below. Setting the offset once when the route changes does not survive them.

**Restoring scroll in a region the browser will not restore.**

- **Learn about the back before the router does.** A router that intercepts traversals through the Navigation API has already committed the new view by the time `popstate` fires, so a `popstate` listener decides too late and mis-attributes one navigation to the next. Take the traversal from the `navigate` event filtered to a traversal type, and keep `popstate` only as the fallback where that API does not exist. Inside `navigate` the location is still the old URL, so read the destination from the event.
- **Restore only on a back or a forward.** A fresh navigation starts at the top, and a view entered any other way must also forget what an earlier visit to that URL left, or a position from two visits ago gets applied to this one. A reload starts at the top unless the browser itself says the navigation was a traversal.
- **Wait for the height, do not assume it.** A region can only hold an offset once its content is that tall. Assigning earlier clamps silently and lands at the top, which looks exactly like no restoration at all. Retry per animation frame until the region can reach the offset, then apply it once. Bound the wait from the user's keypress, not from the mount, since the route commit, the data, and the region existing at all have to fit inside it. Check that deadline only on a frame that found the region still too short, so a restore that becomes possible is taken and only a stalled wait is abandoned.
- **Yield to the user immediately.** A wheel, a touch move, a pointer press on the region, or a scrolling key ends the attempt for good. A restore that arrives after the user has started scrolling is worse than no restore.
- **Restore instantly and to the exact position.** An instant jump to a position the user already had is the only honest answer, and it owes nothing to reduced-motion preferences because nothing about it moves.
- **Key it by the region and the path, not by the query, unless the query can be navigated back to.** Filter and dialog state written with a replace never creates a history entry, so including it only creates keys nothing can return to, and makes a closing dialog look like a new view.
- **Capture continuously, and drop events that belong to the next view.** A scroll event is dispatched a frame or more after the scroll, so the router resetting the outgoing region to the top can arrive while the old view's listener is still attached and overwrite the position the user left. Ignore any event whose current path is no longer the view the listener was attached for.

A definite height is not a minimum height. A minimum leaves every percentage basis inside it resolving against content, so a flex child that was supposed to fill the shell silently grows instead and the surface scrolls the document after all.

**A document scrolls the document.** Long prose, marketing pages, articles, legal text, and generated docs are documents. Let the viewport own their scrollbar: they print correctly, restore scroll position for free, and let a mobile URL bar collapse. Keep them out of an app shell.

**Reserve the gutter on the region that scrolls, and leave the root without one.**

- An app shell's scrolling region keeps its gutter reserved permanently. It is invisible there, because the region's background is the page, so the reserved strip looks like page whether or not a bar is in it.
- The root reserves nothing. A root gutter is carved out of the viewport before `body` exists, so no page background, no fixed texture or backdrop, and no full-bleed header can ever paint into it. Reserved but empty, it is a dead, slightly discolored strip down the edge of the screen.
- Keep a reserved gutter reserved permanently. Reserving it only when it is needed moves every centered column by half a scrollbar and every full-width row by a whole one, every time content grows or shrinks, while the user is reading or typing.

**Chrome that must align with scrolled content has to account for the gutter.** A full-bleed bar above a gutter-reserving region is wider than the content below it by exactly one scrollbar, so its trailing controls land closer to the screen edge than the content does. Measure the width rather than hardcoding it, since it varies by platform and zoom and is zero where scrollbars are overlays. Place an empty element with `overflow-y: scroll` at the trailing end of the chrome. Its used width is exactly one scrollbar, so the chrome's trailing controls line up with the content below.

**Leave scroll-lock compensation off where the gutter is already reserved.** Dialog libraries that add padding or a negative margin when they lock the body will double-compensate. A native modal dialog makes the page inert but leaves it scrollable. Give the dialog's own scrolling box `overscroll-behavior: contain`, which removes no scrollbar and needs no compensation, and confirm that wheel, touch, and keyboard scrolling over the open dialog leave the page behind it where it was. In an app shell the viewport has nothing to scroll, which is one more reason to prefer one.

**Size overlays from their containing block, not from viewport units.** A viewport width unit counts the root scrollbar gutter as available space, so anything sized that way overhangs by exactly one scrollbar wherever the page behind it has a bar.

**Style native scrollbars with the standard properties.** Keep the native scrollbar rather than a scripted scroller that reimplements wheel, touch, keyboard, and assistive behavior. Where `scrollbar-color` or `scrollbar-width` computes to anything other than `auto`, including through inheritance from an ancestor, the engine ignores the vendor-prefixed scrollbar pseudo-elements. Put those rules inside `@supports not (scrollbar-color: auto)` as a fallback, and state every width through the standard property. A transparent track only reads as page inside a region whose background is the page, which is another reason the scrollbar belongs to the content region rather than the window. Keep the primary scrollbar at the platform width and reserve thin scrollbars for compact nested panes.

**Verification.** On every surface, at wide and narrow widths, in light and dark: confirm the header, the page background, and every fixed layer reach the real screen edge with no reserved-but-empty strip beside them, and confirm a known element's x position is identical before and after opening a dialog, opening a dropdown, and filtering content down to nothing and back. Zero pixels, not close enough. A layout that only holds still when nothing is happening has not been tested.

## Surface Considerations

| Surface | Key constraint |
| --- | --- |
| Browser or web app | Full continuous range from the narrowest supported window upward |
| Browser extension popup | Fixed-width container. Overflow, scroll, and padding still apply |
| React Native or Expo | No CSS breakpoints. Mobile-first and fluid principles apply through platform layout APIs |
| Server-rendered framework | Responsiveness is a layout concern, not a server concern. The same rules apply |
| Electron | Resizable window with an explicit minimum size and continuous behavior above it |

## Verification

Before a layout is complete, confirm no horizontal overflow and no broken hierarchy at the smallest target viewport, the largest, and a sweep of widths between. Resize continuously and watch for any width where the layout breaks, not just at named breakpoints. Exercise real interaction states, including selection, partial failure, dialogs, and long content.

Run the layout check script against the served production build for every route the work added or changed, detail, settings, legal, and error routes included, until it passes. Then open its captures, compare the widest and the narrowest of each page side by side against One Design At Every Scale, and fix what reads wrong to a person even when no number caught it: crowding, clipped content, a pair that stacked, an empty region, a control that looks broken. Recheck with enlarged text, which may reflow. A layout judged only from its CSS or its measurements has not been verified.

For dense controls, test the longest placeholder or entered value beside the widest protected status. Confirm the protected content stays inside the control, adornments remain visually centered, and flexible text yields without overlap.
