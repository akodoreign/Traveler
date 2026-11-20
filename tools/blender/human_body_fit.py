"""Shared rest-space deformation for a body and the garments fitted to it."""
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Build:
    """Relative shape controls. Positive values add volume."""

    muscle: float = 0
    weight: float = 0
    chest: float = 0


def garment_regions(weights):
    result = []
    for per_bone in weights:
        arm = sum(value for name, value in per_bone.items() if name.startswith(("upper", "fore", "hand")))
        leg = sum(value for name, value in per_bone.items() if name.startswith(("thigh", "shin", "foot")))
        result.append((1 - arm - leg, arm, leg))
    return np.asarray(result)


def fit_skin(skin, controls):
    """Apply a body build to a weighted garment before projecting its decals."""
    skin.verts = reshape(skin.verts, garment_regions(skin.weights), Build(**controls)).tolist()


def reshape(points, regions, build):
    """Fit clothing and skin together in canonical X-forward, Y-up space.

    Regions supply each vertex's local limb or torso blend. Scaling stature is
    an assembly transform so shoes, head, and equipped gear move together.
    """
    points = np.asarray(points, dtype=float)
    depth, height, lateral = points.T
    torso, arms, legs = np.asarray(regions).T
    abs_width = np.abs(lateral)
    side = np.sign(lateral)
    arm_center = np.interp(height, (54, 62, 77, 93), (13.4, 13.2, 12.5, 11.5))
    leg_center = np.interp(height, (0, 33, 59), (5.5, 5.5, 5.2))
    center = side * (arms * arm_center + legs * leg_center)

    abdomen = np.exp(-((height - 69) / 10) ** 2)
    upper_body = np.exp(-((height - 87) / 9) ** 2)
    limb_mass = arms * np.exp(-((height - 83) / 9) ** 2) + legs * np.exp(-((height - 46) / 14) ** 2)
    shoulder = torso * upper_body * np.clip((abs_width - 3) / 7, 0, 1)
    mass = build.weight * (.12 * torso + .11 * torso * abdomen + .15 * arms + .15 * legs)
    strength = build.muscle * (.12 * upper_body * torso + .21 * limb_mass + .14 * shoulder)

    neck_attenuation = np.clip((98 - height) / 5, 0, 1)
    feet_attenuation = np.clip((height - 3) / 5, 0, 1)
    amplitude = neck_attenuation * feet_attenuation
    chest_zone = torso * np.exp(-((height - 85) / 5.8) ** 2) * np.clip((depth + .4) / 4.5, 0, 1)
    chest_zone *= np.exp(-((abs_width - 3.7) / 5.8) ** 2)

    adjusted = points.copy()
    adjusted[:, 0] += amplitude * (depth * (mass + .85 * strength) + 2.9 * build.chest * chest_zone)
    adjusted[:, 2] += amplitude * (lateral - center) * (mass + strength)
    return adjusted


PREVIEWS = {
    "musculature": Build(muscle=.8),
    "weight": Build(weight=.8),
    "chest_volume": Build(chest=.75),
}
