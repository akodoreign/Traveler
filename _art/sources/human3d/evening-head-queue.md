# Evening Hunyuan head queue

The installed cast and daylight samples are tracked in [the handoff](HANDOFF.md). These jobs used seed 47. Check the local ComfyUI history and current queue before resubmitting. Prompt completion records a mesh export. Use the visual review status to decide whether a mesh can enter the game.

| Job | Prompt ID | Status |
| --- | --- | --- |
| `side_onaka_slim_socket_paint` | `3d048427-fbfe-4256-a538-a75b946d86eb` | Success |
| `side_itami_slim_socket_geometry` | `f13bf45e-55b0-487e-89e3-5ee90c09623d` | Success |
| `side_kanemori_slim_socket` | `50d25412-8970-4c21-8e9d-2ba536cc7bd8` | Success |
| `side_itami_paint` | `b32208f0-4945-4c3f-99fe-9936c732a08e` | Success |
| `side_kanemori_paint` | `560a3312-8c1c-4b8a-be45-2382db1462f9` | Success |
| `side_shiko_geometry` | `26103f5d-82df-419e-a663-437d66ad9d13` | Success |
| `side_naohida_geometry` | `16452993-c2f0-4421-91e4-089ed558f19e` | Success |
| `side_youth_geometry` | `0e30efa8-ffa3-4e43-8b3c-17fcd2efd7f7` | Success |
| `side_munashii_geometry` | `b20ac987-3291-492d-b830-9940dde06528` | Success |
| `side_shiko_paint` | `8cd90b26-65fe-4507-9927-4ce5163a1907` | Success |
| `side_youth_paint` | `329fbef6-6ccb-48d2-bf27-b562e2430917` | Success |
| `side_sonoservant_geometry` | `73de6c24-e418-4e73-a4bb-f3935c6c19f6` | Success |
| `side_sonoservant_paint` | `f335c5ad-db4b-4c68-9e0a-c42ce89e037d` | Success |
| `side_kanbe_geometry` | `e3a2ac0f-b40d-4161-8ba9-117f4aac13e6` | Success |
| `side_kanbe_paint` | `60bbf8a8-5de8-4b64-b04b-c1a92a48761f` | Success |

## Where to resume

- Shiko's throat atlas was cleaned and the final portrait and fan passed the Coast Road check.
- Shadow Hunter and Ichiro Itami have ready candidate heads. Refit the authored cloth and stone masks before enabling the head routes.
- Sono Servant's repaired donor is ready for shared-rig fitting at `work/hunyuan-runway/sonoservant-atlas-repair/side_sonoservant_repaired_atlas.glb`. Use the cleared lower stem sections at the socket.
- Yasuki Kanbe's regenerated head passed the full rig and daylight checks. See [Kanbe's profiles](cast_heads/kanbe-daylight-profiles.png).
- Keep Naohida and Abbot Munashii out of paint with their current geometry. Naohida's low stem is shallow and flares into his beard. Munashii has a broad rear wedge.
- The local workspace `work/hunyuan-runway` contains the screenshots, original queue references, repaired atlases and original receipts. `work/model-rigging/batch-07/evening-cast` contains the fit packages, full profiles, stride images and actor-local staging installers.

## November 21 continuation

| Job | Prompt ID | Status |
| --- | --- | --- |
| `side_kusada_geometry` | `f7698b6c-a890-450d-9fce-e4867e59262c` | Success |
| `side_sabu_geometry` | `83f48caa-ccfe-483a-8cf3-e98e568a1204` | Success |
| `side_kisada_geometry` | `6be127f1-d05a-4006-8095-b132fc608ccb` | Success |
| `side_oracle_geometry` | `cd4db465-880f-4138-86cb-c4cb102c468a` | Success |
| `side_oracle_paint` | `dc49953b-016f-48a2-80a3-c3169a7ab278` | Success |
| `side_kitsuneboy_geometry` | `836c144f-2b5f-4047-bdf3-70fd8294c004` | Success |
| `side_kisada_v2_geometry` | `a938bde5-5901-4c30-81f3-d12ec6b45f20` | Success |
| `side_shinobu_geometry` | `e3d48faa-0487-4bf4-9f2d-bd52637b75f4` | Success |
| `side_kisada_v2_paint` | `5657ab61-6d9c-4831-bf28-2e1f78c4dc00` | Success |
| `side_shinobu_paint` | `4a6c82cf-8444-4150-bde5-d23c45192953` | Success |
| `side_kusada_v2_geometry` | `20e0e10e-a6d6-4662-85a1-d98a5047b9c1` | Success |
| `side_sabu_v2_geometry` | `d0d659d3-c824-49aa-a9d0-10dcb65935ec` | Success |
| `side_kusada_v2_paint` | `a35c1273-4e10-4783-bb29-720a3e87e56e` | Running |
| `side_sabu_v2_paint` | `ddddc72e-f7b9-4340-b33b-851cf1b9c0c1` | Pending |

Kusada's first mesh has a wide rectangular stem and a rear flare. Sabu's first mesh has a rear bulge and a drifting cross-section. Both narrower V2 pilots passed the strict profile check and have same-seed texture jobs. Check the resulting face paint and fitted native socket before enabling either head. The built-in ImageGen references and exact prompts for Kusada, Sabu and Hida Kisada V2 are archived in `reframed_heads`.

Kisada's V2 geometry seats on his actual A112 body. The improved native rim center offsets are under .0011 units. The beard and dark eyes were repaired in the textured output. The old mempo floats ahead of the new head and the kabuto needs its own brow and hair clearance. Keep both as separate fitted pieces. His portable head is staged for bare review in `work/model-rigging/batch-07/evening-cast/side_kisada/v2-unhelmeted`.

Oracle of Fire passed the in-game route on Phoenix A140. The final neck-blend atlas preserves his ember eyes and beard. Sono Servant and Kagemaro also passed the installed A124 collar and decal fix. See [the live handoff](HANDOFF.md).

Kitsune Boy is held at geometry. His neck peg measures about 2.0 by 2.3 native units against his actual scaled shared male body's upper socket of about 5.7 by 5.0. Shinobu's corrected paint is in `work/hunyuan-runway/shinobu-atlas-repair/side_shinobu_repaired_atlas.glb`. Check the long locks against his robe and the existing cloth mask against his new head before promoting the route.
