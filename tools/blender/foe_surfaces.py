"""Tileable painted color and tangent-space relief for native battle models."""

import math

import bpy
import numpy as np

from anime_head import write_lock_uv


# Tile size in model units, roughness, metallic, and relief strength.
SURFACES = {
    "cloth": (12, .84, 0, .055), "skin": (19, .72, 0, .046),
    "fur": (17, .88, 0, .074), "feather": (25, .76, 0, .087),
    "scale": (21, .67, 0, .105), "shell": (25, .59, .04, .098),
    "bark": (24, .9, 0, .115), "stone": (25, .87, 0, .105),
    "metal": (17, .46, .48, .041), "spirit": (32, .73, 0, .021),
    "detail": (16, .61, 0, .02),
}
CREATURE_SURFACE = {
    "ratfolk": "fur", "beast": "fur", "tengu": "feather", "flier": "feather",
    "serpent": "scale", "naga": "scale", "swimmer": "scale", "crab": "shell",
    "crawler": "shell", "plant": "bark", "spirit": "spirit", "relic": "stone",
}


def relief(name, x, y):
    tau = math.tau
    grain = (.55 * np.sin(tau * (5*x + 3*y)) * np.cos(tau * (7*x - 8*y))
             + .45 * np.sin(tau * (13*x + 11*y)))
    curl = np.sin(tau * y) * .12 + np.sin(tau * (x + y)) * .06
    if name == "cloth":
        u, v = np.cos(tau * 9*x), np.cos(tau * 9*y)
        return .42 * (u + v) + .23 * u*v + .13 * grain
    if name in ("scale", "shell"):
        rows = 6 if name == "scale" else 4
        row = y * rows
        u = x * 5 + np.floor(row) * .5
        v = row % 1
        edge = np.cos(tau * u) * .19
        cell = np.sin(math.pi * v) ** 2
        return cell * (.53 + edge) - .24 * np.exp(-90 * np.minimum(v, 1-v)**2) + .12 * grain
    if name in ("fur", "feather", "bark", "metal"):
        count = {"fur": 11, "feather": 5, "bark": 7, "metal": 17}[name]
        fibers = np.sin(tau * (count * (x + curl) + y))
        if name == "feather":
            fibers *= .67 + .33 * np.cos(tau * (5*y + .45 * np.cos(tau * count*x)))
        return .65 * fibers + .26 * grain
    broad = np.sin(tau * (2*x + y)) * np.cos(tau * (x - 3*y))
    return .54 * broad + .35 * grain


def image_from_pixels(path, rgb):
    size = rgb.shape[0]
    image = bpy.data.images.new(path.stem, width=size, height=size, alpha=False)
    image.colorspace_settings.name = "Non-Color"
    image.filepath_raw = str(path)
    image.file_format = "PNG"
    rgba = np.ones((size, size, 4), dtype=np.float32)
    rgba[:, :, :3] = rgb
    image.pixels.foreach_set(rgba.ravel())
    image.save()
    return image


def make_textures(folder):
    folder.mkdir(exist_ok=True)
    coords = (np.arange(128) + .5) / 128
    x, y = np.meshgrid(coords, coords)
    textures = {}
    for name, (_, _, _, strength) in SURFACES.items():
        height = relief(name, x, y)
        color = np.clip(.89 + height * (.16 if name in ("cloth", "fur", "bark", "scale") else .11), .68, 1)
        dx = (np.roll(height, -1, axis=1) - np.roll(height, 1, axis=1)) * 24 * strength
        dy = (np.roll(height, -1, axis=0) - np.roll(height, 1, axis=0)) * 24 * strength
        normal = np.stack((-dx, -dy, np.ones_like(dx)), axis=-1)
        normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
        textures[name] = (
            image_from_pixels(folder / f"foe_{name}_color.png", color[:, :, None]),
            image_from_pixels(folder / f"foe_{name}_normal.png", normal * .5 + .5),
        )
    return textures


class FoeSurface:
    def __init__(self, item, textures):
        self.item, self.textures = item, textures
        self.material_roles = item['recipe'] == 'human'

    def kind(self, rgb):
        source, recipe = self.item["source"], self.item["recipe"]
        if rgb in ((222, 209, 157), (249, 167, 66)):
            return "detail"
        if recipe == "human":
            spec = self.item["spec"]
            roles = {"skin": "skin", "hair": "fur", "armor": "metal", "helm": "metal",
                     "mask_col": "cloth", "top": "cloth", "lower": "cloth",
                     "cloth": "cloth", "accent": "cloth"}
            swatches = [(spec[key], name) for key, name in roles.items()
                        if isinstance(spec.get(key), (tuple, list)) and len(spec[key]) == 3]
            if swatches:
                return min(swatches, key=lambda pair: sum((a-b)**2 for a, b in zip(rgb, pair[0])))[1]
            return "cloth"
        if recipe == "flier":
            return "shell" if "hornet" in source else "fur" if "bat" in source else "feather"
        if recipe == "beast" and any(word in source for word in ("crocodile", "kappa")):
            return "scale"
        if recipe == "relic" and any(word in source for word in ("keg", "bridge", "lantern")):
            return "bark"
        return CREATURE_SURFACE.get(recipe, "skin")

    def apply(self, mesh, uv_layer, materials):
        tiles = []
        for mat in materials:
            rgb = tuple(bytes.fromhex(mat.name[1:7]))
            hair = self.material_roles and "_hair" in mat.name
            kind = "fur" if hair else self.kind(rgb)
            tile, roughness, metal, _ = SURFACES[kind]
            tiles.append(tile)
            nodes, links = mat.node_tree.nodes, mat.node_tree.links
            bsdf = nodes["Principled BSDF"]
            bsdf.inputs["Roughness"].default_value = roughness
            bsdf.inputs["Metallic"].default_value = metal
            color, normal = (nodes.new("ShaderNodeTexImage") for _ in range(2))
            color.image, normal.image = self.textures[kind]
            if hair:
                color.interpolation = normal.interpolation = "Closest"
            bump = nodes.new("ShaderNodeNormalMap")
            links.new(color.outputs["Color"], bsdf.inputs["Base Color"])
            links.new(normal.outputs["Color"], bump.inputs["Color"])
            links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        lock_uv = mesh.attributes.get("rt_lock_uv")
        for face in mesh.polygons:
            if write_lock_uv(mesh, face, uv_layer, lock_uv):
                continue
            axis = max(range(3), key=lambda i: abs(face.normal[i]))
            u, v = (axis + 1) % 3, (axis + 2) % 3
            sign = 1 if face.normal[axis] >= 0 else -1
            tile = tiles[face.material_index]
            for index in face.loop_indices:
                point = mesh.vertices[mesh.loops[index].vertex_index].co
                uv_layer.data[index].uv = sign * point[u] / tile, point[v] / tile

    def restore_tints(self, data, materials):
        from blender_rpgcobo.pm_convert import vec3col

        tints = {mat.name: vec3col(mat.diffuse_color) for mat in materials}
        for face in data.face:
            face.mate.basecol = tints[face.mate.name]
