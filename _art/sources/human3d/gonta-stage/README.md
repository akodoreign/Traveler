# Adult Gonta shared body

Gonta's released field and companion actor already uses `side_gonta.pm`, the shared 50-joint male body and the approved Hunyuan portrait. In the quarry bout, E120 selects EP742's older head and generic profile. The named EP742 route now uses the exact approved cast body, head and scale when the opponent is Gonta.

| Appearance | Runtime route |
| --- | --- |
| Quarry day | M104 events 4 and 15 → EP342 → `side_gonta` |
| Crossing guest | M170 event 6 → EP342 → `side_gonta` |
| Traveling hireling seen in camp | EP342 via the conditional hireling events |
| Playable companion | P125 → EP342. His starter clothes are A100 and starter tetsubo is W113. |
| Real quarry bout | M001 encounter 6 → M812 → E120 → EP742 with the name Gonta |
| Dynamic Sumai | E121 receives the opponent’s name and `EP342` maps to `EP742` for Gonta |
| Default Wrestler | The unnamed-cast E121 route continues to resolve the original EP742 assets |
| Gonta's boy | EP345 and EP745 use his own separate child portrait |

The approved standing profile is X 1.355, Y 1.090 and Z 1.370. Gonta remains broader than Togashi Yosai and Hiruma Natsuko, while they remain taller in the same neutral pose. The foe uses the same axis proportions and world-scale baseline as the cast rig. The field uses its existing common 1.25 NPC scale, and the playable companion keeps the existing equipment and width handling.

The approved portrait’s diffuse sample is sRGB 236, 158, 104 and the calibrated target is sRGB 237, 160, 105. The body uses `0xd95b24ff` for the core, hands, neck and throat. The exact production neck fit and its 107 blended head-to-neck vertices are reused without rescaling the head in isolation. Source and fit metadata are in `_art/sources/human3d/cast_heads/side_gonta_repaired_atlas.glb` and `side_gonta.json`.

The bout retains the A108 field armor, matching ronin trim, independent sash, bare hands and the EP742 combat motion bank. Existing field positioning, seated and walking clips, story logic, Sumai equipment swaps and encounter data remain intact.

## Apply and verify

Run `python -B install_gonta.py <tool-directory> --check` for a read-only preflight. Rerun without `--check` on a closed profile. The installer adds one named route to the EP742 resource entry and applies the corresponding opt-in binding in `RokuganNativeChara.sk`.

Launch with `-battle M001 6` and evaluate `gonta_proof.sk` on M812. The fixture also checks the dynamic Sumai name and the separate default Wrestler route. For the field, evaluate on M104 near the fire at `[66,4,27]` or M170 near the tunnel crossing at `[104,3,17]`. Native verification passed in the original M812 quarry bout and on M104 event 4. The probe verified P125 with his starter A100 and W113, the named Sumai variant, the separate Wrestler, and the original bare-handed punch action. Both tested runtime files match the installed files by SHA-256. See the two native logs and front and side 3840 × 2160 captures in this folder.
