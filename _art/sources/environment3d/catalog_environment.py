"""Inventory every registered map and original map voxel model for the rebuild."""

import csv
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
repo = Path(sys.argv[1])
project = repo / "_tools/rpgcobo-tool/project"
source = project / "resource"
published = set(json.loads((source / "native_environment/index.json").read_bytes()))
out = HERE / "inventory"
out.mkdir(exist_ok=True)
sys.path.insert(0, str(repo / "tools"))
import gen_maps as gm
import voxfile

REBUILD = {
    "M100": ("Fortifications", "Watchtower flagstones, parapet masonry and hut timbers."),
    "M101": ("Fortifications", "Connect the sealed Kaiu gate, armoury, watch posts and training yard."),
    "M102": ("Coastal trade road", "Keep the cart lane open, with an exposed tidal shelf and rest points on the cliff-side verge."),
    "M103": ("Hoshi-no-Ichi market", "Anchor the town street around Kiyo's Drop Soup stall, Taneo, the tea-house door, egg trade, and the quay."),
    "M104": ("Quarry and camp", "Open the shelters, animate their cloth and keep the old quarry's story route through the pit."),
    "M105": ("Coast Road after dark", "Use the same shoreline silhouette and landmark locations with light at the road and cave approach."),
    "M120": ("Inn interior", "Open the reception aisle and separate the shared hearth from the sleeping bays."),
    "M123": ("Tea-house interior", "Keep Satomi accessible with a central aisle, two tea settings and a shoji-backed alcove."),
    "M125": ("Storehouse interior", "Use a raised timber floor, clay infill, storage racks, rice bales, pots and low paper lamps."),
    "M130": ("Rock and underground", "Use limestone cutaways and woven nests beside the existing quest route."),
    "M131": ("Rock and underground", "Frame the painted eggs, cracked wall and underground water with damp limestone."),
    "M132": ("Rock and underground", "Keep the armour chamber readable with a continuous coastal limestone wall."),
    "M133": ("Rock and underground", "Keep the altar, eggs and Ryozo clear with the calcite formations close to the walls."),
    "M345": ("Kyuden Bayushi", "Walk the lacquered bridge over the animated koi pond in the memorial garden."),
    "M346": ("Kyuden Bayushi interior", "Keep Norie, the attendant, and the conversation trigger in a fitted teahouse."),
    "M347": ("Kyuden Bayushi", "Route the town storefronts around the shared well and the theater gate."),
    "M348": ("Scorpion grove", "Keep the eastbound road clear under the dense cedar canopy."),
    "M349": ("River of Gold", "Use lanterns, damp cedar and boat landings to distinguish Shutai."),
    "M350": ("River of Gold", "Continue east into Kudo along a raised river road."),
    "M351": ("Kudo waterfront", "Connect the fish stall, working docks, and three accessible interiors."),
    "M352": ("Kudo interior", "Kitsune household hall with an open center aisle."),
    "M353": ("Kudo interior", "Mantis guest house with a chart desk and dock records."),
    "M354": ("Kudo interior", "Dreaming Carp inn with sake racks and sleeping bays."),
    "M355": ("Kudo marsh", "Follow the stone ford across the river toward the west marsh."),
    "M356": ("Kudo marsh", "Find the drifting barge through willows and reed beds."),
    "M357": ("Kudo marsh", "Follow the trail past the Miya relics."),
    "M358": ("Kudo marsh", "Follow earthen banks around the ritual pool."),
    "M359": ("Hisatu Kensu approach", "Follow the clay road between flooded paddies and the Ojatara waymark."),
    "M360": ("Hisatu Kensu", "Working inn and trader doors face the hot springs and bathhouse."),
    "M361": ("City of Masks approach", "Keep the scout and east gate story path clear."),
    "M362": ("City of Masks", "Enter through the west gateway and reach the Sweet Cup under the lanterns."),
    "M363": ("City of Masks interior", "Reach the back room clerk and preserved mask scenes among sake racks and screens."),
    "M364": ("City of Masks", "Give each mask maker an open awning and display without interrupting the market route."),
    "M365": ("City of Masks temple", "Find the damaged sun statue and its reliquary in the eastern chamber."),
    "M366": ("City of Masks temple", "Keep the scriptorium, cloth-mask shrine and monastery approach reachable."),
    "M367": ("City of Masks interior", "Frame the abbot and dais with the mask silhouette and low lanterns."),
    "M368": ("Ojatara Valleys", "Connect the burned fields and Iuchi roadside shelters to Buried Leaves."),
    "M369": ("Ojatara Valleys", "Keep the tribunal, inn and both traders accessible from the refugee camp."),
    "M370": ("Ojatara interior", "Preserve the testimony route through the refurbished tribunal."),
    "M371": ("Ojatara Valleys", "Distinguish the cream command tent from the refugee shelters."),
    "M372": ("Ojatara Valleys", "Frame Shioden's burned manor and its funeral offering."),
    "M374": ("Ojatara Valleys", "Set Yotomo's bell over the existing approach and story trigger."),
    "M375": ("Ojatara Valleys", "Animate the flower fields and keep the house and grave path accessible."),
    "M376": ("Ojatara interior", "Keep Nihime and both directions of the house entrance accessible."),
    "M377": ("Ojatara Valleys", "Keep the sealed mine blocked and place markers along the grave path."),
    "M378": ("Ojatara Valleys", "Give the dusk road a clear encounter lane between slate and cypress."),
    "M379": ("Dragon mountain town", "Place the incense counter under the cliffs beside the inn and outfitter."),
    "M380": ("Dragon mountain road", "Fit the cypress leaf and slate steps to the actual mountain inn entrance."),
    "M381": ("Dragon mountain inn", "Furnish the common room with clay jars, open shelves and staggered cypress boards."),
    "M382": ("Dragon procession road", "Keep the procession and Furnace road clear around the cedar gate."),
    "M383": ("Kyuden Togashi", "Rake gravel around uncut slate and preserve the courtyard audience scene."),
    "M387": ("Buried Leaves in autumn", "Set the Welcome Road entrance, the stable and fabric stalls along the market road."),
    "M388": ("Welcome Road inn", "Leave a clear aisle to the petition board, testimony and innkeeper."),
    "M389": ("Buried Leaves refugee camps", "Group open canvas shelters around the shared cooking fires."),
    "M390": ("The autumn valley road", "Mark the village and testimony routes between maples and burned plots."),
    "M391": ("Shiro Iuchi garden", "Set banners, maples and basins against the windy garden frontage."),
    "M392": ("Hafuna fields", "Show the salted planting beds and keep the officer's testimony accessible."),
    "M393": ("Motobu crater", "Place fractured stones and timbers below the Jizo temple's former site."),
    "M394": ("Shiro no Soshi hall", "Frame the hearing with brocade screens, low writing tables and an open approach."),
    "M395": ("Miyahana's cottage", "Put the tea setting outside the cottage beside flower beds and autumn foliage."),
    "M396": ("Yotomo pigeon village", "Set dovecotes by the road and lead the eastern route under a recessed cave roof."),
    "M397": ("Yotomo pigeon cave", "Fit the return and vat chamber exits to the playable passages."),
    "M398": ("Yotomo vat chamber", "Keep the chamber and story trigger clear of the cedar vats and lanterns."),
    "M872": ("Dragon mountain combat ground", "Keep the wolf and Traveler formations clear under slate and snow."),
    "M875": ("Autumn valley combat ground", "Frame the bandit encounter with russet maples and burned plots."),
    "M876": ("Pigeon cave combat ground", "Set perches and chalk-streaked slate behind the encounter lanes."),
    "M877": ("Yotomo vat combat ground", "Stage the vat chamber fight between the formations with the barrels in the background."),
    "M861": ("Scorpion combat ground", "Use the grove's cedar silhouette behind the Road Bandit formations."),
    "M862": ("Kudo combat ground", "Keep the ford's low stones clear of both formations."),
    "M863": ("Kudo combat ground", "Frame the battle with drowned timber and a narrow run of marsh water."),
    "M864": ("Kudo combat ground", "Keep the ritual pool between the formations."),
    "M865": ("Hisatu Kensu combat ground", "Show the flooded paddies behind the clear formation lanes."),
    "M866": ("City of Masks combat ground", "Stage the city ambush in front of the district gate and market awnings."),
    "M867": ("City of Masks combat ground", "Light the stitched monks' arena with paper lanterns behind the formation."),
    "M868": ("City of Masks combat ground", "Stage Munashii's fight beneath the monastery shadow."),
    "M869": ("Ojatara combat ground", "Set camp shelters and autumn brush behind the valley arena."),
    "M870": ("Ojatara combat ground", "Frame the arena with grave markers and moving wildflowers."),
    "M871": ("Ojatara combat ground", "Keep the mountain-road formations clear of the hillside lanterns."),
    "M384": ("Volcanic caves", "Set apart three active molten pools in Tamori's Furnace lava tubes."),
    "M385": ("Volcanic caves", "Separate the two glowing pools from the ash-shrine route."),
    "M386": ("Volcanic caves", "Use basalt silhouettes below the crater lip."),
    "M437": ("Volcanic highland", "Cut a walkable passage into the basalt at the pilgrim road's lava tube."),
    "M810": ("Fortifications", "Bring the Kaiu masonry and stone walk into the Wall arena."),
    "M811": ("Coastal combat ground", "Keep the central fight free of tall props and show the tidal shelf, vegetation, and cliff layers around it."),
    "M812": ("Quarry combat ground", "Carry the camp's canvas and old cut stone into the arena while keeping formation lanes clear."),
    "M813": ("Rock and underground", "Frame the arena with coastal calcite, mud and clear sightlines."),
    "M873": ("Volcanic combat ground", "Carry a narrow spattering tributary between travelers and fire elementals."),
    "M874": ("Volcanic combat ground", "Break the crater lip with a narrow tributary and distant molten field."),
    "M894": ("Volcanic combat ground", "Set a shallow molten stream into the ash beside the pilgrim route."),
    "M121": ("Equipment shop", "Keep the clerk and cedar displays accessible."),
    "M122": ("Coastal goods shop", "Give the clerk two open aisles and wood storage racks."),
    "M124": ("Magistrate office", "Frame the hearing desk without blocking Kanbe or the return door."),
    "M212": ("Tidal crossing", "Traversable land bridge at low tide."),
    "M236": ("Tidal crossing", "High-tide shelf with a wait option on both shores."),
    "M457": ("Fortifications", "Light the walkable gate tunnel and mark the separate smith entrance."),
    "M817": ("Shadowlands combat ground", "Frame the formations with tar pools, burnt stumps and bones."),
    "M818": ("Shadowlands combat ground", "Leave formations clear on the road beneath the Kaiu Wall."),
    "M991": ("Smithy interior", "Give the Kaiu smith a hearth, anvil and clear approach from the door."),
    **dict.fromkeys(tuple(f"M{i}" for i in range(171,178)),
                    ("Shadowlands march", "Preserve the chapter route, side chests and existing event pages.")),
    "M458": ("Shadowlands", "Keep the waymarker and winding route through shale and tainted ground."),
    "M460": ("Shadowlands", "Follow the climbing switchbacks to Natsuko's concealed castle approach."),
    "M461": ("Fortifications", "Ruined outer bailey with its gate on the east transition."),
    "M462": ("Interiors", "Shiro Hiruma keep with an open ancestral altar."),
    "M463": ("Interiors", "Lord's hall with charred timber, plaster screens and a clear dais."),
    "M808": ("Combat arena", "Match the lord's hall while keeping formation lanes open."),
    "M555": ("Sacred and garden", "Kyuden Doji theatre with four changing sets and a shared stage."),
    **dict.fromkeys(("M459", "M465", "M466", "M467", "M468", "M469"),
                    ("Shadowlands", "Wind around shale banks and tainted earth. Preserve the original route and treasure detours.")),
}


def rebuild_status(mid):
    if mid == "M555" and mid in published:
        return "Native Kabuki stage pass"
    if mid in published:
        return "Native environment pass"
    if mid == "M351":
        return "Street approach corrected; awaiting voxel replacement"
    return "Awaiting voxel replacement"


def family(name, preset):
    name = name.casefold()
    if re.search(r"castle|palace|keep|citadel|fort|watchtower|garrison|kaiu wall",name):
        return "Fortifications"
    if re.search(r"cave|grotto|mine|tunnel|cavern|crypt|quarry|chasm|pit",name):
        return "Rock and underground"
    if re.search(r"sea|ocean|coast|harbou?r|ferry|port|dock|quay|pier|isle|island",name):
        return "Coast and water"
    if re.search(r"inside|room|quarters|interior|hall|inn|office|kitchen|study|cellar|shop|bedroom|court",name):
        return "Interiors"
    if re.search(r"shrine|temple|monastery|pagoda|sanctuary|garden|grave|cemetery",name):
        return "Sacred and garden"
    if re.search(r"town|market|city|village|street|district|hamlet|settlement",name):
        return "Town and service"
    if re.search(r"forest|wood|grove|bamboo|marsh|swamp|bog|fen",name):
        return "Woodland and wetland"
    if re.search(r"mountain|pass|ridge|peak|snow|ice|summit",name):
        return "Highland"
    if re.search(r"shadowlands|oni|taint|jigoku|hell|desolation|waste",name):
        return "Shadowlands"
    if re.search(r"road|crossing|trail|bridge|field|plain|highway|valley",name):
        return "Road and field"
    return "Named location review"


def detail(row):
    def destinations(node):
        if isinstance(node, dict):
            if node.get("role") == "portal" or node.get("cmd") == "cmd_mapmove":
                target = node.get("dest")
                if isinstance(target, dict):
                    target = target.get("mapid")
                if isinstance(target, str) and re.fullmatch(r"M\d+", target):
                    yield target
            for child in node.values():
                yield from destinations(child)
        elif isinstance(node, (list, tuple)):
            for child in node:
                yield from destinations(child)
    return ", ".join(dict.fromkeys(destinations(row.get("event", {}))))


def write_csv(name, rows):
    with (out/name).open("w",encoding="utf-8-sig",newline="") as target:
        writer=csv.DictWriter(target,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


data=json.loads((project/"data/map.json").read_bytes())
map_files={part.stem for part in (project/"data/mapdata").glob("*.bw")}
maps=[]
for mid in sorted(set(data)|map_files):
    row=data.get(mid,{})
    if not re.fullmatch(r"M\d+",mid):
        continue
    name=row.get("name",mid)
    category,purpose=REBUILD.get(mid,(family(name,row.get("rsetid","")),""))
    maps.append({"map":mid,"name":name,"family":category,"purpose":purpose,
                 "source":"diagnostic" if mid in gm.DEBUG_MAPS else "Traveler generator" if mid in gm.MAPS else "other registered map",
                 "registered":mid in data,"world_on_disk":mid in map_files,"render":row.get("rsetid",""),
                 "event_count":len(row.get("event",{})),"linked_maps":detail(row),
                 "environment_status":rebuild_status(mid)})
write_csv("map-catalog.csv",maps)

voxels=[]
for pack in sorted((source/"vox/map").rglob("*.vox")):
    definition=voxfile.VoxFile.load(pack)
    labels={index:name for name,index in definition.names.items()}
    for index,model in enumerate(definition.models):
        voxels.append({"pack":pack.relative_to(source).as_posix(),"model":labels.get(index,f"model_{index}"),
                       "index":index,"voxel_dimensions":"×".join(map(str,model.size)),
                       "status":"Review source use and build replacement"})
write_csv("voxel-catalog.csv",voxels)
stats={"map_entries":len(maps),"registered_maps":sum(row["registered"] for row in maps),
       "maps_with_worlds":sum(row["world_on_disk"] for row in maps),
       "traveler_generator_maps":sum(row["source"]=="Traveler generator" for row in maps),
       "published_map_passes":sum(row["map"] in published for row in maps),
       "map_passes_remaining":sum(row["map"] not in published for row in maps),
       "map_voxel_models":len(voxels),"voxel_packs":len(set(row["pack"] for row in voxels))}
(out/"summary.json").write_text(json.dumps(stats,indent=2),encoding="utf-8")
print(stats)
