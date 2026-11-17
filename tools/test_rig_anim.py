"""Focused tests for master-pose alignment and polearm rigging.

Run: py -3.12 -E -W ignore::ResourceWarning -m unittest discover -s tools -p test_rig_anim.py
"""
import unittest

import numpy as np

import rig_anim as rig
import rigged_master


class RigAnimationTests(unittest.TestCase):
    @staticmethod
    def joints():
        return {
            "sh_b": np.array([13.0, 7.0]), "el_b": np.array([13.0, 11.0]), "ha_b": np.array([13.0, 15.0]),
            "sh_f": np.array([17.0, 7.0]), "el_f": np.array([17.0, 11.0]), "ha_f": np.array([17.0, 15.0]),
            "hip": np.array([15.0, 25.0]), "hipd": np.array([15.0, 29.0]), "shm": np.array([15.0, 7.0]),
            "waistline_b": np.array([11.0, 25.0]), "waistline_f": np.array([19.0, 25.0]),
            "kn_b": np.array([12.0, 40.0]), "ft_b": np.array([12.0, 60.0]), "toe_b": np.array([17.0, 60.0]),
            "kn_f": np.array([18.0, 40.0]), "ft_f": np.array([18.0, 60.0]), "toe_f": np.array([23.0, 60.0]),
            "neck": np.array([15.0, 3.0]), "head_top": np.array([15.0, -15.0]),
            "hand_tip_b": np.array([15.0, 18.0]), "hand_tip_f": np.array([19.0, 18.0]),
            "weapon_grip": np.array([17.0, 15.0]), "wtip": np.array([17.0, -10.0]),
        }

    def test_waistline_has_its_own_segment_and_rotates_with_the_torso(self):
        master = np.zeros((68, 80, 4), dtype=np.uint8)
        master[23:28, 11:20] = (120, 80, 60, 255)
        joints = self.joints()
        labels = rig.labels(master, joints)
        waistline = [part[0] for part in rig.PARTS].index("waistline")
        self.assertEqual(labels[25, 15], waistline)

        target = {key: value.copy() for key, value in joints.items()}
        target["waistline_b"] = np.array([25.0, 20.0])
        target["waistline_f"] = np.array([25.0, 29.0])
        out = rig.rig_frame(master, labels, joints, target)
        ys, xs = np.where(out[..., 3] > 0)
        self.assertGreater(len(xs), 0)
        self.assertLess(xs.max() - xs.min(), ys.max() - ys.min())

    def test_sheathed_iai_animation_hides_the_weapon_part(self):
        traveler = rig.traveler("trav_rensei")
        self.assertTrue(rig.weapon_sheathed(traveler, "idle8", 0))
        for frame in (0, 1, 5):
            self.assertTrue(rig.weapon_sheathed(traveler, "atk_draw", frame))
        for frame in (2, 3, 4):
            self.assertFalse(rig.weapon_sheathed(traveler, "atk_draw", frame))
        idle = rig.pose_data(traveler, "idle8", 0)
        crouch = rig.pose_data(traveler, "atk_draw", 0)
        self.assertGreater(crouch["hip"][1], idle["hip"][1])
        for frame in range(5):
            self.assertTrue(rig.pose_data(traveler, "atk_draw", frame)["kneel"])
        self.assertGreater(
            rig.pose_data(traveler, "atk_draw", 0)["ft_f"][0] -
            rig.pose_data(traveler, "atk_draw", 0)["ft_b"][0], 20)
        for frame, angle in zip((2, 3, 4), (0.0, 0.0, 1.0)):
            self.assertAlmostEqual(rig.pose_data(traveler, "atk_draw", frame)["wang"], angle)

        master = np.zeros((68, 80, 4), dtype=np.uint8)
        master[10:30, 40:43] = (210, 210, 210, 255)
        labels = np.full(master.shape[:2], -1, dtype=int)
        weapon = [part[0] for part in rig.PARTS].index("weapon")
        labels[10:30, 40:43] = weapon
        joints = self.joints()
        hidden = rig.rig_frame(master, labels, joints, joints, hide_weapon=True)
        visible = rig.rig_frame(master, labels, joints, joints)
        self.assertEqual(int(hidden[..., 3].sum()), 0)
        self.assertGreater(int(visible[..., 3].sum()), 0)

    def test_polearm_keeps_the_shaft_behind_the_grip(self):
        master = np.zeros((68, 80, 4), dtype=np.uint8)
        master[5:63, 39:42] = (210, 210, 210, 255)
        joints = {
            "sh_b": np.array([10.0, 10.0]), "el_b": np.array([12.0, 14.0]), "ha_b": np.array([14.0, 18.0]),
            "sh_f": np.array([20.0, 10.0]), "el_f": np.array([24.0, 14.0]), "ha_f": np.array([40.0, 35.0]),
            "hip": np.array([15.0, 25.0]), "kn_b": np.array([12.0, 40.0]), "ft_b": np.array([12.0, 60.0]),
            "kn_f": np.array([20.0, 40.0]), "ft_f": np.array([20.0, 60.0]),
            "shm": np.array([15.0, 10.0]), "hipd": np.array([15.0, 29.0]), "wtip": np.array([40.0, 15.0]),
            "waistline_b": np.array([11.0, 25.0]), "waistline_f": np.array([19.0, 25.0]),
            "neck": np.array([15.0, 8.0]), "head_top": np.array([15.0, -10.0]),
            "toe_b": np.array([17.0, 60.0]), "toe_f": np.array([25.0, 60.0]),
            "hand_tip_b": np.array([16.0, 18.0]), "hand_tip_f": np.array([42.0, 35.0]),
        }

        labels = rig.labels(master, joints, "yari")
        weapon = [part[0] for part in rig.PARTS].index("weapon")
        hand_f = [part[0] for part in rig.PARTS].index("hand_f")

        self.assertEqual(labels[55, 40], weapon)
        self.assertEqual(labels[35, 40], hand_f)
        self.assertNotEqual(labels[55, 48], weapon)

    def test_joint_overrides_preserve_rest_pose_and_rig_motion(self):
        base = {"ha_f": np.array([2.0, 3.0]), "hip": np.array([4.0, 5.0])}
        override = {"ha_f": (8.0, 9.0)}

        at_rest = rig.apply_master_joints({k: v.copy() for k, v in base.items()}, base, override)
        moved = rig.apply_master_joints(
            {"ha_f": np.array([3.0, 5.0]), "hip": np.array([4.0, 5.0])}, base, override)

        np.testing.assert_array_equal(at_rest["ha_f"], (8.0, 9.0))
        np.testing.assert_array_equal(moved["ha_f"], (9.0, 11.0))
        np.testing.assert_array_equal(moved["hip"], base["hip"])

    def test_leg_motion_scale_preserves_rest_pose_and_reduces_spread(self):
        rest = {
            "hip": np.array([10.0, 10.0]),
            "kn_b": np.array([9.0, 16.0]),
            "ft_b": np.array([8.0, 22.0]),
            "toe_b": np.array([13.0, 22.0]),
        }
        target = {key: value.copy() for key, value in rest.items()}
        target["hip"] += (8.0, 4.0)
        target["kn_b"] += (2.0, 4.0)
        target["ft_b"] += (-4.0, 4.0)
        target["toe_b"] += (-4.0, 4.0)

        at_rest = rig.scale_leg_motion(rest, rest, 0.8)
        adjusted = rig.scale_leg_motion(target, rest, 0.8)

        for key in rest:
            np.testing.assert_array_equal(at_rest[key], rest[key])
        self.assertGreater(np.linalg.norm(target["ft_b"] - target["hip"]),
                           np.linalg.norm(adjusted["ft_b"] - adjusted["hip"]))
        np.testing.assert_array_equal(adjusted["hip"], target["hip"])

    def test_arm_motion_scale_preserves_rest_pose_and_reduces_reach(self):
        rest = {
            "sh_f": np.array([10.0, 10.0]),
            "el_f": np.array([14.0, 12.0]),
            "ha_f": np.array([18.0, 14.0]),
            "hand_tip_f": np.array([20.0, 15.0]),
        }
        target = {key: value.copy() for key, value in rest.items()}
        target["ha_f"] += (12.0, -8.0)
        target["hand_tip_f"] += (12.0, -8.0)

        at_rest = rig.scale_arm_motion(rest, rest, 0.8)
        adjusted = rig.scale_arm_motion(target, rest, 0.8)

        for key in rest:
            np.testing.assert_array_equal(at_rest[key], rest[key])
        self.assertLess(np.linalg.norm(adjusted["ha_f"] - adjusted["sh_f"]),
                        np.linalg.norm(target["ha_f"] - target["sh_f"]))
        np.testing.assert_array_equal(adjusted["sh_f"], target["sh_f"])

    def test_body_motion_scale_reduces_torso_and_head_travel(self):
        rest = {
            "hip": np.array([10.0, 20.0]),
            "shm": np.array([10.0, 8.0]),
            "neck": np.array([10.0, 5.0]),
            "head_top": np.array([10.0, -10.0]),
            "sh_f": np.array([14.0, 8.0]),
            "ha_f": np.array([18.0, 14.0]),
        }
        target = {key: value.copy() for key, value in rest.items()}
        for key in ("hip", "shm", "neck", "head_top", "sh_f"):
            target[key] += (4.0, 2.0)

        adjusted = rig.scale_body_motion(target, rest, 0.25)
        for key in ("hip", "shm", "neck", "head_top", "sh_f"):
            np.testing.assert_array_equal(adjusted[key], rest[key] + (1.0, 0.5))
        np.testing.assert_array_equal(adjusted["ha_f"], target["ha_f"])

    def test_explicit_label_masks_override_nearest_bone_assignment(self):
        labels = np.zeros((4, 5), dtype=int)
        mask = np.zeros(labels.shape, dtype=bool)
        mask[2, 3] = True
        waist = [part[0] for part in rig.PARTS].index("waist")

        labeled = rig.apply_label_masks(labels, {"waist": mask})

        self.assertEqual(labeled[2, 3], waist)
        self.assertEqual(labeled[1, 3], 0)
        with self.assertRaises(ValueError):
            rig.apply_label_masks(labels, {"waist": np.ones((2, 2), dtype=bool)})

    def test_rensei_master_uses_disjoint_explicit_part_masks(self):
        master, masks = rigged_master.make_rensei_parts_master(return_masks=True)

        self.assertEqual(master.shape, (136, 160, 4))
        self.assertEqual(set(masks), {"body", "head", "waist", "foot_b", "foot_f"})
        self.assertTrue(all(mask.any() for mask in masks.values()))
        total = np.sum(np.stack(list(masks.values())), axis=0)
        self.assertLessEqual(int(total.max()), 1)

    def test_limb_transform_reaches_the_target_without_rotating_full_swing(self):
        source_start = np.array([2.0, 3.0])
        source_end = np.array([2.0, 7.0])
        target_start = np.array([10.0, 12.0])
        target_end = np.array([16.0, 12.0])

        matrix, offset = rig.limb_transform(source_start, source_end, target_start, target_end, 0.5)
        mapped_start = matrix @ source_start + offset
        mapped_end = matrix @ source_end + offset

        np.testing.assert_allclose(mapped_start, target_start)
        self.assertAlmostEqual(np.linalg.norm(mapped_end - mapped_start), 6.0)
        self.assertAlmostEqual(np.degrees(np.arctan2(*(mapped_end - mapped_start)[::-1])), 45.0)

    def test_head_hand_and_foot_segments_have_pose_joints(self):
        names = {part[0] for part in rig.PARTS}
        self.assertTrue({"head", "hand_b", "hand_f", "foot_b", "foot_f"} <= names)

        T = rig.traveler("trav_natsuko")
        kind, frame = rig.s2.FRAMES[0]
        joints = rig.joints(T, kind, frame)
        self.assertTrue({"neck", "head_top", "hand_tip_b", "hand_tip_f", "toe_b", "toe_f",
                         "waistline_b", "waistline_f"} <= joints.keys())

    def test_hd_joint_gaps_are_closed_at_the_master_scale(self):
        image = np.zeros((20, 20, 4), dtype=np.uint8)
        image[8, 5] = (120, 80, 60, 255)
        image[8, 9] = (120, 80, 60, 255)
        rig.ZF = 2
        try:
            closed = rig.fill_seams(image, image[..., 3] > 0)
        finally:
            rig.ZF = 1

        self.assertGreater(closed[8, 7, 3], 0)

    def test_arm_pose_cycles_cover_ten_variants_and_align_the_hand(self):
        poses = {"b": [{} for _ in range(10)], "f": [{} for _ in range(10)]}
        self.assertEqual([rig.arm_pose_index("celebration", i, "f", poses) for i in range(10)],
                         list(range(10)))

        image = np.zeros((5, 5, 4), dtype=np.uint8)
        image[2, 0:5] = (80, 140, 210, 255)
        out = np.zeros((16, 16, 4), dtype=np.uint8)
        pose = {"image": image, "anchor": np.array([0.0, 2.0]), "tip": np.array([4.0, 2.0])}
        rig.draw_arm_pose(out, pose, np.array([6.0, 6.0]), np.array([6.0, 10.0]))
        self.assertGreater(out[6, 6, 3], 0)
        self.assertGreater(out[10, 6, 3], 0)
        self.assertEqual(out[6, 6, :3].tolist(), [80, 140, 210])

    def test_squat_and_celebration_gestures_have_distinct_body_and_arm_poses(self):
        base = self.joints()
        squat, _ = rig.gesture_joints(base, np.array([15.0, 2.0]), "squat", 2, 5)
        self.assertGreater(squat["hip"][1], base["hip"][1])
        self.assertGreater(squat["kn_f"][0], base["kn_f"][0])
        self.assertEqual(squat["ft_f"][1], base["ft_f"][1])

        dance = [rig.gesture_joints(base, np.array([15.0, 2.0]), "celebration", i, 10)[0]
                 for i in range(10)]
        self.assertGreater(len({tuple(pose["ha_f"]) for pose in dance}), 5)
        self.assertGreater(len({tuple(pose["ha_b"]) for pose in dance}), 5)
        for pose in dance:
            for side in ("b", "f"):
                self.assertNotEqual(float(np.linalg.norm(pose["hand_tip_" + side] - pose["ha_" + side])), 0.0)

    def test_rensei_victory_animation_is_a_four_frame_dance(self):
        traveler = rig.traveler("trav_rensei")
        self.assertEqual(traveler["victory"], "dance")
        poses = [rig.s2.pose_v4(traveler, "victory2", i) for i in range(4)]
        self.assertGreater(len({tuple(pose["ha_f"]) for pose in poses}), 2)


if __name__ == "__main__":
    unittest.main()
