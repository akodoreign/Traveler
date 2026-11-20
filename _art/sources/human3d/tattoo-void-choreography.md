# Yosai and the tattoo dragon

Yosai's existing Dragon's Breath, S460, transforms him on the first landed Void critical of that cast. The luminous jade coil threads through the chest where the fitted tattoo sits. Yosai folds, draws into the glow, and the folded dragon rises from the same anchor. The independent flare, dragon and folded silhouette overlap before the camera sees the full wingless dragon.

The dragon opens its jaw during the authored breath clip. One continuous flame plume samples the animated mouth and aim sockets. It leaves along the live jaw axis, curves to the screen sweep and passes across the opposing formation before turning back. The beam follows the turn of the dragon. The regular hit is applied once as the sweep crosses the critical target.

After the fire, the original coil spins back toward the tattoo. The dragon curls and draws into that point while the monk unfolds and regains his silhouette. The camera, Yosai's rendered position, body scale and battle pose restore on completion or interruption.

| Beat | Time after cut-in |
| --- | --- |
| Mark lights. Yosai folds into the coil. | 0–1.1 s |
| Dragon settles and draws breath. | 1.1–1.63 s |
| Mouth jet sweeps left and right. | 1.63–2.62 s |
| Coil recedes. Yosai unfolds. | 2.62–3.60 s |

S460 keeps its original attack order, targeting, animations used by hit callbacks, damage, and self-burn. A normal cast still uses the original fire presentation. A boosted cast with no landed Void critical uses that presentation after its hit dispatch, before death checks. This fallback keeps the same roll and callback order. The cinematic suppresses that extra plume only after its own stream starts. Haruki's S335 and other attacks stay on their existing presentation.

Daylight review uses M811 and P132 with S460 against two or more generated foes. Force one of the original S460 damage results to be a landed Void critical if a deterministic capture is needed. Confirm the morph reads clearly in both directions, the plume starts at the lit maw and fills the sweep, each intended enemy is hit exactly once, and Yosai still takes the stock self-burn once. A separate regular cast and a boosted cast with no Void critical exercise the two fallbacks. Check that the camera and renderer return to the original state.

The model files are under `resource/native_effects/tattoo_dragon`. This change adds two 30 fps clips to Yosai's existing shared humanoid skeleton and two native particle definitions. The dragon authoring data gives the mesh origin, baked summon/hover/breath/vanish clips, and live muzzle sockets.
