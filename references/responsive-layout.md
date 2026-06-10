# Responsive Layout

Every page and every view must be fully usable and look intentional on any display, from the smallest phone to the largest desktop, resizing smoothly through everything between. Responsiveness is a requirement of done, not a later polish pass.

Web-derived means any environment whose layout model descends from HTML and CSS: browser apps, SPAs, server-rendered frameworks, browser extensions, React Native, Expo, cross-platform hybrids, and web-adjacent rendering layers. If the environment understands a box model, relative units, or viewport dimensions, this applies.

## Mobile-First

Design from the smallest viable viewport outward. Each added width is an opportunity to use more space, never a patch for a layout that only worked wide. A sound small-screen layout is the foundation.

## Fluid By Default

Prefer continuous, fluid sizing over a few hard breakpoints. Layout should adapt at every width, not jump between two or three fixed designs.

- Use intrinsic and proportional sizing, fractional grids, and flexible wrapping so layout flexes continuously.
- Use fluid type and spacing that scale smoothly with the viewport between sensible minimums and maximums, rather than fixed sizes swapped at breakpoints.
- Reach for container-based responsiveness so a component adapts to the space it occupies, not only to the global viewport. This keeps a component correct when reused in a sidebar, a modal, or a full page.
- Treat breakpoints as a coarse tool for genuine layout changes, such as moving from a stacked to a side-by-side structure, not as the primary mechanism for every size adjustment.

Fixed values belong only where size must never vary: icon assets at a declared size, hairline borders, and minimum touch-target sizes.

## Typography And Reading

Type stays readable at every viewport. Scale heading hierarchy gracefully on small screens, and constrain body line length to a comfortable reading measure on wide screens so text does not stretch across the full width.

## Touch And Pointer

Interactive elements are large enough to activate reliably by touch, and remain comfortable with a mouse. This holds for browser apps, extension popups, React Native, Expo, and any touch-capable surface.

## Media

Images and media stay bounded by their containers, never overflowing and never distorting. Serve appropriately sized assets when the environment supports it.

## Content Priority

At small viewports, decide what to show, defer, or hide, not just how to reflow. A navigation pattern that works on desktop often needs a genuinely different model on mobile rather than a squeezed copy.

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
| Browser or web app | Full continuous range from smallest phone width upward |
| Browser extension popup | Fixed-width container; overflow, scroll, and padding still apply |
| React Native or Expo | No CSS breakpoints; mobile-first and fluid principles apply through platform layout APIs |
| Server-rendered framework | Responsiveness is a layout concern, not a server concern; same rules apply |
| Electron | Desktop-first web app with a minimum window size that can still resize |

## Verification

Before a layout is complete, confirm no horizontal overflow and no broken hierarchy at the smallest target viewport, the largest, and a sweep of widths between. Resize continuously and watch for any width where the layout breaks, not just at named breakpoints. Exercise real interaction states, including selection, partial failure, dialogs, and long content.
