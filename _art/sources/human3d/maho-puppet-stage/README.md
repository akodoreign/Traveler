# Maho Puppet shared-rig fit

E235 is the Maho Puppet. Both the M150 field event and the M815 battle use EP429. The body already used the shared male mesh, while the visible head and headcloth came from the earlier low-detail appearance.

| Location | Verified registration |
| --- | --- |
| Kyuden Hida's deepest cell | M150 event 3 at `[52,3,26]` → EP429 before G214 |
| Puppet and troll encounter | M001 group 14 → M815 → E235 Maho Puppet and E234 Troll |
| Related names | Maho-bujin and Maho-tsukai have separate identities and assets |

EP429 now uses the approved Kitchen Servant donor's regenerated head geometry and the separately fitted woven headcloth. The plain servant clothing follows the authored donjon scene. It uses the generated A100 robe with the ash-brown Crab commoner palette and a separate muted red sash. The combat rig plays the original unarmed attacks and spell poses.

The donor skin sample was sRGB 242, 197, 164. A cooler sRGB 216, 193, 162 target produces face material multiplier `0xc7f4f8ff`. That multiplier is also applied to the donor's calibrated core, hands, throat and neck materials, giving `0xb18b5eff`. The head and neck geometry are byte-identical to the approved donor, with the overlap rings at 98.825 and 99.375 native units. Source and fit metadata are in the worktree under `_art/sources/human3d/cast_heads/side_servant_repaired_atlas.glb` and `side_servant.json`.

The E234 troll is a separate creature on its existing Hunyuan EP121 model. Its combat hazard still points to E235.

## Apply and verify

Run `python -B install_maho_puppet.py <tool-directory> --check` to validate dependencies. Rerun without `--check` on a closed profile. The installer changes the EP429 human and clothing rows, the matching body descriptor and the new portrait descriptor and mesh alias.

Run `maho_puppet_proof.sk` after launching the real encounter with `-battle M001 14`, and again in M150 near event 3 for the field route. Messages start with `[MAHO PUPPET FIT]`. The fixture verifies the real field event, both registered combat actors, skin materials, headcloth, fitted robe, spell animation and the troll's hazard link.

The [bind-space preview](puppet-bind-preview.png) shows the prepared silhouette from the front and both sides. Native lighting and movement remain for supervisor review.

## Native installation

Native verification passed in M150 event 3 and M001 group 14 on M815. The puppet used the shared 50-joint body, fitted headcloth, and ash-brown A100. Its spell action, targeting, and link to the separate troll hazard passed. The installed three mesh or descriptor files match the reviewed bytes, and both installed manifest entries match their reviewed rows.
