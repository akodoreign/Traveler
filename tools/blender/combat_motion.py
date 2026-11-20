"""Build live human combat motions. Plan with tools Python, then export with Blender Python."""
import json
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parents[1]
RESOURCES = TOOLS.parent / "_tools/rpgcobo-tool/project/resource"


def plan():
    sys.path.insert(0, str(TOOLS))
    from chara3d_native_all import build_registry
    from chara3d_victory_all import build
    from foe_batch import clips

    _, motions, _ = build_registry()
    _, weapons = build()
    families = json.loads((RESOURCES / "native_foe/fidget/index.json").read_text(encoding="utf-8"))
    return {
        "shared": motions, "weapons": weapons["combat"], "foes": families,
        "foe_frames": {family: clips(family)[0] for family in set(families.values())},
    }


def export(job, output):
    import bpy
    import chara3d as character
    from chara3d_victory import bank, combat_frames

    def sample(frames, family):
        for name, index, count in frames:
            yield character.pose_frames(character.combat_controls(name, index, count, family))

    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig = character.make_armature(character.rest_frames())
    for folder in ("native_chara", "native_weapons", "native_foe"):
        (output / folder).mkdir(parents=True, exist_ok=True)
    for family, frames in job["shared"].items():
        bank(rig, sample(frames, family), output / "native_chara" / f"motion_{family}.mot")
    for kind, details in job["weapons"].items():
        bank(rig, combat_frames(kind, details), output / "native_weapons" / f"combat_{kind}.mot")

    replacements = {}
    for key, family in job["foes"].items():
        destination = output / "native_foe" / f"{key}.mot"
        if family not in replacements:
            bank(rig, sample(job["foe_frames"][family], family), destination)
            replacements[family] = destination.read_bytes()
        else:
            destination.write_bytes(replacements[family])
    print(f"Exported {len(job['shared'])} shared, {len(job['weapons'])} equipped and {len(job['foes'])} humanoid foe motion banks.")


if __name__ == "__main__":
    if "--plan-only" in sys.argv:
        job_path = Path(sys.argv[sys.argv.index("--plan-only") + 1])
        job_path.write_text(json.dumps(plan()), encoding="utf-8")
    else:
        args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
        export(json.loads(Path(args[0]).read_text(encoding="utf-8")), Path(args[1]) if len(args) > 1 else RESOURCES)

