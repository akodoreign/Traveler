# Yosai’s tattoo dragon

Hunyuan prompt `89da11ab-8ccd-4293-a7c5-8c32f581f66a` generated the textured source. The input cutout is `../void_tattoo_dragon_reference.png`. `tattoo_dragon_source.glb` is the original export. The atlas repair removes fluorescent red and green edge bleed while retaining the source geometry and UVs.

`tools/blender/tattoo_dragon.py` defines the measured spine and limb guides and writes the native mesh and motion. The rig has 24 sequential spine segments, four tail segments, four two-bone limbs, and separate head and jaw controls. The lower lip and chin follow the jaw hinge. The head carries the unweighted `mouth` and `mouth_aim` sockets.

The runtime resource is `/resource/native_effects/tattoo_dragon/tattoo_dragon.pm`. It stands about 3 meters high at scale 0.019. The tail base is near the object origin, and local positive X points toward the mouth. From a standard positive Z battle heading, subtract a quarter turn to align this asset. Read the animated socket from `dragon.findBone("mouth").mat.getTranslation(Vector3D()).transform(dragon.gmat)`. Use `mouth_aim` to obtain a second world position along the breath direction.

| Clip | Frames at 24 fps | Purpose |
| --- | --- | --- |
| Summon | 0–35 | Rise and turn from the caster’s tattoo |
| Hover | 36–60 | Looping suspended motion |
| Breath | 61–96 | Head lift and jaw opening |
| Vanish | 97–128 | Coil down and turn away |

Fire can start 330 milliseconds into Breath. Summon and Vanish include baked root motion. The battle controller owns visual scale and scene lifetime. `tattoo_dragon.json` records the exact clip and bone values.

Rebuild by running `tools/blender/repair_dragon_atlas.py SOURCE.glb COLOR.png` with Python using OpenCV, NumPy, Pillow and trimesh, then run Blender with `--background --python tools/blender/tattoo_dragon.py -- SOURCE.glb COLOR.png STAGE`. Copy the staged PM, MDL, MOT, JSON, and referenced texture into the native resource directory.

