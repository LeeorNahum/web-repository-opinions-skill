# Animation Runtime

An animation is product behavior, so it plays the same way on every engine and device the product supports: browsers, embedded webviews, and desktop shells alike. One that plays only where it was built has not been verified.

## Time, Not Frames

- Drive every scripted animation from a clock: the timestamp a frame callback receives, or the current time, never a per-frame increment. Frame rates run from 30 on a device saving power to 120 and above on high refresh displays, and a frame-counted animation plays at a different speed on each.
- Cap the step taken after a gap only at a stall no running animation produces, around a tenth of a second, so a slow device keeps real time instead of slowing down and a frozen tab does not leap ahead.
- When an effect draws at a fraction of the display rate, set its frame budget a few milliseconds under the target interval, so ordinary vsync jitter cannot push each frame to the next refresh and halve the rate.
- Reset the clock's reference point when the surface becomes visible again or is restored from the back-forward cache, so the time spent away is not played back as motion. Listen for the page-show event with its persisted flag as well as the visibility change, because a restored page resumes its timers and frame callbacks where they stopped.

## Respond To The Layout The Animation Reads

- Recompute an animation's geometry when the box it measures changes, through a resize observer on that element or by comparing the one dimension it uses, never on every window resize. Mobile browsers resize the window each time their toolbar collapses or expands under the reader's scroll, so a window-level handler fires while nothing the animation measured has changed, and one that restarts or cancels the animation ends it just as it comes into view.
- Measure text geometry after the fonts it is drawn in have loaded, and measure again when a late font swap changes it.
- When geometry changes while an animation is paused, redraw its current frame from the new measurements, because no frame is coming to do it.

## Start And Stop With Visibility

- Start a scroll-triggered animation from an intersection observer, and pause any loop that is off screen or in a hidden tab, resuming from where it stopped.
- Give each loop one owner of its frame callback, so pausing, resuming, and restarting can never schedule two.
- Make the state shown without scripts, or before the runtime starts, a complete and readable frame. Hide content in anticipation of an animation only once the runtime is certain it can play it.

## Verify On Real Engines

- Run every animation on each engine the product supports, Chromium, Gecko, and WebKit, and on a real iPhone, where every browser runs WebKit and a desktop emulation of it misses the toolbar and power behavior.
- Reproduce the mobile toolbar by changing only the viewport height while an animation plays, and confirm it plays on. Then change the width and confirm it adapts or settles deliberately.
- Throttle the processor until frames arrive slowly, then run at a high refresh rate, and confirm the animation's duration in wall-clock time is the same.
- Hide and restore the tab, and navigate away and back, and confirm it resumes cleanly with no leap and no doubled speed.
- Judge it by watching it run or by sampling its state over time, long enough to span its longest hold, never by reading the code that drives it.
