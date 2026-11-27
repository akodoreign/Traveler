"""Build regional cave scenery in an extracted pack overlay."""

from pathlib import Path
import shutil
import sys
from copy import copy

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter, label, map_coordinates

import build_river_lion_caves as branch
import build_yasuki_coast as coast
import build_zumiki_ice as ice
import export_coast
import regional_cave_revisit


def pool_regions(water):
    zones, count = label(water)
    regions = []
    for zone in range(1, count + 1):
        zz, xx = np.where(zones == zone)
        region = [max(0, int(xx.min()) - 4), max(0, int(zz.min()) - 4),
                  min(water.shape[1], int(xx.max()) + 5),
                  min(water.shape[0], int(zz.max()) + 5)]
        while True:
            overlap = next((r for r in regions if region[0] < r[2] and r[0] < region[2]
                            and region[1] < r[3] and r[1] < region[3]), None)
            if overlap is None:
                break
            regions.remove(overlap)
            region = [min(region[0], overlap[0]), min(region[1], overlap[1]),
                      max(region[2], overlap[2]), max(region[3], overlap[3])]
        regions.append(region)
    return regions


def rounded_water(ground, liquid, water, world, regions, floor_material, water_material):
    smooth = gaussian_filter(water.astype(float), .9)
    for x0, z0, x1, z1 in regions:
        xs = np.linspace(x0, x1, (x1 - x0) * 4 + 1)
        zs = np.linspace(z0, z1, (z1 - z0) * 4 + 1)
        xx, zz = np.meshgrid(xs, zs)
        depth = map_coordinates(smooth, [zz - .5, xx - .5], order=1, mode="nearest")
        heights = 1.519 - .72 * depth
        heights[[0, -1], :] = 1.519
        heights[:, [0, -1]] = 1.519
        for z in range(len(zs) - 1):
            for x in range(len(xs) - 1):
                points = [(xs[a] * .5, zs[b] * .5, heights[b, a])
                          for b, a in ((z, x), (z, x + 1), (z + 1, x + 1), (z + 1, x))]
                ground.quad(points, [(a / (world.w * .5), 1. - b / (world.d * .5))
                                     for a, b, _ in points], floor_material)
        points = [(x0 * .5, z0 * .5, 1.079), (x1 * .5, z0 * .5, 1.079),
                  (x1 * .5, z1 * .5, 1.079), (x0 * .5, z1 * .5, 1.079)]
        liquid.quad(points, [(x / 4.7, z / 4.7) for x, z, _ in points], water_material)


def rounded_rock(mesh, world, stone, floor):
    z, x = np.indices(stone.shape) * .5
    height = gaussian_filter(coast.rock_heights(world, stone, floor), .85)
    _, nearest = distance_transform_edt(stone, return_indices=True)
    rows = np.indices(stone.shape)[0]
    rear = gaussian_filter((rows >= nearest[0]).astype(float), 1.5)
    height = np.minimum(height, floor + .7 + rear * 8.)
    height[~stone] = floor
    visible = height > floor + .024
    for r, c in np.argwhere(visible[:-1, :-1] | visible[1:, :-1] |
                            visible[1:, 1:] | visible[:-1, 1:]):
        corners = [(x[a, b] + .25, z[a, b] + .25, height[a, b])
                   for a, b in ((r, c), (r, c + 1), (r + 1, c + 1), (r + 1, c))]
        style = coast.WALL if np.mean([p[2] for p in corners]) < floor + .47 else coast.STONE
        coast.face(mesh, corners, style, 3.55)


def build(overlay, profile):
    overlay = Path(overlay).resolve()
    profile = Path(profile).resolve()
    if profile == (regional_cave_revisit.ROOT / "_tools" / "rpgcobo-tool").resolve():
        raise ValueError("Use an isolated profile")
    stage = overlay / "resource" / "native_environment"
    destination = profile / "project" / "resource" / "native_environment"
    _, _, candidate, _, _ = regional_cave_revisit.variant()
    old_stage, old_export = export_coast.STAGE, export_coast.export
    old_branch_stage, old_ice_stage = branch.STAGE, ice.STAGE
    old_branch_rock, old_ice_rock = branch.faceted_rock, ice.faceted_rock
    old_branch_mesh, old_ice_mesh = branch.world_mesh, ice.world_mesh
    old_branch_export, old_ice_export = branch.export, ice.export
    water_geometry = {}
    rock_faces = {}

    def smooth_export(name, geom, maps, **kwargs):
        if name in water_geometry:
            geom = water_geometry[name]
        if name in rock_faces:
            start, end = rock_faces[name]
            material = ice.MID if name == "m485_zumiki_ice" else (
                branch.JADE if name == "m482_branch_landscape" else branch.RUSSET)
            geom.materials[start:end] = [material] * (end - start)
        kwargs["smooth_materials"] = (branch.JADE, branch.RUSSET, branch.SEAM,
                                       branch.DARK, ice.BLUE, ice.MID, ice.SHADE)
        old_export(name, geom, maps, **kwargs)

    def mesh_with_rounded_water(gm, dry, styles):
        water = world.blk == gm.WATER
        if world.mid == "M482":
            zz, xx = np.indices(water.shape)
            channel = 82.3 + 2.8 * np.sin(zz * .094)
            water |= (abs(xx - channel) < 2.25 + .63 * np.cos(zz * .21)) & (zz > 13) & (zz < 57)
        if not water.any():
            return old_branch_mesh(gm, dry, styles)
        regions = pool_regions(water)
        ground_world = copy(dry)
        ground_world.blk = dry.blk.copy()
        for x0, z0, x1, z1 in regions:
            ground_world.blk[z0:z1, x0:x1] = 0
        ground = old_branch_mesh(gm, ground_world, styles)
        clean = export_coast.Geometry()
        for face, uv, material in zip(ground.faces, ground.uvs, ground.materials):
            points = [ground.vertices[i] for i in face]
            p = np.asarray(points)
            wall = np.ptp(p[:, 2]) > .01 and p[:, 2].max() < 1.54
            seam = False
            if wall:
                for x0, z0, x1, z1 in regions:
                    vertical_x = (np.ptp(p[:, 0]) < .001 and
                                  min(abs(p[0, 0] - x0 * .5), abs(p[0, 0] - x1 * .5)) < .03 and
                                  p[:, 1].max() >= z0 * .5 and p[:, 1].min() <= z1 * .5)
                    vertical_z = (np.ptp(p[:, 1]) < .001 and
                                  min(abs(p[0, 1] - z0 * .5), abs(p[0, 1] - z1 * .5)) < .03 and
                                  p[:, 0].max() >= x0 * .5 and p[:, 0].min() <= x1 * .5)
                    if vertical_x or vertical_z:
                        seam = True
                        break
            if not seam:
                clean.quad(points, uv, material)
        ground = clean
        liquid = export_coast.Geometry()
        floor_material = "zumiki_frost_walk_atlas" if world.mid == "M485" else f"{world.mid.lower()}_branch_cave_floor"
        water_material = ice.WATER if world.mid == "M485" else branch.STREAM
        rounded_water(ground, liquid, water, world, regions, floor_material, water_material)
        name = f"{world.mid.lower()}_zumiki_water" if world.mid == "M485" else f"{world.mid.lower()}_branch_water"
        water_geometry[name] = liquid
        return ground

    export_coast.STAGE = branch.STAGE = ice.STAGE = stage
    def rock_with_span(mesh, shell, stone, floor):
        start = len(mesh.faces)
        rounded_rock(mesh, shell, stone, floor)
        terrain = "m485_zumiki_ice" if world.mid == "M485" else f"{world.mid.lower()}_branch_landscape"
        rock_faces[terrain] = (start, len(mesh.faces))

    branch.faceted_rock = ice.faceted_rock = rock_with_span
    branch.world_mesh = ice.world_mesh = mesh_with_rounded_water
    branch.export = ice.export = smooth_export
    try:
        for mid in regional_cave_revisit.MAPS:
            world, _ = candidate.make(mid)
            if mid == "M485":
                terrain, _, _ = ice.landscape(candidate, world)
                atlas = "zumiki_frost_walk_atlas.png"
            else:
                terrain, _, _ = branch.scenery(candidate, world)
                atlas = f"{mid.lower()}_branch_cave_floor.png"
            water_name = "m485_zumiki_water" if mid == "M485" else "m482_branch_water" if mid == "M482" else None
            files = [terrain + ".mdl", terrain + ".pm", "tex/" + atlas]
            if water_name:
                files.extend((water_name + ".mdl", water_name + ".pm"))
            for name in files:
                source = stage / name
                target = destination / name
                if not target.parent.is_dir():
                    raise ValueError(f"Missing preview asset directory: {target.parent}")
                shutil.copyfile(source, target)
    finally:
        export_coast.STAGE = old_stage
        branch.STAGE, ice.STAGE = old_branch_stage, old_ice_stage
        branch.faceted_rock, ice.faceted_rock = old_branch_rock, old_ice_rock
        branch.world_mesh, ice.world_mesh = old_branch_mesh, old_ice_mesh
        branch.export, ice.export = old_branch_export, old_ice_export


if __name__ == "__main__":
    build(*sys.argv[1:3])
