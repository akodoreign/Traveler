"""Stage stronger color on the next twenty published road and river maps."""
from pathlib import Path
import argparse
import json

import coastal_daylight as coast
from coastal_revision import BASE_SKY,COAST_SKY,daylight_ktx


MAPS={
    "M212":"road", "M236":"road", "M811":"arena",
    "M480":"cave", "M481":"cave", "M829":"cave",
    "M414":"road", "M415":"road", "M416":"road", "M417":"road", "M418":"road",
    "M419":"road", "M420":"road", "M883":"arena", "M884":"arena", "M885":"arena",
    "M350":"road", "M351":"road", "M359":"road", "M360":"road",
}

PALETTE={
    "tidal_wet":((100,111,99),.38),
    "yasuki_wet_blue_slate":((22,48,78),.61),
    "cakon_river_grass":((20,109,45),.66),
    "cakon_silt":((116,72,42),.59),
    "cakon_deck_daylight_palette":((112,49,26),.40),
    "cakon_deck_ends":((101,52,30),.40),
    "cakon_market_setts_daylight_palette":((138,114,102),.47),
    "cakon_crane_blue_daylight_palette":((16,66,137),.60),
    "cakon_ivory_plaster":((227,203,166),.46),
    "cakon_paddy_moss":((20,117,51),.53),
    "cakon_paddy_bund":((124,78,44),.50),
    "cakon_tomie_bamboo":((68,93,44),.46),
    "kudo_silt":((104,72,49),.51),
    "kudo_meadow":((34,118,53),.65),
    "kudo_road":((133,91,53),.59),
    "kudo_rice":((59,129,43),.61),
    "kudo_timber":((96,48,30),.53),
    "kudo_kawara":((39,67,112),.55),
    "kensu_meadow":((33,114,59),.63),
    "kensu_road":((133,85,50),.58),
    "kensu_field":((49,121,52),.64),
    "kensu_timber":((98,46,28),.52),
    "kensu_kawara":((39,68,112),.52),
}
LIQUID={
    "yasuki_tidal_pool":("yasuki_shrine_blue_pool",(9,42,103),(39,145,173),.53),
    "cakon_river":("cakon_clear_day_river",(7,50,103),(41,153,176),.47),
    "cakon_paddy_water":("cakon_paddy_clear_day",(12,62,113),(49,138,160),.49),
    "kudo_river":("kudo_clear_gold_river",(10,54,103),(59,156,169),.45),
    "kensu_paddy":("kensu_paddy_clear_day",(13,59,99),(59,139,147),.42),
    "kensu_spring":("kensu_spring_clear_day",(7,61,113),(49,151,165),.48),
}


def prepare(repo,bundle,reference):
    # Use the approved local light family. Its IDs can coexist with the
    # five-map coastal test regardless of the order the batches are staged.
    accepted=coast.read(reference/"coastal-proof.json")["presets"]
    selected={p["id"].split("brilliance_",1)[1].split("_horizon",1)[0]:p for p in accepted}
    def preset(old,kind):
        row=json.loads(json.dumps(selected[kind]))
        row["id"]="rt_river_town_color_"+kind
        return row
    coast.preset=preset
    coast.ALIAS="_river_town_color"
    coast.GROUPS["retrospective"]=MAPS
    coast.PAINT.update(PALETTE)
    coast.WATER.update(LIQUID)
    coast.ATLAS.update(("m480_mineral_floor","m481_mineral_floor","m829_mineral_floor"))
    coast.prepare(repo,bundle,("retrospective",))
    info=coast.read(bundle/"coastal-proof.json")
    live=repo/"_tools/rpgcobo-tool"
    old=(live/BASE_SKY).read_bytes()
    image=daylight_ktx(old)
    output=bundle/"files"/COAST_SKY
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(image)
    info["projectSource"]={BASE_SKY.as_posix():coast.digest(old)}
    info["projectFiles"]={COAST_SKY.as_posix():coast.digest(image)}
    (bundle/"coastal-proof.json").write_text(json.dumps(info,indent=2)+"\n",encoding="utf8")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("repo",type=Path)
    p.add_argument("bundle",type=Path)
    p.add_argument("reference",type=Path)
    a=p.parse_args()
    prepare(a.repo.resolve(),a.bundle.resolve(),a.reference.resolve())
