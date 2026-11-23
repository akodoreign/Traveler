"""The Game of Masks at Kyuden Bayushi (user 2026-11-22: "move the whole masks into the Bayushi castle ... a battle
creature type theme ... the masks represent the combat monsters ... swap between them, level them up with random
fights in the castle ... if a player in the castle sees you they run up and challenge you to a sadane match. each mask
will have different sadane subtle pokes, and the list each one has grows as it levels up. Switching the masks gives you
types, water > fire etc like the instructions say ... 3/4 view from behind the Shosuro ... commands such as swap
(masks) attack (list of insults for the mask equipped)").
Picks (AskUserQuestion): an optional side game on Mitsue's path after Ch1; masks come from the City of Masks story,
from beaten rivals and from the castle town's mask-maker; prizes are gear, zeni and Honor; all 7 materials.

The one source for the game's content. Writes
  _tools/rpgcobo-tool/project/resource/sadane/sadane.json   (plugin RokuganSadane.sk reads it; gen_maps places the
                                                             rivals, the keeper and the hidden duellists from it)
  docs/rules/game-of-masks.md                               (the rules and every mask's barbs, for reading)
python -E tools/gen_sadane.py"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource", "sadane", "sadane.json")
OUT_DOC = os.path.join(HERE, "..", "docs", "rules", "game-of-masks.md")

# The material chart, word for word what Kamen no Toshi teaches (M362: "wood fears metal, metal fears fire, fire
# fears water, water fears earth, earth fears wood, stone fears silk") and the Silk Mask's own line ("Stone fears it.
# It fears nothing but stone"): a barb of the material a mask fears cuts twice as deep; a barb of the material it
# overcomes glances off at half. Stone and silk fear each other.
TYPES = ["Metal", "Wood", "Fire", "Water", "Earth", "Stone", "Silk"]
TYPE_COLOUR = {"Metal": [200, 204, 212], "Wood": [127, 176, 105], "Fire": [224, 87, 42], "Water": [74, 143, 214],
               "Earth": [176, 138, 74], "Stone": [142, 142, 150], "Silk": [228, 166, 200]}   # [r, g, b] (the chips)
FEARS = {"Wood": ["Metal"], "Metal": ["Fire"], "Fire": ["Water"], "Water": ["Earth"], "Earth": ["Wood"],
         "Stone": ["Silk"], "Silk": ["Stone"]}          # defender -> the attacking materials it fears


def mult(atk, dfn):
    if atk in FEARS[dfn]:
        return 2.0
    if dfn in FEARS[atk] and atk not in FEARS[dfn]:        # the defender is what the attacker fears: half
        return 0.5
    return 1.0


# A barb: (level learned, name, power, accuracy, effect, the line said aloud). Effects: None = composure damage only;
# "poise-" lowers the target's Poise a step; "timing-" lowers its Timing; "wit+" raises the wearer's Wit; "heal" puts
# back a share of the wearer's composure. Power 0 for a pure effect.
def B(lv, name, power, acc, fx, line):
    return {"lv": lv, "name": name, "power": power, "acc": acc, "fx": fx, "line": line}


# Masks: key -> name, material, base [Composure, Wit, Poise, Timing], where it comes from, five barbs.
MASKS = {
    # ------------------------------------------------------------------------------------------------ Metal
    "iron": dict(name="Iron Mask", type="Metal", base=[55, 55, 60, 35], src="story A145", item="A145", barbs=[
        B(1, "Plain Speaking", 35, 100, None, "I'll say it plainly, since no one else will: your poem was long."),
        B(1, "Hammered Smile", 0, 100, "poise-", "What a brave choice of colours. Truly. Brave."),
        B(6, "Cold Quench", 55, 95, None, "You've cooled since winter court, I hear. So has every room you walk "
                                          "into."),
        B(11, "Anvil Silence", 70, 95, None, "(a long, ringing silence, exactly where the compliment should be)"),
        B(16, "Kaiu Fire", 90, 90, None, "The Kaiu test a blade by striking it. Yours bent on the first word.")]),
    "bronze": dict(name="Bronze Mask", type="Metal", base=[50, 50, 55, 40], src="common", barbs=[
        B(1, "Polished Remark", 30, 100, None, "Your fan is lovely. It must be the one your mother carried."),
        B(1, "Green with Age", 0, 100, "timing-", "Is that the new style? It was new when my grandfather wore it."),
        B(6, "Bell Tone", 50, 95, None, "Everyone heard what you said to the Crane. Everyone. Even the Crane."),
        B(11, "Tarnish", 70, 95, None, "I polished my opinion of you for an hour. It still came out dull."),
        B(16, "Temple Bell at Dawn", 85, 90, None, "Like the temple bell, you are loud, early, and nobody asked.")]),
    "oni": dict(name="Oni Mask", type="Metal", base=[60, 65, 50, 40], src="rival", barbs=[
        B(1, "Horned Grin", 40, 100, None, "Smile wider. It helps hide the rest of your face."),
        B(1, "Iron Club", 0, 100, "wit+", "(the mask laughs, once, like a club on a drum)"),
        B(6, "Demon's Courtesy", 60, 95, None, "Even an oni says please before it eats. You didn't, at dinner."),
        B(11, "Torn Gate", 75, 90, None, "I came through your defences like rice paper. Because they were."),
        B(16, "Ogre's Table Manners", 95, 85, None, "My lord the oni sends his regards. He says your manners remind "
                                                    "him of home.")]),
    # ------------------------------------------------------------------------------------------------ Wood
    "cedar": dict(name="Cedar Mask", type="Wood", base=[55, 50, 55, 40], src="story A146", item="A146", barbs=[
        B(1, "Sap and Splinter", 35, 100, None, "Your verse had such a strong root. Pity about everything that grew "
                                                "from it."),
        B(1, "Fragrant Pause", 0, 100, "heal", "(she breathes in the cedar and lets the insult pass through her)"),
        B(6, "Deep Roots", 55, 95, None, "My family has sat in these halls for six hundred years. Remind me how long "
                                         "yours has?"),
        B(11, "Knot in the Grain", 0, 100, "poise-", "Something's caught in your story. Just there. A knot. Shall I "
                                                     "pull it?"),
        B(16, "Felled Cedar", 90, 90, None, "The tallest cedar falls loudest. Do keep standing. We're all "
                                            "listening.")]),
    "willow": dict(name="Willow Mask", type="Wood", base=[50, 45, 50, 50], src="common", barbs=[
        B(1, "Bending Agreement", 30, 100, None, "Oh, you're quite right. Quite right. Everyone says so, behind "
                                                 "you."),
        B(1, "Weeping Branch", 0, 100, "timing-", "(she sighs, very gently, at nothing in particular)"),
        B(6, "River-Bank Gossip", 50, 95, None, "The ferrymen talk about you. They say you tip like a Crab."),
        B(11, "Supple Retort", 70, 95, None, "I bend. You break. That is the whole difference between us."),
        B(16, "Willow in the Storm", 85, 90, None, "I've weathered worse winds than you. Hotter ones, too.")]),
    "tengu": dict(name="Tengu Mask", type="Wood", base=[50, 60, 45, 60], src="rival", barbs=[
        B(1, "Long Nose", 40, 100, None, "I'd look down on you, but first I'd have to find you."),
        B(1, "Feather Flick", 0, 100, "wit+", "(she flicks an imaginary feather from her sleeve, unhurried)"),
        B(6, "Mountain Lesson", 60, 95, None, "The tengu taught the first swordsmen. Someone should teach you to "
                                              "sit."),
        B(11, "Crow's Cackle", 75, 90, None, "Ha! You thought that was clever. How sweet. How mortal."),
        B(16, "Sermon from the Peak", 95, 85, None, "From up here your ambitions look like ants. Very busy ants.")]),
    "munashii": dict(name="Munashii's Mask", type="Wood", base=[65, 45, 65, 35], src="story A151", item="A151",
                     barbs=[
        B(1, "Empty Bowl", 35, 100, None, "You've filled your speech with so much. Was any of it yours?"),
        B(1, "Still Breath", 0, 100, "heal", "(the plain mask says nothing, and the nothing steadies her)"),
        B(6, "Whose Face?", 55, 95, None, "Forgive me. Which of your faces am I speaking to today?"),
        B(11, "Unchosen", 0, 100, "poise-", "You don't have to choose, you know. You can simply stop pretending."),
        B(16, "Silent Self", 90, 90, None, "(the plain wooden face regards them, and they hear every unkind thing "
                                           "they ever thought of themselves)")]),
    # ------------------------------------------------------------------------------------------------ Fire
    "lacquer": dict(name="Fire-Lacquer Mask", type="Fire", base=[45, 60, 40, 55], src="common", barbs=[
        B(1, "Hot Lacquer", 35, 100, None, "Red suits you. It hides the blushing."),
        B(1, "Gloss", 0, 100, "wit+", "(her laugh is bright and sticky as fresh lacquer)"),
        B(6, "Burnt Offering", 55, 95, None, "A gift for the Champion? How thoughtful. He'll give it to his "
                                             "servants."),
        B(11, "Seven Coats", 70, 95, None, "Seven coats of lacquer, and I can still see straight through you."),
        B(16, "Crack in the Kiln", 88, 90, None, "Some pots crack in the kiln. It isn't shameful. It's only what "
                                                 "they were.")]),
    "hannya": dict(name="Hannya Mask", type="Fire", base=[50, 70, 40, 55], src="rival", barbs=[
        B(1, "Jealous Glance", 40, 100, None, "What a handsome escort. Does he know he's yours yet?"),
        B(1, "Smouldering", 0, 100, "timing-", "(the painted eyes follow them, slow and patient)"),
        B(6, "Letters", 60, 95, None, "Your husband writes beautiful letters. To several people."),
        B(11, "Horns Behind the Smile", 75, 90, None, "Smile, darling. The horns only come out when you frown."),
        B(16, "The Bell at Dojo-ji", 95, 85, None, "The bell at Dojo-ji is still warm, they say. Someone should "
                                                   "have kept his promises.")]),
    "giseiki": dict(name="Giseiki's Mask", type="Fire", base=[55, 65, 50, 50], src="story A150", item="A150", barbs=[
        B(1, "Apologetic Truth", 40, 100, None, "I'm so sorry. Someone should have told you, and it seems it has to "
                                                "be me."),
        B(1, "Warm Like Skin", 0, 100, "heal", "(Giseiki murmurs something kind inside the mask, and she steadies)"),
        B(6, "The Maker's Regret", 60, 95, None, "I made a mask like your face once. I broke it. I hope you don't "
                                                 "mind my saying."),
        B(11, "Hungry", 0, 100, "poise-", "Some masks are fuller than others. Yours seems... hungry."),
        B(16, "Red and Black", 95, 85, None, "Three hundred years in a mask teaches patience. You, sama, have "
                                             "exhausted it.")]),
    # ------------------------------------------------------------------------------------------------ Water
    "ink": dict(name="Ink Mask", type="Water", base=[50, 55, 45, 50], src="story A147", item="A147", barbs=[
        B(1, "Blotted Line", 35, 100, None, "Lovely brushwork in your letter. Was the blot on purpose? It's the best "
                                            "part."),
        B(1, "Washes Off", 0, 100, "heal", "(the ink runs a little, then sets again)"),
        B(6, "Ink Stone", 55, 95, None, "Your name will be in the histories. In a footnote. In a small brush."),
        B(11, "Tattooed Wall", 0, 100, "poise-", "A Togashi drew a wall on his face. You would need a castle."),
        B(16, "Last Stroke", 90, 90, None, "Every scroll ends somewhere. I think we've reached yours.")]),
    "rain": dict(name="Rain Mask", type="Water", base=[50, 45, 50, 50], src="common", barbs=[
        B(1, "Drizzle", 30, 100, None, "Ah. You've arrived. Like the rainy season: expected, endured."),
        B(1, "Grey Sky", 0, 100, "timing-", "(she says nothing at all, and the conversation clouds over)"),
        B(6, "Puddle Deep", 50, 95, None, "Such depth. Ankle-deep, I'd say. Perhaps shin."),
        B(11, "Leaking Roof", 70, 95, None, "Your secrets drip, my lord. We can all hear them in the night."),
        B(16, "Monsoon", 85, 90, None, "I'd hoped you would pass, like weather. Yet here you remain.")]),
    "noh": dict(name="Noh Ghost Mask", type="Water", base=[55, 60, 50, 50], src="rival", barbs=[
        B(1, "Ghost's Whisper", 40, 100, None, "Your grandfather sat in that seat. He said it fit him better."),
        B(1, "Pale Stare", 0, 100, "wit+", "(the white face turns, slowly, and does not blink, because it cannot)"),
        B(6, "Lingering", 60, 95, None, "Some guests stay long after the party. Most of them are dead. You're the "
                                        "exception."),
        B(11, "Restless Water", 75, 90, None, "I can't rest while your verse goes unanswered. No one can. It's that "
                                              "bad."),
        B(16, "The Drowned Act", 95, 85, None, "In the last act, the ghost gets the best lines. Here are mine.")]),
    # ------------------------------------------------------------------------------------------------ Earth
    "clay": dict(name="Clay Mask", type="Earth", base=[60, 45, 55, 40], src="common", barbs=[
        B(1, "Unfired", 35, 100, None, "So soft. You'll set, in time. Most do."),
        B(1, "Wet Hands", 0, 100, "poise-", "(she smooths her sleeve slowly, as if shaping something that isn't her "
                                            "sleeve)"),
        B(6, "Potter's Wheel", 55, 95, None, "You keep turning and turning, and nothing takes shape."),
        B(11, "Cracked Glaze", 70, 95, None, "Beautiful outside. One knock, and we'll know what's inside."),
        B(16, "Return to Earth", 88, 90, None, "We all go back to the earth eventually. You seem keen to start "
                                               "early.")]),
    "jade": dict(name="Jade Mask", type="Earth", base=[60, 55, 60, 40], src="story A149", item="A149", barbs=[
        B(1, "Clear Green", 40, 100, None, "How pure your intentions are. I can see right through them."),
        B(1, "Untainted", 0, 100, "heal", "(the jade cools against her skin; nothing they say can stick)"),
        B(6, "Remember Your Name", 60, 95, None, "I remember my name. Do you remember what yours used to mean?"),
        B(11, "Clean Finger", 0, 100, "poise-", "(she points, once, with one clean finger, at the stain on their "
                                                "sleeve)"),
        B(16, "Weighed in Jade", 95, 85, None, "Jade weighs a soul. Yours tipped the scale the wrong way, I'm "
                                               "afraid.")]),
    "fox": dict(name="Fox Mask", type="Earth", base=[50, 60, 45, 60], src="rival", barbs=[
        B(1, "Rice-Field Wink", 40, 100, None, "A fine harvest of compliments you brought. All chaff, but a fine "
                                               "harvest."),
        B(1, "Nine Tails", 0, 100, "timing-", "(a fox's yip of laughter, from somewhere just behind her)"),
        B(6, "Kitsune's Bargain", 60, 95, None, "I'll trade you a better poem for your worse one. No? Pity."),
        B(11, "Borrowed Shape", 75, 90, None, "I've worn many faces. None as forgettable as yours."),
        B(16, "Inari's Rice", 95, 85, None, "The fox steals only from the proud. Look how fat I've grown "
                                            "tonight.")]),
    # ------------------------------------------------------------------------------------------------ Stone
    "stone": dict(name="Stone Mask", type="Stone", base=[65, 45, 70, 25], src="common", barbs=[
        B(1, "Stone Face", 35, 100, None, "(an expression of perfect, carved disinterest)"),
        B(1, "Weathered", 0, 100, "wit+", "(she simply waits, the way a stone waits for the rain to finish)"),
        B(6, "Millstone", 55, 95, None, "You grind on, my lord. Grind, grind, grind. And the flour is always grey."),
        B(11, "Garden Rock", 0, 100, "poise-", "Raked gravel goes round a stone. Everyone goes round you, too."),
        B(16, "Kaiu Wall", 88, 90, None, "Shout at a wall all you like. The Wall has heard worse. From the "
                                         "Shadowlands.")]),
    "komainu": dict(name="Komainu Mask", type="Stone", base=[65, 55, 65, 35], src="rival", barbs=[
        B(1, "Open Mouth", 40, 100, None, "Ah. You may enter. The servants' door is to the left."),
        B(1, "Closed Mouth", 0, 100, "wit+", "(the guardian's stone mouth shuts with a satisfied click)"),
        B(6, "Guardian's Ledger", 60, 95, None, "Your name isn't on the list. It isn't on any list, is it?"),
        B(11, "Paw on the Ball", 75, 90, None, "I keep the world under one paw. You I keep under a claw."),
        B(16, "Temple Gate", 95, 85, None, "Every shrine has two guardians: one to welcome, one to judge. I'm not "
                                           "the one who welcomes.")]),
    # ------------------------------------------------------------------------------------------------ Silk
    "shosuro": dict(name="Shosuro Half-Mask", type="Silk", base=[50, 55, 45, 55], src="start", barbs=[
        B(1, "Silk Whisper", 35, 100, None, "Your secret is safe with me. With me, and the eleven people I've "
                                            "told."),
        B(1, "Half a Smile", 0, 100, "poise-", "(she smiles with exactly half her face; the other half is "
                                               "listening)"),
        B(6, "Rehearsal", 55, 95, None, "I rehearsed this conversation last night. You were wittier in rehearsal."),
        B(11, "Untied Cord", 0, 100, "timing-", "Your obi has come loose. No, don't look. It's far too late to "
                                                "look."),
        B(16, "The Many Faces", 90, 90, None, "I could be anyone. Tonight I'm the one who remembers everything you "
                                              "said.")]),
    "silk": dict(name="Silk Mask", type="Silk", base=[45, 55, 40, 65], src="story A148", item="A148", barbs=[
        B(1, "Soft as Breath", 35, 100, None, "How brave, to wear cotton to court. It must be so... breathable."),
        B(1, "Smooth Fold", 0, 100, "wit+", "(her sleeve falls into a perfect fold, as if it had rehearsed)"),
        B(6, "Weaver's Count", 55, 95, None, "My robe has nine hundred threads to the inch. Your argument has "
                                             "three."),
        B(11, "Silk over Steel", 70, 95, None, "Silk wraps a blade, my lord. Wouldn't you like to know whose?"),
        B(16, "Imperial Bolt", 90, 90, None, "This silk was a gift from the Empress. Yours was a gift too, I'm "
                                             "sure. From someone.")]),
    "koomote": dict(name="Ko-omote Mask", type="Silk", base=[50, 60, 45, 60], src="rival", barbs=[
        B(1, "Innocent Question", 40, 100, None, "Forgive me, I'm new to court. Is it the custom to say that out "
                                                 "loud?"),
        B(1, "Downcast Eyes", 0, 100, "heal", "(the young girl's face tilts down, and the room forgives her "
                                              "everything)"),
        B(6, "Blossom Fall", 60, 95, None, "Blossoms are lovely because they don't stay. You've stayed quite a "
                                           "while."),
        B(11, "Maiden's Fan", 0, 100, "poise-", "(a giggle behind her fan, and the giggle is entirely about them)"),
        B(16, "Moon on the Water", 95, 85, None, "You reach for me like the moon in a pond. Mind your sleeves. It's "
                                                 "deep.")]),
}

# The castle town's mask-maker (M347): what she sells to a player of the game (zeni).
SHOP = [("lacquer", 300), ("clay", 300), ("stone", 300), ("bronze", 400), ("willow", 400), ("rain", 400)]

# Random duels: on each Kyuden Bayushi map, walking a while may bring a masked stranger (one of the map's three hidden
# duellists) out from behind a screen. Their masks are commons; levels by how deep into the castle the map is.
COMMONS = ["bronze", "willow", "lacquer", "rain", "clay", "stone"]
TIERS = {  # map -> (lowest, highest level, masks they carry at most)
    "M520": (2, 4, 1), "M579": (3, 6, 1), "M580": (3, 6, 1),
    "M581": (5, 8, 1), "M582": (5, 8, 1), "M583": (5, 8, 2),
    "M584": (8, 11, 2), "M585": (8, 11, 2), "M586": (9, 12, 2),
    "M587": (11, 14, 2), "M588": (12, 15, 2), "M589": (12, 15, 2),
    "M521": (14, 16, 2), "M522": (15, 17, 2), "M523": (16, 18, 3), "M524": (17, 19, 3)}
DUELLIST_MODELS = ["EP620", "EP621", "EP640"]           # Soshi courtier, Bayushi courtier, masked citizen
DROP_PCT = 20                                           # a stranger leaves the mask behind (a mask she lacks)

# Named players. They see her (7 m, in front of them), walk up and challenge once; after that they play again on a
# word. A gift mask on the first win (theirs), zeni every win (half on a rematch), gear and Honor from the keep's four.
RIVALS = [
    dict(id="tsuyu", name="Shosuro Tsuyu", mdl="EP635", map="M520", masks=[("willow", 3)], zeni=60,
         who="a page of the house, twelve and very serious",
         hello="Shosuro-sama! You wear a mask. That means you play. That means you play me.",
         win="(bowing very low) I'll practise. I'll practise until my face hurts.",
         lose="You need to practise, Shosuro-sama. I'll wait.",
         after="Your barbs are better than mine. For now."),
    dict(id="gentaro", name="Bayushi Gentaro", mdl="EP623", map="M579", masks=[("bronze", 4), ("stone", 5)], zeni=120,
         who="a gate guard who has been insulted by experts",
         hello="Halt. Nobody passes the barracks without a word. A sharp one.",
         win="...That one stung. Pass, then.",
         lose="Back to the gate with you. Come back with a sharper tongue.",
         after="I'll be thinking about that one on watch tonight."),
    dict(id="heishiro", name="Heishiro the groom", mdl="EP640", map="M580", masks=[("bronze", 6)], zeni=90,
         who="a groom in a borrowed courtier's mask",
         hello="My lady! The horses don't talk back. Would you?",
         win="(laughing) The horses never said anything that bad about me.",
         lose="Even the horses were laughing, my lady.",
         after="I'll tell the horses. They'll be pleased for you."),
    dict(id="karyu", name="Bayushi Karyu", mdl="EP620", map="M581", masks=[("lacquer", 7), ("oni", 9)], zeni=200,
         gift="oni", who="a duellist who prefers words because they leave no blood on the mats",
         hello="Shosuro. A blade takes a second. A word takes a whole winter to heal. Draw.",
         win="Hm. Take the oni. He's wasted on a man you've just made blush.",
         lose="Words leave no marks. You'll feel this one anyway.",
         after="The oni likes you better. He always did prefer women."),
    dict(id="sumie", name="Yogo Sumie", mdl="EP621", map="M582", masks=[("rain", 7), ("koomote", 8)], zeni=200,
         gift="koomote", who="a poetess who writes verses about her guests, afterwards",
         hello="A Shosuro in the garden. How fortunate. I've been short of a subject.",
         win="(fanning herself) Take the girl's face. She never did suit me.",
         lose="I shall write about you. Not kindly.",
         after="I've started the poem. It's about you. It's very flattering. Mostly."),
    dict(id="kaneko", name="Ide Kaneko", mdl="EP640", map="M583", masks=[("clay", 8), ("fox", 9)], zeni=220,
         gift="fox", who="a Unicorn guest who learned the game from losing at it",
         hello="They told me the Scorpion play this for fun. I'm here to see if it's fun yet.",
         win="It is fun! For one of us. Here, the fox is yours.",
         lose="Oh. Oh, that IS fun.",
         after="I'm writing home about you. They won't believe a word."),
    dict(id="nobuo", name="Soshi Nobuo", mdl="EP620", map="M584", masks=[("stone", 10), ("noh", 11)], zeni=260,
         gift="noh", who="an archivist who has catalogued every insult since the Second Day of Thunder",
         hello="Shosuro. Your file is thin. Let us add to it.",
         win="Filed under: defeats, regrettable. The ghost is yours.",
         lose="Filed under: Shosuro, adequate. For now.",
         after="I've updated your file. It's thicker now. Congratulations."),
    dict(id="masaru", name="Bayushi Masaru", mdl="EP620", map="M585",
         masks=[("lacquer", 10), ("bronze", 11), ("clay", 11)], zeni=300, gear="A193",
         who="the officer who keeps the keep's door and its gossip",
         hello="Nobody climbs the keep who can't hold their face at the door. Hold yours.",
         win="Take my fan. You'll need something to hide behind up there.",
         lose="The keep is closed to you. Not literally. Socially.",
         after="They're talking about you on the second floor. Good things. Mostly."),
    dict(id="asami", name="Shosuro Asami", mdl="EP635", map="M586", masks=[("rain", 12), ("hannya", 13)], zeni=300,
         gift="hannya", who="an actress who plays the jealous wife in every shrine play",
         hello="Every play needs a jealous woman, Mitsue. Tonight it's me. Tomorrow, you.",
         win="Take her. She's better at being angry than I am.",
         lose="You'll make a lovely jealous wife one day. Practise.",
         after="I'm playing a forgiving woman next week. It's my hardest role."),
    dict(id="ochika", name="Ochika", mdl="EP640", map="M587", masks=[("clay", 12), ("willow", 13)], zeni=180,
         who="a kitchen girl who has heard everything said over every tray",
         hello="Begging your pardon, lady. I've carried trays for every lord in this castle. I know what they say.",
         win="(curtsying, grinning) I'll save you the good dumplings.",
         lose="Pardon, lady. Even the cook heard that.",
         after="The cook says you'll do. That's the highest praise there is."),
    dict(id="shiramu", name="Bayushi Shiramu", mdl="EP620", map="M588", masks=[("willow", 14), ("tengu", 15)],
         zeni=340, gift="tengu", who="an old master who has played since before the Champion was born",
         hello="Ah. The young Shosuro. Sit. Lose slowly; I'm old and I enjoy it.",
         win="(a dry laugh) Take the tengu. He's been bored with me for years.",
         lose="You'll improve. I won't. That's the beauty of it.",
         after="Come back when I'm dead. I'll still win."),
    dict(id="tetsue", name="Yogo Tetsue", mdl="EP621", map="M589", masks=[("stone", 13), ("komainu", 15)], zeni=340,
         gift="komainu", who="a watch-officer who guards the terrace and its view of everyone",
         hello="From up here I see everyone who comes in. I saw you. I have notes.",
         win="Take the lion-dog. He's tired of watching.",
         lose="Noted.",
         after="I've moved you to the other list. The short one."),
    dict(id="kaname", name="Shosuro Kaname", mdl="EP635", map="M521",
         masks=[("lacquer", 15), ("noh", 15), ("willow", 16)], zeni=500, gear="A194",
         who="the stage-master of the house theatre",
         hello="The house theatre needs a lead. Audition. Here. Now.",
         win="The part is yours. And the cord: every lead ties her mask with it.",
         lose="Understudy. Come back when you've learned your lines.",
         after="Opening night is whenever you say."),
    dict(id="rieko", name="Soshi Rieko", mdl="EP621", map="M522",
         masks=[("rain", 16), ("fox", 17), ("stone", 17)], zeni=600, gear="A195", honor=1,
         who="secretary of the council, who writes down what the council didn't say",
         hello="The council sits in silence. I write the silence down. Let us see what you leave unsaid.",
         win="Take the seal. When you say nothing now, it will be official.",
         lose="Minuted: the Shosuro had nothing to say.",
         after="I wrote down your silence. It was very eloquent."),
    dict(id="saburo", name="Yogo Saburo", mdl="EP620", map="M523",
         masks=[("hannya", 17), ("komainu", 18), ("clay", 18)], zeni=700, gear="A196", honor=1,
         who="keeper of the Yogo curse-ledgers",
         hello="Every insult is a small curse, Shosuro. I keep the ledger. Let's see what you owe.",
         win="Your account is settled. Take the charm; it balances the books.",
         lose="Entered in the ledger. Interest accrues.",
         after="Your page is blank again. Enjoy it."),
    dict(id="kyoko", name="Bayushi Kyoko", mdl="EP621", map="M524",
         masks=[("koomote", 18), ("oni", 19), ("tengu", 19), ("noh", 20)], zeni=1000, gear="A197", honor=1,
         who="Mistress of Masks of Kyuden Bayushi, who has never lost in this castle",
         hello="So you're the one climbing my stairs. Every face in this castle is mine, Shosuro. Let's see yours.",
         win="(she takes off her own mask, and smiles with her real face) ...Wear the red one. You've earned it.",
         lose="(she doesn't even lower her fan) Again, when you're ready. I'll still be here.",
         after="Every face in this castle is mine. Except yours, it seems."),
]

# Gear (gen_data adds the items; numbers here for the docs and gen_maps): accessory id, name, description.
GEAR = {
    "A193": ("Courtier's Fan", "Bayushi Masaru's fan, for hiding a smile at court. (Speed +6)"),
    "A194": ("Lead Actor's Mask Cord", "The house theatre's lead ties her mask with this red cord. (Magic DEF +12%)"),
    "A195": ("Council Seal of Silence", "A small seal for minuting what no one said. (Magic ATK +10%)"),
    "A196": ("Curse-Ledger Charm", "A Yogo ledger-charm: every account settled. (Critical +8%)"),
    "A197": ("Mistress's Red Mask", "Bayushi Kyoko's red mask, given to the only player who beat her in this castle. "
                                    "(Attack +10%, Speed +6)"),
}

# Rules the plugin reads.
RULES = {
    "sleeve": 4,                    # masks carried into a duel (the rest wait on the stand in the guest pavilion)
    "maxlevel": 20,
    "see_range": 7.0, "see_cone": 60,
    "walk_per_roll": 22.0, "random_pct": 16,    # metres walked per roll on a castle map; chance a stranger steps out
    "honor_cap": 3,
}


def main():
    for k, m in MASKS.items():
        assert m["type"] in TYPES, k
        assert len(m["barbs"]) == 5, k
        for b in m["barbs"]:
            assert len(b["name"]) <= 22, b["name"]
            assert all(ord(c) < 128 for c in b["line"] + b["name"]), b["name"]     # (ASCII game terms)
    for r in RIVALS:
        for mk, lv in r["masks"]:
            assert mk in MASKS, (r["id"], mk)
        if r.get("gift"):
            assert MASKS[r["gift"]]["src"] == "rival", r["id"]
    data = {"types": TYPES, "colour": TYPE_COLOUR, "fears": FEARS, "masks": MASKS, "shop": SHOP, "commons": COMMONS,
            "tiers": TIERS, "duellists": DUELLIST_MODELS, "drop_pct": DROP_PCT,
            "rivals": [dict(r, masks=[list(x) for x in r["masks"]]) for r in RIVALS],
            "gear": {k: v[0] for k, v in GEAR.items()}, "rules": RULES}
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=1, ensure_ascii=True)
    write_doc()
    print("sadane: %d masks, %d barbs, %d rivals -> %s" % (len(MASKS), 5 * len(MASKS), len(RIVALS),
                                                           os.path.normpath(OUT_JSON)))


def write_doc():
    L = ["# The Game of Masks (Kyuden Bayushi)", "",
         "Generated by `tools/gen_sadane.py` (the one source; plugin `RokuganSadane.sk` reads "
         "`resource/sadane/sadane.json`). Do not edit by hand.", "",
         "An optional side game on Shosuro Mitsue's path, open after Scorpion Ch1. Masks are the players: each has a "
         "material, a level and the barbs (sadane pokes) it knows; more barbs as it levels. Duels are played in the "
         "castle in a 3/4 view from behind Mitsue: **Barb** (the equipped mask's list), **Swap** (another mask from "
         "the sleeve; it costs the turn), **Withdraw** (strangers only).", "",
         "## Rules", "",
         "- **Composure** is a mask's health; at 0 it *loses face* and can't play until restored (tea from Soshi "
         "Kagero in the Entrance reception, or the guest pavilion's tea tray). Losing a duel restores every mask; "
         "nothing else is lost.",
         "- **Wit** drives a barb, **Poise** turns it aside, **Timing** decides who speaks first.",
         "- **Effects**: *poise-* lowers the target's Poise a step, *timing-* its Timing, *wit+* raises the wearer's "
         "Wit, *heal* restores a third of the wearer's composure. Steps go to +/-3 (x1.25 / x0.8 each).",
         "- **Experience** goes to the mask that wins the exchange (half to masks that played earlier in the duel). "
         "Max level %d. A level that matches a barb's level teaches it." % RULES["maxlevel"],
         "- **Sleeve**: %d masks are carried into a duel; the rest wait on the mask stand (guest pavilion)." %
         RULES["sleeve"],
         "- **Random duels**: walking the castle, a masked stranger sometimes steps out. Their masks are commons; "
         "%d%% leave theirs behind if she doesn't have it." % DROP_PCT,
         "- **Rivals** see her (%d m, in front of them), walk up and challenge once; afterwards they play again on a "
         "word. Gift masks and gear on the first win; zeni every time (half on a rematch); Honor +1 from three keep "
         "champions (cap %d)." % (RULES["see_range"], RULES["honor_cap"]), "",
         "## Materials", "",
         "Wood fears metal, metal fears fire, fire fears water, water fears earth, earth fears wood; stone and silk "
         "fear each other. A barb of the material a mask fears does x2; a barb of the material it overcomes does "
         "x0.5.", "",
         "| Barb \\ Mask | " + " | ".join(TYPES) + " |", "|---" * (len(TYPES) + 1) + "|"]
    for a in TYPES:
        L.append("| **%s** | " % a + " | ".join({2.0: "x2", 0.5: "x0.5", 1.0: "-"}[mult(a, d)] for d in TYPES) + " |")
    L += ["", "## Masks", ""]
    for k, m in MASKS.items():
        b = m["base"]
        L += ["### %s (%s)" % (m["name"], m["type"]), "",
              "Composure %d, Wit %d, Poise %d, Timing %d. From: %s." % (b[0], b[1], b[2], b[3], m["src"]), "",
              "| Lv | Barb | Power | Effect | Line |", "|---|---|---|---|---|"]
        for x in m["barbs"]:
            L.append("| %d | %s | %s | %s | %s |" % (x["lv"], x["name"], x["power"] or "-", x["fx"] or "-",
                                                     x["line"].replace("|", "/")))
        L.append("")
    L += ["## Rivals", "", "| Where | Rival | Masks | Prize |", "|---|---|---|---|"]
    for r in RIVALS:
        prize = ["%d zeni" % r["zeni"]]
        if r.get("gift"):
            prize.append(MASKS[r["gift"]]["name"])
        if r.get("gear"):
            prize.append(GEAR[r["gear"]][0])
        if r.get("honor"):
            prize.append("Honor +1")
        L.append("| %s | %s, %s | %s | %s |" % (r["map"], r["name"], r["who"],
                                                ", ".join("%s Lv%d" % (MASKS[m]["name"], lv) for m, lv in r["masks"]),
                                                ", ".join(prize)))
    L += ["", "## Mask-maker (castle town)", ""] + ["- %s: %d zeni" % (MASKS[k]["name"], z) for k, z in SHOP]
    L += ["", "## Gear", ""] + ["- **%s** %s: %s" % (k, v[0], v[1]) for k, v in GEAR.items()]
    with open(OUT_DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
