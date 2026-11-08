"""Human enemy sprites (docs/rules/bestiary.md A1-A7: bandits, ronin, contentious samurai, ashigaru, pirates,
cultists, ninja), drawn with the gen_sprites2d.py pipeline so mobs match the party's HD-2D look.
Enemies stand on the left facing right -> no flipx. Writes resource/enemy_pic/hum_<key>.png, enemy_pic.json EP400+,
preview _art/preview/human_enemies.png.
Run: python -E tools/gen_human_enemies.py [--preview-only]
"""
import json
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_sprites2d as g  # noqa: E402

BLACK, BROWN, GREY = (40, 34, 40), (92, 60, 38), (150, 150, 156)
TAN, SKIN, PALE = g.SKIN_TAN, g.SKIN, (232, 214, 200)
RAG = dict(top=(118, 104, 78), lower=(86, 78, 62), accent=(120, 90, 60))
MANTIS = dict(mon="mantis", top=(70, 140, 96), lower=(40, 84, 64), accent=(214, 186, 80), armor=(60, 120, 90), lace=(214, 186, 80))

ENEMIES = [
    # A1 bandits
    dict(key="road_bandit", name="Road Bandit", skin=TAN, hair=BROWN, hairstyle="spiky", build="peasant",
         head="headcloth", cloth=(120, 70, 50), facial="stubble", mouth="grin", weapon="katana", face="square", **RAG),
    dict(key="mountain_bandit", name="Mountain Bandit", skin=TAN, hair=BLACK, hairstyle="ponytail", build="normal",
         haori=(110, 84, 60), trim="fur", head="hachimaki", band=(160, 50, 40), facial="mustache", weapon="yumi",
         props=["quiver"], brow="thick", **RAG),
    dict(key="bandit_captain", name="Bandit Captain", skin=TAN, hair=BLACK, hairstyle="chonmage", build="armored_light",
         haori=(96, 64, 44), trim="fur", facial="beard", scar=True, weapon="naginata", height=2, wide=1,
         armor=(100, 84, 70), lace=(150, 50, 40), face="square", brow="stern", **RAG),
    dict(key="kolat_brigand", name="Kolat-paid Brigand", skin=SKIN, hair=BLACK, hairstyle="short", bangs="side",
         top=(52, 50, 58), lower=(40, 38, 46), accent=(110, 30, 40), cloak=(60, 56, 66), mask="cloth",
         mask_col=(40, 38, 46), eyes="narrow", weapon="tanto"),
    # A2 ronin
    dict(key="hungry_ronin", name="Hungry Ronin", skin=TAN, hair=BLACK, hairstyle="ponytail", hat="jingasa",
         hat_col=(170, 150, 100), top=(120, 116, 110), lower=(84, 80, 76), accent=(90, 80, 70), wide=-1,
         facial="stubble", weapon="katana", props=["saya"], eyes="narrow"),
    dict(key="sword_for_hire", name="Sword-for-Hire", skin=TAN, hair=BLACK, hairstyle="long", bangs="side",
         haori=(84, 70, 96), top=(150, 140, 130), lower=(70, 64, 80), accent=(150, 120, 60), scar=True,
         weapon="katana", props=["daisho"], face="sharp", brow="stern", mouth="frown"),
    dict(key="waveman_duelist", name="Wave-man Duelist", skin=SKIN, hair=(60, 60, 70), hairstyle="long",
         bangs="center", top=(226, 224, 216), lower=(60, 66, 90), accent=(40, 60, 110), pattern="waves",
         pattern_on=("lower",), pcol=(90, 100, 130), idle="iai", weapon="katana", props=["daisho"], eyes="narrow",
         face="sharp"),
    dict(key="masterless_champion", name="Masterless Champion", skin=TAN, hair=GREY, hairstyle="chonmage",
         build="armored", armor=(90, 86, 80), lace=(120, 110, 90), top=(100, 96, 90), lower=(70, 66, 62),
         accent=(150, 120, 60), facial="goatee_mustache", height=3, weapon="katana", props=["daisho"], face="long",
         eyes="old"),
    # A3 contentious samurai
    dict(key="drunken_samurai", name="Drunken Samurai", skin=(244, 190, 160), hair=BLACK, hairstyle="chonmage",
         build="round", haori=(170, 110, 60), top=(236, 220, 190), lower=(120, 90, 70), accent=(200, 60, 50),
         eyes="closed", mouth="grin", female=False, weapon="katana", props=["gourd"], face="round", blushm=True),
    dict(key="glory_bushi", name="Glory-Hungry Bushi", skin=SKIN, hair=BLACK, hairstyle="ponytail",
         build="armored_light", head="hachimaki", band=(220, 220, 230), top=(170, 60, 50), lower=(70, 50, 50),
         accent=(220, 190, 80), armor=(150, 50, 44), lace=(230, 200, 90), brow="stern", weapon="katana",
         props=["saya"]),
    dict(key="clan_duellist", name="Clan Duellist", skin=PALE, hair=(220, 226, 238), hairstyle="long_topknot",
         haori=(110, 150, 206), top=(236, 238, 246), lower=(200, 210, 228), accent=(60, 96, 170), idle="iai",
         weapon="katana", props=["daisho"], eyes="narrow", face="sharp", mouth="frown"),
    dict(key="hatamoto_champion", name="Hatamoto's Champion", skin=SKIN, hair=BLACK, hairstyle="short",
         build="armored", head="kabuto", crest="moon", helm=(60, 60, 70), armor=(120, 40, 40), lace=(220, 190, 90),
         top=(140, 40, 40), lower=(60, 40, 40), accent=(220, 190, 80), facial="mustache", height=2, wide=1,
         weapon="katana", props=["daisho"], brow="stern"),
    # A4 ashigaru
    dict(key="ashigaru", sashimono=(150, 40, 36), name="Ashigaru Spearman", skin=TAN, hair=BLACK, hairstyle="short", bangs="short",
         build="armored_light", hat="jingasa", hat_col=(52, 48, 54), armor=(70, 66, 70), lace=(140, 40, 36),
         top=(80, 90, 110), lower=(70, 74, 84), accent=(140, 40, 36), weapon="yari", face="round"),
    dict(key="border_patrol", sashimono=(120, 40, 36), name="Border Patrol", skin=TAN, hair=BLACK, hairstyle="short", bangs="short",
         build="armored_light", hat="jingasa", hat_col=(120, 40, 36), armor=(80, 76, 80), lace=(200, 180, 120),
         top=(90, 80, 70), lower=(70, 64, 58), accent=(200, 180, 120), weapon="yumi", props=["quiver"]),
    dict(key="sergeant_spears", sashimono=(160, 50, 40), name="Sergeant of Spears", skin=TAN, hair=BLACK, hairstyle="chonmage",
         build="armored", head="kabuto", crest="disc", helm=(60, 58, 64), armor=(84, 80, 86), lace=(160, 50, 40),
         top=(80, 90, 110), lower=(70, 74, 84), accent=(160, 50, 40), facial="mustache", weapon="yari", height=1,
         brow="thick"),
    dict(key="heavy_infantry", sashimono=(66, 84, 116), mon="crab", scale=1.12, name="Heavy Infantry", skin=TAN, hair=BLACK, hairstyle="short", build="heavy",
         head="kabuto_full", mask="mempo", crest="none", helm=(70, 74, 86), armor=(80, 92, 110), lace=(60, 70, 90),
         top=(66, 84, 116), lower=(48, 54, 72), accent=(164, 54, 44), height=4, wide=2, weapon="tetsubo",
         eyes="narrow"),
    # A5 pirates
    dict(key="dock_ruffian", name="Dock Ruffian", skin=TAN, hair=BLACK, hairstyle="bald", build="peasant",
         head="hachimaki", band=(60, 90, 140), facial="stubble", mouth="toothless", weapon="kama", face="square",
         top=(70, 100, 130), lower=(90, 80, 70), accent=(60, 90, 140), wide=1),
    dict(key="wako_raider", name="Wako Raider", skin=TAN, hair=BROWN, hairstyle="spiky", build="peasant",
         head="headcloth", cloth=(40, 60, 100), pattern="stripes", pcol=(200, 200, 210), top=(60, 80, 120),
         lower=(80, 70, 60), accent=(180, 60, 40), facial="goatee", weapon="nodachi", rusty=True, mouth="grin"),
    dict(key="mantis_corsair", name="Mantis Corsair", skin=TAN, hair=BLACK, hairstyle="long", bangs="side",
         build="armored_light", weapon="kama", props=["gourd"], brow="stern", **MANTIS),
    dict(key="storm_renegade", name="Storm Legion Renegade", skin=TAN, hair=BLACK, hairstyle="short", build="armored",
         head="kabuto", crest="horns", crest_col=(120, 200, 160), helm=(40, 70, 60), weapon="naginata", height=2,
         facial="mustache", **MANTIS),
    # A6 cultists
    dict(key="painted_cultist", glow=(230, 90, 60), name="Painted Cultist", skin=TAN, hair=BLACK, hairstyle="bald", head_tattoo=True,
         tattoo=(150, 30, 34), build="monk", top=(70, 60, 60), lower=(60, 50, 50), accent=(150, 30, 34),
         eyes="narrow", mouth="grin", weapon="kama"),
    dict(key="blood_acolyte", glow=(220, 40, 60), name="Blood-Hungry Acolyte", skin=PALE, hair=BLACK, hairstyle="long", bangs="center",
         build="robe", top=(110, 30, 40), lower=(70, 24, 32), accent=(40, 30, 34), eyes="glow", weapon="none",
         props=["scroll"], face="sharp"),
    dict(key="stitched_monk", name="Stitched-face Monk", skin=SKIN, hair=BLACK, hairstyle="bald", build="robe",
         top=(120, 116, 110), lower=(96, 92, 88), accent=(60, 56, 54), mask="stitched", eyes="narrow",
         weapon="shakujo", ofuda_staff=False),
    dict(key="maho_tsukai", glow=(200, 30, 50), name="Maho-tsukai", skin=PALE, hair=BLACK, hairstyle="mane", build="robe",
         top=(40, 34, 40), lower=(30, 26, 30), accent=(150, 24, 34), pattern="flames", pattern_on=("top", "lower"),
         pcol=(120, 20, 30), eyes="glow", weapon="none", props=["ofuda"], face="long"),
    dict(key="bloodspeaker", glow=(240, 50, 70), name="Bloodspeaker Adept", skin=PALE, hair=(30, 24, 30), hairstyle="long", build="robe",
         top=(150, 20, 34), lower=(60, 16, 26), accent=(220, 180, 70), cloak=(40, 20, 26), mask="death",
         eyes="glow", weapon="shakujo", ofuda_staff=False, height=2),
    # A7 ninja
    dict(key="shadow_in_black", name="Shadow-in-Black", skin=SKIN, hair=BLACK, hairstyle="short", bangs="none",
         head="headcloth", cloth=(30, 28, 36), cloth_dots=False, top=(34, 32, 40), lower=(28, 26, 34), accent=(60, 56, 70),
         mask="cloth", mask_col=(30, 28, 36), eyes="narrow", weapon="tanto"),
    dict(key="kolat_agent", name="Kolat Agent", skin=SKIN, hair=GREY, hairstyle="short", bangs="side",
         top=(110, 110, 116), lower=(80, 80, 86), accent=(60, 60, 66), cloak=(90, 90, 96), mask="cloth",
         mask_col=(80, 80, 86), eyes="narrow", weapon="tanto", props=["inro"]),
    dict(key="shosuro_renegade", name="Shosuro Renegade", skin=SKIN, hair=BLACK, hairstyle="long", bangs="center",
         top=(150, 26, 40), lower=(36, 30, 38), accent=(212, 170, 70), pattern="diamonds", pcol=(100, 18, 30),
         mask="noh", eyes="narrow", weapon="tanto", female=True),
    # Crab Ch2 (production/crab-ch2.md) -> EP428+
    dict(key="noboru", name="Shiba Noboru", skin=SKIN, hair=BLACK, hairstyle="chonmage", build="armored_light",
         top=(222, 104, 40), lower=(172, 58, 34), accent=(246, 206, 92), armor=(170, 84, 40), lace=(246, 206, 92),
         mon="phoenix", weapon="katana", props=["daisho"], face="square",
         kit=dict(eye="gentle", brow="straight", mouth="set", marks=[])),
    dict(key="maho_puppet", name="Maho Puppet", skin=(214, 206, 196), hair=BLACK, hairstyle="short", bangs="messy",
         build="peasant", head="headcloth", cloth=(200, 194, 180), top=(130, 122, 108), lower=(96, 88, 76),
         accent=(160, 40, 50), weapon="none", props=["scroll"], face="round",
         kit=dict(eye="half", brow="none", mouth="smile", marks=["bags", "paint_red"])),
    # Crab Ch2 guest side stories (sidestories/guests-07-12.md) -> EP430+
    dict(key="daidoji_agent", name="Daidoji Agent", skin=SKIN, hair=BLACK, hairstyle="chonmage", build="armored_light",
         top=(64, 92, 150), lower=(40, 54, 92), accent=(220, 228, 240), armor=(58, 84, 140), lace=(220, 228, 240),
         mon="crane", weapon="yari", face="sharp", height=1,
         kit=dict(eye="sharp", brow="angled", mouth="frown", marks=[])),
    dict(key="matsu_braggart", name="Matsu Braggart", skin=TAN, hair=(96, 58, 34), hairstyle="mane", build="normal",
         top=(214, 166, 56), haori=(150, 92, 40), lower=(128, 86, 44), accent=(158, 42, 36), mon="lion",
         weapon="katana", props=["daisho"], facial="mustache", face="square", wide=1,
         kit=dict(eye="round", brow="thick", mouth="grin", marks=[])),
    # Crab Ch3 Shadowlands (bestiary F, bosses.md b_boss_kommei) -> EP432+
    dict(key="zombie", name="Zombie", skin=(150, 160, 128), hair=BLACK, hairstyle="mane", build="peasant",
         head="headcloth", cloth=(84, 78, 64), top=(92, 86, 68), lower=(70, 66, 54), accent=(60, 50, 40),
         eyes="glow", glow=(150, 220, 110), weapon="none", face="long", **{"mouth": "open"}),
    dict(key="maho_bujin", name="Maho-bujin", skin=(176, 150, 140), hair=BLACK, hairstyle="chonmage",
         build="armored", top=(58, 58, 68), lower=(40, 40, 48), accent=(140, 30, 40), armor=(70, 64, 76),
         lace=(140, 30, 40), mon="crab", mask="mempo", eyes="glow", glow=(200, 30, 50), weapon="yari"),
    dict(key="moto_akutsukai", name="Moto Akutsukai", skin=(200, 196, 186), hair=GREY, hairstyle="mane",
         build="armored_light", top=(90, 60, 120), lower=(50, 36, 70), accent=(160, 150, 170), armor=(70, 60, 80),
         lace=(160, 150, 170), cloak=(30, 24, 36), mask="death", eyes="glow", glow=(150, 80, 255),
         weapon="naginata", height=2),
    dict(key="oni_kommei", name="Oni no Kommei", skin=(176, 84, 72), hair=BLACK, hairstyle="mane", build="heavy",
         top=(60, 64, 80), lower=(44, 46, 58), accent=(200, 60, 50), armor=(90, 96, 110), lace=(200, 60, 50),
         mon="crab", eyes="glow", glow=(255, 90, 40), weapon="tetsubo", facial="beard", height=3, wide=2,
         scale=1.3, mouth="grin"),
    # Crane Ch1 (production/crane-ch1.md; bestiary F "Crane coast & Beiden forest") -> EP500+ (epid)
    dict(key="kakita_senior", name="Senior Student", skin=SKIN, hair=BLACK, hairstyle="ponytail", build="normal",
         top=(236, 238, 246), lower=(120, 160, 214), accent=(60, 96, 170), mon="crane", weapon="bokken",
         face="sharp", height=1, kit=dict(eye="sharp", brow="angled", mouth="smirk", marks=[])),
    dict(key="forest_bandit", name="Forest Bandit", skin=TAN, hair=BLACK, hairstyle="short", bangs="messy",
         build="peasant", hat="jingasa", hat_col=(176, 150, 96), top=(110, 116, 84), lower=(86, 80, 64),
         accent=(70, 96, 60), facial="stubble", weapon="bo", face="round",
         kit=dict(eye="round", brow="thick", mouth="frown", marks=[])),
    # Crane Ch2 (production/crane-ch2.md S04): a Daidoji sentry under Miyako's charm, eyes glazed pink
    dict(key="seduced_sentry", sashimono=(70, 96, 150), name="Seduced Sentry", skin=SKIN, hair=BLACK, hairstyle="short", bangs="short",
         build="armored_light", hat="jingasa", hat_col=(60, 70, 96), armor=(70, 96, 150), lace=(200, 210, 230),
         mon="crane", eyes="glow", glow=(255, 150, 210), weapon="yari", face="round"),
    # Crane Ch2 boss: the three Iron Crane generals under Miyako's charm (iron-grey Daidoji armour, glazed pink eyes)
    dict(key="charmed_general", name="Charmed General", skin=SKIN, hair=BLACK, hairstyle="chonmage",
         build="armored", armor=(104, 110, 124), lace=(70, 96, 150), mon="crane", eyes="glow", glow=(255, 150, 210),
         facial="mustache", weapon="katana", props=["daisho"], face="square", height=1),
    # Lion Ch1: the Phoenix warehouse guards on the Magonojo (b_warehouse_raid, the Command tutorial)
    dict(key="phoenix_guard", sashimono=(222, 104, 40), mon="phoenix", name="Phoenix Guard", skin=SKIN, hair=BLACK, hairstyle="short", bangs="short",
         build="armored_light", armor=(196, 92, 44), lace=(246, 206, 92), hat="jingasa", hat_col=(172, 58, 34),
         weapon="yari", face="round"),
    # Lion Ch3: Miya Yachiko's hired archers on the rocks (b_boss_miya_killers)
    dict(key="miya_archer", name="Miya Archer", skin=SKIN, hair=BLACK, hairstyle="short", bangs="short",
         build="armored_light", armor=(90, 76, 120), lace=(214, 176, 64), hat="jingasa", hat_col=(70, 60, 90),
         weapon="yumi", props=["quiver"], face="square"),
    # Lion Ch4: the Matsu berserkers who charge the ford by mistake, and the Crane archers on the far bank
    dict(key="matsu_berserker", name="Matsu Berserker", skin=TAN, hair=BLACK, hairstyle="mane",
         build="armored_light", armor=(200, 120, 40), lace=(150, 40, 34), weapon="katana", face="square"),
    dict(key="crane_archer", name="Crane Archer", skin=PALE, hair=BLACK, hairstyle="short", bangs="short",
         build="armored_light", armor=(150, 186, 236), lace=(236, 238, 246), hat="jingasa", hat_col=(120, 150, 200),
         weapon="yumi", props=["quiver"], face="long"),
    # Crane Ch3: Ryohei the Eldest fights beside Katsuo if his offer is refused (a Mantis bushi; nunchaku)
    # Dragon Ch3 (the year 400; bestiary E): deserter palace guards with tachi, and the gaijin (pale, bearded, steel
    # morions read as jingasa, red doublets); the vanguard captain is bigger, with a broadsword
    dict(key="palace_deserter", name="Palace Guard", skin=SKIN, hair=BLACK, hairstyle="chonmage",
         build="armored_light", armor=(96, 110, 84), lace=(150, 130, 80), hat="jingasa", hat_col=(80, 90, 70),
         facial="stubble", weapon="katana", face="square"),
    dict(key="gaijin_pikeman", name="Gaijin Pikeman", skin=(236, 200, 180), hair=(150, 110, 60), hairstyle="short",
         bangs="short", build="armored_light", armor=(160, 162, 170), lace=(140, 40, 40), hat="jingasa",
         hat_col=(176, 178, 186), top=(150, 46, 44), lower=(70, 60, 56), facial="beard", weapon="yari", face="long"),
    dict(key="gaijin_musketeer", name="Gaijin Musketeer", skin=(236, 200, 180), hair=(190, 150, 80),
         hairstyle="short", bangs="short", build="normal", hat="jingasa", hat_col=(176, 178, 186),
         top=(150, 46, 44), lower=(70, 60, 56), accent=(200, 170, 90), facial="mustache", weapon="musket",
         face="long"),
    dict(key="gaijin_captain", name="Vanguard Captain", skin=(236, 200, 180), hair=(120, 80, 50), hairstyle="long",
         build="armored", armor=(170, 172, 180), lace=(150, 40, 40), hat="jingasa", hat_col=(190, 190, 196),
         facial="beard", weapon="nodachi", face="square", height=2, wide=1, brow="stern"),
    dict(key="ryohei", name="Ryohei the Eldest", skin=TAN, hair=BLACK, hairstyle="chonmage", build="armored_light",
         armor=(64, 116, 70), lace=(206, 170, 70), top=(64, 116, 70), lower=(96, 84, 52), facial="stubble",
         eyes="old", weapon="nunchaku", face="long", height=1),
    # Scorpion Ch3 / Unicorn Ch2 (Fortune's Lost Part II): the Iuchi hit squad, the war's "disappeared" officers in
    # basket hats and masks, festooned with meishodo amulets
    dict(key="iuchi_shugenja", name="Iuchi Shugenja", skin=TAN, hair=BLACK, hairstyle="chonmage", build="robe",
         top=(118, 72, 158), lower=(70, 50, 90), hat="jingasa", hat_col=(150, 120, 80), mask="cloth",
         mask_col=(60, 44, 70), weapon="katana", props=["ofuda"], face="long", brow="stern"),
    dict(key="amulet_bearer", name="Amulet-bearer", skin=TAN, hair=GREY, hairstyle="chonmage", build="robe",
         top=(80, 60, 110), lower=(60, 44, 80), hat="jingasa", hat_col=(120, 96, 60), mask="cloth",
         mask_col=(40, 30, 50), weapon="none", props=["ofuda", "inro", "gourd"], face="square", wide=1,
         brow="stern"),
    # Unicorn Ch1 "Fault Lines": Naohida's peasant guerrillas (Fortune's Lost: "hodgepodge scavenger style", bits of
    # Unicorn leather armour, kama and farm tools), powder-black hands
    dict(key="peasant_guerrilla", name="Peasant Guerrilla", skin=TAN, hair=BLACK, hairstyle="spiky", build="peasant",
         top=(110, 90, 70), lower=(80, 70, 56), head="headcloth", cloth=(140, 120, 150), weapon="kama",
         props=["gourd"], face="square", facial="stubble", brow="angled"),
    # Unicorn Ch3 "The Noblest Blood": Shiro Iuchi's servants, possessed by Regret through their ears. Kitchen
    # aprons, blank eyes, mouths open on the same song (bestiary D III Singing Servant)
    dict(key="singing_servant", name="Singing Servant", skin=PALE, hair=BLACK, hairstyle="bun", build="peasant",
         top=(196, 186, 200), lower=(118, 72, 158), head="headcloth", cloth=(230, 226, 220), weapon="none",
         face="long", eyes="glow", glow=(226, 226, 236), brow="worried", mouth="open"),
    # Unicorn Ch4 "Regret": the Emerald Legion, possessed, marching in a circle in the wind tunnel and chanting a dead
    # woman's name (Fortune's Lost: "Himeko. The war is over.")
    dict(key="possessed_legion", sashimono=(60, 120, 90), name="Possessed Legionnaire", skin=SKIN, hair=BLACK, hairstyle="chonmage",
         build="armored", armor=(60, 120, 90), lace=(214, 200, 120), weapon="yari", hat="jingasa",
         face="square", eyes="glow", glow=(226, 226, 236), brow="worried", mouth="open"),
    # Ronin Ch1 "What's Eating the Eta" (Honor and Eta): Tomie Cho in her first form, the old woman at the hut door
    # (long white hair to her knees, cloudy eyes, a faded cotton kimono); Tetsuo of Daigoro's band (a scarred lip, dirty
    # leather armour, a wakizashi)
    dict(key="tomie_old", name="Tomie Cho", skin=TAN, hair=(226, 230, 238), hairstyle="long", build="peasant",
         top=(170, 160, 140), lower=(130, 120, 104), weapon="none", age="old", eyes="old", face="round",
         mouth="toothless", female=True, brow="worried"),
    dict(key="tetsuo", name="Tetsuo", skin=TAN, hair=BLACK, hairstyle="ponytail", build="armored_light",
         armor=(96, 76, 56), lace=(70, 60, 50), weapon="tanto", scar=True, facial="stubble", face="square",
         eyes="narrow", brow="angled", mouth="frown"),
    # Ronin Ch2 "The Noble and the Ronin": Ikoma Sadanobu's retainers (Lion gold, ashigaru jingasa, yari) and their
    # captain; the Order of the Snake in the den under the harbourmaster's floor mats (Entanglements & Tied Snakes:
    # scholars, courtiers and "peasant ninjas", a snake tattoo on the forearm) -> EP1300+
    dict(key="ikoma_retainer", sashimono=(214, 166, 56), mon="lion", name="Ikoma Retainer", skin=TAN, hair=BLACK, hairstyle="chonmage",
         build="armored_light", armor=(188, 144, 58), lace=(150, 40, 34), weapon="yari", hat="jingasa",
         hat_col=(120, 86, 44), face="square", facial="stubble", brow="angled", mouth="frown"),
    dict(key="retainer_captain", name="Retainer Captain", skin=TAN, hair=BLACK, hairstyle="chonmage",
         build="armored", armor=(214, 166, 56), lace=(158, 42, 36), weapon="katana", props=["daisho"],
         face="square", facial="mustache", brow="thick", mouth="set", wide=1),
    dict(key="snake_enforcer", name="Snake Enforcer", skin=PALE, hair=BLACK, hairstyle="ponytail",
         build="armored_light", armor=(40, 46, 40), lace=(90, 130, 70), weapon="katana", mask="cloth",
         mask_col=(30, 36, 30), face="long", eyes="narrow", brow="angled"),
    dict(key="order_watcher", name="Order Watcher", skin=TAN, hair=BLACK, hairstyle="short", build="peasant",
         top=(60, 66, 56), lower=(44, 48, 40), head="headcloth", cloth=(50, 60, 46), weapon="tanto",
         face="round", brow="worried", mouth="set"),
    # Ronin Ch3: the rebel Imperial Guard of three hundred years ago, frozen, replaying the night (Past Heroes: "the green
    # & white of the Imperial Guard", mostly Lions and Crabs): pale, glowing-eyed, frost in the lacing
    dict(key="ghost_guard", sashimono=(150, 196, 176), name="Ghost-Guard", skin=(206, 222, 220), hair=(200, 214, 214), hairstyle="chonmage",
         build="armored", armor=(150, 196, 176), lace=(226, 236, 232), weapon="yari", hat="jingasa",
         hat_col=(170, 200, 190), face="square", eyes="glow", glow=(220, 250, 240), brow="stern", mouth="open"),
]


def epid(n):
    """EP400-435 for the first 36 entries (E200-E227 and the Crab chapters), then EP500-519, then EP1300+ (EP436-439
    are beasts, EP450-456 boss banners, EP460+ side cast, EP1100+ more side cast)."""
    if n < 36:
        return "EP%03d" % (400 + n)
    return "EP%03d" % (500 + n - 36) if n < 56 else "EP%d" % (1300 + n - 56)


EP = {c["key"]: epid(n) for n, c in enumerate(ENEMIES)}                  # gen_data: sprite ids by key


def config(c):
    T = dict(eye=(96, 62, 44), build="normal", female=False, bangs="normal", accent=(120, 90, 60),
             top=(110, 100, 90), lower=(80, 74, 66))
    T.update(c)
    return T


def main():
    preview_only = "--preview-only" in sys.argv
    jpath = os.path.join(g.RES, "enemy_pic.json")
    j = json.load(open(jpath, encoding="utf-8"))
    tmpl = j["EP000"]
    per, cw, ch = 4, g.FW * 3, g.FH + 4
    rows = (len(ENEMIES) + per - 1) // per
    sheet = Image.new("RGBA", (cw * per, ch * rows), (64, 90, 58, 255))
    d = ImageDraw.Draw(sheet)
    for n, c in enumerate(ENEMIES):
        T = config(c)
        r, cc = n // per, n % per
        for k, (kind, i) in enumerate((("idle", 0), ("attack", 0), ("attack", 1))):
            f = Image.fromarray(g.frame(T, kind, i), "RGBA")
            sheet.paste(f, (cc * cw + k * g.FW, r * ch - 6), f)
        d.text((cc * cw + 4, r * ch + g.FH - 10), c["name"], fill=(255, 255, 255, 255))
        if not preview_only:
            fname = "hum_%s" % c["key"]
            g.sheet(T).save(os.path.join(g.PIC, fname + ".png"))
            e = json.loads(json.dumps(tmpl))
            e.update({"name": {"en": c["name"], "ja": c["name"]}, "pic3d": "/resource/enemy_pic/%s.png" % fname,
                      "aniuv": [g.COLS, g.ROWS], "memo": "human enemy sprite (tools/gen_human_enemies.py)",
                      "gndpos": [0.5, (g.FH - g.GROUND - 1) / g.FH], "atkpos": [0.75, 0.55],
                      "cntpos": [0.5, 0.6], "scale": 1.05 * g.CAST_SCALE * g.HUMAN_SCALE * c.get("scale", 1.0), "flipx": False})  # engine draws enemies larger than party
            e["animap"] = [{"id": k, "st": v[0], "en": v[1], "spd": v[2], "loop": v[3], "replay": not v[3]}
                           for k, v in g.animap_for(T).items()]          # v4 layout: per-weapon main attack
            j[epid(n)] = e
        print("drew", c["name"])
    if not preview_only:
        json.dump(j, open(jpath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(os.path.join(g.PREVIEW, "human_enemies.png"))


if __name__ == "__main__":
    main()
