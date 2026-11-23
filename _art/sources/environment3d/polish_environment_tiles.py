"""Stage and publish richer roof, wood, accent, and street textures."""
from pathlib import Path
import argparse
import io
import json
import re

import numpy as np
from PIL import Image

from publish_castle_gates import INDEX, replace_file_contents
from install_clan_castles import set_file

THEMES = {
    "hida": (24,42,73), "doji": (54,94,138), "akodo": (110,71,42),
    "isawa": (120,59,37), "bayushi": (62,36,49), "kitsuki": (38,73,54),
    "iuchi": (76,53,108), "togashi": (46,75,58),
}
CAKON = {
    "cakon_crane_blue.png": (1.34, .96, (36,75,119), .40),
    "cakon_deck.png": (1.21, .92, (124,84,46), .25),
    "cakon_market_setts.png": (1.23, .95, (121,100,88), .17),
    "cakon_hut_timber.png": (1.26, .95, (96,66,43), .22),
}
KINDS = {
    "roof": (1.49,.86,.43),
    "floor": (1.36,.93,.46),
    "accent": (1.33,.97,.59),
    "gravel": (1.18,.97,.18),
}
FLOOR=(125,83,47)
GRAVEL=(144,124,102)
ADJUSTED="_daylight_palette"


def transform(source, image_key):
    match=re.fullmatch(r"castle_([a-z]+)_(roof|floor|accent|gravel)[.]png",image_key)
    if match and match[1] in THEMES:
        theme,kind=match.groups()
        roof=THEMES[theme]
        style={"roof": roof, "floor":FLOOR, "accent":None, "gravel":GRAVEL}[kind]
        sat,exposure,strength=KINDS[kind]
    elif image_key in CAKON:
        sat,exposure,style,strength=CAKON[image_key]
    else:
        return None

    source_image=Image.open(io.BytesIO(source)).convert("RGB")
    rgb=np.asarray(source_image,dtype=float)
    gray=rgb@[.22,.68,.10]
    if style is not None:
        tint=np.array(style,dtype=float)
        tint_gray=tint@[.22,.68,.10]
        gray_target=(1-strength)*gray+strength*tint_gray
        chroma=rgb-gray[...,None]
        target=(1-strength)*chroma+strength*(tint-tint_gray)
        rgb=gray_target[...,None]+sat*target
    else:
        rgb=gray[...,None]+sat*(rgb-gray[...,None])
    rgb*=exposure
    # Keep the original high-frequency texture detail and matte highlights.
    buffer=io.BytesIO()
    Image.fromarray(np.uint8(np.clip(rgb, 0, 255))).save(buffer,format="PNG")
    return buffer.getvalue()


def models(engine):
    rows=json.loads((engine/INDEX).read_bytes())
    castle_rows={mid for mid,row in rows.items() if "_castle" in (row.get("terrain") or "")}
    target_ids=castle_rows|{"M413","M414","M415","M416","M417","M418","M419","M883","M884"}
    for mid in target_ids & rows.keys():
        row=rows[mid]
        if row.get("terrain"):
            yield row["terrain"]
        for item in row.get("placements",()):
            if item[0].startswith("cakon_"):
                yield item[0]


def main(repo,profile,publish):
    engine=repo/"_tools/rpgcobo-tool"
    root=(engine/INDEX).parent
    candidate=(profile/INDEX).parent
    updates={}
    textures={}
    for model in sorted(set(models(engine))):
        rel=Path(model+".pm")
        before=(root/rel).read_bytes()
        text=before.decode()
        sources=re.findall(r'texture0 = "tex/([^"]+)"',text)
        for source in sources:
            asset=Path("tex")/source
            if source not in textures:
                textures[source]=transform((root/asset).read_bytes(),source)
            new=textures[source]
            if new is None:
                continue
            target=asset.with_stem(asset.stem+ADJUSTED)
            updates[target]=new
            text=text.replace(f'texture0 = "tex/{source}"',f'texture0 = "{target.as_posix()}"')
        if text.encode()==before:
            continue
        updates[rel]=text.encode()
        if not publish:
            model_name=re.search(r'modeldata = "([^"]+)"',text)[1]
            model_path=Path(model_name)
            set_file(candidate/model_path,(root/model_path).read_bytes())
            for source in sources:
                path=Path("tex")/source
                set_file(candidate/path,(root/path).read_bytes())
    if publish:
        assert all((candidate/p).read_bytes()==data for p,data in updates.items())
    dest=root if publish else candidate
    before={path:(dest/path).read_bytes() if (dest/path).exists() else None for path in updates}
    changed=[]
    try:
        for path,data in updates.items():
            current=(dest/path).read_bytes() if (dest/path).exists() else None
            assert current==before[path], path
            changed.append(path)
            set_file(dest/path,data)
    except BaseException:
        for path in reversed(changed):
            if before[path] is None:
                (dest/path).unlink(missing_ok=True)
            else:
                set_file(dest/path,before[path])
        raise
    mode="Installed" if publish else "Staged"
    print(f"{mode} {sum(p.suffix=='.png' for p in updates)} refined tile textures across "
          f"{sum(p.suffix=='.pm' for p in updates)} native terrain and prop descriptors.")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("repo",type=Path)
    p.add_argument("profile",type=Path)
    p.add_argument("--publish",action="store_true")
    args=p.parse_args()
    main(args.repo.resolve(),args.profile.resolve(),args.publish)
