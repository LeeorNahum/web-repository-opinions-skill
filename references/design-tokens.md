# Design Tokens

A product gets one design token layer that every surface draws from, so the public site and the signed-in app feel like one product even when they are separate codebases. When a product has more than one app, keep the token source in one workspace package that every app imports its theme from.

Keep tokens in a single source of truth: colors, typography scale, spacing, radius, elevation, and named component styles. Components consume tokens, and any one-off value a component needs stays consistent with the system.

When a design decision changes, update the token source rather than patching a component. A new color, type step, or component pattern goes into the token layer first.

Surfaces share the token system but not necessarily their components. Prefer duplicating a component across apps over coupling them, unless the component is genuinely identical. Shared tokens, independent composition.

Icons come from one set at consistent size and weight across every surface.

## Variants Own Their Utilities

A shared component owns its shape through named variants and sizes, rather than through a caller passing utility classes that are meant to override the component's own.

If class strings are combined by plain concatenation, a caller's class does not beat a base class in the same property group. The compiled stylesheet's source order decides, so a passed `px-0` loses to a base `px-3` and the component silently renders at a size nobody asked for. This fails quietly: the markup looks right, the class is present in the DOM, and only the rendered box is wrong.

So put every utility a caller might need to change into a variant or size that the component owns. Reserve the pass-through class name for properties the base never sets, such as layout position within a parent. If overriding really is required, use a class merger that understands the utility framework's property groups, and say so, rather than depending on stylesheet ordering.

## Ambient Texture

A product with a lot of deliberate empty space, which is most dashboards and most catalogs, reads as a void rather than a surface when its large regions are flat fills. Give the product one ambient texture so the emptiness looks intentional.

The rule is about the region, not the page. A page background, a sidebar, a pane with nothing in it yet, and the run of empty space under a short list all read as voids, and all carry the texture. A region that paints its own opaque fill covers the layer beneath it, so it either leaves its fill transparent and lets that layer show through, or carries the same texture token over its own fill. Either way the shell reads as one continuous surface.

Make it a token, not a component: a background image value plus a per-theme opacity, so any surface that wants it reads the same value and a theme only changes how strongly it shows.

Build it in CSS with no asset and no script. An inline SVG turbulence tile, desaturated to neutral grain, is the portable default and works on any site. A hairline grid is the other defensible choice when the product's identity is structural. Choose one texture per product.

Paint it on a fixed, non-interactive layer behind the content, with the page color on the root element so the body can stay transparent and the texture sits between them. Fixed means it never repaints while scrolling. It is decoration, so remove it in print and under a forced-colors palette.

### Calibrate It By Measurement

Calibrate by measurement, not by eye. These are the targets. Reproduce them and stop.

- **Amplitude.** Aim for a per-pixel luminance standard deviation of about `0.7/255` on a near-black page and about `0.55/255` on a near-white one. That is under half of one percent of the range, and the two figures are the same amount of grain once converted to L\*, where a code step near black is worth roughly `0.27` L\* and a step near white roughly `0.35`.
- **Grain size.** About one CSS pixel. On a turbulence tile whose CSS size equals its user-unit size, `baseFrequency` near `0.82` puts the lattice cell at `1.22px` and measures a lag-one autocorrelation around `-0.06`, which is the signature of grain the eye reads as film rather than as blotches. Below about `0.7` the correlation turns positive and the texture starts to look like mottling.
- **Octaves.** Two at most. Extra octaves double the frequency each time, which at one sample per unit is already past the pixel Nyquist limit, so they do not add finer detail. They fold back as coarser structure and buy nothing but amplitude.
- **Achromatic.** The variation is brightness, not color. Keep the `saturate 0` matrix so the rendered R, G, and B deviations at each pixel are identical. Measuring one back will show a little per-channel jitter regardless, because an achromatic signal near the quantization floor picks it up from a dithered 8-bit output. Judge the shared brightness component, which carries most of the variance, rather than the residual chroma.

Two traps sit in the arithmetic.

The first is that dark themes want a **lower** opacity than light ones. A neutral turbulence tile renders as light grey, far from a near-black page and close to a near-white one, so the same opacity gives dark mode two to three times the grain. Set each theme's opacity by measuring it against its own target.

The second is that the layer shifts the page color as well as varying it. A grey tile over a dark page lifts it, and over a light page darkens it, by a few times the standard deviation it delivers. Keep the amplitude in range and the shift stays near one code level, small enough that the page token still means what it says. Push the grain louder and the paper color quietly stops being the paper color.

Verify from pixels, never from a screenshot the tool encoded as JPEG, because JPEG destroys exactly the fine grain being measured. Render the page to a lossless PNG, for example with a headless browser screenshot, decode it, and compute the standard deviation and the lag-one autocorrelation over a large empty region. Below about `0.5/255` the output is quantization, not texture, so a very low opacity replaces the grain rather than fading it.

The judgment test still governs the target. It is not whether you can see the texture. It is whether the page stops looking flat. If a viewer notices the texture as texture, it is too strong, and it has become the ambient visual noise that a quiet interface is supposed to avoid.
