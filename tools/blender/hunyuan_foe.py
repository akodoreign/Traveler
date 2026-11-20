"""Stage textured Hunyuan3D meshes with Traveler's native battle clips.

Run with Blender in background mode and pass the source GLB, an output
directory, and a creature name after --. Install the staged MDL, MOT, PM,
and referenced textures in project/resource/native_foe.
"""
import argparse
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix


def distances(points, a, b):
    a, b = np.array(a), np.array(b)
    line = b - a
    offsets = points - a
    t = np.clip(offsets @ line / (line @ line), 0, 1)
    return np.linalg.norm(offsets - t[:, None] * line, axis=1)


def add_weights(mesh, points, bones, shell):
    names = list(bones)
    d = np.column_stack([distances(points, a, b) / radius for a, b, radius, _, _ in bones.values()])
    strength = np.exp(-2.8 * (d ** 2 - (d ** 2).min(axis=1, keepdims=True)))
    strength[shell] = 0
    strength[shell, names.index("root")] = 1
    groups = [mesh.vertex_groups.new(name=name) for name in names]
    for i, weights in enumerate(strength):
        nearest = np.argsort(weights)[-4:]
        selected = [j for j in nearest if weights[j] > weights.max() * .025]
        total = sum(weights[j] for j in selected)
        for j in selected:
            groups[j].add([i], weights[j] / total, "REPLACE")


def kappa_bones():
    bones = {
        "root": ((-7, 38, 0), (-7, 60, 0), 17, "root", 0),
        "head": ((2, 57, 0), (2, 76, 0), 15, "head", 0),
    }
    for side in (-1, 1):
        bones[f"arm{side}"] = ((3, 51, 13 * side), (12, 32, 26 * side), 8, "claw", side)
        bones[f"leg{side}"] = ((-1, 30, 7 * side), (8, 4, 14 * side), 10, "leg", -side)
    return bones


def crab_bones():
    bones = {"root": ((-19, 19, 0), (10, 19, 0), 19, "root", 0)}
    for side in (-1, 1):
        bones[f"claw{side}"] = ((15, 15, 15 * side), (35, 10, 24 * side), 10, "claw", side)
        for n, depth in enumerate((10, 0, -10, -19)):
            bones[f"leg{side}_{n}"] = (
                (depth, 19, 23 * side), (depth - 5, 2, (46 - n * 3) * side), 7, "leg", side * (-1) ** n
            )
    return bones


def spider_bones():
    bones = {"root": ((-33, 19, 0), (27, 20, 0), 18, "root", 0)}
    ends = ((44, 6, 29), (23, 8, 46), (7, 15, 45), (-11, 16, 39))
    for side in (-1, 1):
        for n, (depth, height, width) in enumerate(ends):
            bones[f"leg{side}_{n}"] = (
                (27 - n * 6, 21, 11 * side), (depth, height, width * side), 7, "leg", side * (-1) ** n
            )
    return bones


def warmonger_bones():
    bones = {
        "root": ((-3, 22, 0), (-3, 56, 0), 17, "root", 0),
        "head": ((0, 52, 0), (8, 74, 0), 14, "head", 0),
    }
    for side in (-1, 1):
        bones[f"arm{side}"] = ((1, 52, 18 * side), (5, 23, 29 * side), 10, "claw", side)
        bones[f"leg{side}"] = ((-3, 23, 14 * side), (3, 2, 18 * side), 9, "leg", -side)
    return bones


def nezumi_bones():
    bones = {
        "root": ((-1, 30, 0), (-1, 58, 0), 14, "root", 0),
        "head": ((-1, 60, 0), (5, 75, 0), 12, "head", 0),
        "tail0": ((-10, 37, 0), (-22, 26, -8), 5, "tail", 1),
        "tail1": ((-22, 26, -8), (-34, 21, -20), 5, "tail", 2),
        "tail2": ((-34, 21, -20), (-37, 12, -27), 5, "tail", 3),
        "tail3": ((-37, 12, -27), (-30, 8, -19), 5, "tail", 4),
    }
    for side in (-1, 1):
        bones[f"arm{side}"] = ((1, 56, 12 * side), (5, 29, 20 * side), 8, "claw", side)
        bones[f"leg{side}"] = ((-2, 32, 9 * side), (5, 3, 17 * side), 8, "leg", -side)
    return bones


def cellar_ogre_bones():
    bones = {
        "root": ((-8, 30, 0), (-8, 102, 0), 28, "root", 0),
        "head": ((9, 76, 0), (24, 90, 0), 14, "head", 0),
    }
    for side in (-1, 1):
        bones[f"arm{side}"] = ((-4, 84, 30 * side), (18, 32, 58 * side), 16, "claw", side)
        bones[f"leg{side}"] = ((-6, 43, 22 * side), (2, 4, 35 * side), 14, "leg", -side)
    return bones


def naga_champion_bones():
    bones = {
        "root": ((0, 16, 0), (0, 70, 0), 17, "root", 0),
        "head": ((0, 71, 0), (0, 96, 0), 15, "head", 0),
        "arm1": ((1, 72, 17), (3, 47, 35), 11, "claw", 1),
        "arm-1": ((1, 72, -17), (9, 32, -28), 10, "claw", -1),
    }
    curve = [(3, 8, 0), (5, 8, -28), (-25, 8, -39), (-49, 8, -20),
             (-52, 8, 11), (-36, 8, 34), (-13, 8, 35), (1, 8, 26)]
    for i, (a, b) in enumerate(zip(curve, curve[1:])):
        bones[f"tail{i}"] = (a, b, 11, "tail", i)
    return bones


def red_tengu_bones():
    bones = {
        "root": ((-2, 25, 0), (-2, 73, 0), 17, "root", 0),
        "head": ((0, 73, 0), (2, 96, 0), 13, "head", 0),
        "arm1": ((3, 69, 15), (14, 62, 37), 10, "claw", 1),
        "arm-1": ((3, 66, -15), (13, 38, -23), 10, "claw", -1),
    }
    for side in (-1, 1):
        bones[f"leg{side}"] = ((-3, 28, 10 * side), (5, 3, 14 * side), 9, "leg", -side)
        bones[f"wing{side}"] = ((-8, 79, 14 * side), (-12, 26, 45 * side), 13, "wing", side)
    return bones


def oni_bones():
    bones = {
        "root": ((-3, 29, 0), (-3, 82, 0), 24, "root", 0),
        "head": ((2, 80, 0), (4, 105, 0), 19, "head", 0),
    }
    for side in (-1, 1):
        bones[f"arm{side}"] = ((0, 83, 25 * side), (8, 40, 43 * side), 13, "claw", side)
        bones[f"leg{side}"] = ((-4, 45, 20 * side), (5, 3, 27 * side), 12, "leg", -side)
    return bones


def shelf_kami_bones():
    bones = {
        "root": ((0, 33, 0), (0, 66, 0), 21, "root", 0),
        "head": ((2, 65, 0), (2, 83, 0), 18, "head", 0),
    }
    for side in (-1, 1):
        bones[f"arm{side}"] = ((0, 55, 24 * side), (12, 17, 43 * side), 11, "claw", side)
        bones[f"leg{side}"] = ((-1, 29, 13 * side), (5, 3, 25 * side), 10, "leg", -side)
    return bones


def ningyo_bones():
    return {
        "root": ((-5, 43, 0), (0, 66, 0), 15, "root", 0),
        "head": ((2, 62, 0), (7, 84, 0), 16, "head", 0),
        "arm1": ((2, 59, 12), (13, 34, 27), 8, "claw", 1),
        "arm-1": ((0, 59, -12), (5, 38, -28), 8, "claw", -1),
        "tail0": ((-7, 43, 0), (-18, 22, 0), 12, "tail", 1),
        "tail1": ((-18, 22, 0), (-3, 14, 0), 11, "tail", 2),
        "tail2": ((-3, 14, 0), (21, 17, 3), 11, "tail", 3),
        "tail3": ((21, 17, 3), (32, 23, 8), 12, "tail", 4),
    }


def nukekubi_bones():
    return {
        "root": ((-4, 32, 0), (-2, 55, 0), 17, "root", 0),
        "head": ((6, 36, -7), (12, 62, -7), 19, "head", 0),
        "hair1": ((-7, 43, 7), (-17, 33, 30), 11, "tail", 1),
        "hair-1": ((-7, 43, -7), (-17, 34, -28), 11, "tail", 3),
    }


def onibaba_bones():
    bones = {
        "root": ((-5, 24, 0), (-5, 62, 0), 17, "root", 0),
        "head": ((7, 58, 0), (13, 81, 0), 16, "head", 0),
        "arm1": ((0, 57, 15), (5, 29, 24), 8, "claw", 1),
        "arm-1": ((0, 56, -13), (14, 34, -21), 9, "claw", -1),
    }
    for side in (-1, 1):
        bones[f"leg{side}"] = ((-5, 36, 10 * side), (2, 3, 15 * side), 9, "leg", -side)
    return bones


def mamushi_bones():
    return {
        "root": ((-4, 7, 0), (-4, 16, 0), 19, "root", 0),
        "head": ((6, 28, -7), (19, 38, -17), 9, "head", 0),
        "neck": ((-7, 15, 0), (4, 30, -9), 9, "tail", 0),
        "tail0": ((-8, 10, -24), (12, 8, -26), 8, "tail", 2),
        "tail1": ((12, 8, -26), (25, 3, -14), 7, "tail", 3),
    }


def troll_bones():
    bones = {
        "root": ((-8, 41, 0), (-7, 108, 0), 23, "root", 0),
        "head": ((15, 92, 0), (37, 79, 0), 14, "head", 0),
    }
    for side in (-1, 1):
        bones[f"arm{side}"] = ((-2, 97, 26 * side), (22, 18, 41 * side), 13, "claw", side)
        bones[f"leg{side}"] = ((-13, 52, 17 * side), (6, 3, 21 * side), 11, "leg", -side)
    return bones


def shark_bones():
    return {
        "root": ((-10, 42, 0), (24, 40, 0), 15, "root", 0),
        "head": ((23, 40, 0), (45, 38, 0), 12, "head", 0),
        "tail0": ((-10, 42, 0), (-26, 42, 0), 9, "tail", 0),
        "tail1": ((-26, 42, 0), (-37, 42, 0), 8, "tail", 1),
        "tail2": ((-37, 42, 0), (-44, 42, 0), 12, "tail", 2),
        "fin1": ((18, 39, 5), (6, 27, 23), 7, "claw", 1),
        "fin-1": ((18, 39, -5), (6, 27, -23), 7, "claw", -1),
    }


def four_limbs(shoulder, hand, hip, foot, arm_radius, leg_radius):
    bones = {}
    for side in (-1, 1):
        def point(p):
            return p[0], p[1], p[2] * side

        bones[f"arm{side}"] = (point(shoulder), point(hand), arm_radius, "claw", side)
        bones[f"leg{side}"] = (point(hip), point(foot), leg_radius, "leg", -side)
    return bones


def hanemuri_bones():
    bones = {
        "root": ((0, 42, 0), (0, 65, 0), 14, "root", 0),
        "head": ((4, 62, 0), (9, 78, 0), 11, "head", 0),
        "tail0": ((-7, 41, 0), (-19, 31, 0), 7, "tail", 1),
        "tail1": ((-19, 31, 0), (-37, 22, 0), 7, "tail", 2),
    } | four_limbs((0, 58, 11), (10, 41, 22), (0, 43, 9), (7, 16, 12), 6, 7)
    for side in (-1, 1):
        bones[f"wing{side}"] = ((-7, 66, 10 * side), (-15, 61, 45 * side), 15, "wing", side)
    return bones


def ogre_hag_bones():
    return {
        "root": ((-12, 28, 0), (-10, 88, 0), 25, "root", 0),
        "head": ((10, 65, 0), (25, 64, 0), 13, "head", 0),
    } | four_limbs((0, 70, 23), (26, 15, 36), (-9, 34, 19), (-1, 3, 24), 12, 11)


def kuzushi_bones():
    return {
        "root": ((-8, 42, 0), (-8, 119, 0), 30, "root", 0),
        "head": ((19, 77, 0), (36, 84, 0), 12, "head", 0),
    } | four_limbs((1, 95, 31), (25, 16, 48), (-8, 53, 17), (10, 3, 21), 17, 13)


def hyakuhei_bones():
    bones = {
        "root": ((-5, 30, 0), (-5, 99, 0), 25, "root", 0),
        "head": ((9, 89, 0), (16, 109, 0), 16, "head", 0),
    } | four_limbs((3, 93, 29), (22, 63, 52), (-4, 44, 19), (9, 3, 29), 12, 13)
    for side in (-1, 1):
        bones[f"lower_arm{side}"] = ((7, 68, 22 * side), (20, 36, 36 * side), 9, "claw", -side)
    return bones


def shaman_bones():
    return {
        "root": ((1, 25, 0), (1, 68, 0), 14, "root", 0),
        "head": ((2, 67, 0), (8, 85, 0), 12, "head", 0),
        "arm1": ((3, 66, 9), (13, 58, 23), 8, "claw", 1),
        "arm-1": ((3, 65, -10), (10, 39, -16), 8, "claw", -1),
        "leg1": ((0, 35, 8), (6, 3, 11), 8, "leg", -1),
        "leg-1": ((0, 35, -8), (4, 3, -11), 8, "leg", 1),
        "tail0": ((-5, 23, -8), (-13, 10, -19), 6, "tail", 0),
        "tail1": ((-13, 10, -19), (-24, 11, -31), 6, "tail", 1),
        "tail2": ((-24, 11, -31), (-34, 19, -43), 6, "tail", 2),
    }


def cage_bones():
    return {"root": ((0, 50, 0), (0, 100, 0), 45, "root", 0)}


def tsuno_bones():
    return {
        "root": ((-3, 35, 0), (-3, 79, 0), 21, "root", 0),
        "head": ((1, 75, 0), (10, 101, 0), 17, "head", 0),
    } | four_limbs((2, 79, 20), (8, 44, 30), (-3, 44, 13), (5, 3, 23), 11, 12)


def zokujin_miner_bones():
    return {
        "root": ((-7, 28, 0), (-7, 63, 0), 18, "root", 0),
        "head": ((4, 51, 0), (21, 57, 0), 13, "head", 0),
    } | four_limbs((-3, 56, 19), (16, 26, 30), (-7, 30, 12), (3, 3, 17), 9, 9)


def hioninmaru_bones():
    return {
        "root": ((-10, 35, 0), (-10, 103, 0), 24, "root", 0),
        "head": ((4, 82, 0), (30, 96, 0), 16, "head", 0),
    } | four_limbs((-3, 82, 25), (15, 33, 42), (-6, 46, 16), (7, 3, 31), 13, 12)


def ianwa_bones():
    return oni_bones() | {
        "tail0": ((-9, 44, 0), (-28, 20, 4), 10, "tail", 1),
        "tail1": ((-28, 20, 4), (-52, 13, 20), 10, "tail", 2),
        "tail2": ((-52, 13, 20), (-68, 31, 37), 10, "tail", 3),
        "tail3": ((-68, 31, 37), (-67, 51, 45), 10, "tail", 4),
    }


def regret_bones():
    return {
        "root": ((-5, 31, 0), (-6, 83, 0), 23, "root", 0),
        "head": ((4, 81, 0), (12, 105, 0), 16, "head", 0),
    } | four_limbs((0, 79, 22), (14, 43, 31), (-3, 39, 14), (6, 3, 22), 11, 11)


def stolen_face_bones():
    return {
        "root": ((-6, 36, 0), (-5, 81, 0), 23, "root", 0),
        "head": ((15, 45, 0), (22, 67, 0), 13, "head", 0),
        "cloth": ((-2, 40, 4), (8, 14, 9), 11, "tail", 1),
    }


def bakeneko_bones():
    return {
        "root": ((-1, 12, 0), (-1, 28, 0), 9, "root", 0),
        "head": ((1, 31, 0), (4, 51, 0), 13, "head", 0),
        "arm1": ((5, 27, 6), (9, 22, 6), 5, "claw", 1),
        "arm-1": ((5, 27, -6), (9, 21, -6), 5, "claw", -1),
        "leg1": ((-1, 11, 4), (3, 2, 7), 5, "leg", -1),
        "leg-1": ((-1, 11, -4), (3, 2, -7), 5, "leg", 1),
        "tail0": ((-7, 11, -4), (-16, 7, -16), 5, "tail", 0),
        "tail1": ((-16, 7, -16), (-20, 19, -18), 6, "tail", 1),
        "tail2": ((-20, 19, -18), (-11, 30, -18), 6, "tail", 2),
        "tail3": ((-11, 30, -18), (-15, 32, -26), 7, "tail", 3),
    }


def quadruped_legs(shoulder, forepaw, hip, hindpaw, radius):
    bones = {}
    for side in (-1, 1):
        for kind, a, b, phase in (("front", shoulder, forepaw, side), ("rear", hip, hindpaw, -side)):
            start = (a[0], a[1], side * a[2])
            end = (b[0], b[1], side * b[2])
            bones[f"{kind}_leg{side}"] = (start, end, radius, "leg", phase)
    return bones


def tiger_bones():
    return {
        "root": ((-21, 26, 0), (26, 30, 0), 17, "root", 0),
        "head": ((27, 27, 0), (54, 19, 0), 13, "head", 0),
        "tail0": ((-20, 26, 0), (-32, 18, 0), 8, "tail", 1),
        "tail1": ((-32, 18, 0), (-43, 14, 0), 7, "tail", 2),
        "tail2": ((-43, 14, 0), (-55, 14, 0), 7, "tail", 3),
    } | quadruped_legs((25, 33, 9), (36, 1, 13), (-13, 31, 9), (-16, 1, 11), 9)


def stonehunter_bones():
    return {
        "root": ((-6, 24, 0), (-6, 66, 0), 18, "root", 0),
        "head": ((4, 52, 0), (21, 58, 0), 13, "head", 0),
        "arm1": ((-2, 53, 18), (10, 36, 30), 9, "claw", 1),
        "arm-1": ((-2, 53, -17), (17, 22, -30), 10, "claw", -1),
        "leg1": ((-7, 29, 12), (3, 3, 20), 10, "leg", -1),
        "leg-1": ((-7, 29, -12), (3, 3, -18), 10, "leg", 1),
        "tail": ((-11, 26, 0), (-35, 3, 24), 10, "tail", 2),
    }


def onikage_bones():
    return {
        "root": ((-17, 49, 0), (24, 52, 0), 18, "root", 0),
        "head": ((27, 55, 0), (48, 68, 0), 13, "head", 0),
        "tail0": ((-26, 55, 0), (-41, 53, 0), 8, "tail", 1),
        "tail1": ((-41, 53, 0), (-50, 32, 0), 8, "tail", 2),
        "tail2": ((-50, 32, 0), (-52, 13, 0), 7, "tail", 3),
    } | quadruped_legs((25, 52, 9), (27, 2, 13), (-14, 51, 10), (-23, 2, 13), 10)


def umibozu_bones():
    return {
        "root": ((0, 16, 0), (0, 55, 0), 33, "root", 0),
        "head": ((18, 47, 0), (27, 72, 0), 17, "head", 0),
    }


def horror_bones():
    bones = {"root": ((-28, 32, 0), (22, 28, 0), 23, "root", 0)}
    feet = ((39, 2, 32), (16, 4, 31), (8, 3, 53), (-15, 3, 43), (-38, 5, 22))
    for side in (-1, 1):
        for i, (depth, height, width) in enumerate(feet):
            start = (26 - i * 11, 23, (13 + (i % 2) * 3) * side)
            bones[f"leg{side}_{i}"] = (start, (depth, height, width * side), 9, "leg", side * (-1) ** i)
        bones[f"claw{side}"] = ((24, 20, 8 * side), (37, 9, 13 * side), 6, "claw", side)
    return bones


def kansen_bones():
    return {
        "root": ((-4, 8, 0), (-4, 57, 0), 17, "root", 0),
        "head": ((2, 62, 0), (11, 93, 0), 26, "head", 0),
        "vine1": ((0, 30, 12), (1, 63, 43), 12, "claw", 1),
        "vine-1": ((0, 30, -12), (1, 56, -43), 12, "claw", -1),
    }


def mine_guardian_bones():
    return {
        "root": ((-3, 32, 0), (-3, 76, 0), 22, "root", 0),
        "head": ((2, 72, 0), (11, 96, 0), 15, "head", 0),
    } | four_limbs((-2, 80, 27), (12, 36, 38), (-3, 39, 15), (4, 3, 23), 13, 12)


def damned_time_bones():
    return {
        "root": ((0, 15, 0), (0, 85, 0), 19, "root", 0),
        "head": ((0, 75, 0), (2, 114, 0), 13, "head", 0),
        "sleeve1": ((1, 76, 8), (0, 73, 48), 14, "claw", 1),
        "sleeve-1": ((1, 76, -8), (0, 73, -48), 14, "claw", -1),
        "hem1": ((-1, 48, 7), (2, 10, 33), 12, "tail", 1),
        "hem-1": ((-1, 48, -7), (2, 10, -33), 12, "tail", 3),
    }


def beetle_bones():
    bones = {
        "root": ((-22, 11, 0), (14, 10, 0), 15, "root", 0),
        "head": ((14, 8, 0), (29, 5, 0), 8, "head", 0),
    }
    for side in (-1, 1):
        for i, ((depth, width), (end_depth, end_width)) in enumerate(
            zip(((15, 9), (0, 13), (-14, 13)), ((34, 16), (8, 34), (-27, 30)))
        ):
            bones[f"leg{side}_{i}"] = (
                (depth, 6, width * side), (end_depth, 1, end_width * side), 5, "leg", side * (-1) ** i
            )
    return bones


def hornet_bones():
    bones = {
        "root": ((-3, 56, 0), (9, 60, 0), 11, "root", 0),
        "head": ((8, 53, 0), (16, 61, 0), 9, "head", 0),
        "abdomen": ((-6, 50, 0), (-11, 32, 0), 9, "tail", 1),
    }
    for side in (-1, 1):
        bones[f"wing{side}"] = ((5, 57, 7 * side), (1, 71, 38 * side), 8, "wing", side)
        bones[f"wing_lower{side}"] = ((4, 54, 7 * side), (-3, 53, 30 * side), 6, "wing", side)
        bones[f"leg{side}"] = ((4, 51, 8 * side), (9, 35, 15 * side), 6, "claw", side)
    return bones


def wolf_bones():
    return {
        "root": ((-10, 39, 0), (28, 44, 0), 17, "root", 0),
        "head": ((30, 43, 0), (50, 53, 0), 15, "head", 0),
        "tail0": ((-17, 41, 0), (-29, 28, 0), 9, "tail", 1),
        "tail1": ((-29, 28, 0), (-42, 18, 0), 9, "tail", 2),
        "tail2": ((-42, 18, 0), (-51, 10, 0), 8, "tail", 3),
    } | quadruped_legs((30, 42, 9), (36, 2, 12), (-10, 38, 8), (-13, 2, 12), 9)


def kumo_bones():
    bones = {"root": ((-27, 16, 0), (21, 18, 0), 16, "root", 0)}
    feet = ((35, 2, 18), (16, 3, 33), (2, 4, 33), (-12, 7, 37))
    for side in (-1, 1):
        for i, (depth, height, width) in enumerate(feet):
            start = (20 - i * 7, 14, 8 * side)
            bones[f"leg{side}_{i}"] = (start, (depth, height, width * side), 6, "leg", side * (-1) ** i)
    return bones


def other_face_bones():
    return {
        "root": ((-4, 36, 0), (-4, 69, 0), 17, "root", 0),
        "head": ((6, 49, 0), (16, 70, 0), 14, "head", 0),
        "cloth": ((0, 40, 0), (7, 20, 6), 10, "tail", 2),
    }


def poppy_bones():
    return {
        "root": ((-3, 4, 0), (-3, 18, 0), 14, "root", 0),
        "stem": ((-4, 17, 0), (-11, 40, 0), 10, "tail", 2),
        "head": ((-5, 41, 0), (15, 57, 0), 17, "head", 0),
        "leaf1": ((-2, 18, 4), (7, 22, 22), 9, "claw", 1),
        "leaf-1": ((-2, 18, -4), (7, 17, -23), 9, "claw", -1),
    }


def yurei_bones():
    return {
        "root": ((-3, 37, 0), (-3, 78, 0), 14, "root", 0),
        "head": ((-1, 73, 0), (6, 87, 0), 10, "head", 0),
        "sleeve1": ((1, 66, 7), (10, 47, 10), 8, "claw", 1),
        "sleeve-1": ((1, 66, -7), (11, 44, -11), 8, "claw", -1),
        "hem": ((-3, 42, 0), (5, 11, 0), 11, "tail", 2),
        "hair": ((-8, 70, 0), (-15, 48, 0), 9, "tail", 1),
    }


def tomie_bones():
    return {
        "root": ((-2, 31, 0), (-2, 81, 0), 20, "root", 0),
        "head": ((5, 80, 0), (13, 104, 0), 17, "head", 0),
        "tail0": ((-10, 42, -10), (-24, 29, -22), 8, "tail", 1),
        "tail1": ((-24, 29, -22), (-33, 29, -42), 8, "tail", 2),
        "tail2": ((-33, 29, -42), (-36, 42, -63), 8, "tail", 3),
    } | four_limbs((0, 78, 22), (14, 41, 32), (-3, 43, 14), (6, 3, 30), 12, 11)


def naga_scout_bones():
    bones = {
        "root": ((0, 12, 0), (0, 68, 0), 16, "root", 0),
        "head": ((0, 71, 0), (6, 90, 0), 11, "head", 0),
        "arm1": ((2, 66, 11), (7, 51, 24), 8, "claw", 1),
        "arm-1": ((2, 68, -10), (9, 36, -21), 8, "claw", -1),
    }
    curve = [(6, 9, 0), (8, 8, -25), (-19, 8, -25), (-42, 8, -11),
             (-42, 8, 21), (-20, 8, 38), (13, 8, 25), (12, 8, -15), (-16, 12, -52)]
    for i, (a, b) in enumerate(zip(curve, curve[1:])):
        bones[f"tail{i}"] = (a, b, 9, "tail", i)
    return bones


def leech_bones():
    return {
        "root": ((-2, 7, 0), (13, 12, 0), 13, "root", 0),
        "head": ((8, 34, 0), (25, 37, 0), 11, "head", 0),
        "neck": ((13, 14, 0), (3, 32, 0), 10, "tail", 0),
        "tail0": ((0, 7, 0), (-16, 8, 0), 8, "tail", 2),
        "tail1": ((-16, 8, 0), (-29, 4, 0), 7, "tail", 3),
    }


def ape_bones():
    return {
        "root": ((-28, 61, 0), (18, 72, 0), 26, "root", 0),
        "head": ((20, 77, 0), (44, 86, 0), 15, "head", 0),
    } | quadruped_legs((22, 78, 22), (34, 3, 33), (-28, 54, 14), (-28, 3, 15), 13)


def badger_bones():
    return {
        "root": ((-13, 16, 0), (19, 18, 0), 12, "root", 0),
        "head": ((18, 15, 0), (31, 12, 0), 9, "head", 0),
        "tail": ((-15, 14, 0), (-31, 7, -8), 7, "tail", 1),
    } | quadruped_legs((17, 15, 6), (20, 1, 8), (-10, 16, 7), (-10, 1, 8), 6)


def crocodile_bones():
    return {
        "root": ((-14, 13, 0), (24, 16, 0), 16, "root", 0),
        "head": ((28, 14, 0), (53, 11, 0), 10, "head", 0),
        "tail0": ((-15, 11, 0), (-32, 8, 0), 9, "tail", 1),
        "tail1": ((-32, 8, 0), (-48, 6, -10), 8, "tail", 2),
        "tail2": ((-48, 6, -10), (-53, 4, -25), 7, "tail", 3),
        "tail3": ((-53, 4, -25), (-33, 3, -34), 7, "tail", 4),
    } | quadruped_legs((21, 11, 8), (33, 1, 14), (-12, 11, 9), (-14, 1, 15), 7)


def gaki_bones():
    return {
        "root": ((-4, 29, 0), (0, 57, 0), 14, "root", 0),
        "head": ((2, 59, 0), (12, 76, 0), 12, "head", 0),
    } | four_limbs((0, 55, 11), (11, 35, 22), (-2, 26, 9), (4, 3, 13), 8, 7)


def goblin_bones():
    return {
        "root": ((-3, 19, 0), (-3, 46, 0), 15, "root", 0),
        "head": ((0, 46, 0), (10, 63, 0), 16, "head", 0),
    } | four_limbs((0, 43, 16), (10, 18, 25), (-3, 19, 11), (8, 2, 17), 8, 9)


def dryad_bones():
    return {
        "root": ((-4, 4, 0), (-4, 51, 0), 14, "root", 0),
        "head": ((1, 57, 0), (4, 92, 0), 15, "head", 0),
        "branch1": ((-1, 57, 8), (8, 34, 22), 8, "claw", 1),
        "branch-1": ((-1, 57, -8), (8, 32, -24), 8, "claw", -1),
        "roots1": ((-2, 9, 4), (12, 3, 20), 8, "tail", 1),
        "roots-1": ((-2, 9, -4), (12, 3, -20), 8, "tail", 3),
    }


def shade_bones():
    return {
        "root": ((-2, 34, 0), (-2, 74, 0), 15, "root", 0),
        "head": ((0, 73, 0), (4, 94, 0), 12, "head", 0),
        "sleeve1": ((0, 70, 9), (8, 46, 21), 8, "claw", 1),
        "sleeve-1": ((0, 70, -9), (8, 46, -21), 8, "claw", -1),
        "hem1": ((-3, 46, 5), (-8, 15, 11), 9, "tail", 1),
        "hem-1": ((-3, 46, -5), (2, 18, -16), 9, "tail", 3),
    }


def snow_bear_bones():
    return {
        "root": ((-26, 49, 0), (25, 53, 0), 23, "root", 0),
        "head": ((26, 51, 0), (54, 34, 0), 16, "head", 0),
    } | quadruped_legs((25, 50, 11), (36, 2, 18), (-27, 51, 12), (-38, 2, 18), 14)


def empress_bones():
    return {
        "root": ((-3, 16, 0), (-3, 86, 0), 21, "root", 0),
        "head": ((0, 86, 0), (4, 115, 0), 12, "head", 0),
        "arm1": ((1, 85, 14), (8, 43, 25), 9, "claw", 1),
        "arm-1": ((1, 85, -14), (8, 43, -25), 9, "claw", -1),
        "cape1": ((-6, 60, 6), (-12, 10, 32), 12, "tail", 1),
        "cape-1": ((-6, 60, -6), (-12, 10, -32), 12, "tail", 3),
    }


def bird_bones():
    bones = {
        "root": ((-13, 52, 0), (13, 56, 0), 10, "root", 0),
        "head": ((16, 56, 0), (27, 58, 0), 9, "head", 0),
        "tail": ((-10, 48, 0), (-25, 40, 0), 8, "tail", 1),
    }
    for side in (-1, 1):
        bones[f"wing{side}"] = ((6, 57, 6 * side), (-5, 66, 41 * side), 10, "wing", side)
    return bones


def bat_bones():
    bones = {
        "root": ((-8, 48, 0), (8, 55, 0), 8, "root", 0),
        "head": ((5, 53, 0), (17, 62, 0), 9, "head", 0),
    }
    for side in (-1, 1):
        bones[f"wing{side}"] = ((3, 53, 5 * side), (-2, 60, 38 * side), 9, "wing", side)
    return bones


def fever_bones():
    return {
        "root": ((-4, 34, 4), (-4, 58, 0), 15, "root", 0),
        "head": ((3, 57, -7), (9, 72, -7), 14, "head", 0),
        "tail": ((-4, 41, 7), (-11, 25, 17), 9, "tail", 2),
    }


def fire_bones():
    return {
        "root": ((-4, 29, 0), (-4, 66, 0), 20, "root", 0),
        "head": ((0, 67, 0), (10, 91, 0), 16, "head", 0),
        "flame": ((-5, 34, 0), (8, 9, 6), 14, "tail", 1),
        "arm1": ((-1, 67, 18), (14, 39, 33), 11, "claw", 1),
        "arm-1": ((-1, 66, -18), (15, 33, -34), 11, "claw", -1),
    }


def akaname_bones():
    return {
        "root": ((-28, 37, 0), (12, 52, 0), 15, "root", 0),
        "head": ((13, 55, 0), (33, 53, 0), 14, "head", 0),
        "tongue0": ((34, 42, 0), (37, 26, 0), 8, "tail", 1),
        "tongue1": ((37, 26, 0), (48, 17, 0), 7, "tail", 2),
    } | quadruped_legs((8, 44, 11), (17, 2, 24), (-26, 30, 12), (-29, 2, 21), 9)


def blood_eel_bones():
    return {
        "root": ((-12, 11, 0), (16, 18, 0), 16, "root", 0),
        "head": ((13, 35, 0), (30, 38, 0), 12, "head", 0),
        "neck": ((-7, 27, 1), (13, 36, 0), 12, "tail", 1),
        "tail0": ((-19, 17, -8), (-26, 14, -22), 10, "tail", 2),
        "tail1": ((-26, 14, -22), (-11, 7, -32), 9, "tail", 3),
    }


def chucker_bones():
    return goblin_bones() | {"arm1": ((0, 44, 15), (16, 45, 25), 10, "claw", 1)}


def scaled_bones(layout, scale):
    return {name: (tuple(v * scale for v in a), tuple(v * scale for v in b), radius * scale, motion, phase)
            for name, (a, b, radius, motion, phase) in layout().items()}


def grub_bones():
    return {
        "root": ((-5, 9, 0), (13, 17, 0), 10, "root", 0),
        "head": ((15, 19, 0), (30, 17, 0), 9, "head", 0),
        "tail0": ((0, 8, 0), (-12, 7, 0), 8, "tail", 1),
        "tail1": ((-12, 7, 0), (-23, 6, 0), 7, "tail", 2),
        "tail2": ((-23, 6, 0), (-30, 7, 0), 5, "tail", 3),
    }


def stone_bones():
    return {
        "root": ((-3, 4, 0), (-6, 39, 0), 21, "root", 0),
        "head": ((9, 34, 0), (14, 53, 0), 14, "head", 0),
    }


def sea_eel_bones():
    pts = [(49, 34, 1), (31, 42, 0), (15, 48, 0), (0, 29, -3),
           (-20, 28, -4), (-34, 31, 0), (-50, 28, 7)]
    bones = {
        "head": (pts[1], pts[0], 10, "head", 0),
        "root": (pts[2], pts[3], 11, "root", 0),
    }
    for i, (a, b) in enumerate(zip(pts[3:], pts[4:])):
        bones[f"tail{i}"] = (a, b, 8, "tail", i)
    return bones


def wolf_rider_bones():
    return {
        "root": ((-18, 32, 0), (23, 43, 0), 14, "root", 0),
        "head": ((28, 37, 0), (49, 33, 0), 11, "head", 0),
        "tail0": ((-19, 42, 0), (-39, 38, 0), 10, "tail", 1),
        "tail1": ((-39, 38, 0), (-54, 49, 0), 11, "tail", 2),
        "rider": ((2, 48, 0), (6, 68, 0), 11, "root", 0),
        "rider_head": ((6, 63, 0), (10, 82, 0), 12, "head", 0),
        "arm1": ((8, 63, 7), (23, 61, 8), 8, "claw", 1),
        "arm-1": ((5, 62, -7), (12, 47, -10), 7, "claw", -1),
    } | quadruped_legs((25, 33, 8), (30, 1, 12), (-19, 35, 9), (-17, 1, 12), 9)


def ghul_bones():
    return {
        "root": ((-22, 44, 0), (9, 66, 0), 17, "root", 0),
        "head": ((13, 68, 0), (35, 64, 0), 12, "head", 0),
    } | four_limbs((7, 62, 12), (35, 23, 26), (-22, 45, 12), (-23, 3, 19), 10, 10)


def mujina_bones():
    return {
        "root": ((-3, 21, 0), (-3, 58, 0), 17, "root", 0),
        "head": ((4, 53, 0), (14, 70, 0), 15, "head", 0),
        "tail0": ((-12, 28, -5), (-24, 31, -10), 10, "tail", 1),
        "tail1": ((-24, 31, -10), (-38, 45, -18), 9, "tail", 2),
    } | four_limbs((0, 51, 10), (9, 31, 14), (-3, 18, 9), (4, 2, 11), 8, 7)


def shadowspawn_bones():
    return {
        "root": ((-15, 41, 0), (21, 47, 0), 17, "root", 0),
        "head": ((22, 42, 0), (48, 35, 0), 13, "head", 0),
        "tail0": ((-14, 36, 0), (-29, 25, 0), 8, "tail", 1),
        "tail1": ((-29, 25, 0), (-44, 19, 0), 8, "tail", 2),
        "tail2": ((-44, 19, 0), (-52, 36, 0), 8, "tail", 3),
    } | quadruped_legs((22, 40, 9), (37, 3, 14), (-14, 36, 11), (-14, 2, 15), 9)


def cage_rig(c, scene, frames):
    center = (0, 50, 0)
    rig = c.make_armature({"root": c.frame(center, (0, 51, 0), c.EX)})
    bone = rig.pose.bones["root"]
    rest = bone.bone.matrix_local
    pivot = Matrix.Translation(c.blender(center))
    for frame, (pose, i, count) in enumerate(frames):
        t = i / max(1, count - 1)
        beat = math.sin(math.pi * t)
        yaw = 5 * math.sin(math.tau * i / count)
        roll = 0
        x, lift = 0, 2 * beat
        if pose == "walk8":
            roll, lift = 16 * math.sin(math.tau * i / count), 10 * beat * beat
        elif pose.startswith("atk_"):
            roll, x, lift = 28 * beat, 19 * beat, 16 * beat * beat
        elif pose == "cast":
            yaw, lift = 20 * beat, 12 * beat
        elif pose == "hurt":
            roll, x = -12 * beat, -8 * beat
        elif pose == "collapse":
            roll, x = 65 * t, 9 * t
        orient = Matrix.Rotation(math.radians(roll), 4, "Y") @ Matrix.Rotation(math.radians(yaw), 4, "Z")
        transform = Matrix.Translation(c.blender((x, lift, 0))) @ pivot @ orient @ pivot.inverted()
        bone.matrix_basis = rest.inverted() @ transform @ rest
        for path in ("location", "rotation_quaternion", "scale"):
            bone.keyframe_insert(path, frame=frame, group=bone.name)
    scene.frame_start, scene.frame_end = 0, len(frames) - 1
    scene.frame_set(0)
    return rig


def stinger_plant_bones():
    return {
        "root": ((0, 5, 0), (0, 18, 0), 19, "root", 0),
        "head": ((0, 20, 0), (4, 81, 19), 15, "head", 0),
        "branch1": ((-5, 16, 7), (8, 53, 31), 12, "claw", 1),
        "branch-1": ((-5, 15, -9), (-3, 55, -27), 12, "claw", -1),
    }


def tanglevine_bones():
    return {
        "root": ((0, 5, 0), (0, 24, 0), 22, "root", 0),
        "head": ((-2, 24, 5), (10, 85, 32), 18, "head", 0),
        "branch1": ((-2, 20, 5), (-9, 56, 36), 13, "claw", 1),
        "branch-1": ((-4, 17, -4), (3, 56, -30), 14, "claw", -1),
    }


def paper_spirit_bones():
    return {
        "root": ((-2, 19, 0), (0, 41, 0), 13, "root", 0),
        "head": ((-2, 42, 0), (2, 80, 0), 19, "head", 0),
        "fold1": ((-2, 37, 6), (3, 34, 21), 7, "wing", 1),
        "fold-1": ((-2, 37, -6), (3, 34, -21), 7, "wing", -1),
        "paper_tail": ((0, 33, 0), (0, 10, 0), 9, "tail", 2),
    }


def wild_boar_bones():
    return {
        "root": ((-30, 33, 0), (24, 41, 0), 17, "root", 0),
        "head": ((19, 39, 0), (42, 15, 0), 13, "head", 0),
        "tail0": ((-35, 45, 0), (-47, 61, 0), 6, "tail", 1),
    } | quadruped_legs((19, 35, 12), (25, 1, 14), (-29, 37, 12), (-36, 1, 14), 9)


def wisp_bones():
    return {
        "root": ((17, 26, 0), (17, 55, 0), 19, "root", 0),
        "tail0": ((11, 49, 0), (-12, 52, 0), 11, "tail", 1),
        "tail1": ((-12, 52, 0), (-38, 73, 0), 8, "tail", 2),
    }


def berserker_bones():
    return {
        "root": ((0, 29, -5), (-1, 59, -5), 19, "root", 0),
        "head": ((2, 58, -5), (8, 79, -5), 16, "head", 0),
        "arm1": ((0, 62, 14), (13, 39, 22), 10, "claw", 1),
        "arm-1": ((0, 62, -25), (8, 29, -30), 11, "claw", -1),
        "leg1": ((0, 30, 9), (8, 2, 17), 11, "leg", -1),
        "leg-1": ((0, 30, -19), (8, 2, -31), 11, "leg", 1),
    }


def kommei_bones():
    return {
        "root": ((0, 31, 0), (0, 68, 0), 17, "root", 0),
        "head": ((0, 70, 0), (0, 95, 0), 16, "head", 0),
    } | four_limbs((0, 63, 13), (4, 35, 19), (0, 34, 9), (4, 2, 13), 8, 10)


def orochi_bones():
    bones = {"root": ((-13, 10, 0), (21, 15, 0), 23, "root", 0)}
    axes = (
        ((7, 24, 7), (12, 82, 22), 13),
        ((7, 23, 12), (10, 70, 39), 11),
        ((12, 19, 19), (6, 57, 56), 10),
        ((22, 12, 25), (6, 41, 65), 9),
    )
    for side in (-1, 1):
        for i, (base, tip, radius) in enumerate(axes):
            start = (base[0], base[1], base[2] * side)
            end = (tip[0], tip[1], tip[2] * side)
            bones[f"neck{side}_{i}"] = (start, end, radius, "tail", i * 2 + (side + 1) // 2)
    return bones


def akuma_bones():
    bones = {
        "root": ((-28, 47, 0), (-3, 56, 0), 22, "root", 0),
        "head": ((10, 55, 0), (40, 51, 0), 15, "head", 0),
    }
    for side in (-1, 1):
        bones[f"arm{side}"] = ((1, 53, 24 * side), (42, 7, 53 * side), 13, "claw", side)
        for i, (base, tip) in enumerate((
            ((-3, 33, 14), (24, 5, 28)),
            ((-24, 29, 14), (-6, 8, 32)),
        )):
            start = (base[0], base[1], base[2] * side)
            end = (tip[0], tip[1], tip[2] * side)
            bones[f"leg{side}_{i}"] = (start, end, 8, "leg", side * (-1) ** i)
    return bones


def skull_tide_bones():
    return {
        "root": ((-34, 9, 0), (26, 16, 0), 23, "root", 0),
        "curl": ((-22, 29, 0), (25, 59, 0), 22, "head", 0),
        "backwash": ((-30, 14, 0), (-59, 7, 0), 11, "tail", 3),
        "surge1": ((-13, 25, 27), (24, 42, 43), 17, "tail", 1),
        "surge-1": ((-13, 25, -27), (24, 42, -43), 17, "tail", 5),
    }


PROFILES = {
    "kappa": ("EP459", "beast", 2, 80, kappa_bones),
    "tide_crab": ("EP104", "crab", 1, 94, crab_bones),
    "tsuchigumo": ("EP161", "crawler", 1, 94, spider_bones),
    "goblin_warmonger": ("EP110", "goblin", 2, 75, warmonger_bones),
    "nezumi_warrior": ("EP101", "ratfolk", 2, 80, nezumi_bones),
    "boss_cellar_ogre": ("EP124", "ogre", 2, 108, cellar_ogre_bones),
    "boss_naga_champion": ("EP184", "naga", 2, 100, naga_champion_bones),
    "boss_tengu_red": ("EP158", "tengu", 2, 98, red_tengu_bones),
    "boss_red_oni": ("EP134", "demon", 2, 112, oni_bones),
    "boss_shelf_kami": ("EP132", "beast", 2, 86, shelf_kami_bones),
    "foe_ningyo": ("EP2618", "swimmer", 2, 80, ningyo_bones),
    "foe_nukekubi": ("EP2617", "spirit", 1, 68, nukekubi_bones),
    "foe_onibaba": ("EP2633", "demon", 2, 86, onibaba_bones),
    "mamushi": ("EP103", "serpent", 1, 61, mamushi_bones),
    "boss_troll": ("EP121", "ogre", 2, 115, troll_bones),
    "foe_aoizame": ("EP2602", "swimmer", 0, 92, shark_bones),
    "foe_hanemuri": ("EP2627", "flier", 1, 97, hanemuri_bones),
    "foe_ogre_hag": ("EP2628", "ogre", 2, 94, ogre_hag_bones),
    "boss_kuzushi": ("EP141", "demon", 2, 130, kuzushi_bones),
    "foe_free_ogre": ("EP2629", "ogre", 2, 108, cellar_ogre_bones),
    "foe_hyakuhei": ("EP2636", "crawler", 2, 112, hyakuhei_bones),
    "boss_nezumi_shaman": ("EP120", "ratfolk", 2, 90, shaman_bones),
    "boss_tsukakoro": ("EP125", "demon", 2, 100, cage_bones),
    "foe_tsuno": ("EP2634", "demon", 2, 106, tsuno_bones),
    "foe_zokujin_miner": ("EP2631", "ghoul", 2, 72, zokujin_miner_bones),
    "boss_hioninmaru": ("EP140", "demon", 2, 112, hioninmaru_bones),
    "boss_ianwa": ("EP136", "demon", 2, 112, ianwa_bones),
    "boss_regret": ("EP154", "demon", 2, 110, regret_bones),
    "boss_stolen_face": ("EP148", "spirit", 2, 75, stolen_face_bones),
    "foe_bakeneko": ("EP2605", "beast", 2, 55, bakeneko_bones),
    "foe_tiger": ("EP2610", "beast", 0, 110, tiger_bones),
    "foe_zokujin_hunter": ("EP2632", "ghoul", 2, 75, stonehunter_bones),
    "onikage": ("EP116", "beast", 2, 80, onikage_bones),
    "umibozu": ("EP442", "spirit", 2, 76, umibozu_bones),
    "boss_horror": ("EP188", "crawler", 1, 106, horror_bones),
    "boss_kansen_hana": ("EP146", "plant", 2, 94, kansen_bones),
    "boss_mine_guardian": ("EP152", "ogre", 2, 100, mine_guardian_bones),
    "boss_nashiko_time": ("EP192", "spirit", 2, 112, damned_time_bones),
    "cave_beetle": ("EP102", "crawler", 1, 72, beetle_bones),
    "giant_hornet": ("EP165", "flier", 1, 80, hornet_bones),
    "grey_wolf": ("EP170", "beast", 0, 105, wolf_bones),
    "kumo_brood": ("EP109", "crawler", 1, 76, kumo_bones),
    "other_face": ("EP119", "spirit", 2, 58, other_face_bones),
    "toothed_poppy": ("EP117", "plant", 2, 62, poppy_bones),
    "yurei": ("EP112", "spirit", 2, 76, yurei_bones),
    "boss_ashimoshi": ("EP139", "demon", 2, 108, oni_bones),
    "boss_ryozo_oni": ("EP186", "demon", 2, 112, oni_bones),
    "boss_tomie_tiger": ("EP182", "beast", 2, 108, tomie_bones),
    "naga_scout": ("EP107", "naga", 2, 92, naga_scout_bones),
    "tengu": ("EP167", "tengu", 2, 94, red_tengu_bones),
    "blood_leech": ("EP163", "serpent", 2, 45, leech_bones),
    "boss_okura": ("EP196", "demon", 2, 112, hioninmaru_bones),
    "foe_ape": ("EP2612", "beast", 2, 105, ape_bones),
    "foe_badger": ("EP2600", "beast", 0, 65, badger_bones),
    "foe_crocodile": ("EP2601", "beast", 0, 110, crocodile_bones),
    "gaki": ("EP160", "ghoul", 2, 79, gaki_bones),
    "goblin_anim": ("EP106", "goblin", 2, 66, goblin_bones),
    "lava_dryad": ("EP108", "plant", 2, 95, dryad_bones),
    "mieko_shadow": ("EP162", "spirit", 2, 84, shade_bones),
    "snow_bear": ("EP166", "beast", 0, 112, snow_bear_bones),
    "troll": ("EP113", "ogre", 2, 115, troll_bones),
    "ash_ghoul": ("EP169", "ghoul", 2, 82, gaki_bones),
    "boss_nashiko_true": ("EP194", "spirit", 2, 116, empress_bones),
    "carrion_crow": ("EP171", "flier", 1, 83, bird_bones),
    "cave_bats": ("EP111", "flier", 1, 77, bat_bones),
    "fear_shade": ("EP446", "spirit", 2, 84, shade_bones),
    "fever_spirit": ("EP449", "spirit", 2, 52, fever_bones),
    "fire_elemental": ("EP168", "spirit", 2, 84, fire_bones),
    "foe_aka_name": ("EP2615", "ghoul", 2, 68, akaname_bones),
    "foe_blood_eel": ("EP2614", "serpent", 2, 48, blood_eel_bones),
    "foe_goblin_chucker": ("EP2621", "goblin", 2, 66, chucker_bones),
    "foe_goblin_sneak": ("EP2620", "goblin", 2, 66, goblin_bones),
    "foe_heart_grubs": ("EP2624", "crawler", 0, 62, grub_bones),
    "foe_monkeys": ("EP2608", "beast", 2, 53, lambda: scaled_bones(ape_bones, .50)),
    "foe_muck_monster": ("EP2616", "spirit", 2, 82, lambda: scaled_bones(ape_bones, .78)),
    "guardian_stone": ("EP448", "relic", 2, 58, stone_bones),
    "oni_spawn": ("EP208", "demon", 2, 69, goblin_bones),
    "paddy_python": ("EP164", "serpent", 1, 72, lambda: scaled_bones(mamushi_bones, 1.15)),
    "sea_eel": ("EP441", "swimmer", 0, 101, sea_eel_bones),
    "wolfrider": ("EP436", "beast", 0, 112, wolf_rider_bones),
    "foe_ghul": ("EP2625", "ghoul", 2, 81, ghul_bones),
    "foe_mujina": ("EP2606", "beast", 2, 74, mujina_bones),
    "foe_shadowspawn": ("EP2635", "spirit", 0, 105, shadowspawn_bones),
    "foe_stinger_plant": ("EP2630", "plant", 2, 89, stinger_plant_bones),
    "foe_tanglevines": ("EP2619", "plant", 2, 91, tanglevine_bones),
    "paper_spirit": ("EP443", "spirit", 2, 70, paper_spirit_bones),
    "goblin_hat": ("EP100", "goblin", 2, 68, goblin_bones),
    "wild_boar": ("EP439", "beast", 0, 95, wild_boar_bones),
    "will_o_wisp": ("EP438", "spirit", 0, 78, wisp_bones),
    "foe_goblin_berserker": ("EP2626", "goblin", 2, 87, berserker_bones),
    "boss_kommei": ("EP123", "demon", 2, 107, kommei_bones),
    "boss_orochi": ("EP198", "serpent", 1, 145, orochi_bones),
    "foe_oni_no_akuma": ("EP2639", "crawler", 1, 128, akuma_bones),
    "foe_skull_tide": ("EP2638", "spirit", 1, 130, skull_tide_bones),
}


def main(root, model, out, creature):
    sys.path[:0] = [str(root / "tools/blender"), str(root / "tools")]
    import chara3d as c
    from chara3d_native import clearCaches, convertToPM, saveModelData, saveMotionData, savePolygonMesh
    from foe_batch import clips, creature_rig

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    bpy.ops.import_scene.gltf(filepath=str(model))
    meshes = [o for o in scene.objects if o.type == "MESH"]
    if len(meshes) != 1 or len(meshes[0].data.materials) != 1:
        raise ValueError("Expected one mesh and one textured material")
    obj, = meshes
    yaw = {
        "foe_ningyo": 0, "foe_tiger": 0, "foe_aoizame": math.pi, "onikage": math.pi,
        "mamushi": math.pi / 3, "grey_wolf": math.pi, "blood_leech": 0,
        "foe_badger": math.pi, "foe_crocodile": math.pi, "snow_bear": 0, "ash_ghoul": 0,
        "foe_aka_name": 0, "foe_blood_eel": math.pi * .72,
        "foe_heart_grubs": math.pi, "foe_monkeys": 0,
        "paddy_python": math.pi / 3, "sea_eel": math.pi,
        "wolfrider": 0, "foe_ghul": 0, "foe_shadowspawn": math.pi, "wild_boar": math.pi,
        "will_o_wisp": math.pi,
        "boss_kommei": math.pi * .56,
        "foe_skull_tide": 0,
    }.get(creature, math.pi / 2)
    obj.data.transform(Matrix.Rotation(yaw, 4, "Z") @ obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    vertices = np.array([list(v.co) for v in obj.data.vertices])
    lo, hi = vertices.min(axis=0), vertices.max(axis=0)
    center = (lo + hi) / 2
    centered = {
        "nezumi_warrior": (.56, .78),
        "boss_naga_champion": (.56, .78),
        "boss_nezumi_shaman": (.56, .78),
        "foe_tsuno": (.56, .78),
        "boss_ianwa": (.56, .78),
        "foe_bakeneko": (.29, .53),
        "foe_zokujin_hunter": (.38, .63),
        "boss_tomie_tiger": (.53, .78),
        "naga_scout": (.51, .75),
        "foe_mujina": (.48, .70),
    }
    if creature in centered:
        # Center on the torso, independent of the tail silhouette.
        level = (vertices[:, 2] - lo[2]) / (hi[2] - lo[2])
        low, high = centered[creature]
        center[:2] = np.median(vertices[(level > low) & (level < high), :2], axis=0)
    center[2] = lo[2]
    ep, recipe, size_axis, size, joint_layout = PROFILES[creature]
    scale = size / (hi[size_axis] - lo[size_axis])
    bones = joint_layout()
    lift = {
        "foe_ningyo": 10, "foe_nukekubi": 18, "foe_aoizame": 25,
        "foe_hanemuri": 14, "boss_stolen_face": 13,
        "boss_nashiko_time": 7, "giant_hornet": 29, "other_face": 18, "yurei": 11,
        "mieko_shadow": 11,
        "carrion_crow": 32, "cave_bats": 36,
        "fear_shade": 11, "fever_spirit": 22,
        "fire_elemental": 7,
        "sea_eel": 20,
        "paper_spirit": 10,
        "will_o_wisp": 16,
    }.get(creature, 0)
    obj.data.transform(Matrix.Translation((0, 0, lift)) @ Matrix.Scale(scale, 4) @ Matrix.Translation(-center))
    obj.data.update()
    points = np.array([(v.co.x, v.co.z, -v.co.y) for v in obj.data.vertices])
    depth, height, width = points.T
    # Carapaces stay rigid while the limbs move.
    if creature == "kappa":
        shell = (depth < -8) & (height > 28) & (height < 64)
    elif creature == "tide_crab":
        shell = (depth < 15) & (height > 16) & (np.abs(width) < 25)
    elif creature == "tsuchigumo":
        shell = (np.abs(width) < 9) | ((depth < 7) & (np.abs(width) < 23))
    elif creature == "boss_horror":
        shell = (height > 20) & (np.abs(width) < 23)
    elif creature == "cave_beetle":
        shell = (height > 6) & (depth < 15) & (np.abs(width) < 16)
    elif creature == "kumo_brood":
        shell = (np.abs(width) < 8) | ((depth < 2) & (np.abs(width) < 18))
    elif creature == "boss_orochi":
        shell = (height < 14) | ((height < 22) & (depth < 8))
    elif creature == "foe_oni_no_akuma":
        shell = (height > 48) & (depth < 7) & (np.abs(width) < 29)
    elif creature == "foe_skull_tide":
        shell = (height < 6) & (np.abs(width) < 46)
    else:
        shell = np.zeros(len(points), dtype=bool)
    add_weights(obj, points, bones, shell)
    held_weapon = {
        "goblin_warmonger": (width > 27) & (height < 20),
        "boss_naga_champion": (width > 30) & (height > 28) & (depth > -20),
        "boss_tengu_red": (width > 26) & (depth > 14),
        "foe_onibaba": (width > 20) & (height < 35) & (depth > 5),
        "foe_hyakuhei": (width > 40) & (depth > 15) & (height < 73),
        "boss_nezumi_shaman": (width > 19) & (depth > -9) & (height > 2),
        "foe_tsuno": (width > 28) & (height < 46) & (depth > 0),
        "foe_zokujin_miner": (width > 21) & (depth > 3) & (height < 33),
        "foe_zokujin_hunter": (width > 18) & (depth > 5) & (height > 2),
        "naga_scout": (width > 17) & (depth > 3) & (height > 21),
        "goblin_anim": (width > 18) & (depth > 8) & (height < 27),
        "foe_goblin_chucker": (width > 18) & (depth > 7) & (height > 36),
        "foe_goblin_sneak": (width > 19) & (depth > 7) & (height < 39),
        "oni_spawn": (width > 21) & (height < 29) & (depth > 3),
        "wolfrider": (depth > 21) & (height > 62),
    }.get(creature)
    if creature == "foe_goblin_berserker":
        held_weapon = distances(points, (-31, 17, -41), (25, 45, 37)) < 6
    if held_weapon is not None:
        weapon_vertices = np.flatnonzero(held_weapon).tolist()
        for group in obj.vertex_groups:
            group.remove(weapon_vertices)
        obj.vertex_groups["arm1"].add(weapon_vertices, 1.0, "REPLACE")
    frames, _ = clips("fist")
    joints = {name: (a, motion, phase) for name, (a, _, _, motion, phase) in bones.items()}
    rig = cage_rig(c, scene, frames) if creature == "boss_tsukakoro" else creature_rig(c, scene, frames, joints, recipe)
    rig.name = creature
    rig.animation_data.action.name = f"{creature} battle"
    obj.name = f"{creature} textured mesh"
    obj.parent = rig
    modifier = obj.modifiers.new("Creature skin", "ARMATURE")
    modifier.object = rig

    tex = out / "tex"
    tex.mkdir(parents=True, exist_ok=True)
    mat = obj.data.materials[0]
    shader = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    base = shader.inputs["Base Color"].links[0].from_node.image
    base_path = tex / f"{ep.lower()}_hunyuan_color.png"
    base.filepath_raw = str(base_path)
    base.file_format = "PNG"
    base.save()
    base.filepath = str(base_path)
    shader.inputs["Metallic"].default_value = 0
    shader.inputs["Roughness"].default_value = .75
    normal_path = tex / "hunyuan_flat_normal.png"
    normal_image = bpy.data.images.new("Neutral tangent normal", 4, 4, alpha=False)
    normal_image.colorspace_settings.name = "Non-Color"
    normal_image.pixels[:] = [.5, .5, 1., 1.] * 16
    normal_image.filepath_raw = str(normal_path)
    normal_image.save()
    normal = mat.node_tree.nodes.new("ShaderNodeNormalMap")
    normal_tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    normal_tex.image = normal_image
    mat.node_tree.links.new(normal_tex.outputs["Color"], normal.inputs["Color"])
    mat.node_tree.links.new(normal.outputs["Normal"], shader.inputs["Normal"])

    clearCaches()
    data = convertToPM(scene, obj, {"export_mesh": True, "export_anime": True})
    if set(data.wmapname) != bones.keys():
        raise RuntimeError(f"Incomplete exported weights: {data.wmapname}")
    pad = np.array((12, 8, 12))
    pos = points * (1, 1, -1)
    data.aabb = [*(pos.min(axis=0) - pad), *(pos.max(axis=0) + pad)]
    saveModelData(data, str(out / f"{ep}.mdl"))
    saveMotionData(data.mot, str(out / f"{ep}.mot"))
    savePolygonMesh(data, str(out / f"{ep}.pm"), ep, ep, None)
    pm = out / f"{ep}.pm"
    descriptor = pm.read_text(encoding="utf8")
    color_export_name = base_path.stem + "_srgb.png"
    if color_export_name in descriptor:
        base_path.replace(tex / color_export_name)
        base.filepath = str(tex / color_export_name)
    for name in (line.split('"')[1] for line in descriptor.splitlines() if 'texture' in line and '"' in line):
        if not (out / name).is_file():
            raise RuntimeError(f"Missing native material texture {name}")

    # Make clip boundaries available to GLB viewers as individually named animations.
    action = rig.animation_data.action
    for clip in clips("fist")[1]:
        if clip["id"] not in {"stand", "fight", "walk", "attack", "magic", "damage", "guard", "dead"}:
            continue
        track = rig.animation_data.nla_tracks.new()
        track.name = clip["id"]
        strip = track.strips.new(clip["id"], 0, action)
        strip.action_frame_start = clip["st"]
        strip.action_frame_end = clip["en"]
        strip.frame_start = 0
        strip.frame_end = clip["en"] - clip["st"]
    rig.animation_data.action = None
    bpy.ops.export_scene.gltf(filepath=str(out / f"{creature}_animated.glb"), export_animation_mode="NLA_TRACKS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("creature", choices=PROFILES)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    main(args.root, args.model, args.out, args.creature)
