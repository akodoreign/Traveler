"""Engine test: a castle's story staged in the roamable castle (gen_maps CASTLE_STORY): start on a district / keep floor
with the chapter's flags, take shots, and print where the quest marker points.
python -E tools/test_castle_story.py CASE   (cases below)   -> _art/preview/bot/cs/"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import playbot  # noqa: E402

CRANE = ["G403"]
LION_PRE = ["G440", "G441", "G442", "G443", "G444", "G445", "G446", "G447", "G448", "G449", "G450", "G451", "G452", "G454", "G455", "G456", "G457", "G458", "G460", "G461", "G462", "G463", "G464", "G465", "G466", "G467", "G468", "G469", "G470", "G471", "G472", "G473", "G474", "G475", "G476", "G477", "G478", "G479", "G480", "G481", "G482", "G483", "G484", "G485", "G486", "G487", "G488", "G489"]   # Lion Ch1 done, Ch2 started
CASES = {   # map, builder x, z, flags, lead
    # Shiro Iuchi (2026-11-23): Unicorn Ch2's case 1 in the Courtyard garden; the valley road's door is the gate
    "iuchi_garden": ("M604", 24, 26, ["G967", "G968", "G970", "G971"], "P106"),
    "iuchi_oldsave": ("M391", 6, 4, ["G967", "G968", "G970", "G971"], "P106"),
    # Kyuden Isawa (2026-11-23): Phoenix Ch3's Council on the keep's 4F; the sealed library's door in the Archive court
    "isawa_fever_back": ("M288", 54, 18, ["G630", "G651", "G660"], "P104"),
    "isawa_council": ("M519", 48, 44, ["G630", "G651", "G660"], "P104"),
    "isawa_library": ("M573", 21, 38, ["G630", "G651", "G660", "G662", "G664", "G671"], "P104"),
    # Shiro Kitsuki (2026-11-23): Dragon Ch4's homecoming on the keep's 4F; Gendo's office (the epilogue) on 3F
    "kitsuki_home": ("M529", 48, 44, ["G830"], "P102"),
    "kitsuki_oldsave": ("M344", 6, 4, ["G830"], "P102"),
    "kitsuki_coda": ("M528", 20, 20, ["G830", "G821", "G823", "G1197", "G1198", "G1199"], "P102"),
    # Kyuden Togashi (2026-11-23): Scorpion Ch4's audience in the Courtyard garden; the road is the castle's town
    "togashi_procession": ("M382", 50, 15, ["G946"], "P105"),
    "togashi_audience": ("M615", 38, 40, ["G946", "G959"], "P105"),
    "togashi_oldsave": ("M383", 6, 4, ["G946", "G959"], "P105"),
    "togashi_after": ("M382", 80, 15, ["G946", "G959", "G947"], "P105"),
    "togashi_look": ("M615", 38, 40, ["G946"], "P105"),
    # Kyuden Bayushi (2026-11-23): Scorpion Ch1's memorial in the Shrine court, the teahouse in the North garden
    "bayushi_start": ("M586", 24, 7, ["G831"], "P105"),
    "bayushi_heard": ("M586", 24, 9, ["G831", "G832", "G834", "G835", "G836", "G833"], "P105"),
    "bayushi_teahouse": ("M588", 75, 48, ["G831", "G832", "G834", "G835", "G836", "G837"], "P105"),
    "bayushi_oldsave": ("M345", 6, 4, ["G831", "G832"], "P105"),
    "bayushi_teahouse_look": ("M588", 75, 47, ["G831", "G832", "G834", "G835", "G836", "G837", "G838"], "P105"),
    "doji_suite": ("M507", 70, 36, CRANE + ["G417"], "P101"),
    "doji_stacks": ("M508", 10, 20, CRANE + ["G417"], "P101"),
    "doji_stacks_open": ("M508", 10, 20, CRANE + ["G417", "G418"], "P101"),
    "doji_court": ("M509", 48, 40, CRANE + ["G417", "G418", "G419", "G420", "G422", "G423", "G424", "G425", "G426", "G428", "G430"], "P101"),
    "doji_gate": ("M228", 57, 27, CRANE + ["G417"], "P101"),
    "lion_gate": ("M255", 50, 27, LION_PRE, "P103"),
    "lion_hall": ("M511", 48, 26, LION_PRE + ["G1452"], "P103"),
    "lion_beat1_done": ("M511", 48, 26, LION_PRE + ["G491"], "P103"),
    "lion_beat2_done": ("M511", 48, 26, LION_PRE + ["G491", "G493", "G495"], "P103"),
    "lion_south": ("M511", 48, 26, LION_PRE + ["G1452", "G491", "G493", "G495", "G497", "G498", "G499", "G500"], "P103"),
    "lion_beat3": ("M511", 48, 26, LION_PRE + ["G1452", "G491", "G493", "G495", "G497"], "P103"),
    "lion_cell_done": ("M557", 30, 18, LION_PRE + ["G1452", "G491", "G493", "G495", "G497", "G498", "G499", "G500", "G502", "G501", "G511", "G513", "G503", "G504", "G506"], "P103"),
    "lion_arrest": ("M513", 72, 36, LION_PRE + ["G491", "G493", "G495", "G497", "G498", "G499", "G500", "G502", "G501",
                                                "G511", "G513", "G503", "G504"], "P103"),
    "doji_after_play": ("M555", 48, 46, CRANE + ["G417", "G418", "G419", "G420", "G422", "G423", "G424", "G425", "G426"], "P101"),
    "doji_letter_read": ("M550", 58, 14, CRANE + ["G417", "G418", "G419", "G420", "G422", "G423", "G424", "G425", "G426", "G1646"], "P101"),
    "doji_eve": ("M507", 70, 36, CRANE + ["G417", "G418", "G419", "G420", "G422", "G423", "G424", "G425", "G426", "G1646", "G440", "G428", "G437"], "P101"),
    "doji_dawn": ("M550", 58, 14, CRANE + ["G417", "G418", "G419", "G420", "G422", "G423", "G424", "G425", "G426", "G1646", "G440", "G428", "G437", "G1647"], "P101"),
}


def main():
    case = sys.argv[1]
    mp, x, z, flags, lead = CASES[case]
    bx, bz = playbot.block(mp, x, z)
    lines = ["wait 2500", "shot cs_%s_a" % case, "evalf ../../tools/test_marker_here.sk", "wait 9000",
             "shot cs_%s_b" % case]
    kept, timed = playbot.launch("cs", mp, bx, bz, lines, vars_=",".join(flags), lv="44", secs=90.0, quiet=True,
                                 lead=lead)
    for ln in kept:
        if any(k in ln for k in ("MARKER", "MSG", "rror", "xception", "CHOICE")):
            print(ln[:200])
    print("--", "TIMED OUT" if timed else "finished")
    playbot.convert_shots("cs", os.path.join(HERE, "..", "_art", "preview", "bot", "cs"))


if __name__ == "__main__":
    main()
