"""Review Gonta's shared fit in the native quarry bout and in the field."""
from pathlib import Path
import struct
import sys

from PIL import Image

from preview_clan_castles import HERE, OUTPUTS, run, spawn
from verify_gusai import CAPTURE


def verify(profile, fixtures):
    fixture = (fixtures / "gonta_proof.sk").read_text("utf8")
    preview = (HERE / "preview_coast.sk").read_text("utf8")
    screenshot = preview[preview.index("function screenshot("):preview.index("\n\nlocal views")]
    camera = CAPTURE.replace("GusaiReviewCamera", "GontaReviewCamera").replace("bot_gusai_", "bot_gonta_")
    assert fixture.count("\treturn;") == 1
    bout = screenshot + "\n" + fixture.replace("\treturn;", camera + "\n\treturn;", 1)
    steps = "wait,1250|evalf,tmp/castle_native.sk"
    run(profile, "gonta-real-bout", "M104", "hida", spawn(66, 27, 4), steps,
        ("[GONTA FIT] P125", "[GONTA FIT] M812 E120"), bout, battle=("M001", "6"), timeout=77)
    for view in ("front", "side"):
        blob = (profile / "tmp/rt_shot" / f"bot_gonta_{view}.raw").read_bytes()
        size = struct.unpack_from("<II", blob)
        assert size == (3840, 2160), size
        image = Image.frombytes("RGBA", size, blob[8:]).convert("RGB")
        image.save(OUTPUTS / f"gonta-{view}-daylight-4k.png")
    run(profile, "gonta-quarry-field", "M104", "hida", spawn(66, 27, 4), steps,
        ("[GONTA FIT] P125", "[GONTA FIT] M104 adult field event"), fixture, timeout=70)


if __name__ == "__main__":
    verify(*(Path(value).resolve() for value in sys.argv[1:3]))
