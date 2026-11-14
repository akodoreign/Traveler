"""Random-encounter balance (user: "the monsters should reflect expected party strength"): every encounter group on
each map, fought on auto by the party that is actually there at the chapter's expected level. Prints rounds, the
outcome and the party's HP left (lowest member and total). Target for a random battle: won in 2-5 rounds, the party
keeps roughly 50-90% of its HP.
python -E tools/balance_encounters.py [MAP ...]"""
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine_lock  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool"))
sys.path.insert(0, HERE)
import gen_maps as gm  # noqa: E402
import testbattle as tb  # noqa: E402

# map -> (Natsuko's expected level, companions present) - the join/leave points in gen_maps
PARTY = {"M102": (2, ""), "M130": (5, ""), "M131": (6, ""), "M132": (7, ""),
         "M140": (18, "P123"), "M148": (21, "P123,P124,P120"), "M149": (22, "P123,P124,P120"),
         "M171": (25, "P122"), "M172": (25, "P122"), "M173": (26, "P122"), "M176": (27, "P122,P126"),
         "M152": (34, "P120,P123"),
         # Crane Ch1: Rensei leads (-rtlead), the story guest is called in (G232; -rtguest)
         "M201": (2, "lead P101", "G232=5"), "M203": (5, "lead P101", "G232=6"), "M204": (6, "lead P101", "G232=6"),
         "M216": (20, "lead P101"), "M212": (21, "lead P101;party P123"),
         "M214": (22, "lead P101"), "M222": (30, "lead P101;equip P101+0+W130"),
         "M225": (33, "lead P101;equip P101+0+W130"), "M226": (33, "lead P101;equip P101+0+W130"),
         "M231": (41, "lead P101;equip P101+0+W130"), "M232": (42, "lead P101;equip P101+0+W130"),
         "M233": (43, "lead P101;equip P101+0+W130"),
         "M250": (5, "lead P103"), "M251": (6, "lead P103"),
         # Dragon Ch1: Gendo leads, Togashi Yosai joined at the dump (S03)
         "M309": (3, "lead P102;party P132"), "M310": (4, "lead P102;party P132"),
         "M311": (5, "lead P102;party P132"), "M312": (5, "lead P102;party P132"),
         "M318": (21, "lead P102;party P132"), "M319": (22, "lead P102;party P132"),
         # Dragon Ch3: Gendo + Seppun Ushimo (if Tsuhime was helped; :solo for Gendo alone)
         "M333": (30, "lead P102;party P134"), "M334": (31, "lead P102;party P134"),
         "M335": (32, "lead P102;party P134"),
         "M340": (42, "lead P102;party P132"),                         # Dragon Ch4: Gendo + Togashi Yosai
         # Scorpion Ch1: Mitsue alone on the roads south; with Yoritomo Rui in the west marsh
         "M348": (2, "lead P105"), "M350": (4, "lead P105"),
         "M356": (6, "lead P105;party P136"), "M357": (7, "lead P105;party P136"),
         # Scorpion Ch2: Mitsue alone on the plains; with Isawa Kasiko in the Temple District
         "M359": (20, "lead P105"), "M361": (21, "lead P105"),
         "M365": (22, "lead P105;party P137"), "M366": (23, "lead P105;party P137"),
         # Scorpion Ch3 (Mitsue's view): Mitsue + Akodo Rin in the Ojatara Valleys
         "M368": (30, "lead P105;party P138"), "M374": (31, "lead P105;party P138"),
         "M377": (32, "lead P105;party P138"),
         "M380": (40, "lead P105;party P132"), "M382": (41, "lead P105;party P132"),
         "M384": (42, "lead P105;party P132"), "M385": (43, "lead P105;party P132"),
         "M390": (4, "lead P106;party P140"), "M397": (7, "lead P106;party P140,P138"),
         # Unicorn Ch2 = Tamotsu's view of the same valleys (G967): Tamotsu + Ryuko + Rin
         "M368:uni": (23, "lead P106;party P140,P138", "G967=1"), "M374:uni": (24, "lead P106;party P140,P138", "G967=1"),
         "M377:uni": (26, "lead P106;party P140,P138", "G967=1"),
         # Unicorn Ch3: Tamotsu + Ryuko + Rin (Karasu is a Guest call); the tower with the wax in (G999)
         "M399": (30, "lead P106;party P140,P138", "G967=1"), "M400": (31, "lead P106;party P140,P138", "G967=1,G999=1"),
         "M401": (31, "lead P106;party P140,P138", "G967=1,G999=1"), "M405": (32, "lead P106;party P140,P138", "G967=1"),
         "M406": (33, "lead P106;party P140,P138", "G967=1"),
         "M409": (41, "lead P106;party P140,P138", "G967=1,G999=1"), "M410": (42, "lead P106;party P140,P138", "G967=1,G999=1"),
         # Ronin Ch1: Sayo alone outside Cakon (Warrior school)
         "M419": (5, "lead P107", "G1039=1"), "M420": (6, "lead P107", "G1039=1"),
         # Ronin Ch4: Sayo alone on the pilgrim road (Excellent Katana from the Ch3 outfitter)
         "M437": (41, "lead P107;equip P107+0+W134", "G1039=1,G1092=4"),
         # the finale: Party A of four travelers in the arrival kits (plugin FKIT), at the road's level
         "M444": (51, "party P101,P102,P103;equip P100+0+W127,P100+3+A116,P101+0+W131,P101+3+A141,P102+0+W144,"
                      "P102+3+A141,P103+0+W134,P103+3+A135", "G1162=1"),
         # the finale, Act 2: the Shinomen (Party A in the arrival kits, a level or two on from the shrine)
         "M447": (56, "party P101,P102,P103;equip P100+0+W127,P100+3+A116,P101+0+W131,P101+3+A141,P102+0+W144,"
                      "P102+3+A141,P103+0+W134,P103+3+A135", "G1162=1"),
         # the post-game deep Shadowlands (P1): Party A of the clear save, Lv 61-65, still in the arrival kits
         "M458": (61, "party P101,P102,P103;equip P100+0+W127,P100+3+A116,P101+0+W131,P101+3+A141,P102+0+W144,"
                      "P102+3+A141,P103+0+W134,P103+3+A135", "G1162=1"),
         "M459": (63, "party P101,P102,P103;equip P100+0+W127,P100+3+A116,P101+0+W131,P101+3+A141,P102+0+W144,"
                      "P102+3+A141,P103+0+W134,P103+3+A135", "G1162=1"),
         "M461": (69, "party P101,P102,P103;equip P100+0+W127,P100+3+A116,P101+0+W131,P101+3+A141,P102+0+W144,"
                      "P102+3+A141,P103+0+W134,P103+3+A135", "G1162=1"),
         "M462": (72, "party P101,P102,P103;equip P100+0+W127,P100+3+A116,P101+0+W131,P101+3+A141,P102+0+W144,"
                      "P102+3+A141,P103+0+W134,P103+3+A135", "G1162=1"),
         "M460": (65, "party P101,P102,P103;equip P100+0+W127,P100+3+A116,P101+0+W131,P101+3+A141,P102+0+W144,"
                      "P102+3+A141,P103+0+W134,P103+3+A135", "G1162=1"),
         "M254": (21, "lead P103;equip P103+0+W100"), "M261": (22, "lead P103;equip P103+0+W137"),
         "M266": (27, "lead P103;equip P103+0+W137,P103+4+A119"), "M269": (29, "lead P103;equip P103+0+W137,P103+4+A119", "G232=8"),
         "M270": (29, "lead P103;equip P103+0+W137,P103+4+A119", "G232=8"),
         "M272": (41, "lead P103;equip P103+0+W138,P103+4+A119", "G232=8"),
         # Phoenix Ch1: Haruki and his yojimbo (user: a shugenja never travels alone)
         "M251:phx": (2, "lead P104;party P131", "G585=1,G588=1"), "M250:phx": (3, "lead P104;party P131", "G585=1,G588=1"),
         "M278": (5, "lead P104;party P131", "G585=1,G588=1"),
         "M283": (20, "lead P104;party P131"), "M284": (21, "lead P104;party P131"),
         "M289": (30, "lead P104;party P131"), "M292": (32, "lead P104;party P131")}


def fight(mid, gid, lv, party, rtvar=""):
    engine_lock.wait_free()                                              # (single-instance engine: never kill one this script did not start)
    log = os.path.join(HERE, "..", "_art", "preview", "bal_%s_%d.log" % (mid, gid))
    args = [os.path.join(TOOL, "rpgcobo.exe"), "-testplay", "-battle", mid, str(gid), "-debuglv", str(lv),
            "-rtauto", "-rtfast"]
    if rtvar:
        args += ["-rtvar", rtvar]
    if party:
        args += ["-rt", party if ";" in party or party.startswith("lead") else "party " + party]
    with open(log, "w") as lf:
        p = engine_lock.launch(args, cwd=TOOL, stdout=lf, stderr=subprocess.STDOUT)
    t0 = time.time()
    while p.poll() is None and time.time() - t0 < 300:
        time.sleep(1)
    if p.poll() is None:
        subprocess.run(["taskkill", "/PID", str(p.pid), "/F"], capture_output=True)
    txt = open(log, errors="replace").read()
    rounds = txt.count("[RT] order now")
    lost = "DEFEATED" in txt
    hp = tb.party_hp(txt)
    party_names = list(hp)
    left = [hp[n][0] / max(1, hp[n][1]) for n in party_names]
    tot = sum(hp[n][0] for n in party_names) / max(1, sum(hp[n][1] for n in party_names))
    return rounds, lost, (min(left) if left else 1.0), tot


def main():
    mids = sys.argv[1:] or list(PARTY)
    for key in mids:
        lv, party, *rtvar = PARTY[key]
        mid = key.split(":")[0]                   # "M251:phx": the same map on another path (ENCOUNTERS rt_if)
        on = set(v.split("=")[0] for v in (rtvar[0].split(",") if rtvar else []))
        groups = gm.ENCOUNTERS[mid][1]
        for i, row in enumerate(groups):
            name = row[0]
            cond = row[3] if len(row) > 3 else {}
            if ("rt_if" in cond and cond["rt_if"] not in on) or ("rt_ifnot" in cond and cond["rt_ifnot"] in on):
                continue
            r, lost, low, tot = fight(mid, i + 1, lv, party, *rtvar)
            flag = "LOST" if lost else ("hard" if tot < 0.45 or r > 6 else "easy" if tot > 0.92 and r <= 2 else "ok")
            print("%s Lv%-2d %-26s %-34s %2d rounds  low %3d%%  total %3d%%  %s" % (
                mid, lv, party or "solo", name, r, low * 100, tot * 100, flag))


if __name__ == "__main__":
    main()
