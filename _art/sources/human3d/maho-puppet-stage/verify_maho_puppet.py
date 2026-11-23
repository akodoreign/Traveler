"""Verify Maho Puppet in the original deepest-cell scene and troll encounter."""
from pathlib import Path
import struct
import sys

from PIL import Image

from preview_clan_castles import HERE, OUTPUTS, run, spawn
from verify_gusai import CAPTURE


def verify(profile, fixtures):
    fixture = (fixtures / "maho_puppet_proof.sk").read_text("utf8")
    preview = (HERE / "preview_coast.sk").read_text("utf8")
    screenshot = preview[preview.index("function screenshot("):preview.index("\n\nlocal views")]
    camera = CAPTURE.replace("GusaiReviewCamera", "MahoReviewCamera").replace("bot_gusai_", "bot_maho_")
    assert fixture.count("\treturn;") == 1
    bout = screenshot + "\n" + fixture.replace("\treturn;", camera + "\n\treturn;", 1)
    steps = "wait,1250|evalf,tmp/castle_native.sk"
    origin = spawn(52, 26, 1.5)
    run(profile, "maho-puppet-field", "M150", "hida", origin, steps,
        ("[MAHO PUPPET FIT] M150 event 3",), fixture, timeout=72)
    run(profile, "maho-puppet-real-bout", "M150", "hida", origin, steps,
        ("[MAHO PUPPET FIT] M815 E235",), bout, battle=("M001", "14"), timeout=72)
    for view in ("front", "side"):
        blob = (profile / "tmp/rt_shot" / f"bot_maho_{view}.raw").read_bytes()
        size = struct.unpack_from("<II", blob)
        assert size == (3840, 2160), size
        image = Image.frombytes("RGBA", size, blob[8:]).convert("RGB")
        image.save(OUTPUTS / f"maho-puppet-{view}-daylight-4k.png")


if __name__ == "__main__":
    verify(*(Path(value).resolve() for value in sys.argv[1:3]))
