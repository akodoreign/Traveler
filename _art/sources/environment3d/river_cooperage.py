"""Build fitted sake casks and lidded vats for the original river settlements."""

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from math import cos, sin, tau
from pathlib import Path

import numpy as np

from build_hoshi_stall import box
from build_iuchi_tower import tint_texture
from cakon_huts import barrel_shell
from export_coast import Geometry, STAGE, export


HERE = Path(__file__).resolve().parent
SAKE = "shutai_fitted_sake_casks"
VAT = "yotomo_fitted_storage_vat"
STAVE = tuple(f"river_cooper_stave_{index}" for index in range(3))
RIM = "river_cooper_rim"
ROPE = "river_cooper_rope"
POTTERY = "river_cooper_pottery"
ENDGRAIN = "river_cooper_lid"
BLACK = "river_cooper_recess"
PALETTE = {
    STAVE[0]: ("cakon_cedar_deck_scan", (113, 68, 38), .048),
    STAVE[1]: ("cakon_cedar_deck_scan", (102, 62, 36), .048),
    STAVE[2]: ("cakon_cedar_deck_scan", (124, 75, 41), .048),
    RIM: ("cakon_cedar_deck_scan", (72, 51, 39), .029),
    ROPE: ("cakon_cedar_deck_scan", (149, 122, 80), .029),
    POTTERY: ("cakon_plaster_scan", (74, 51, 44), .031),
    ENDGRAIN: ("cakon_cedar_deck_scan", (128, 94, 58), .039),
    BLACK: ("cakon_plaster_scan", (29, 24, 24), .016),
}
MATERIALS = {key: (f"{key}.png", .94) for key in PALETTE}


def add_drum(geo, center, profile, lugs, *, rope, depth_scale=1.):
    cx, cz = center
    before = len(geo.vertices)
    barrel_shell(geo, [(h, r - .010) for h, r in profile], 28, (RIM,))
    barrel_shell(geo, profile, 28, (STAVE[0], STAVE[1], STAVE[0], STAVE[2]), .007)
    material = ROPE if rope else RIM
    for h, r in lugs:
        barrel_shell(geo, ((h - .011, r - .011), (h, r), (h + .032, r),
                           (h + .043, r - .010)), 28, (material,))
    cap_h, cap_r = profile[-1]
    barrel_shell(geo, ((cap_h - .015, cap_r), (cap_h + .024, cap_r + .014),
                       (cap_h + .048, cap_r + .014)), 28, (RIM,))
    for place in range(28):
        a, b = tau * place / 28, tau * (place + 1) / 28
        rad = cap_r + .014
        top = cap_h + .048
        corners = [(0., 0., top), (rad * cos(a), rad * sin(a), top),
                   (rad * cos(b), rad * sin(b), top)]
        pts = corners + [corners[-1]]
        geo.quad(pts, [(x + .5, z + .5) for x, z, _ in pts], ENDGRAIN)
    for z in (-cap_r * .43, cap_r * .39):
        box(geo, (-cap_r * .66, z, cap_h + .047), (cap_r * 1.32, .041, .030), STAVE[1])
    for i in range(before, len(geo.vertices)):
        x,z,y = geo.vertices[i]
        geo.vertices[i] = (x + cx, z * depth_scale + cz, y)


def sake_casks():
    geo = Geometry()
    box(geo, (-.725, -.415, .048), (1.45, .83, .081), ENDGRAIN, .77)
    for x in (-.646, .527):
        for z in (-.337, .208):
            box(geo, (x,z,0.), (.118, .129, .092), RIM)
    add_drum(geo, (-.29, .012), ((.128,.279),(.169,.283),(.415,.313),(.76,.304),
                               (1.10,.274),(1.133,.266)),
             ((.196,.299),(.416,.324),(.747,.317),(1.06,.289)), rope=True)
    # A small glazed earthenware vessel shares the rack without becoming part of the cask.
    start = len(geo.vertices)
    barrel_shell(geo, ((.127,.149),(.168,.184),(.323,.216),(.483,.207),(.575,.137),
                       (.622,.109),(.650,.126),(.679,.122)), 24, (POTTERY,))
    for i in range(24):
        a,b = tau * i / 24, tau * (i + 1) / 24
        circle = [(0.,0.,.661),(.122*cos(a),.122*sin(a),.679),(.122*cos(b),.122*sin(b),.679)]
        geo.quad(circle + [circle[-1]], [(0.,0.),(1.,0.),(1.,1.),(1.,1.)], BLACK)
    for i in range(start,len(geo.vertices)):
        x,z,y=geo.vertices[i]
        geo.vertices[i]=(x+.39,z-.086,y)
    return geo


def mineral_vat():
    geo = Geometry()
    for x in (-.243,.145):
        for z in (-.238,.142):
            box(geo,(x,z,0.),(.098,.096,.092),RIM)
    add_drum(geo,(0.,0.),((.089,.344),(.206,.361),(.48,.385),(.702,.391),(.833,.382)),
             ((.196,.379),(.677,.410),(.798,.394)),rope=False,depth_scale=.77/.82)
    return geo


def build():
    for key, (scan, tint, contrast) in PALETTE.items():
        tint_texture(key, scan, tint, contrast)
    for name, geo, size in ((SAKE,sake_casks(),(1.45,1.21,.83)),(VAT,mineral_vat(),(.82,.91,.77))):
        verts = np.asarray(geo.vertices, dtype=float)
        assert np.allclose(np.ptp(verts[:, [0,2,1]], axis=0),size,atol=.004), name
        export(name,geo,MATERIALS)


def replacement_rows(repo):
    index_path = repo / "_tools/rpgcobo-tool/project/resource/native_environment/index.json"
    current = json.loads(index_path.read_bytes())
    changes = {"M349": ("scorpion_shutai_sake_store", SAKE, 5),
               "M877": ("autumn_yotomo_storage_vat", VAT, 6)}
    before = {mid: current[mid] for mid in changes}
    rows = deepcopy(before)
    for mid,(old,new,count) in changes.items():
        pieces = [part for part in rows[mid]["placements"] if part[0] == old]
        assert len(pieces) == count, (mid, len(pieces))
        for part in pieces:
            part[0] = new
    files = [f"tex/{key}.png" for key in PALETTE]
    files += [f"{name}.{ext}" for name in (SAKE,VAT) for ext in ("pm","mdl")]
    receipt = {"before": before, "rows": rows,
               "files": {file: sha256((STAGE / file).read_bytes()).hexdigest() for file in files},
               "followUp": {"M398": {
                   "duplicateStockEventIds": ["#82#","#83#","#84#"],
                   "modelSwap": ["autumn_yotomo_storage_vat", VAT],
               }}}
    path = HERE / "river-cooperage-replacement.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo",type=Path)
    args = parser.parse_args()
    build()
    print(f"Staged row receipt {replacement_rows(args.repo)}.")
