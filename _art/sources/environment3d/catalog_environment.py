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
native_index = json.loads((source / "native_environment/index.json").read_bytes())
prop_only = {mid for mid, row in native_index.items() if row.get("propOnly")}
published = set(native_index) - prop_only
out = HERE / "inventory"
out.mkdir(exist_ok=True)
sys.path.insert(0, str(repo / "tools"))
import gen_maps as gm
import voxfile

REBUILD = {
    "M153": ("Hida siege cellars", "Follow the usable cellar path to the servants stair and reachable save shrine."),
    "M501": ("Hida reception and service hall", "Fit the cellar arrival and first siege stair gate into the live keep."),
    "M502": ("Hida guest and council chambers", "Gate the upper stair on both original siege checks."),
    "M503": ("Hida archives and strategy halls", "Keep the false-servant encounter and original deep-tunnel handoff."),
    "M816": ("Hida castle hall arena", "Frame the registered keep combats in cedar and indigo."),
    "M148": ("Hida donjon cells", "Fit cell fronts, warm lanterns and walkable shored bores around the original route."),
    "M149": ("Hida trap catacombs", "Follow the original winding path past the roller and jade traps."),
    "M150": ("Hida deepest cell", "Keep the troll staging and original entry in the dark slate cell."),
    "M157": ("Deep Hida trap tunnels", "Retain the flare scene and true passage to the Wall."),
    "M158": ("Kaiu Wall tunnel mouth", "Fit the arrival into a full vaulted battlement passage."),
    "M170": ("Kaiu trap tunnels", "Keep both original story exits on the winding cave route."),
    "M815": ("Hida donjon arena", "Preserve the puppet and troll formations in the matching gaol terrain."),
    "M442": ("Oracle switchback stair", "Frame the original switchback with fractured indigo basalt and incandescent lava."),
    "M443": ("Oracle crater shrine", "Retain the shrine approach beside a recessed irregular crater pool."),
    "M896": ("Oracle lava crossing arena", "Fit a walkable dry causeway between the champion formations."),
    "M450": ("Shinomen lava glade", "Frame the road with diorama pines, charred trees, and active lava pools."),
    "M476": ("Dragon mountain road", "Keep both story gates and the ridge bridge passable beside the recessed cave mouth."),
    "M488": ("Dragon mountain cave", "Use a walkable mountain passage with the original loot and a return to the same mouth."),
    "M798": ("Dragon cavern arena", "Stage the actual cave encounter in an underground arena."),
    "M477": ("Beiden hill road", "Fit the timber-shored bandit entrance into the hillside and preserve the two story gates."),
    "M489": ("Beiden bandit hideout", "Fit cots and provision racks to the gallery floor around the original chests."),
    "M821": ("Beiden hill-road arena", "Keep outdoor combat on its own hillside arena."),
    "M797": ("Beiden bandit cave arena", "Use a dedicated underground arena for the hideout encounter."),
    "M475": ("Northern Phoenix road", "Keep both story gates accessible from the main road and place the real fox-cave entry on a wooded side path."),
    "M487": ("Phoenix fox cave", "Follow mineral springs to original loot and the fox offering shrine."),
    "M799": ("Fox shrine arena", "Put the votive shrine behind the fighting lane and keep the forest for outdoor battles."),
    "M846": ("Isawa Mori arena", "Frame outdoor encounters with miniature pines and maples, a visible torii and a gentle breeze."),
    "M474": ("Doji tide road", "Follow the Crane coast between the cedar causeway, recessed tide-cave entry, and story gates."),
    "M486": ("Doji tide cave", "Cross a timber footbridge between tide pools, down to the original loot and cache branches."),
    "M828": ("Doji cove arena", "Keep the original formations on the sand with miniature shore defenses and a skiff behind them."),
    "M473": ("Zumiki snow road", "Place the recessed ice cave off the snowy ridge road and keep both northern gates clear."),
    "M485": ("Zumiki ice cave", "Run powdery footpaths around cobalt pools and crystalline pillars with warm Japanese lanterns."),
    "M844": ("Snowbound cavern arena", "Frame the cave encounters in a sheltered blue ice cutaway without blocking either formation."),
    "M471": ("River of Gold east bank", "Frame the river with stepped banks, a continuous boardwalk and a shallow cliff passage."),
    "M472": ("Lion hills road", "Give the two canyon mouths distinct rocky silhouettes and preserve the gated cross-country routes."),
    "M482": ("River Cave", "Run an animated stream below a fitted footbridge and connect the original caches."),
    "M483": ("Lion hill cave", "Give the standing stone a dais and lion-colored votive cloths along the warm mineral chambers."),
    "M484": ("Lion old mine", "Tie the smelter galleries together with continuous tracks, three switch stands and buffered terminals."),
    "M819": ("Lion cavern arena", "Keep ochre rock, timber supports and the rail turnout behind active combat formations."),
    "M470": ("Yasuki coastal road", "Set both cave mouths into the coast ridge and leave the Hoshi and Yasuki approaches open when their story gates permit."),
    "M480": ("Yasuki tidal cave", "Keep the return passage on the same mouth and give the tidal chambers an inset shore landing."),
    "M481": ("Yasuki smuggler cave", "Put the original caches along separate galleries and a concealed landing."),
    "M829": ("Yasuki coastal cave arena", "Keep animated tide pools and standing stones behind both combat formations."),
    "M422": ("Winter River of Gold", "Frame the Fox Shrine and snow-covered road with a sapphire river and clear shoreline."),
    "M423": ("Winter rice barge", "Give the party a walkable fitted deck during the medicine voyage."),
    "M424": ("Floating Flowers", "Fit the market stalls, moorings and warehouse door to the winter waterfront."),
    "M425": ("Snake Den archive", "Lead from the harbor stair through curved limestone archive chambers."),
    "M426": ("Snake Den ritual chamber", "Set the serpent character into warm ritual sand beside carved stone niches."),
    "M427": ("Snake Den serpent doorway", "Carve a deep central jade passage with solid rock flanks and test both directions."),
    "M428": ("Snake Den exit chamber", "Keep the enforcer arena and boathouse ladder on connected ground."),
    "M888": ("Winter river battle", "Frame the Wako ambush by the animated winter river."),
    "M889": ("Floating Flowers storm battle", "Use a distinct storm current behind the jetty fight."),
    "M890": ("Snake Den battle", "Frame the enforcer fight with jade details, Japanese lanterns and cave pools."),
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
    "M399": ("Shiro Iuchi star field", "Read eight scorched rays against the frost and follow the story-driven tower gate."),
    "M400": ("Shiro Iuchi tower hall", "Keep the notes table and indigo runner clear of the stairs and singing servants."),
    "M401": ("Shiro Iuchi tower stair", "Frame the wind ledge and the existing stair with fitted rails."),
    "M402": ("Shiro Iuchi upper room", "Dress Shahai's room around the barricade, bedding and story event."),
    "M403": ("Iuchi woods", "Set birches, wildflowers and a slow brook around Daiyu's clearing."),
    "M404": ("Mirumoto war-camp", "Keep the field kitchen and command tent separate from the walkable jade mine entrance."),
    "M405": ("Jade mine entrance", "Place the miners' memorials and jade seams along the approach to the galleries."),
    "M406": ("Jade galleries", "Fit the carts, jade seams and foreman's desk beside the original ledger event."),
    "M407": ("Deep jade gallery", "Set the fractured shrine above the guardian's approach."),
    "M408": ("Shiro Iuchi siege camp", "Place the field kitchen under the green pavilions and put the wax choice beneath the tunnel roof."),
    "M409": ("Shiro Iuchi wind tunnel", "Keep the pale gale strips visible and synchronize the dust with the gust and lull cycle."),
    "M410": ("Shiro Iuchi narrows", "Frame the inner castle gate around the walk-through portal unlocked by defeating the Legion."),
    "M411": ("Shiro Iuchi great stair", "Distinguish the central ceremonial steps from the east stair to the storm room."),
    "M412": ("Shiro Iuchi storm room", "Open the rear windows and keep the story dais clear around Kurosho."),
    "M413": ("Iuchi valley road home", "Dress the refugee caravan route below the castle and retain the chapter handoff."),
    "M414": ("Cakon memory riverbank", "Keep the herb gathering site visible by a slow river with fitted riverside huts."),
    "M415": ("Cakon docks", "Fit the river barge, mooring gear and staved barrels to the working quay."),
    "M416": ("Cakon market", "Keep the stalls, musicians, herb seller and armoury readable beside their doors."),
    "M417": ("Cakon alley and river gate", "Close the wall flanks and tie the portcullis collision and lift to the existing unlock."),
    "M418": ("Cakon outer hamlet", "Fit timber and thatch houses beside the shrine, with barrel and straw details off the trail."),
    "M419": ("Cakon canal crossing", "Fit the old maple log to its original crossing and let the slow canal continue below it."),
    "M872": ("Dragon mountain combat ground", "Keep the wolf and Traveler formations clear under slate and snow."),
    "M875": ("Autumn valley combat ground", "Frame the bandit encounter with russet maples and burned plots."),
    "M876": ("Pigeon cave combat ground", "Set perches and chalk-streaked slate behind the encounter lanes."),
    "M877": ("Yotomo vat combat ground", "Stage the vat chamber fight between the formations with the barrels in the background."),
    "M878": ("Shiro Iuchi tower combat ground", "Frame the servants' combat lane with an indigo runner, screens and andon."),
    "M879": ("Jade mine combat ground", "Keep the jade carts and mineral seams outside the fight lane."),
    "M880": ("Deep jade gallery combat ground", "Frame the Mine Guardian with a fractured shrine and jade seams."),
    "M881": ("Wind tunnel combat ground", "Keep windswept slate and pale scoured sand outside the party and Legion formations."),
    "M882": ("Storm room combat ground", "Continue the open windows, fallen lattices and drifting wind around the boss formation."),
    "M883": ("Cakon street combat", "Continue market paving and timber shopfronts behind the combat lane."),
    "M884": ("Cakon canal combat", "Frame the existing log encounter with a slow river and miniature trees along the banks."),
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
    if mid in prop_only:
        return "Props installed, terrain pending"
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
       "prop_only_map_updates":len(prop_only),
       "map_passes_remaining":sum(row["map"] not in published for row in maps),
       "map_voxel_models":len(voxels),"voxel_packs":len(set(row["pack"] for row in voxels))}
(out/"summary.json").write_text(json.dumps(stats,indent=2),encoding="utf-8")
print(stats)
