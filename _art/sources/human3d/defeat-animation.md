# Native combat defeat pilot

This package covers all eight Travelers and four generated foe models. The Traveler motion uses the shared native skeleton and keeps equipped weapons, hats, and cloth on the existing skin bindings. It supplies separate fits for blade, bow, club, fist, gun, iai, pole, and short-weapon motion families.

| Traveler | Collapse and recovery |
| --- | --- |
| Hiruma Natsuko | Forward knee gives, scout’s near hand braces, then the shoulder follows. |
| Kakita Rensei | Short restrained recoil, rearward fall, then a hand-led recovery back to ready. |
| Kitsuki Gendo | Sinks from the knees into a seated diagonal, with the closer hand bearing weight. |
| Akodo Shizue | Commits to a forward brace and falls across the opposite shoulder. |
| Isawa Haruki | Dips the head and reaches out before the hips settle. |
| Shosuro Mitsue | Small, low-profile side roll with arms tucked close and a quick return to balance. |
| Ide Tamotsu | Broad stagger, reaches out for balance, rolls back and settles. |
| Sayo | Reaches down with the far hand and settles into a forward diagonal. |

The collapse is 31 frames at 30 fps, about 1.03 seconds. Its last frame is the held pose. Native Travelers hold that pose after the collapse completes until revival. A normal revival has a 45-frame, 1.5 second rise. The motion opens with a side or forward roll, catches on a palm or forearm, transfers the hips over a tucked knee, and finishes with a planted rise into ready. The free hand stays available when there is a bulky held weapon. A revival that interrupts the fall uses the original stand transition. Ordinary new skill poses can interrupt the recovery without holding gameplay input. Players can fight, move, and resolve conditions according to the existing battle rules.

| Foe | Arena fixture | Visual |
| --- | --- | --- |
| EP459 | E430, Kappa | Recoils, tucks its legs, rolls back onto its shell, and settles after a small bounce. |
| EP165 | E463, Giant Hornet | Flutters unevenly while losing lift, folds its wings, and settles after striking the ground. |
| EP438 | E108, Will-o’-wisp | Wavers, curls inward, and contracts with a soft downward drift. |
| EP120 | E106, Nezumi Shaman | Takes a heavy stagger, buckles, rotates onto one shoulder, and settles. |

Each foe motion lasts 32 frames at 30 fps. The existing enemy hide schedule and battle logic still determine removal and rewards. Foes outside these four assets keep their current motions. Future variants can extend this same layout, matching the generated skeleton and using the existing stand as a starting pose.

## Installation and daylight review

For an updated installation, copy only the eight motion files and index.json under assets/native_chara/defeat, plus the revised traveler_defeat.py source. For a first installation, use the staged installer with the repository root as its argument. It installs the motion banks, preserves existing animations and integration hooks, and layers small changes into `RokuganNativeChara.sk` and `RokuganBattle.sk`. The installer checks that its edit anchors are present before writing the live scripts.

In Coast Road M811, keep another party member standing while a Traveler reaches zero HP. Review the stagger, weight transfer through the hand and hips, contact with the ground, and the held pose across a turn change. Then use the normal revival action and watch for separate roll, support plant, push, knee-under-hips, and standing beats. Watch the support hand near the intended contact from about 0.4 to 0.9 seconds, and the tucked knee touching down before the hips rise. Check the same route with one traveler who uses a long weapon and one with a sheathed weapon. For the foe shots, keep a second enemy active so the victory camera does not cover the death. Use the normal finishing attack and review the model through the existing hide. Confirm that health, return to readiness, rewards, and target selection retain the original behavior. A rapid-revival case should take the standard stand transition instead of restarting the fall.

To re-export, run `traveler_defeat.py` with Blender Python followed by `--`, repository root and output directory. Run `foe_defeat.py` with regular project Python and positional repository root and output directory. Each output directory is for one branch of the staged resource tree.



## Collapse routing correction

The native Traveler fall lasts 31 frames at 30 fps. The first quarter is a recoil and short recovery step. The knees buckle and the lead hand braces in the middle. The chest drops through the last third, makes contact around 0.87 seconds, and settles into the unchanged down pose. The approved 45-frame get-up and its initial held pose are identical in the packed animation frames for every actor and weapon family.

The engine normally executes X005 from ManualMoveAction.deathAnime, and X005 immediately asks to play the held die pose. That direct macro call bypassed the separate RPG3DPicture collapse override. Native Travelers at zero HP now enter the authored collapse directly. The native hold waits for the actual layer to finish instead of using the legacy 700 ms timer. An interrupted fidget releases props without requesting the held die pose. All foe death handling and non-native fallbacks retain their original routes.

For an existing defeat installation, apply install_collapse_fix.py with the repository root as the only argument. It updates the native Traveler banks and their ranges together, and layers narrow changes over RokuganNativeChara.sk and RokuganBattle.sk. No foe asset or recovery runtime change is required. Review a fresh knock-out at full speed as well as a repeated fall following revival.

