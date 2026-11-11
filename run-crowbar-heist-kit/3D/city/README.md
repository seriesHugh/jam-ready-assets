# Crowbar Heist Kit

40 props and 4 rigged characters. GLB, Y up, front +Z, metres replaced by tile units: 1u = one city road tile. Character H = 0.243u; lane width = 0.29u. Each GLB embeds the shared 32×16 palette. Use nearest texture filtering.

Character clips at 30 fps: idle 60f, walk 32f, run 20f, sneak 40f, alert_point 30f, hands_up 24f. Loops have extras.loop=true. The mask, duffel, cap and flashlight are rigid bone children. Use Source/budgets.json for class ceilings.

Load a GLB with your RUN project glTF loader, add its scene to the world and play a named animation using the imported animation mixer. For one-shots, clamp the last frame. Vehicle wheel nodes are separate for runtime driving rotation.

See License.txt for the complete distribution terms. Editable sources and content hashes are in Source/.
