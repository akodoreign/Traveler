"""Painted strand, weave, and metal detail for native head meshes."""

import math

import numpy as np

from foe_surfaces import image_from_pixels
from anime_head import write_lock_uv


# Repeat size in model units, roughness, metallic, height amplitude.
SURFACES = {
    "hair": (17., .68, 0., .069),
    "iron": (17., .54, .28, .066),
    "lacquer": (19., .44, .08, .045),
    "straw": (14., .86, 0., .100),
    "linen": (13., .84, 0., .084),
}
HAT_SURFACE = {"band": "linen", "champion_band": "linen", "eboshi": "linen", "straw": "straw",
               "jingasa": "lacquer", "guard": "iron", "scout": "lacquer", "kabuto": "iron", "legion": "iron"}


def height_field(role, u, v):
    tau = math.tau
    grain = np.sin(tau * (13*u + 11*v)) * np.cos(tau * (9*u - 15*v))
    if role == "hair":
        flow = u + .029 * np.sin(tau * v) + .013 * np.sin(tau * (2*v + u))
        locks = np.cos(tau * 4 * flow)
        strands = np.cos(tau * (17 * flow + .16 * locks))
        return .52 * locks + .31 * strands + .12 * np.sin(tau * (27 * flow + v))
    if role == "straw":
        warp, weft = np.cos(tau * 10*u), np.cos(tau * 7*v)
        return .5 * warp + .45 * weft + .4 * warp * weft + .12 * grain
    if role == "linen":
        warp, weft = np.cos(tau * 9*u), np.cos(tau * 9*v)
        return .38 * (warp + weft) + .32 * warp * weft + .16 * grain
    pits = np.cos(tau * (5*u + v)) * np.cos(tau * (u - 7*v))
    scratches = np.sin(tau * (16*u + 3*v + .13*np.sin(tau * 5*v)))
    if role == "iron":
        return .39 * grain + .29 * scratches - .47 * np.maximum(0, pits) ** 6
    return .57 * np.cos(tau * (4*u + 2*v)) + .18 * scratches - .17 * np.maximum(0, pits) ** 7


def make_textures(folder, roles, color_maps=True):
    folder.mkdir(parents=True, exist_ok=True)
    textures = {}
    for role in sorted(roles):
        size = 64 if role == "hair" else 128
        samples = (np.arange(size) + .5) / size
        u, v = np.meshgrid(samples, samples)
        height = height_field(role, u, v)
        strength = SURFACES[role][3]
        dx = (np.roll(height, -1, axis=1) - np.roll(height, 1, axis=1)) * 25 * strength
        dy = (np.roll(height, -1, axis=0) - np.roll(height, 1, axis=0)) * 25 * strength
        normal = np.stack((-dx, -dy, np.ones_like(dx)), axis=-1)
        normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
        color = None
        if color_maps:
            # Use clustered values on the 64px hair map. The runtime light
            # ramp supplies the larger shadow shapes as the actor turns.
            if role == "hair":
                tint = np.select((height < -.27, height > .25), (.72, 1.), default=.87)
            else:
                tint = .87 + .16 * height
            color = image_from_pixels(folder / f"head_{role}_color.png", np.clip(tint[:, :, None], .58, 1))
        textures[role] = (color, image_from_pixels(folder / f"head_{role}_normal.png", normal * .5 + .5))
    return textures


class HeadSurface:
    def __init__(self, textures, hat=None):
        self.textures = textures
        self.hat = HAT_SURFACE[hat] if hat else None
        self.material_roles = hat is None

    def apply(self, mesh, color_uv, materials):
        # Equipped items use UV0 to sample their wearer palette and UV1 for surface relief.
        detail_uv = mesh.uv_layers.new(name="HeadDetail") if self.hat else color_uv
        roles = []
        for mat in materials:
            role = self.hat or mat.name.partition("_")[2].split(".")[0]
            roles.append(role)
            if role not in self.textures:
                continue
            _, roughness, metallic, _ = SURFACES[role]
            color, normal = self.textures[role]
            nodes, links = mat.node_tree.nodes, mat.node_tree.links
            bsdf = nodes["Principled BSDF"]
            bsdf.inputs["Roughness"].default_value = roughness
            bsdf.inputs["Metallic"].default_value = metallic
            if color and not self.hat:
                image = nodes.new("ShaderNodeTexImage")
                image.image = color
                if role == "hair":
                    image.interpolation = "Closest"
                links.new(image.outputs["Color"], bsdf.inputs["Base Color"])
            image = nodes.new("ShaderNodeTexImage")
            image.image = normal
            if role == "hair":
                image.interpolation = "Closest"
            if self.hat:
                uv = nodes.new("ShaderNodeUVMap")
                uv.uv_map = detail_uv.name
                links.new(uv.outputs["UV"], image.inputs["Vector"])
            bump = nodes.new("ShaderNodeNormalMap")
            links.new(image.outputs["Color"], bump.inputs["Color"])
            links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        lock_uv = mesh.attributes.get("rt_lock_uv")
        for face in mesh.polygons:
            role = roles[face.material_index]
            tile = SURFACES.get(role, SURFACES["iron"])[0]
            axis = max(range(3), key=lambda i: abs(face.normal[i]))
            if role == "hair" and axis != 2:
                # Keep strands descending on the sides, fringe, and tail.
                u, v, sign = 1 - axis, 2, 1 if face.normal[axis] * (1 - 2*axis) >= 0 else -1
            else:
                u, v = (axis + 1) % 3, (axis + 2) % 3
                sign = 1 if face.normal[axis] >= 0 else -1
            if role == "hair" and write_lock_uv(mesh, face, detail_uv, lock_uv):
                continue
            for i in face.loop_indices:
                vid = mesh.loops[i].vertex_index
                point = mesh.vertices[vid].co
                detail_uv.data[i].uv = sign * point[u] / tile, point[v] / tile

    def restore_tints(self, data, materials):
        from blender_rpgcobo.pm_convert import vec3col

        tints = {mat.name: vec3col(mat.diffuse_color) for mat in materials}
        for face in data.face:
            face.mate.basecol = tints[face.mate.name]
