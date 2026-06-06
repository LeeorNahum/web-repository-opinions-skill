# Design Tokens

A product gets one design token layer that both apps draw from, so the public site and the signed-in app feel like one product even when they are separate codebases.

Keep tokens in a single source of truth: colors, typography scale, spacing, radius, elevation, and named component styles. Components consume tokens; they do not invent one-off values that contradict the system.

When a design decision changes, update the token source rather than patching a component. A new color, type step, or component pattern extends the token layer, it does not get hardcoded in one place.

Two surfaces share the token system but not necessarily their components. Prefer duplicating a component across apps over coupling them, unless the component is genuinely identical. Shared tokens, independent composition.

Icons come from one set at consistent size and weight across both surfaces.
