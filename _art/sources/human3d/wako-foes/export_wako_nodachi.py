"""Fit the existing generated sword and saya meshes as Wako's long blade."""

from pathlib import Path
import sys


repo=Path(sys.argv[sys.argv.index("--")+1]).resolve()
stage=Path(__file__).resolve().parent
sys.path[:0]=[str(repo/"tools"),str(repo/"tools/blender")]

import hunyuan_weapon as weapon


# The reused katana source is tip down. Keep the 57-unit nodachi envelope
# and longer saya from the standard fitter.
weapon.FITS["nodachi"]=(57.,.136,True)
source=repo/"_art/sources/human3d/weapons"
out=stage/"project/resource/native_human"
(out/"tex").mkdir(parents=True,exist_ok=True)
weapon.export_weapon(out,"ep417_wako_nodachi","nodachi",source/"katana_source.glb",
                     source/"saya_source.glb","Wako weathered nodachi",preview=True)
