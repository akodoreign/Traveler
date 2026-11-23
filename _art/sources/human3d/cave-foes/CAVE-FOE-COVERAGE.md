# Cave route foe coverage

The encounter tables in M470–M472 and M480–M484 reference 20 distinct human models. The cave installer stages regenerated portrait and wardrobe fits for 18. The remaining two are the previously upgraded EP404 Hungry Ronin and EP417 Wako Raider.

| Model | Foe | Encounter IDs | Appearance |
| --- | --- | --- | --- |
| EP413 | Border Patrol | E651, E652, E653, E680, E721, E855 | Seppun guard portrait, light guard armor, jingasa, yumi |
| EP414 | Sergeant of Spears | E739, E740, E741 | Mirumoto yari sergeant portrait, do-maru, disc-crested kabuto, yari |
| EP411 | Hatamoto’s Champion | E738 | Lion sergeant portrait, red lacquer armor, crescent kabuto, katana |
| EP405 | Sword-for-Hire | E727, E728 | Ronin yojimbo portrait, layered coat, katana |
| EP426 | Kolat Agent | E949 | Bayushi guard portrait and fitted facecloth, wrapped clothing, tanto |
| EP415 | Heavy Infantry | E737 | Guard sergeant portrait, broad Crab armor, kabuto and mempo, tetsubo |
| EP400 | Road Bandit | E304, E450, E623, E658, E823, E824 | Boatman portrait, common robe, katana |
| EP401 | Mountain Bandit | E645–E650, E852, E867 | Ferryman portrait, wrapped clothing, yumi |
| EP402 | Bandit Captain | E724 | Yosuke portrait, light armor, naginata |
| EP409 | Glory-Hungry Bushi | E682, E720 | Soshi officer portrait, red lacquer armor, katana |
| EP416 | Dock Ruffian | E528 | Drunken sailor portrait, wrapped dock clothes, kama |
| EP425 | Shadow-in-Black | E837 | Bayushi guard portrait and fitted facecloth, dark wrap, tanto |
| EP427 | Shosuro Renegade | E951 | Shosuro Shiko portrait on shared female rig, red cloth armor, noh mask, tanto |
| EP115 | Drunken Samurai | E642–E644 | Drunken sailor portrait, layered commoner coat, katana |
| EP2603 | Desperate Fisherman | E023 | Fisherman portrait, plain robe, yari |
| EP2611 | Bandit Lord | E031 | Yosuke portrait, broad do-maru, fitted nodachi |
| EP2613 | Disgraced Yojimbo | E033 | Scorpion yojimbo portrait, light guard armor, katana |
| EP2623 | Kolat Master Killer | E043 | Bayushi guard portrait and fitted facecloth, dark wrap, katana |

Each foe keeps its combat animation bank and enemy record. The installer copies the portrait donor's calibrated body descriptor, which uses the same skin color for the core, hands, neck and throat. Width and height vary by foe. Three armored portraits fit within their existing Hunyuan helmet crown envelopes in the offline geometry check. The native proof evaluates the six priority fits after combat loads. Inspect skin seams, helmet skirts and facecloth in native side views as part of visual review. W103 is the available native tetsubo and uses material colors.

| Enemy | Native model | Assessment |
| --- | --- | --- |
| E035 Aka-name | EP2615 | Hunyuan GLB source `_art/sources/foe3d/foe_aka_name.glb`, dedicated texture and creature motion |
| E926 Kappa | EP459 | Hunyuan GLB source `_art/sources/foe3d/kappa.glb`, dedicated texture and creature motion, established smaller scale |
| E703 Ink-pot Spirit | EP444 | Legacy modular model on M470/M480/M481. Needs a regenerated creature mesh. |
| E706 Lantern Spirit | EP445 | Legacy modular model on M470/M480/M481. Needs a regenerated creature mesh. |

The other 25 nonhuman models in the eight encounter tables use Hunyuan textures. The Carrion Crow EP437 and Grey Wolf EP440 use texture aliases EP171 and EP170, respectively.

Run `python -B C:/Users/akodo/Documents/Codex/2026-11-20/ok/work/human-foes/cave-stage/install_cave_foes.py <tool-directory> --check` to validate dependencies, then rerun without `--check` on the closed target profile. Add `--priority` to install the first six. Evaluate `cave_foe_proof.sk` once on M480 or M482 for the Border Patrol, M483 for the Sword-for-Hire, or M484 for the champion, sergeant, infantry and Kolat agent. Evaluate the fixture again once the battle loads. It prints the mapped actor, fitted outfit and weapon followed by `[CAVE FOE FIT] <map> fixture passed`.

## Installed and verified

All 18 human model IDs loaded in native combat with their selected shared body template, textured faces, four calibrated skin materials, equipped outfits and weapons. The assigned attack motion was also tested. Daylight 4K frames capture the Border Patrol, Sword-for-Hire pair and four mine fighters. Earlier Wako and Hungry Ronin fittings were preserved. The two remaining spirit shapes are generated and still need their creature rigs and native combat checks.
