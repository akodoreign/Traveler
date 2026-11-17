"""Invariants of the 3-D mannequin: fixed bones, planted feet, gap-free shoulders, real weapon handling."""
import unittest

import numpy as np

import rig3d
import rig3d_poses as poses
import rig3d_sheet as sheet

KEYS = ("trav_natsuko", "trav_rensei", "trav_gendo", "trav_shizue", "trav_haruki", "trav_mitsue",
        "trav_tamotsu", "trav_sayo", "side_yosai")
ATTACKS = ("atk_slash", "atk_thrust", "atk_overhead", "atk_draw")


def length(a, b):
    return float(np.linalg.norm(a - b))


class Rig3dTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rigs = {key: rig3d.Mannequin(key) for key in KEYS}
        cls.plan = sheet.plan()[0]

    def solved(self, key, kind, index, count, view=None):
        m = self.rigs[key]
        kind, view = poses.VIEWS.get(kind, (kind, view))
        if kind in ("critical", "void_critical"):
            kind = poses.SPECIAL[m.family][kind == "void_critical"]
        c = poses.controls(kind, index, count, m.family)
        return m.solve(c, view), m.frames[view], c

    def test_sheet_keeps_the_legacy_frame_ranges_and_appends_specials(self):
        self.assertEqual(sum(count for _, _, count, _ in self.plan), 211)
        self.assertEqual([name for name, *_ in self.plan[-4:]], ["squat", "celebration", "critical", "void_critical"])

    def test_no_pose_stretches_a_limb(self):
        for key in KEYS:
            for name, kind, count, view in self.plan:
                for index in range(count):
                    s, f, _ = self.solved(key, kind, index, count, view)
                    for side in "NF":
                        thigh, shin, _, _ = f.leg[side]
                        upper, fore, hand, _ = f.arm[side]
                        J = s.J
                        for a, b, expected in ((J["hip" + side], J["knee" + side], thigh),
                                               (J["knee" + side], J["ankle" + side], shin),
                                               (J["sh" + side], J["elbow" + side], upper),
                                               (J["elbow" + side], J["grip" + side], fore + hand)):
                            self.assertAlmostEqual(length(a, b), expected, places=6, msg=f"{key} {name}:{index}")

    def test_arms_start_on_the_drawn_shoulders_in_every_view(self):
        for key in KEYS:
            for view, name in ((None, "nod"), ("front", "fnod"), ("back", "bnod")):
                s, f, _ = self.solved(key, name, 0, 4)
                _, body, torso, at, _ = s.items[0]
                for side in "NF":
                    pin = at + torso @ (f.pins[side] - body.anchor)
                    np.testing.assert_allclose(s.S["sh" + side][0], pin, atol=1e-6, err_msg=f"{key} {view}")
            for index in range(6):                  # a leaning strike keeps the skeleton within a pixel or two
                s, f, _ = self.solved(key, "atk_thrust", index, 6)
                _, body, torso, at, _ = s.items[0]
                for side in "NF":
                    drift = length(s.S["sh" + side][0], at + torso @ (f.pins[side] - body.anchor))
                    self.assertLess(drift, 3.5, f"{key} thrust {index}")

    def test_relaxed_standing_staggers_the_camera_side_foot_and_turns_it_to_the_camera(self):
        for key in KEYS:
            m = self.rigs[key]
            s, f, _ = self.solved(key, "idle8", 0, 8)
            ready, _, _ = self.solved(key, "ready", 0, 2)
            self.assertLess(s.J["ankleN"][0], s.J["ankleF"][0] - 3)
            self.assertGreater(s.J["ankleN"][0], ready.J["ankleN"][0] + 3)        # not as deep as combat
            drawn = [part for _, part, *_ in s.items]
            self.assertTrue(any(part is m.parts["foot_b_camera"] for part in drawn), key)
            for view, look in (("fidle", "camera"), ("bidle", "heel")):
                s, _, _ = self.solved(key, view, 0, 4)
                self.assertTrue(any(part is m.parts[f"foot_f_{look}"] for _, part, *_ in s.items), key)

    def test_combat_feet_stay_planted_on_a_compact_base(self):
        for key in KEYS:
            for kind in ATTACKS:
                first = None
                for index in range(6):
                    s, f, c = self.solved(key, kind, index, 6)
                    if self.rigs[key].family == "iai" and kind in ("atk_slash", "atk_draw"):
                        continue                    # the draw-cut kneels: covered by the Kakita test
                    for side in "NF":
                        if side in c["kick"]:
                            continue
                        self.assertAlmostEqual(s.J["ankle" + side][1], f.leg[side][2], places=6)
                    if c["kick"]:
                        continue
                    feet = np.array([s.J["ankleN"], s.J["ankleF"]])
                    first = feet if first is None else first
                    np.testing.assert_allclose(feet, first, atol=1e-6, err_msg=f"{key} {kind}:{index}")
                    spread = feet[1][0] - feet[0][0]
                    self.assertTrue(.45 * f.L < spread < .8 * f.L, f"{key} {kind}")

    def test_both_hands_hold_two_handed_weapons(self):
        for key in KEYS:
            for kind in ("ready", "guard", *ATTACKS):
                count = 6 if kind in ATTACKS else 2
                for index in range(count):
                    s, _, c = self.solved(key, kind, index, count)
                    w = c["weapon"]
                    if w and w.get("sep") is not None:
                        other = "N" if w["hand"] == "F" else "F"
                        hold = s.J["grip" + w["hand"]] + s.gear["dir"] * w["sep"]
                        self.assertLess(length(s.J["grip" + other], hold), 2.5, f"{key} {kind}:{index}")

    def test_spear_thrust_is_level_and_carries_the_weight_forward(self):
        m = self.rigs["trav_natsuko"]
        wind, f, _ = self.solved("trav_natsuko", "atk_thrust", 1, 6)
        strike, _, _ = self.solved("trav_natsuko", "atk_thrust", 3, 6)
        self.assertGreater(strike.J["pelvis"][0] - wind.J["pelvis"][0], 5)
        self.assertGreater(strike.gear["at"][0] - wind.gear["at"][0], 15)
        tip = m.screen(strike.gear["at"] + strike.gear["dir"] * m.tip, f)[0]
        self.assertLess(abs(tip[1] - m.screen(strike.gear["at"], f)[0][1]), 3)

    def test_kakita_draws_from_the_hip_and_cuts_outward_over_a_dropped_knee(self):
        m = self.rigs["trav_rensei"]
        ready, f, _ = self.solved("trav_rensei", "ready", 0, 2)
        self.assertAlmostEqual(ready.gear["reveal"], m.tsuba)                  # only the hilt shows
        self.assertLess(length(ready.J["gripF"], ready.gear["at"]), 1)         # sword hand on the hilt
        self.assertLess(length(ready.J["gripN"], ready.J["saya"]), 4)          # other hand on the scabbard
        self.assertLess(abs(ready.gear["at"][1] - ready.J["pelvis"][1]), 12)   # at the hip
        for kind, count in (("atk_slash", 6), ("atk_draw", 6), ("critical", 6), ("void_critical", 8)):
            first, _, _ = self.solved("trav_rensei", kind, 0, count)
            last, _, _ = self.solved("trav_rensei", kind, count - 1, count)
            self.assertAlmostEqual(first.gear["reveal"], m.tsuba)
            self.assertAlmostEqual(last.gear["reveal"], m.tsuba)
            cut, _, _ = self.solved("trav_rensei", kind, count // 2, count)
            self.assertIsNone(cut.gear["reveal"])
            self.assertGreater(cut.gear["dir"][0], .8)                          # the blade ends pointing forward
            self.assertGreater(cut.J["gripF"][0] - first.J["gripF"][0], 15)     # and has travelled outward
            self.assertLess(cut.J["pelvis"][1], first.J["pelvis"][1] - .3 * f.L)
            self.assertLess(cut.J["kneeN"][1], 8)                               # rear knee on the ground
            self.assertGreater(cut.J["kneeF"][1], cut.J["kneeN"][1] + 15)
            self.assertLess(length(cut.J["gripN"], cut.J["saya"]), 4)           # scabbard hand never lets go
            self.assertLess(cut.J["saya"][0] - cut.J["pelvis"][0],
                            first.J["saya"][0] - first.J["pelvis"][0] - 2)      # and pulls it back

    def test_togashi_fights_bare_handed_with_a_guard_and_a_kick(self):
        f = self.rigs["side_yosai"].frames[None]
        for name, kind, count, view in self.plan:
            for index in range(count):
                self.assertIsNone(self.solved("side_yosai", kind, index, count, view)[0].gear, name)
        ready, _, _ = self.solved("side_yosai", "ready", 0, 2)
        for side in "NF":
            self.assertGreater(ready.J["grip" + side][1], ready.J["sh" + side][1] - .2 * sum(f.arm[side][:3]))
        kick, _, _ = self.solved("side_yosai", "atk_draw", 3, 6)
        self.assertGreater(kick.J["ankleF"][1], .6 * f.L)
        self.assertAlmostEqual(kick.J["ankleN"][1], f.leg["N"][2], places=6)

    def test_archer_draw_hand_is_on_the_string(self):
        for index in (2, 3):
            s, _, _ = self.solved("trav_tamotsu", "atk_slash", index, 6)
            self.assertLess(length(s.J["gripF"], s.gear["string"]), 2)

    def test_arm_layers_reassemble_the_drawn_arm(self):
        m = self.rigs["trav_natsuko"]
        source = m.parts["arm_f_relaxed"]
        pieces = np.zeros_like(source.pixels)
        for segment in ("upper", "forearm", "hand"):
            layer = m.parts[f"arm_f_relaxed_{segment}"].pixels
            pieces[layer[..., 3] > 0] = layer[layer[..., 3] > 0]
        np.testing.assert_array_equal(pieces, source.pixels)


if __name__ == "__main__":
    unittest.main()
