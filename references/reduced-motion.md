# Reduced Motion

Motion is on by default for everyone. A reduced-motion preference asks to be spared the motion that can make someone uneasy, not for a still product, so honor it by reducing exactly that motion and keeping the rest. A surface that freezes everything under the preference takes its demonstrations, feedback, and life away from people who asked for none of that.

## Where The Line Falls

Reduce or freeze under the preference:

- Large-area and full-viewport movement, such as a moving background, panning or zooming imagery, and continuous ambient drift.
- Movement linked to scrolling beyond the scroll itself, such as parallax, elements that travel or scale as the page scrolls, and smooth scrolling to anchors.
- Zooming, spinning, and large changes of scale.

Keep under the preference:

- Small movement inside a bounded component, such as a pointer crossing a tile, a key going down, a menu opening, or text typing in.
- Fades and changes of color or opacity, which move nothing and change no size or shape.
- A short entrance that moves an element a few pixels once.

Judge every animation on the surface against that line, and record which side each falls on beside the surface's design rules. Replace rather than remove where the motion carries meaning: a light that would travel across the screen can fade out where it was and in where it goes. Follow a change to the preference while the surface is open.

## Verification

Run the surface with the preference on and off on each supported engine. Confirm that what should still move does and that what should stop has stopped.
