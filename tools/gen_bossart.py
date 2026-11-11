"""Octopath-style bosses (user: "larger than life bosses on the left hand side of the screen, minions in front"):
L5R wiki art (_sources/wiki_art, fetched with the MediaWiki API) cut out of its background, tinted, pixelated and
quantized like the 16-Bit-Style-Pixel-Art-Converter the user linked (_sources/pixelconv, MIT: downscale, ADAPTIVE
palette, nearest-neighbour), outlined like the cast, then animated by gen_enemy_art.animate.
Big frames are drawn at the cast's pixel density (same per-pixel scale), so a 150 px boss stands ~3x a traveler.
Writes resource/enemy_pic/boss_<key>.png, enemy_pic.json EP120+, preview _art/preview/bosses.png.
Run after gen_human_enemies.py / gen_monsters.py:  python -E tools/gen_bossart.py [boss key ...]
"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_sprites2d as g  # noqa: E402
import gen_enemy_art as ea  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "..", "_sources", "wiki_art")


def ramp(*stops):
    """Gradient map for line art: luminance 0..1 -> colour through the given stops."""
    stops = [np.array(c, np.float32) for c in stops]

    def f(lum):
        t = np.clip(lum, 0, 1) * (len(stops) - 1)
        i = np.minimum(t.astype(int), len(stops) - 2)
        w = (t - i)[..., None]
        a = np.stack(stops)[i]
        b = np.stack(stops)[i + 1]
        return a * (1 - w) + b * w
    return f


# key: (epid, source, crop box, mode, target height px, tint, label)
BOSSES = [
    ("nezumi_shaman", "EP120", "Nezumi_Shaman_2.jpg", (0, 20, 417, 770), "line", 132,
     ramp((34, 24, 22), (92, 68, 52), (158, 128, 96), (214, 196, 160), (240, 232, 214)), "Nezumi Shaman"),
    ("troll", "EP121", "Troll_2.jpg", (40, 8, 508, 612), "line", 156,
     ramp((26, 32, 24), (72, 86, 60), (126, 140, 100), (182, 186, 146), (226, 220, 196)), "Troll"),
    ("akutsukai", "EP122", "Onikage.jpg", (0, 0, 600, 450), "paint", 150, None, "Moto Akutsukai"),
    # Oni no Kommei: the wiki's only Kommei picture is a crowd scene, so the two-faced boss wears the TCG/Diskwars art
    # of Oni no Megada, a two-headed oni (user: "I'm sure you can find something")
    ("kommei", "EP123", "cand/Oni_no_Megada-Diskwars.jpg", (48, 96, 462, 356), "green", 150, None, "Oni no Kommei"),
    # Crab Ch4: the cellar ogre (mini-boss of b_siege_breach_b) and Oni no Tsukakoro (the bouncing bone-cage)
    ("cellar_ogre", "EP124", "Ogre.jpg", (0, 0, 497, 359), "paint", 140, None, "Cellar Ogre"),
    ("tsukakoro", "EP125", "Tsukakoro_no_Oni.jpg", (30, 0, 690, 296), "line", 140,
     ramp((30, 18, 36), (86, 56, 92), (152, 120, 146), (218, 202, 194), (244, 236, 224)), "Oni no Tsukakoro"),
    # Crane Ch1: Kakita Yasurugi, an adventure NPC with no card of his own, wears the wiki's painted "Kakita Bushi"
    # (a calm, white-haired Crane swordsman, hand on the hilt) on its plain white ground (mode "white": keep colour)
    # Crane Ch2 (b_boss_iron_cranes): Doji Miyako watches from the ridge while her charm holds the three generals (they
    # are regular-size sprites in front). The wiki's painted "Doji Ayano": a serene white-haired Crane lady with blue
    # eyes (Nashiko's tell) in pale teal, on a warm golden room (keyed out). Three identical busts of the generals
    # were tried first: stacked, cut off at the screen's top, floating like cards.
    ("miyako", "EP127", "cand_crane6/Doji_Ayano.jpg", (1000, 0, 2800, 3200), "coolkey", 180, None, "Doji Miyako"),
    # Crane Ch3 "The White Squid": the pirate brothers. Chihaya the Quick (mid-boss) wears the painted "Shinjo Bushi"
    # (a woman in armour on white), hue-shifted from Unicorn purple to sea teal; Yosuke the Bold the painted "Ronin
    # Bushi" (Ronin_3: a ronin in mismatched armour, caption erased); Katsuo the White Brother "Iuchiban 2" (white
    # robes, a bloody blade at the sash; Iuchiban's line fits Yajinden's heir), his black hair whitened: the albino.
    ("chihaya", "EP128", "cand_crane8/Shinjo_Bushi.jpg", (0, 0, 546, 1088), "white", 170, None, "Chihaya the Quick"),
    ("yosuke", "EP129", "cand_crane8/Ronin_3.jpg", (0, 0, 348, 521), "white", 170, None, "Yosuke the Bold"),
    ("katsuo", "EP130", "cand_crane9/Iuchiban_2.jpg", (0, 0, 396, 500), "coolkey", 190, None,
     "Katsuo the White Brother"),
    # Crane Ch4 "The Play No One Performs": Kakita Masanori, Rensei's father, wears the wiki's painted "Kakita
    # Toshimoko 5" (a white-haired old master in Kakita blue, hand on the hilt, a full figure in black ink on a cyan
    # swirl: mode "inkflood"); the archive's shelf kami (mid-boss) the wiki's "Shiryo" (an ancestor spirit, line art on
    # white, tinted ghost-blue): a Doji ancestor guarding the family's shame. Tried first: "Tsukumogami" (a ghost over
    # armour, semi-transparent on a dark ground: a broken mesh) and a stone kami (it merges into its rocks).
    ("masanori", "EP131", "cand_crane11/Kakita_Toshimoko_5.jpg", (0, 0, 1428, 1896), "inkflood", 200, None,
     "Kakita Masanori"),
    ("shelf_kami", "EP132", "cand_crane12/Shiryo.jpg", (0, 40, 346, 528), "line", 190,
     ramp((22, 30, 52), (66, 88, 128), (132, 164, 204), (200, 220, 240), (238, 244, 252)), "Shelf Kami"),
    # Lion Ch1 "The Blood of Family": O-Tamai in a borrowed body wears the painted "Bloodspeaker" (a screaming man in
    # red robes, blood magic streaming from his hands); the red-shadow oni is "Akeru no Oni" (ink on paper, tinted
    # blood-red); the possessed Matsu Nagai (mid-boss) the painted "Lion Bushi" (gold Lion armour, on white).
    ("otamai", "EP133", "cand_crane7/Bloodspeaker.jpg", (0, 0, 613, 565), "paint", 200, None, "O-Tamai"),
    ("red_oni", "EP134", "cand_lion1/Akeru_no_Oni_2.jpg", (0, 0, 548, 560), "line", 125,
     ramp((30, 6, 10), (110, 20, 26), (186, 50, 46), (236, 140, 120), (250, 226, 214)), "Red-shadow Oni"),
    ("nagai", "EP135", "cand_lion1/Lion_Bushi.jpg", (0, 0, 304, 525), "white", 180, None, "Possessed Matsu Nagai"),
    # Lion Ch2 "Shadow of a Doubt": Oni no Ianwa, the wiki's painted "Ianwa no Oni" (the slug-oni with a ring of teeth;
    # its pile of stolen treasure is cut away)
    ("ianwa", "EP136", "cand_lion2/Ianwa_no_Oni.jpg", (0, 0, 314, 241), "paint", 190, None, "Oni no Ianwa"),
    # Lion Ch3 "The Deadly Message": the Seppun-trained duelist who leads Yachiko's killers wears the painted "Harue
    # (duelist)" (a tall topknotted man, a long perfect blade, on a bright mountain sky). (The "Kakita Duelist" line
    # art tinted green was tried first: a monochrome man reads as a ghost.)
    ("seppun_duelist", "EP137", "cand_lion3/Harue__duelist_.jpg", (290, 0, 800, 590), "paint", 210, None,
     "Seppun-trained Duelist"),
    # Lion Ch4 "Sorrow's Path": Matsu Rokuro, the huge Matsu champion ridden by a Fear-demon, wears the painted
    # "Matsu Gohei 3" (a giant in gold lacquer and a lion mane on a rock at sunset; a 40% copy for GrabCut)
    ("rokuro", "EP138", "cand_lion4/Matsu_Gohei_3_small.jpg", (140, 40, 780, 905), "paint", 240, None,
     "Matsu Rokuro"),
    # Phoenix Ch1 "The Silent Kami": Ashimoshi, the samurai's ghost spinning in a silent hurricane in Hiruto's west
    # tower, wears the painted "Daidoji Yurei" (a pale ghost-samurai, robes streaming in the wind; the wiki has no
    # Ashimoshi art)
    ("ashimoshi", "EP139", "cand_phx1/Daidoji_Yurei.jpg", (160, 30, 440, 455), "paint", 150, None, "Ashimoshi"),
    # Phoenix Ch2 "The Silent Court": Hioninmaru, Kokujin's cowardly bloodspeaker ("a thin man in red ... sweating"),
    # wears "Bloodspeaker 3" (line art: a thin man kneeling in a candle circle, cutting his own arm to pay for maho),
    # in a blood-red ramp like the red-shadow oni
    ("hioninmaru", "EP140", "cand_phx2/Bloodspeaker_3.jpg", (120, 0, 546, 415), "line", 125,
     ramp((18, 4, 8), (84, 10, 18), (150, 24, 30), (196, 60, 52), (232, 190, 172)), "Hioninmaru"),
    # Phoenix Ch3 "The Darkfever": Oni no Kuzushi wears the wiki's own "Kuzushi no Oni" (white line work on a black,
    # starry ground: the mask is built from the inverted image, INVERT) in a bruised fever ramp; Mieko's dark half
    # wears the painted "Isawa Shugenja" (a woman with burning eyes), its fire turned black-violet (HUE_SHIFT, LIFT)
    ("kuzushi", "EP141", "cand_phx3/Kuzushi_no_Oni.jpg", (0, 0, 518, 470), "line", 135,
     ramp((18, 10, 22), (64, 36, 74), (116, 84, 118), (168, 176, 138), (226, 236, 204)), "Oni no Kuzushi"),
    ("mieko_dark", "EP142", "cand_phx2/Bloodspeaker_2.jpg", (0, 90, 380, 543), "paint", 130, None,
     "Mieko (dark half)"),
    # Dragon Ch2 "The Painting": Seppun Ushimo, the Imperial guard of the year 400 who wants to die, wears the wiki's
    # line art "Seppun Ishikawa 2" (an armoured Seppun with a long blade, on white) in Seppun green and gold
    ("ushimo", "EP143", "cand_dragon2/Seppun_Ishikawa_2.jpg", (0, 0, 448, 526), "line", 150,
     ramp((14, 26, 20), (36, 76, 52), (70, 130, 86), (186, 180, 110), (240, 236, 214)), "Seppun Ushimo"),
    # Dragon Ch3 "Past Mistakes": Togashi Akuro (an old ise zumi who wears faces; calm, unhurried) wears the wiki's
    # painted "Togashi Gozato" (an old bald monk with a goatee and tattooed arms, on a plain cream ground)
    ("akuro", "EP144", "cand_dragon3/Togashi_Gozato.jpg", (0, 0, 487, 637), "paperkey", 160, None, "Togashi Akuro"),
    # Dragon Ch4 "The Battle of the White Stag": Kakita Kumpei, the thin, elegant failed artist, wears the wiki's painted
    # "Kakita Tadanobu" (a young Crane man in blue robes, a green sash flying) on its pale ground (paperkey)
    ("kumpei", "EP145", "cand_dragon4/Kakita_Tadanobu.jpg", (150, 0, 1900, 1537), "paperkey", 150, None,
     "Kakita Kumpei"),
    # Scorpion Ch1 "Blood and Iron": Kitsune Hana possessed by a Greater Kansen wears the wiki's painted "Kansen
    # (TCG)": a yellow-green leaf-storm spirit looming over a grey-haired woman who lifts a bowl of blood
    ("kansen_hana", "EP146", "cand_scorpion1/Kansen_(TCG).jpg", (0, 0, 578, 506), "paint", 165, None,
     "Kansen-Hana"),
    # Scorpion Ch2 "City of Masks": Abbot Munashii kneels before the vast faceless shadow he prays to; the wiki's
    # line art "Goju Assassin" (a kneeling man, a faceless figure rising behind him) in a cold dusk ramp
    ("munashii", "EP147", "cand_scorpion2/Goju_Assassin.jpg", (0, 0, 717, 756), "line", 165,
     ramp((14, 12, 22), (52, 44, 70), (104, 96, 122), (176, 168, 182), (234, 230, 226)), "Abbot Munashii"),
    # Scorpion Ch4 "The Eve": the Bloodspeaker remnant who waits at the crater in Mitsue's own face wears the wiki's
    # painted "Kitsune Impersonator Tradition" (a woman in a red kimono lowering a fox mask from her face, a blade at
    # her hip; the fox drawn on the wall behind is cropped away)
    ("stolen_face", "EP148", "cand_scorpion1/Kitsune_Impersonator_Tradition.jpg", (690, 0, 1181, 812), "paint", 175,
     None, "Bloodspeaker Remnant"),
    # Unicorn Ch1 "Fault Lines": Naohida, the bearded peasant-raised ronin (silk under dirty cotton, a gaijin dao),
    # wears the wiki's painted "Koji (ronin)" (a bearded man drawing a blade; the cherry garden behind is cut away)
    ("naohida", "EP150", "cand_unicorn1/Koji_(ronin).jpg", (150, 60, 1050, 1400), "paint", 170, None, "Naohida"),
    # Unicorn Ch3 "The Noblest Blood": the mine guardian, a corpse in Iuchi armour three hundred years old, wears the
    # wiki's "Undead (TCG)" (an armoured dead samurai with a spear, red eyes, on a white ground; the ghost-fire at its
    # feet stays: the mine's dead)
    ("mine_guardian", "EP152", "cand_unicorn3/Undead_(TCG).jpg", (0, 60, 1920, 2150), "white", 180, None,
     "Mine Guardian"),
    # Unicorn Ch4 "Regret": the Shuten Doji of Regret ("grotesquely elongated, eyes that pour constant tears ... its
    # body trails off into a salty cloud of tears", Fortune's Lost p.42) wears the wiki's pencil "Shuten Doji 2" (a
    # skeletal crowned figure trailing into cloud; caption and signature cropped), tinted the grey-violet of old tears;
    # Iuchi Kurosho, the possessed old meishodo master, the painted "Iuchi Haruma" (a grey-bearded Iuchi in purple
    # robes reading a scroll, maho skulls wreathing him)
    ("regret", "EP154", "cand_unicorn4/Shuten_Doji_2.jpg", (60, 0, 529, 560), "line", 230,
     ramp((20, 16, 34), (60, 50, 86), (120, 108, 150), (190, 186, 214), (236, 236, 246)), "Shuten Doji of Regret"),
    ("kurosho", "EP156", "cand_unicorn4/Iuchi_Haruma.jpg", (170, 0, 1080, 941), "paint", 185, None, "Iuchi Kurosho"),
    # Ronin Ch1 "What's Eating the Eta": the two crow-tengu on the log bridge (Honor and Eta: "crow-like features and
    # black wings clad in rich red silk kimonos"): the wiki's painted "Ajari" (a crow tengu in a red kimono with a staff,
    # on a mountain peak; the sky cut away) and "Tengu" (a crow tengu with a katana, in blue); Tomie Cho's tiger form,
    # the painted "Tiger" (a tiger walking toward you, on a green wall)
    ("tengu_red", "EP158", "cand_ronin1/Ajari.jpg", (0, 0, 1509, 1090), "paint", 165, None, "Crow-Tengu"),
    ("tomie_tiger", "EP182", "cand_ronin1/Tiger.jpg", (0, 0, 238, 249), "paint", 175, None, "Tomie Cho"),
    # Ronin Ch2 "The Noble and the Ronin": the lead enforcer of the Order of the Snake wears the wiki's painted "Kolat
    # Assassin" (a grey-robed man with glowing eyes and a bloodied blade, a storm behind the bars; the body on the floor
    # and the window cut away); Ronin Ch3 "The Village of the Wounded Lion": the shade of the Crab lord whose rebel
    # guards stole the prince (Past Heroes: Hida Kito, cut in two in the pagoda) wears the card art "Shiryo no Hida" (a
    # screaming green spirit of a Crab, fading into the dark)
    ("order_enforcer", "EP176", "cand_ronin2/Kolat_Assassin.jpg", (0, 0, 480, 479), "paint", 175, None,
     "Enforcer of the Order"),
    ("crab_shade", "EP178", "cand_ronin3/Shiryo_no_Hida-card.jpg", (50, 117, 378, 352), "paint", 190, None,
     "Shade of the Crab Lord"),
    # Ronin Ch4 "The Oracle's Choice": the Great Naga's champion at the top of the switchback stair wears the front naga
    # of the wiki's painted "Naga Spearmen 2" (a green, serpent-bodied spearman in a pale robe, spear lowered; the two
    # behind him, the sun and the mountains cut away along a hand-traced polygon)
    ("naga_champion", "EP184", "cand_ronin4/Naga_Spearmen_2.jpg", (0, 0, 599, 494), "paint", 200, None,
     "The Naga's Champion"),
    # The finale, Act 1 (the Shrine of Osano-Wo): wave 4's "Ryozo", the oni that took the Seppun guardsman's name,
    # wears the wiki's painted "Seppun Heavy Elite" (an Imperial guard in full armour, blade raised, on a teal bamboo
    # forest: keyed out like "green"), his face greyed; wave 7's many-legged horror is the line art "Kumo 3" (a great
    # hairy spider, the "Kumo" caption and the signature erased), inked in Shadowlands violet
    ("ryozo_oni", "EP186", "cand_dragon2/Seppun_Heavy_Elite_by_Greg_Lambrakis.jpg", (0, 0, 550, 443), "paint", 205,
     None, "\"Ryozo\""),
    ("horror", "EP188", "cand_finale1/Kumo_3.jpg", (0, 0, 554, 396), "line", 190,
     ramp((22, 12, 26), (64, 30, 52), (120, 58, 84), (190, 150, 160), (234, 224, 216)), "Many-Legged Horror"),
    ("yasurugi", "EP126", "cand_crane2/Kakita_Bushi.jpg", (0, 0, 265, 566), "white", 190, None, "Kakita Yasurugi"),
    # The finale, Act 4 "The Empress of Nothing" (production F09): phases 1-2 wear the line art "White Woman" (a
    # long-haired woman in court robes, hands folded, rising out of smoke; the swirls and the signature erased), inked
    # bride-pale for "The Bride" and in starfield ink for "Body of Damned Time"; phase 3, the true form, is the painted
    # "Doji Nashiko" (the Demon Bride of Fu Leng on her cushions, half her face scaled, the red centipede behind her)
    ("nashiko_bride", "EP190", "cand_crane5/White_Woman.jpg", (0, 0, 197, 400), "line", 200,
     ramp((40, 8, 18), (120, 26, 40), (196, 160, 164), (236, 226, 222), (250, 246, 240)), "Doji Nashiko"),
    ("nashiko_time", "EP192", "cand_crane5/White_Woman.jpg", (0, 0, 197, 400), "line", 210,
     ramp((6, 6, 24), (26, 30, 78), (84, 100, 170), (170, 186, 236), (226, 232, 250)), "Body of Damned Time"),
    ("nashiko_true", "EP194", "cand_crane5/Doji_Nashiko.jpg", (0, 0, 1528, 1080), "paint", 225, None,
     "The Empress of Nothing"),
    # the post-game, P2 Shiro Hiruma: Oni no Okura, Akuma's daughter in samurai armour (the 1999 CCG card, W. O'Connor;
    # the card's illustration only, the figure traced by hand: horns, the blue face, the armour, the long dark hair)
    ("okura", "EP196", "cand/Oni_no_Okura-card.jpg", (165, 95, 375, 310), "paint", 190, None, "Oni no Okura"),
    # P3 the Orochi superboss (wiki "Orochi": sea serpents of Sakkaku, shimmering green scales, golden eyes; line art
    # Orochi_4.jpg, the head and frill rising out of the surf; the signature is outside the crop)
    ("orochi", "EP198", "cand_postgame/Orochi_4.jpg", (360, 15, 600, 250), "line", 215,
     ramp((10, 30, 22), (30, 78, 52), (74, 140, 92), (160, 206, 150), (226, 240, 214)), "The Orochi"),
]
# per boss: pixelated islands smaller than this many pixels are dropped (line art with loose ink flecks)
CLEAN = {"nashiko_bride": 30, "nashiko_time": 30, "nashiko_true": 40, "horror": 40, "yasurugi": 10, "miyako": 24, "shelf_kami": 60, "seppun_duelist": 30, "kuzushi": 80}
# mode "coolkey": the warm ground to drop (OpenCV hue range, and the saturation above which it is wall, not skin)
COOLKEY = {"miyako": dict(hue=(3, 35), sat=160, dark=120, column=(620, 1320), sat_side=95, head=((760, 1080), 1000)),
           # the skull wall is dark and saturated; his skin is bright and his hair unsaturated: both survive
           "katsuo": dict(hue=(0, 35), sat=70, val_max=150)}
# post-passes on the cut-out colours: hue shift (OpenCV hue range, shift) and whitening (dark, unsaturated pixels in a
# box become pale: an albino's hair)
POLY = {"okura": [(180, 153), (173, 130), (182, 108), (207, 117), (227, 102), (260, 101), (290, 103), (323, 117),
                 (350, 140), (363, 170), (367, 210), (360, 247), (350, 283), (347, 309), (187, 309), (182, 283),
                 (187, 257), (178, 230), (177, 210), (185, 190), (177, 170)],
        "nashiko_true": [(10, 745), (40, 705), (150, 695), (225, 668), (250, 600), (215, 520), (160, 400), (130, 300),
                         (160, 285), (200, 330), (260, 420), (290, 400), (255, 330), (300, 300), (345, 310), (352, 270),
                         (350, 60), (358, 25), (372, 40), (392, 230), (418, 205), (430, 40), (468, 25), (500, 60),
                         (510, 120), (540, 100), (600, 120), (680, 150), (730, 180), (780, 240), (830, 320),
                         (850, 240), (900, 195), (980, 160), (1100, 115), (1110, 60), (1140, 30), (1200, 20),
                         (1240, 60), (1255, 110), (1225, 175), (1300, 212), (1312, 240), (1250, 262), (1225, 300),
                         (1300, 305), (1345, 320), (1365, 385), (1300, 470), (1310, 560), (1340, 690), (1342, 780),
                         (1312, 812), (1268, 800), (1240, 760), (1250, 700), (1225, 620), (1190, 570), (1050, 620),
                         (1000, 650), (900, 700), (820, 780), (800, 840), (640, 845), (560, 805), (420, 835),
                         (330, 840), (290, 790), (240, 790), (110, 825), (95, 800), (55, 765), (10, 762)],
        "order_enforcer": [(166, 45), (180, 26), (205, 20), (232, 28), (247, 55), (246, 105), (258, 135), (282, 150), (285, 255), (330, 330), (400, 375),
                           (468, 385), (465, 400), (395, 402), (380, 415), (330, 410), (270, 400), (262, 479),
                           (118, 479), (118, 335), (98, 330), (100, 152), (140, 138), (164, 128)],
        "naga_champion": [(0, 168), (30, 160), (70, 168), (100, 188), (118, 196), (128, 160), (150, 122), (185, 113),
                          (208, 120), (220, 140), (222, 178), (218, 214), (250, 232), (330, 236), (352, 262),
                          (400, 300), (438, 335), (450, 372), (452, 408), (480, 418), (599, 436), (599, 494),
                          (0, 494)]}
DARKKEY = {"crab_shade": (70, (28, 96), [(145, 38, 190, 88)])}  # min value, green hues kept; boxes kept (crop)
HUE_SHIFT = {"chihaya": (118, 168, -38), "naohida": (140, 179, 32)}   # naohida: the pink cast to warm brown
INVERT = {"kuzushi"}
PAPERKEY = {"akuro": dict(sat=40, val=185), "kumpei": dict(sat=140, val=150)}                                 # mode "paperkey": the cream ground
DESAT = {"naohida": 0.7}
# per boss: hue ranges to drop (OpenCV hue lo, hi, min saturation, min value) and boxes (source coords) kept anyway
KEYOUT = {"mine_guardian": dict(drop=[(80, 112, 90, 150), (150, 180, 20, 150), (0, 8, 20, 150), (0, 180, 0, 205),
                                      (90, 130, 30, 50, (0, 1150, 520, 2150))],         # the mist, lower left
                                keep=[(880, 480, 1150, 800)])}           # the red moon and the cyan ghost-fire; his eyes
KEYOUT["ryozo_oni"] = dict(drop=[(78, 112, 125, 20), (40, 80, 60, 20, (0, 360, 550, 443))])   # the bamboo; the ferns
KEYOUT["tengu_red"] = dict(drop=[(85, 118, 20, 120), (0, 180, 0, 222), (0, 180, 0, 0, (1180, 0, 1509, 1090))],
                           keep=[(720, 380, 980, 640)])                              # the sky, the swirl; his kimono
KEYOUT["tomie_tiger"] = dict(drop=[(26, 80, 35, 70), (0, 180, 0, 0, (0, 0, 70, 249)), (0, 180, 0, 0, (180, 0, 238, 249)),
                                   (0, 30, 0, 0, (60, 236, 190, 249)), (0, 25, 60, 0, (172, 140, 238, 249))])    # wall, posts, floor, bar
# mode "line": pale paper enclosed by the figure (between a spider's legs) is dropped outside the body polygon
LINEPAPER = {"horror": dict(lum=175, body=[(150, 40), (300, 20), (400, 40), (440, 110), (425, 190), (380, 250),
                                          (260, 250), (130, 200), (100, 120)])}
DROP = {"kuzushi": [[(250, 190), (450, 190), (450, 420), (250, 420)]]}   # the sky inside the arm-and-leg loop
DROP_ALL = {"nashiko_true": [[(200, 335), (300, 325), (345, 345), (352, 445), (405, 470), (410, 555), (300, 560),
                              (268, 520), (240, 450), (205, 380)],
                             [(1240, 262), (1300, 262), (1300, 300), (1232, 298)]],
            "kuzushi": [[(440, 0), (518, 0), (518, 115), (440, 115)]],
            "munashii": [[(520, 0), (717, 0), (717, 756), (565, 756), (565, 420), (520, 400)],   # cabinet, vase
                         [(0, 460), (205, 460), (205, 756), (0, 756)]],          # the low table and teapot
            "kumpei": [[(150, 820), (700, 980), (1000, 1537), (150, 1537)]]}      # the pale floor under the sash  # the planet in the corner                            # saturation x this after the hue shift (a dusky, not neon, violet)                                    # line art drawn white-on-black: mask from the inverted image
# mode "inkflood": a figure inside a closed black ink outline on a coloured ground. Flood the ground in from the edges,
# stopped by the (dilated) ink; inside keep boxes, any pixel that isn't the saturated ground hue is figure too (thin
# grey hair strokes leak the flood)
INKFLOOD = {"masanori": dict(dark=80, dil=5, keep=[(440, 190, 960, 740)], ground_hue=(75, 105), ground_sat=15)}
WHITEN = {"ryozo_oni": dict(box=(190, 90, 305, 205), val_max=0, sat_max=0, pale_skin=True),   # not a man
          "katsuo": dict(box=(115, 25, 275, 330), val_max=100, sat_max=90, pale_skin=True)}
# line-art regions to drop (source pixels, before the crop): Tsukakoro's victim's katana
ERASE = {"cand_crane2/Kakita_Bushi.jpg": [[(168, 14), (265, 14), (265, 88), (168, 88)]],
         "cand_crane5/White_Woman.jpg": [[(148, 350), (197, 350), (197, 392), (148, 392)]],     # the signature
         "cand_finale1/Kumo_3.jpg": [[(262, 330), (330, 330), (330, 362), (262, 362)],        # the caption
                                     [(10, 280), (62, 280), (62, 340), (10, 340)]],          # the signature
         "cand_crane8/Ronin_3.jpg": [[(0, 0), (128, 0), (128, 96), (0, 96)]],
         "cand_lion1/Akeru_no_Oni_2.jpg": [[(340, 10), (460, 10), (460, 48), (340, 48)],          # the caption
                                           [(20, 450), (90, 450), (90, 505), (20, 505)]],         # the signature
         "cand_lion1/Lion_Bushi.jpg": [[(196, 222), (290, 222), (290, 292), (196, 292)]]}                 # the "Ronin Bushi" caption   # the "Crane Bushi" caption
# line-art strokes to inpaint away (source pixels, polyline, width): the victim's katana crossing Tsukakoro's tentacles
INPAINT = {"Tsukakoro_no_Oni.jpg": [([(609, 2), (585, 40), (560, 80), (540, 120), (524, 160), (512, 200), (505, 238),
                                     (502, 258)], 15)]}


def line_mask(gray, paper_lum=222):
    """Paper is near-white and touches the border: flood it from the edges; everything else is the figure."""
    paper = (gray > paper_lum).astype(np.uint8)
    h, w = gray.shape
    ff = np.zeros((h + 2, w + 2), np.uint8)
    reach = paper.copy()
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)] + [(x, 0) for x in range(0, w, 7)] + \
            [(x, h - 1) for x in range(0, w, 7)] + [(0, y) for y in range(0, h, 7)] + [(w - 1, y) for y in range(0, h, 7)]:
        if reach[y, x] == 1:
            cv2.floodFill(reach, ff, (x, y), 2)
    fig = (reach != 2).astype(np.uint8)
    fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return fig


# GrabCut seeds for painted art (source pixels): sure figure / sure background boxes (x0, y0, x1, y1)
PAINT_HINTS = {"cand_crane6/Doji_Ayano.jpg": dict(                       # boxes in CROP coordinates (x - 1000)
    redkey=True,
    fg=[(780, 300, 1060, 780), (700, 1140, 1180, 2060), (820, 2180, 1180, 2380), (780, 2500, 1220, 3100),
        (260, 1540, 420, 2440), (1420, 1540, 1620, 2440)],
    bg=[(0, 0, 560, 1000), (1240, 0, 1800, 1000), (0, 1000, 100, 1300), (1700, 1000, 1800, 1300)]),
    "Onikage.jpg": dict(
    fg=[(380, 60, 430, 120), (390, 130, 440, 240), (300, 170, 360, 230), (450, 140, 500, 190), (225, 250, 255, 300),
        (348, 300, 368, 390), (495, 240, 520, 290)],
    bg=[(0, 0, 95, 450), (0, 0, 600, 18), (0, 330, 330, 450), (420, 340, 600, 450), (540, 0, 600, 200)],
    # always figure (polygons), after the smooth-sky filter: the jingasa is as smooth and grey as the sky (user:
    # "fix his hat") and the red hair under it
    keep=[[(347, 74), (356, 48), (370, 30), (392, 24), (421, 25), (410, 33), (380, 50), (360, 66)],
          [(352, 78), (366, 62), (395, 45), (420, 50), (416, 62), (382, 76), (370, 92), (354, 90)]])}
FLIP = {"akutsukai", "cellar_ogre", "masanori", "seppun_duelist", "kumpei", "okura"}
# (2026-11-11 animation watcher: kumpei + okura were painted facing left and their installed sheets still did, so
# enemy_pic.json EP145/EP196 got flipx True; a rebuild here flips the image and writes flipx False - same result.)
# gamma per painted boss (< 1 brightens the shadows): the Onikage painting is a night scene and read as a black blob
# on the battle backdrop (mean 47/255; the troll is 131)
LIFT = {"akutsukai": 0.62, "cellar_ogre": 0.85, "iron_crane": 0.8}
PAINT_HINTS["cand_scorpion1/Kansen_(TCG).jpg"] = dict(                 # Scorpion Ch1: the leaf-storm Kansen and Hana
    tealkey=True,
    fg=[(150, 60, 430, 250), (110, 240, 470, 300), (205, 290, 330, 506)],     # the spirit, its arms, the woman
    bg=[(0, 0, 80, 140), (450, 0, 578, 130), (510, 0, 578, 240), (0, 320, 150, 506), (390, 320, 578, 506), (150, 440, 195, 506),
        (345, 430, 390, 506)])
PAINT_HINTS["cand_phx2/Bloodspeaker_2.jpg"] = dict(                     # CROP coords (y - 90): Mieko's dark half
    fg=[(100, 80, 160, 170), (10, 70, 90, 300), (0, 230, 300, 450), (300, 130, 360, 250)],
    bg=[(0, 0, 60, 60), (180, 0, 240, 70), (250, 0, 380, 40), (362, 180, 380, 453), (0, 90, 10, 210),
        (300, 405, 380, 453)])
PAINT_HINTS["cand_phx3/Isawa_Shugenja.jpg"] = dict(
    fg=[(110, 60, 150, 130), (90, 135, 200, 300), (60, 300, 230, 440)],
    bg=[(0, 420, 62, 446), (226, 420, 265, 446), (75, 0, 105, 40), (165, 0, 192, 40)])
PAINT_HINTS["cand_crane7/Bloodspeaker.jpg"] = dict(
    fg=[(262, 78, 312, 148), (200, 160, 350, 300), (170, 320, 420, 560)],
    bg=[(0, 0, 613, 50), (0, 120, 150, 300), (470, 140, 613, 330), (0, 440, 110, 520), (520, 330, 613, 565),
        (0, 0, 245, 120), (330, 0, 613, 150), (355, 150, 475, 205)])
PAINT_HINTS["cand_lion2/Ianwa_no_Oni.jpg"] = dict(
    fg=[(75, 75, 180, 165), (150, 75, 208, 160), (232, 84, 250, 100), (128, 18, 165, 40)],   # inside the body only
    bg=[(0, 0, 35, 90), (235, 0, 314, 70), (0, 215, 50, 241), (268, 105, 314, 160), (225, 160, 314, 241),
        (205, 180, 240, 241), (0, 0, 314, 4), (30, 8, 100, 52), (140, 168, 200, 195)])
PAINT_HINTS["cand_lion3/Harue__duelist_.jpg"] = dict(                  # boxes in CROP coordinates (x - 290)
    fg=[(188, 50, 238, 130), (185, 175, 275, 330), (80, 370, 220, 580),       # inside the figure only
        (60, 274, 140, 294), (60, 380, 140, 470)],                             # the katana hilt; the hakama
    bg=[(0, 0, 150, 220), (0, 0, 510, 30), (310, 0, 510, 200), (330, 200, 510, 330), (340, 520, 510, 590),
        (0, 340, 12, 590), (282, 30, 510, 160), (0, 220, 28, 330)])
PAINT_HINTS["cand_lion4/Matsu_Gohei_3_small.jpg"] = dict(            # CROP coords (x*0.4 - 140, y*0.4 - 40)
    fg=[(220, 72, 300, 208), (180, 220, 340, 480), (200, 480, 380, 800), (100, 500, 148, 640), (320, 140, 480, 300),
        (508, 640, 600, 732)],
    bg=[(0, 0, 200, 50), (440, 0, 640, 50), (0, 0, 30, 420), (0, 420, 40, 560), (500, 520, 640, 600),
        (540, 0, 640, 120), (0, 735, 172, 865), (390, 800, 640, 865)])
PAINT_HINTS["cand_phx1/Daidoji_Yurei.jpg"] = dict(                     # CROP coords (x - 160, y - 30)
    fg=[(100, 15, 135, 65), (90, 90, 190, 240), (60, 270, 190, 400), (20, 150, 70, 230), (200, 125, 235, 195)],
    bg=[(0, 0, 80, 90), (160, 0, 280, 70), (0, 240, 40, 425), (240, 280, 280, 425), (150, 20, 280, 90),
        (250, 90, 280, 280)])
PAINT_HINTS["cand_scorpion1/Kitsune_Impersonator_Tradition.jpg"] = dict(   # CROP coords (x - 690)
    fg=[(150, 40, 230, 190), (225, 105, 295, 200), (130, 230, 330, 560), (90, 600, 300, 800), (50, 250, 95, 500)],
    bg=[(0, 0, 95, 150), (380, 0, 491, 560), (310, 0, 491, 90), (400, 600, 491, 812), (0, 560, 25, 812),
        (0, 150, 40, 240), (305, 215, 380, 420), (345, 515, 400, 600), (315, 770, 400, 812), (0, 240, 28, 560),
        (240, 0, 491, 30), (300, 90, 380, 215), (232, 30, 300, 98), (30, 150, 75, 230)])
PAINT_HINTS["cand_unicorn1/Koji_(ronin).jpg"] = dict(                 # CROP coords (x - 150, y - 60)
    fg=[(390, 200, 520, 420), (230, 520, 720, 1000), (160, 1060, 600, 1320)],
    bg=[(0, 0, 300, 220), (610, 0, 900, 340), (0, 220, 70, 700), (760, 1100, 900, 1340), (840, 0, 900, 700),
        (590, 160, 800, 380), (60, 250, 160, 420), (240, 0, 320, 150), (0, 0, 290, 400), (585, 0, 900, 420)])
PAINT_HINTS["Ogre.jpg"] = dict(
    fg=[(215, 60, 300, 180), (310, 150, 460, 300), (40, 60, 90, 150), (110, 180, 190, 280), (240, 190, 330, 260),
        (300, 40, 470, 150), (420, 150, 497, 300)],
    bg=[(0, 300, 120, 359), (0, 200, 25, 300), (455, 0, 497, 25)], warm_sky=True)                         # the art faces left; enemies face the party on the right (user)


PAINT_HINTS["cand_unicorn4/Iuchi_Haruma.jpg"] = dict(                       # (crop coords) the maho skulls are sky
    fg=[(340, 80, 560, 320), (300, 520, 860, 820), (120, 420, 300, 900), (800, 420, 900, 600), (260, 300, 640, 520)],
    bg=[(0, 0, 230, 280), (690, 0, 910, 320), (0, 600, 50, 900), (0, 280, 70, 560)],
    keep=[[(180, 790), (540, 400), (900, 470), (910, 860), (250, 885)]])   # the pale scroll


PAINT_HINTS["cand_ronin1/Ajari.jpg"] = dict(                                # the crow-tengu in red, on a peak
    fg=[(650, 320, 1040, 740), (760, 160, 990, 320), (440, 160, 780, 430), (340, 280, 500, 980), (720, 720, 930, 1040)],
    bg=[(0, 0, 260, 1090), (1250, 0, 1509, 700), (1120, 640, 1509, 1090), (260, 0, 600, 140), (0, 1060, 1509, 1090)])
PAINT_HINTS["cand_ronin2/Kolat_Assassin.jpg"] = dict(                     # the enforcer, off the body and the bars
    fg=[(170, 35, 250, 130), (130, 120, 290, 300), (120, 300, 240, 470), (250, 310, 390, 395)],
    bg=[(0, 0, 100, 479), (100, 0, 160, 95), (295, 0, 480, 290), (330, 405, 480, 479), (400, 290, 480, 405),
        (255, 420, 330, 479)])
PAINT_HINTS["cand_ronin3/Shiryo_no_Hida-card.jpg"] = dict(               # CROP coords (x - 50, y - 117): the shade
    fg=[(120, 8, 215, 130), (60, 120, 280, 247)],
    bg=[(0, 0, 55, 110), (275, 0, 328, 110)])
PAINT_HINTS["cand_crane5/Doji_Nashiko.jpg"] = dict(                     # the bride on her cushions, the centipede
    fg=[(860, 250, 1180, 640), (560, 400, 1000, 820), (250, 260, 540, 520), (300, 40, 520, 220), (1150, 400, 1300, 560),
        (200, 600, 560, 760), (1010, 160, 1260, 250)],
    bg=[(0, 0, 250, 250), (560, 0, 1000, 120), (1340, 0, 1528, 300), (1420, 300, 1528, 1080), (0, 1000, 1528, 1080),
        (0, 300, 120, 560)])
PAINT_HINTS["cand_ronin1/Tiger.jpg"] = dict(                                # the tiger, off its green wall
    fg=[(95, 10, 160, 90), (75, 95, 172, 165), (80, 170, 165, 230)],
    bg=[(0, 0, 60, 249), (190, 0, 238, 249), (0, 238, 238, 249), (60, 0, 85, 60), (170, 0, 190, 80)])


def paint_mask(rgb, src):
    """Painted art: GrabCut seeded with sure-figure and sure-background boxes, then the biggest blob."""
    h, w = rgb.shape[:2]
    hint = PAINT_HINTS.get(src, {})
    mask = np.full((h, w), cv2.GC_PR_BGD, np.uint8)
    mask[int(h * 0.05):int(h * 0.95), int(w * 0.15):int(w * 0.95)] = cv2.GC_PR_FGD
    for (x0, y0, x1, y1) in hint.get("bg", []):
        mask[y0:y1, x0:x1] = cv2.GC_BGD
    if hint.get("redkey"):                                      # red armour / autumn leaves behind a blue figure
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        hue, sat = hsv[..., 0], hsv[..., 1]
        mask[((hue < 14) | (hue > 160)) & (sat > 110)] = cv2.GC_BGD
        mask[(hue >= 8) & (hue <= 32) & (sat > 90)] = cv2.GC_BGD           # the bridge's warm wood (cream cloth is
                                                                            # far less saturated and stays)
        mask[(hue >= 35) & (hue <= 88) & (sat > 50)] = cv2.GC_BGD          # green trees (the armour is blue)
    if hint.get("tealkey"):                                     # a teal-blue sky behind a yellow-green figure
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        mask[(hsv[..., 0] >= 78) & (hsv[..., 0] <= 110) & (hsv[..., 1] > 50)] = cv2.GC_BGD
    for (x0, y0, x1, y1) in hint.get("fg", []):
        mask[y0:y1, x0:x1] = cv2.GC_FGD
    bg, fg = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), mask, None, bg, fg, 8, cv2.GC_INIT_WITH_MASK)
    fig = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 1, 0).astype(np.uint8)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)          # painted sky is smooth; bone is busy
    mu = cv2.blur(gray, (7, 7))
    sd = np.sqrt(np.maximum(cv2.blur(gray * gray, (7, 7)) - mu * mu, 0))
    smooth_sky = (sd < 6.0) & (gray > 70)
    seeded = np.zeros_like(fig)                                 # sure-figure boxes are exempt from the sky filters
    for (x0, y0, x1, y1) in hint.get("fg", []):
        seeded[y0:y1, x0:x1] = 1
    fig[smooth_sky & (seeded == 0)] = 0
    if hint.get("tealkey"):                                     # (seed boxes overlap the sky: not exempt here)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        fig[(hsv[..., 0] >= 78) & (hsv[..., 0] <= 110) & (hsv[..., 1] > 50)] = 0
    if hint.get("warm_sky"):                                    # brushy dusk sky: bright yellow-orange, not seeded
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        sky = (hsv[..., 2] > 168) & (hsv[..., 0] >= 8) & (hsv[..., 0] <= 30) & (hsv[..., 1] > 60)
        fig[sky] = 0                                            # (seed boxes overlap sky: not exempt here)
    for poly in hint.get("keep", []):
        cv2.fillPoly(fig, [np.array(poly, np.int32)], 1)
    fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(fig)
    if n > 1:                                                   # keep the biggest blob (horse + rider)
        big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        fig = (lab == big).astype(np.uint8)
    return cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))


CONVERTER = os.path.join(HERE, "..", "_sources", "pixelconv", "asciiartist.py")
TMP = os.path.join(HERE, "..", "_art", "tmp_bossart")


def _load_converter():
    """The user's 16-Bit-Style-Pixel-Art-Converter (MIT, _sources/pixelconv/asciiartist.py). Only its imports and
    convert_to_16bit_style_pixel_art() are run: the file's module-level demo call uses a hard-coded path."""
    import ast
    src = open(CONVERTER, encoding="utf-8").read()
    tree = ast.parse(src)
    keep = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom)) or
            (isinstance(n, ast.FunctionDef) and n.name == "convert_to_16bit_style_pixel_art")]
    ns = {}
    exec(compile(ast.Module(body=keep, type_ignores=[]), CONVERTER, "exec"), ns)
    return ns["convert_to_16bit_style_pixel_art"]


PIX = 1.4                       # boss pixels are drawn 1.4x the cast's: visibly pixel art at boss size


def pixelate(rgba, height, palette=32):
    """Run the cutout through the user's converter (downscale to pixel_size, ADAPTIVE palette, nearest upscale).
    It works on a square RGB image and opens a preview window, so: pad to a square on a key colour, silence .show(),
    then read one pixel per block back and take the alpha from our own mask."""
    convert = _load_converter()
    os.makedirs(TMP, exist_ok=True)
    h, w = rgba.shape[:2]
    S = max(h, w)
    sq = np.zeros((S, S, 4), np.uint8)
    sq[(S - h) // 2:(S - h) // 2 + h, (S - w) // 2:(S - w) // 2 + w] = rgba
    key = np.array([255, 0, 255], np.uint8)
    rgb = sq[..., :3].copy()                                   # bleed the figure's edge colours outwards so the
    bg = (sq[..., 3] == 0).astype(np.uint8)                     # converter's bilinear downscale has nothing to blend
    for _ in range(24):                                         # a key colour into (no magenta fringe)
        grown = cv2.dilate(rgb, np.ones((3, 3), np.uint8))
        rgb[bg > 0] = grown[bg > 0]
        bg = cv2.erode(bg, np.ones((3, 3), np.uint8))
    rgb[bg > 0] = key
    px = max(16, int(round(height * S / h)))                  # block count across the square
    S2 = (S // px) * px                                        # the converter upscales by integer blocks
    src = Image.fromarray(rgb, "RGB").resize((S2, S2), Image.LANCZOS)
    inp, outp = os.path.join(TMP, "in.png"), os.path.join(TMP, "out.png")
    src.save(inp)
    show = Image.Image.show
    Image.Image.show = lambda *a, **k: None
    try:
        convert(inp, outp, pixel_size=px, palette_size=palette)
    finally:
        Image.Image.show = show
    big = np.array(Image.open(outp).convert("RGB"))
    b = S2 // px
    col = big[b // 2::b, b // 2::b][:px, :px]
    alpha = np.array(Image.fromarray(sq[..., 3]).resize((px, px), Image.BOX)) > 110
    alpha &= ~np.all(np.abs(col.astype(int) - key.astype(int)) < 40, axis=2)   # far key-coloured blocks: empty
    out = np.zeros((px, px, 4), np.uint8)
    out[..., :3] = col
    out[..., 3] = np.where(alpha, 255, 0)
    ys, xs = np.nonzero(alpha)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def outline(a):
    """A dark 1 px outline outside the figure, like the cast (g.outline_outer)."""
    alpha = a[..., 3] > 0
    grow = np.zeros_like(alpha)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        grow |= np.roll(np.roll(alpha, dy, 0), dx, 1)
    ring = grow & ~alpha
    a[ring] = ea.OUTLINE
    return a


def build(key, src, box, mode, height, tint):
    img = Image.open(os.path.join(ART, src)).convert("RGB").crop(box)
    rgb = np.array(img)
    if mode == "line":
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        for pts, wd in INPAINT.get(src, []):                    # fill the stroke from what surrounds it
            m = np.zeros_like(gray)
            cv2.polylines(m, [np.array([(x - box[0], y - box[1]) for x, y in pts], np.int32)], False, 255, wd)
            gray = cv2.inpaint(gray, m, 7, cv2.INPAINT_TELEA)
            gray[(m > 0) & (gray > 150)] = 255                  # the smear over paper is paper
        for poly in ERASE.get(src, []):                         # paint the region white: it becomes paper
            cv2.fillPoly(gray, [np.array([(x - box[0], y - box[1]) for x, y in poly], np.int32)], 255)
        fig = line_mask(255 - gray, paper_lum=165) if key in INVERT else line_mask(gray)
        for poly in DROP.get(key, []):                          # ground enclosed by the figure: dark pixels only
            pm = np.zeros_like(fig)
            cv2.fillPoly(pm, [np.array([(x - box[0], y - box[1]) for x, y in poly], np.int32)], 1)
            fig[(pm == 1) & (gray < 90)] = 0
        for poly in DROP_ALL.get(key, []):                      # whole regions that are not the figure
            pm = np.zeros_like(fig)
            cv2.fillPoly(pm, [np.array([(x - box[0], y - box[1]) for x, y in poly], np.int32)], 1)
            fig[pm == 1] = 0
        if key in LINEPAPER:                                    # paper enclosed by legs: drop the pale
            lp = LINEPAPER[key]                                 # outside the body polygon
            body = np.zeros_like(fig)
            cv2.fillPoly(body, [np.array([(x - box[0], y - box[1]) for x, y in lp["body"]], np.int32)], 1)
            fig[(gray > lp["lum"]) & (body == 0)] = 0
            fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
            n, lab, stats, _ = cv2.connectedComponentsWithStats(fig)
            if n > 1:
                fig = (lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
        lum = cv2.GaussianBlur(gray, (3, 3), 0).astype(np.float32) / 255.0
        col = tint(lum ** 1.15)
    elif mode == "coolkey":                                     # a cool figure on a warm, saturated ground
        k = COOLKEY[key]
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        hue, sat = hsv[..., 0], hsv[..., 1]
        val = hsv[..., 2]
        warm = ((hue >= k["hue"][0]) & (hue <= k["hue"][1])) | (hue >= 160)
        ground = warm & (sat > k["sat"]) & (val < k.get("val_max", 256))
        ground |= warm & (val < k.get("dark", 0))                       # dark wood beams and panels
        if "column" in k:                                               # skin-toned wood away from her face/hands
            outside = np.ones_like(ground)
            outside[:, k["column"][0]:k["column"][1]] = False
            ground |= warm & outside & (sat > k["sat_side"])
        if "head" in k:                                                 # above the shoulders only the face is warm
            (fx0, fx1), fy = k["head"]
            above = np.zeros_like(ground)
            above[:fy, :] = True
            above[:fy, fx0:fx1] = False
            ground |= warm & above & (sat > k["sat_side"])
        fig = cv2.morphologyEx((~ground).astype(np.uint8), cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
        n, lab, stats, _ = cv2.connectedComponentsWithStats(fig)
        if n > 1:
            fig = (lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
        fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))
        holes = (fig == 0).astype(np.uint8)                     # fill enclosed holes (eyes, the scroll's shadow)
        ff = np.zeros((holes.shape[0] + 2, holes.shape[1] + 2), np.uint8)
        outside = holes.copy()
        for x0, y0 in ((0, 0), (holes.shape[1] - 1, 0)):
            if outside[y0, x0]:
                cv2.floodFill(outside, ff, (x0, y0), 2)
        fig[(holes == 1) & (outside != 2)] = 1
        col = np.clip((rgb.astype(np.float32) - 128) * 1.08 + 128, 0, 255)
    elif mode == "paperkey":                                    # painted art on cream paper (pale, unsaturated)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        k = PAPERKEY.get(key, {})
        ground = (hsv[..., 1] < k.get("sat", 45)) & (hsv[..., 2] > k.get("val", 190))
        fig = cv2.morphologyEx((~ground).astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        n, lab, stats, _ = cv2.connectedComponentsWithStats(fig)
        if n > 1:
            fig = (lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
        fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
        holes = (fig == 0).astype(np.uint8)                     # fill enclosed holes (pale skin highlights)
        ff = np.zeros((holes.shape[0] + 2, holes.shape[1] + 2), np.uint8)
        outside = holes.copy()
        hh, ww = holes.shape
        for x0, y0 in [(x, y) for x in range(0, ww, 8) for y in (0, hh - 1)] +                       [(x, y) for y in range(0, hh, 8) for x in (0, ww - 1)]:     # paper touching any edge
            if outside[y0, x0]:
                cv2.floodFill(outside, ff, (x0, y0), 2)
        fig[(holes == 1) & (outside != 2)] = 1
        for poly in DROP_ALL.get(key, []):                      # floor or wall that the key can't tell from the figure
            pm = np.zeros_like(fig)
            cv2.fillPoly(pm, [np.array([(x - box[0], y - box[1]) for x, y in poly], np.int32)], 1)
            fig[pm == 1] = 0
        col = np.clip((rgb.astype(np.float32) - 128) * 1.1 + 128, 0, 255)
    elif mode == "inkflood":                                    # an ink-outlined figure on a coloured ground
        k = INKFLOOD[key]
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        ink = cv2.dilate((gray < k["dark"]).astype(np.uint8), np.ones((k["dil"], k["dil"]), np.uint8))
        reach = (1 - ink).astype(np.uint8)
        h, w = gray.shape
        ff = np.zeros((h + 2, w + 2), np.uint8)
        for x, y in [(x, y) for x in range(0, w, 9) for y in (0, h - 1)] + [(x, y) for y in range(0, h, 9)
                                                                           for x in (0, w - 1)]:
            if reach[y, x] == 1:
                cv2.floodFill(reach, ff, (x, y), 2)
        fig = (reach != 2).astype(np.uint8)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        ground = (hsv[..., 0] >= k["ground_hue"][0]) & (hsv[..., 0] <= k["ground_hue"][1]) &                  (hsv[..., 1] > k["ground_sat"])
        for x0, y0, x1, y1 in k.get("keep", []):
            sub = fig[y0 - box[1]:y1 - box[1], x0 - box[0]:x1 - box[0]]
            sub |= (~ground[y0 - box[1]:y1 - box[1], x0 - box[0]:x1 - box[0]]).astype(np.uint8)
        n, lab, stats, _ = cv2.connectedComponentsWithStats(fig)
        if n > 1:
            fig = (lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
        col = np.clip((rgb.astype(np.float32) - 128) * 1.08 + 128, 0, 255)
    elif mode == "white":                                       # painted art on a white ground: keep its colours
        rgb = rgb.copy()
        for poly in ERASE.get(src, []):                         # captions etc. become paper
            cv2.fillPoly(rgb, [np.array([(x - box[0], y - box[1]) for x, y in poly], np.int32)], (255, 255, 255))
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        fig = line_mask(gray, 240)
        col = np.clip((rgb.astype(np.float32) - 128) * 1.1 + 128, 0, 255)
    elif mode == "green":                                       # bamboo-forest art: key out the greens
        r, gg, b = [rgb[..., i].astype(np.int16) for i in range(3)]
        fig = ~((gg > r + 12) & (gg > b + 6)) & (rgb.max(axis=2) > 18)         # pale cyan skin has B >= G: kept
        fig = cv2.morphologyEx(fig.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, stats, _ = cv2.connectedComponentsWithStats(fig)
        if n > 1:
            fig = (lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
        fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        col = np.clip((rgb.astype(np.float32) - 128) * 1.1 + 128, 0, 255)
    else:
        fig = paint_mask(rgb, src)
        col = 255.0 * (rgb.astype(np.float32) / 255.0) ** LIFT.get(key, 1.0)   # dark night paintings: lift shadows
        col = np.clip((col - 128) * 1.12 + 128, 0, 255)          # a touch more contrast for the pixel look
    if key in KEYOUT:                                           # painted splashes behind the figure (a red moon,
        ko, hs = KEYOUT[key], cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)   # ghost-fire): drop them by hue
        sel = np.zeros(hs.shape[:2], bool)
        for h0, h1, smin, vmin, *zone in ko["drop"]:                # zone: only inside this box (source coords)
            m_ = (hs[..., 0] >= h0) & (hs[..., 0] <= h1) & (hs[..., 1] >= smin) & (hs[..., 2] >= vmin)
            if zone:
                x0, y0, x1, y1 = zone[0]
                z_ = np.zeros_like(m_)
                z_[max(0, y0 - box[1]):y1 - box[1], max(0, x0 - box[0]):x1 - box[0]] = True
                m_ &= z_
            sel |= m_
        for x0, y0, x1, y1 in ko.get("keep", []):
            sel[max(0, y0 - box[1]):y1 - box[1], max(0, x0 - box[0]):x1 - box[0]] = False
        fig = (fig.astype(bool) & ~sel).astype(np.uint8)
        fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        n, lab, stats, _ = cv2.connectedComponentsWithStats(fig)
        if n > 1:
            fig = (lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    if key in POLY:                                             # the figure traced by hand (source coords): grey
        fig = np.zeros(rgb.shape[:2], np.uint8)                 # robes on a grey wall defeat GrabCut
        cv2.fillPoly(fig, [np.array([(x - box[0], y - box[1]) for x, y in POLY[key]], np.int32)], 1)
        for poly in DROP_ALL.get(key, []):                      # curtain showing through the traced outline
            cv2.fillPoly(fig, [np.array([(x - box[0], y - box[1]) for x, y in poly], np.int32)], 0)
    if key in DARKKEY:                                          # a pale spirit on a night sky: drop the dark
        t, (h0, h1), keeps = DARKKEY[key]
        hsv_ = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)             # the halo of sky round him is blue-grey
        fig = ((hsv_[..., 2] >= t) & (hsv_[..., 0] >= h0) & (hsv_[..., 0] <= h1)).astype(np.uint8)
        for x0, y0, x1, y1 in keeps:                            # (crop coords) the open mouth stays
            fig[y0:y1, x0:x1] = 1
        fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, stats, _ = cv2.connectedComponentsWithStats(fig)
        if n > 1:
            fig = (lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    if key in HUE_SHIFT or key in WHITEN or key in DESAT:
        hsv = cv2.cvtColor(np.clip(col, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.int32)
        if key in HUE_SHIFT:
            h0, h1, dh = HUE_SHIFT[key]
            sel = (hsv[..., 0] >= h0) & (hsv[..., 0] <= h1)
            hsv[..., 0][sel] = (hsv[..., 0][sel] + dh) % 180
        if key in DESAT:
            hsv[..., 1] = (hsv[..., 1] * DESAT[key]).astype(np.int32)
        if key in WHITEN:
            wsp = WHITEN[key]
            x0, y0, x1, y1 = wsp["box"]
            reg = np.zeros(hsv.shape[:2], bool)
            reg[y0:y1, x0:x1] = True
            sel = reg & (hsv[..., 2] < wsp["val_max"]) & (hsv[..., 1] < wsp["sat_max"])
            hsv[..., 2][sel] = 255 - hsv[..., 2][sel] // 2              # dark strands -> pale, keeping the shading
            hsv[..., 1][sel] = 12
            if wsp.get("pale_skin"):                                    # warm skin -> albino-pale, a little pink
                skin = (hsv[..., 0] <= 25) & (hsv[..., 1] > 40) & (hsv[..., 2] > 70)
                hsv[..., 1][skin] = hsv[..., 1][skin] * 3 // 10
                hsv[..., 2][skin] = np.minimum(255, hsv[..., 2][skin] * 13 // 10 + 30)
        col = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
    rgba = np.zeros(rgb.shape[:2] + (4,), np.uint8)
    rgba[..., :3] = col.astype(np.uint8)
    rgba[..., 3] = fig * 255
    ys, xs = np.nonzero(fig)
    rgba = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    px = pixelate(rgba, int(round(height / PIX)))
    if key in CLEAN:                                            # drop stray ink specks (pixelated islands)
        n, lab, stats, _ = cv2.connectedComponentsWithStats((px[..., 3] > 0).astype(np.uint8), connectivity=8)
        for i in range(1, n):
            if stats[i, cv2.CC_STAT_AREA] < CLEAN[key]:
                px[lab == i, 3] = 0
    px = outline(np.pad(px, ((2, 2), (2, 2), (0, 0))))
    im = Image.fromarray(px, "RGBA")
    return im.transpose(Image.FLIP_LEFT_RIGHT) if key in FLIP else im


def big_sprite(src_png, factor):
    """An existing cast sprite blown up (nearest) as a boss: its first idle frame."""
    sheet = Image.open(src_png).convert("RGBA")
    fr = sheet.crop((0, 0, g.FW, g.FH))
    box = fr.split()[3].getbbox()
    fr = fr.crop(box)
    return fr.resize((fr.width * factor, fr.height * factor), Image.NEAREST)


def idle_frames(img):
    """Two-beat breathing: the frame, then the same lifted 1 px (Octopath bosses sway)."""
    w, h = img.size
    a = Image.new("RGBA", (w, h + 2), (0, 0, 0, 0))
    b = Image.new("RGBA", (w, h + 2), (0, 0, 0, 0))
    a.paste(img, (0, 2), img)
    b.paste(img, (0, 1), img)
    return [a, a, b, b]


def write(j, tmpl, epid, key, label, img):
    frames = idle_frames(img)
    sheet, (cols, rows), animap = ea.animate(frames)
    fname = "boss_%s" % key
    sheet.save(os.path.join(g.PIC, fname + ".png"))
    w, h = frames[0].size
    e = json.loads(json.dumps(tmpl))
    e.update({"name": {"en": label, "ja": label}, "pic3d": "/resource/enemy_pic/%s.png" % fname,
              "aniuv": [cols, rows], "animap": animap, "memo": "boss art (tools/gen_bossart.py; wiki art, pixelated)",
              "gndpos": [0.5, 1.0 / h], "atkpos": [0.8, 0.5], "cntpos": [0.5, 0.55],
              "scale": 1.05 * g.CAST_SCALE * PIX, "flipx": False})
    j[epid] = e
    return frames[0]


# Octopath boss intro: a brush-ink name banner shown over the battle as it opens (plugin RokuganBattle BOSS_BANNER)
EPITHET = {"nezumi_shaman": "Name-keeper of the Egg Caves", "troll": "The Wall's Oldest Enemy",
           "akutsukai": "Rider of the Restless Dead", "kommei": "The Oni of Two Faces",
           "cellar_ogre": "Beneath Kyuden Hida", "tsukakoro": "The Bone-cage",
           "wall_troll": "Up the Wall in the Night", "yasurugi": "The Silent Blade", "miyako": "The Woman in White", "masanori": "First Blood at Dawn",
           "shelf_kami": "Keeper of Shelf Nine", "otamai": "Beloved of Iuchiban", "red_oni": "It Eats the Breath",
           "nagai": "Many Voices, One Sword", "ianwa": "The Coward's Feast",
           "seppun_duelist": "The Message Never Arrives", "rokuro": "Only Fools and Matsu",
           "ashimoshi": "The Silent Hurricane", "hioninmaru": "My Blood, Gladly, Less Gladly",
           "kuzushi": "The Door You Opened", "mieko_dark": "Hello, Little Void",
           "chihaya": "Who Walks on Oars", "yosuke": "Captain in the Storm", "katsuo": "Maker of True Lies",
           "ushimo": "At the End of His Rope", "akuro": "Who Wears Every Face",
           "kumpei": "The Light Exactly Right", "kansen_hana": "Take It Away From Me",
           "munashii": "A Mask Is a Mercy", "stolen_face": "We Wear What We Need",
           "naohida": "Judge the Living", "mine_guardian": "All Who Dig Here Stay",
           "regret": "Say It Again", "kurosho": "For Want of a Son", "tengu_red": "Cross With Dignity",
           "tomie_tiger": "Such a Long Time to Be Hungry", "order_enforcer": "The Line Must Stay True",
           "crab_shade": "The Prince Must Not Come Down", "naga_champion": "The True Lines",
           "ryozo_oni": "A Good Man's Name", "horror": "Out of the Shinomen",
           "nashiko_bride": "The Bride", "nashiko_time": "Look How You End", "okura": "Akuma's Daughter", "orochi": "Keeper of the Drowned Ships",
           "nashiko_true": "I Was Going to Be Empress"}
BANNER_EP = {"nezumi_shaman": "EP450", "troll": "EP451", "akutsukai": "EP452", "kommei": "EP453",
             "cellar_ogre": "EP454", "tsukakoro": "EP455", "wall_troll": "EP456", "yasurugi": "EP457", "miyako": "EP458",
             "chihaya": "EP520", "yosuke": "EP521", "katsuo": "EP522",
             "masanori": "EP523", "shelf_kami": "EP524",
             "otamai": "EP525", "red_oni": "EP526", "nagai": "EP527", "ianwa": "EP528", "seppun_duelist": "EP529",
             "rokuro": "EP530", "ashimoshi": "EP531", "hioninmaru": "EP532",
             "kuzushi": "EP533", "mieko_dark": "EP534", "ushimo": "EP535", "akuro": "EP536", "kumpei": "EP537",
             "kansen_hana": "EP538", "munashii": "EP539", "stolen_face": "EP149", "naohida": "EP151",
             "mine_guardian": "EP153", "regret": "EP155", "kurosho": "EP157", "tengu_red": "EP159",
             "tomie_tiger": "EP183", "order_enforcer": "EP177", "crab_shade": "EP179",
             "naga_champion": "EP185", "ryozo_oni": "EP187", "horror": "EP189",
             "nashiko_bride": "EP191", "nashiko_time": "EP193", "nashiko_true": "EP195", "okura": "EP197", "orochi": "EP199"}               # EP459 free; EP460+ is cast             # EP450+ (EP387+ are side-story badges)
FONTS = "C:/Windows/Fonts/"
EXTRA_BANNERS = [("wall_troll", "Wall Troll")]                     # Goro SS2 (gen_data E256 uses the troll art)


def banner(key, label):
    from PIL import ImageDraw, ImageFilter, ImageFont
    W, H = 960, 190
    rng = np.random.default_rng(sum(map(ord, key)))
    xs = np.arange(W)
    edge = np.clip(np.minimum(xs, W - 1 - xs) / 150.0, 0, 1)            # the stroke tapers at both ends
    a = np.zeros((H, W), np.float32)
    for y in range(H):                                                     # dry-brush: rows end raggedly
        t = abs(y - H * 0.55) / (H * 0.36)
        if t >= 1:
            continue
        reach = edge - rng.uniform(0, 0.35) * t ** 2
        a[y] = np.clip(reach * 4.0, 0, 1) * (1 - t ** 6) * rng.uniform(0.82, 1.0)
    a = cv2.GaussianBlur(a, (0, 0), 1.2) * 215
    im = np.zeros((H, W, 4), np.uint8)
    im[..., :3] = (14, 10, 12)
    im[..., 3] = np.clip(a, 0, 255).astype(np.uint8)
    img = Image.fromarray(im, "RGBA")
    d = ImageDraw.Draw(img)
    gold = (214, 178, 96, 255)
    big = ImageFont.truetype(FONTS + "georgiab.ttf", 66)
    small = ImageFont.truetype(FONTS + "georgiai.ttf", 26)
    sub = EPITHET[key]
    sw = d.textlength(sub, font=small)
    d.text(((W - sw) / 2, 34), sub, font=small, fill=gold)
    nw = d.textlength(label, font=big)
    for dx, dy in ((3, 3), (2, 2)):                                        # a dark drop under the name
        d.text(((W - nw) / 2 + dx, 70 + dy), label, font=big, fill=(0, 0, 0, 200))
    d.text(((W - nw) / 2, 70), label, font=big, fill=(244, 236, 220, 255))
    for y in (154, 157):                                                   # gold rule, fading at the ends
        for x in range(int(W * 0.2), int(W * 0.8)):
            f = 1 - abs(x - W / 2) / (W * 0.3)
            d.point((x, y if y == 154 else y), fill=(214, 178, 96, int(255 * f ** 0.6 * (1 if y == 154 else 0.5))))
    return img


def write_banner(j, tmpl, key, label):
    img = banner(key, label)
    fname = "banner_%s" % key
    img.save(os.path.join(g.PIC, fname + ".png"))
    e = json.loads(json.dumps(tmpl))
    e.update({"name": {"en": label + " (banner)", "ja": label}, "pic3d": "/resource/enemy_pic/%s.png" % fname,
              "aniuv": [1, 1], "memo": "boss intro banner (tools/gen_bossart.py)", "gndpos": [0.5, 0.5], "scale": 1.0,
              "flipx": False, "animap": [{"id": "stand", "st": 0, "en": 1, "spd": 1.0, "loop": True,
                                          "replay": False}]})
    j[BANNER_EP[key]] = e
    return img


def main():
    only = set(sys.argv[1:])                                       # boss keys: rebuild only these, keep the rest as is
    jpath = os.path.join(g.RES, "enemy_pic.json")
    j = json.load(open(jpath, encoding="utf-8"))
    tmpl = j["EP000"]
    for k in [k for k, v in j.items() if "boss intro banner" in str(v.get("memo", ""))]:
        if not only or k in {BANNER_EP[b] for b in only}:
            del j[k]                                               # banners move with BANNER_EP
    prev = []
    banners = []
    for key, epid, src, box, mode, height, tint, label in BOSSES:
        if only and key not in only:
            continue
        prev.append(write(j, tmpl, epid, key, label, build(key, src, box, mode, height, tint)))
        banners.append(write_banner(j, tmpl, key, label))
        print("boss", epid, label, "banner", BANNER_EP[key])
    for key, label in EXTRA_BANNERS:                               # mini-bosses that reuse a boss's art
        if only and key not in only:
            continue
        banners.append(write_banner(j, tmpl, key, label))
    sheet = Image.new("RGBA", (960, 190 * len(banners)), (88, 110, 80, 255))
    for i, b in enumerate(banners):
        sheet.alpha_composite(b, (0, 190 * i))
    sheet.save(os.path.join(g.PREVIEW, "boss_banners.png"))
    json.dump(j, open(jpath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    W = sum(p.width for p in prev) + 12 * len(prev)
    H = max(p.height for p in prev)
    strip = Image.new("RGBA", (W, H), (70, 98, 62, 255))
    x = 0
    for p in prev:
        strip.paste(p, (x, H - p.height), p)
        x += p.width + 12
    out = os.path.join(g.PREVIEW, "bosses.png")
    strip.resize((W * 3, H * 3), Image.NEAREST).save(out)
    print(out)


if __name__ == "__main__":
    main()
