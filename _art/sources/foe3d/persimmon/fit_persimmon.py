"""Fit the generated bay pony using the native equine export orientation."""
from pathlib import Path
import sys


def pony_points(exporter):
    return {
        "root": ((-33,59,0),(24,63,0),21,"root",0),
        "neck": ((23,65,0),(44,83,0),11,"head",0),
        "head": ((44,83,0),(61,67,0),12,"head",0),
        "tail0": ((-40,70,0),(-56,53,0),8,"tail",1),
        "tail1": ((-56,53,0),(-61,33,0),8,"tail",2),
        "tail2": ((-61,33,0),(-63,11,0),7,"tail",3),
    } | exporter.quadruped_legs((22,60,9),(27,1,8),(-35,64,10),(-37,1,9),9)


def main(repo, source):
    sys.path[:0] = [str(repo / "tools/blender"), str(repo / "tools")]
    import hunyuan_foe as export

    out = Path(__file__).resolve().parent / "native_foe"
    out.mkdir(parents=True, exist_ok=True)
    # Both source horses face -X. Reuse the equine orientation, with fitted
    # bone positions and the pony's own measurements and textures.
    export.PROFILES["onikage"] = ("EP172","beast",0,132,lambda: pony_points(export))
    export.main(repo,source,out,"onikage")
    (out / "onikage_animated.glb").replace(out / "persimmon_animated.glb")


if __name__ == "__main__":
    main(*(Path(arg).resolve() for arg in sys.argv[1:3]))
