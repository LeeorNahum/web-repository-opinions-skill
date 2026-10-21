# Runtime Truth

A change is complete when the runtime it depends on is true, not when the code compiles or a branch is pushed.

Design every provider workflow around its order of operations, not its happy path. The failure point, not the success path, decides whether the design is sound. Ask what happens if a step half-completes, if the user leaves mid-flow, or if a retry overlaps a running job, and make the answer explicit.

When the backend function shape changes, regenerate the clients and types before claiming the app is ready. Generated files are part of the runtime contract, not a build detail.

A green build or typecheck proves the code compiles, not that the served surface renders or behaves correctly. Before calling a surface done, load each route the change touches from the served production build in a browser, and confirm every stylesheet, script, font, and image request succeeds and the console shows no errors.

Saying done after a Git push while a runtime deploy, migration, or provider setting is still missing is not done. It is only locally edited.
