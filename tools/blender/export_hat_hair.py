"""Stage a hat-specific variant of an already fitted Hunyuan head."""
import argparse
import json
from pathlib import Path

import bpy
import bmesh
from mathutils import Matrix

from hunyuan_weapon import PolygonMesh, buildPolygonMesh, clearCaches, saveModelData


def remove_hidden_hair(mesh, recipe):
    edit = bmesh.new()
    edit.from_mesh(mesh)
    if crown_y := recipe.get("crown_y"):
        bmesh.ops.bisect_plane(
            edit, geom=[*edit.verts, *edit.edges, *edit.faces], dist=.0001,
            plane_co=(0, 0, crown_y), plane_no=(0, 0, 1), clear_outer=True,
        )
    for low, high in recipe.get("strand_boxes", []):
        def hidden(vertex):
            # Recipe positions use Traveler's forward, up, side ordering.
            x, side, up = vertex.co
            return all(a < c < b for a, c, b in zip(low, (x, up, -side), high))
        hidden_faces = [face for face in edit.faces if all(hidden(vertex) for vertex in face.verts)]
        bmesh.ops.delete(edit, geom=hidden_faces, context="FACES")
    edit.to_mesh(mesh)
    edit.free()
    mesh.update()


def export(source, descriptor, recipe, out, key):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    clearCaches()
    bpy.ops.import_scene.gltf(filepath=str(source))
    face, = [
        obj for obj in bpy.context.scene.objects
        if obj.type == "MESH" and "head" in obj.vertex_groups and len(obj.data.vertices) >= 400
    ]
    face.data.transform(face.matrix_world, shape_keys=True)
    face.matrix_world = Matrix.Identity(4)
    remove_hidden_hair(face.data, recipe)
    face.name = key

    data = PolygonMesh()
    buildPolygonMesh(face, face.data, data, [group.name for group in face.vertex_groups])
    data.aabb = [-15, 90, -20, 22, 145, 20]
    out.mkdir(parents=True, exist_ok=True)
    saveModelData(data, str(out / f"{key}.mdl"))

    body = descriptor.read_text(encoding="utf-8")
    source_mesh = f'modeldata = "{descriptor.stem}.mdl"'
    if source_mesh not in body:
        raise ValueError(f"Missing native mesh reference in {descriptor}")
    (out / f"{key}.pm").write_text(
        body.replace(source_mesh, f'modeldata = "{key}.mdl"', 1), encoding="utf-8",
    )

    # Retain the fitted portrait's face morphs in the optional portable output.
    if recipe.get("portable"):
        bpy.ops.object.select_all(action="DESELECT")
        face.select_set(True)
        if face.parent and face.parent.type == "ARMATURE":
            face.parent.select_set(True)
        bpy.context.view_layer.objects.active = face
        bpy.ops.export_scene.gltf(filepath=str(out / f"{key}.glb"), use_selection=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("descriptor", type=Path)
    parser.add_argument("recipe", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("key")
    args = parser.parse_args()
    export(args.source, args.descriptor, json.loads(args.recipe.read_text("utf-8")), args.out, args.key)
