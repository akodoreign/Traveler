"""Dialogue clean-up pass (user, 2026-11-09: "go through the text dialog for whole game, make sure it makes sense").
Runs at the end of tools/regen.py, after apply_bust_emotions.py, on project/data/map.json. It is a post-pass on purpose:
the lines come from two places (tools/gen_maps.py and the scripts in docs/story/production/*.md), and one table here
is easier to read and to check than fifty scattered edits. Every fix prints how many lines it changed; a fix that no
longer matches anything is listed as STALE (the source text changed: update or delete the entry).
  python -E tools/apply_dialog_fixes.py            apply
  python -E tools/apply_dialog_fixes.py --check    report only, write nothing
Reading copies of the whole script (branches, flags, busts): _art/preview/agents/dialog/ (see NOTES.md)."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "data"))

# ("sub", where, old fragment, new fragment)       where = None | "M123" | "M123/#4#" | ("M1", "M2")
# ("name", where, old speaker, new speaker[, text fragment])
# ("del", where, exact text)
# ("before" | "after", where, anchor text fragment, [(speaker, text[, emo]), ...])
# ("set", where, exact text, {"name":..., "text":..., "emo":...})
# ("page", "M143/#3#", [reqs], [(speaker, text[, emo]), ...])      a new last page on that event
# ("dir", where, "Speaker|text fragment" or "text fragment", {"emo": .., "act": .., "zoom": ..})
#     direction on existing lines (2026-11-22, conversational exposition): emo = the bust (travelers have all 8),
#     act = the speaker's 3D emote, zoom = the camera closes on the speaker for that line (RokuganCloseup.sk).
#     Inserted lines take the same as a 4th tuple item: (speaker, text, emo, {"act": "nod", "zoom": True}).
def msg(name, text, emo=None, extra=None):
    c = {"cmd": "cmd_showmsg", "key": "message_talk", "text": text, "name": name, "uiclose": 2}
    if emo:
        c["emo"] = emo
    c.update(extra or {})
    return c


def IF(flag, lines, else_lines=None, op="==", val=True):
    """A conditional block inside a before/after insert: IF("G208", [(speaker, text, ...), ...])."""
    mk = lambda ls: [x if isinstance(x, dict) else msg(*x) for x in ls]
    return {"cmd": "cmd_if", "reqs": [{"lvar": flag, "op": op, "rvar": val}],
            "cmdblocks": [mk(lines), mk(else_lines or [])]}


Z = {"zoom": True}
SANAE_WAITS = {"cmd": "cmd_compute", "lvar": "G1649", "op": "=", "rvar": True}     # Doji Sanae waits / rejoins
SANAE_BACK = {"cmd": "cmd_compute", "lvar": "G1649", "op": "=", "rvar": False}      # (RokuganBattle guestPresent)                                                 # direction shorthands (RokuganCloseup.sk)


def A(act, zoom=False):
    return {"act": act, "zoom": True} if zoom else {"act": act}


PAST = ("M325", "M326", "M337")                                    # the year 400: nobody may say "Kitsuki"
FIXES = [
    # ---- leaked stage directions and notes
    ("sub", "M148", " rat-way shortcut through donjon_1) [END]", ""),
    ("sub", "M148", "Filed. Just like the Crab said.", "Filed. Somebody came down here with a rasp."),   # true with or without the veteran's tip
    ("sub", "M174", "A clean stroke, off-screen. She", "A clean stroke. She"),
    ("del", "M174", "(Natsuko leaves his patrol report under a stone.)"),
    ("sub", "M133", "The party turns to leave. Seppun Ryozo, bleeding, crawls into a side tunnel. The camera stays behind.",
     "Natsuko turns to leave. Seppun Ryozo, bleeding, crawls into a side tunnel, and nobody sees him go."),
    ("sub", "M511", "The camera slides past the great names and stops at the last cushion: Akodo Shizue.",
     "Past all the great names, on the very last cushion: Akodo Shizue."),
    ("sub", "M306", "Quick cuts: Kitsuki Gendo shouting for a healer; Kosai \"can't find one\"; Gendo's hands steady as he sniffs the tea.",
     "Gendo shouts for a healer. Kosai \"can't find one\". Gendo's hands are steady as he sniffs the tea."),
    ("sub", "M317", "Training montage. Kitsuki Gendo drops", "An afternoon of it. Kitsuki Gendo drops"),
    ("sub", "M342", "The scene shimmers.", "The room shimmers."),
    ("sub", "M377", "Not this chapter. Not without", "Not today. Not without"),
    ("sub", "M445", "The post-game regions - the Shadowlands deep, Hiruma Castle, Lv 61-80 - aren't built yet.",
     "Two more roads open from the shrine gate: the deep Shadowlands, and a storm off the Crane coast."),
    ("sub", "M220", "Ship'S Master", "ship's master"),
    # ---- lines that answered nothing, or contradicted the scene
    ("sub", "M101", "Hiruma. Not today. Come back when the court's done with you.",
     "Hiruma. Not today. The Wall will still be here when you get back."),
    ("sub", "M101", "Back from the Shadowlands and still in one piece. Mostly.",
     "Still in one piece, Natsuko? Mostly? Good. Keep it that way."),
    ("before", "M101", "Keep it.", [("", "Inside the gate, Kage holds the map case out to Natsuko. Then he draws it back.")]),
    # (2026-11-22: Mutsuye's G210 page moved into gen_maps hida_garden with the castle rework; M143 is a stub now)
    ("before", "M205/#10#", "Take them. You'll need them more", [("", "The village granary. Imuro has left the lid off a crate of rice balls.")]),
    ("sub", "M207", "Certainty is worse.", "It says Heaven decides. My father thinks Heaven sounds like him. Certainty is worse than cruelty, Kakita-san."),
    ("sub", ("M208", "M209"), "Kakita Morishu dies. Sariko's cry carries across the yard.",
     "Kakita Morishu dies before the sun is up. In the village, Sariko's cry carries a long way."),
    ("sub", ("M208", "M209"), "- and stood beside him.", "- and had to decide what kind of Crane to be."),
    ("sub", ("M208", "M209"), "Kitsuki Seigen and Matsu Kiku go their own ways. (Their side stories come later.)",
     "Kitsuki Seigen and Matsu Kiku take their leave for now. (Either will answer the Guest call again when you find them on the road.)"),
    ("before", "M210", "My father's. A copy of one corner.", [("", "She presses a folded scrap of oiled paper into his hand.")]),
    ("before", "M210", "For the scalding sake.", [("", "He hands her a small porcelain cup, wrapped in white silk.")]),
    ("sub", "M509", "refused his father, and drew first blood - and found", "faced his father on the white sand - and found"),
    ("sub", "M248/#4#", "He's impatient now. He'll do something tonight.", "He's here. In this room. The dead have stopped whispering."),
    ("sub", "M252", "guard. I challenge you. First blood.", "Shiba-san. I challenge you. First blood."),
    ("sub", "M512", "My wedding is in eleven weeks.", "My wedding is before the thaw."),
    ("before", "M513", "...It's lying. It won't come back.", [
        ("", "The oni squeals - \"I will return! I will devour your souls!\" - and is gone through the floor.")]),
    ("del", "M285", "Night falls over the treaty city."),
    ("set", "M289", "Every hour he stays, it spreads further. I'm sorry. I'm so sorry.",
     {"name": "Isawa Haruki", "text": "Every hour I stay, it spreads further. I'm sorry. I'm so sorry.", "emo": "worried"}),
    ("before", "M290", "It won't cure this. Nothing cures this.", [
        ("", "On the last mat, a healer with dark veins to her jaw presses a scroll into Haruki's hands.")]),
    ("sub", "M317", "That's the second time someone's said that to me in a way that sounded like praise.",
     "I'll file that under praise. Nobody will check."),
    ("del", "M326", "You're asking after Seppun Ushimo? ..."),
    ("sub", "M326", "Ushimo? He lives by the south gate", "Seppun Ushimo? He lives by the south gate"),
    ("sub", PAST, "Coin first, Kitsuki-sama.", "Coin first, sir."),
    ("sub", "M328", "Three thousand, magistrate.", "Three thousand, stranger."),
    ("before", "M344", "The son will become the dark brother.", [("", "Later, alone, Gendo opens his notebook and writes down Akuro's prophecy.")]),
    ("del", "M352", "Kitsune Hana: older, in dark green with gold leaves. She bows and makes to leave, the way she leaves every room he is in."),
    ("before", "M352", "The governor hasn't been himself since spring.", [
        ("", "A Fox lady in dark green with gold leaves: Kitsune Hana. She bows, and makes to leave, the way she leaves every room the governor is in.")]),
    ("sub", "M418", "Ume-baa would be proud. She'd also tell you to eat something.",
     "Ume-baa will be proud when she hears. She'll also tell you to eat something."),
    ("before", "M418", "Akari? You're better!", [("", "A thin girl sits by the shrine fire, wrapped in a quilt: Akari.")]),
    ("sub", "M104", "Coin first, Hiruma-sama.", "Coin first, Crab."),
    # ---- speaker names (one name = one bust)
    ("name", None, "Nezumi shaman", "Nezumi Shaman"),
    ("name", None, "Nezumi warrior", "Nezumi Warrior"),
    ("name", None, "Bandit chief", "Bandit Chief"),
    ("name", None, "Seduced sentry", "Seduced Sentry"),
    ("name", None, "Crane Soldier", "Crane soldier"),
    ("name", "M303", "Captain", "Mantis captain"),
    ("name", ("M289", "M290"), "Kitsune Hana", "Little Hana"),         # the Phoenix fever child is not Scorpion Ch1's Fox lady
    ("name", "M379", "Shosuro Norie", "Shosuro Norie (letter)"),
] + [
    # =================================================================================================================
    # Conversational exposition (user 2026-11-22: "you are responsible now for conversational exposition"; "crabs
    # first story has great exposition, it just falls off after that"). Rules: a fact is said only by someone who
    # needs it said right then (a newcomer, a superior about to be asked, a culprit cornered); it changes trust or
    # stakes; it comes in small beats with a gesture or a reaction between. Travelers get moods, emotes, close-ups.
    # ---- Crab Ch2, the women's shrine (M147): the clues land on Natsuko's face
    ("dir", "M147", "Hiruma Natsuko|Tunnel of Quiescent Flame. You were the only honest", {"emo": "sad", "zoom": True}),
    ("dir", "M147", "Hiruma Natsuko|Shrine-path mud is red clay.", {"emo": "determined", "act": "think", "zoom": True}),
    ("dir", "M147", "Hiruma Natsuko|(Why would a Phoenix lady walk", {"emo": "worried"}),
    ("dir", "M147", "Hiruma Natsuko|Then walk with me. I have mud.", {"emo": "happy", "act": "point"}),
    # ---- Crab Ch2 S01 (M504): why a scout is at court
    ("before", "M504", "Kyuden Hida. Seven floors of black stone.", [
        ("", "Kaiu Takakana, karo of the Crab, has called Hiruma Natsuko off the Wall to Winter Court. He did not say why.")]),
    ("sub", "M504", "The audience hall. Hida Kisada in the Armor of the Shadow Warrior,",
     "The audience hall. Hida Kisada, the Great Bear, Champion of the Crab, in the Armor of the Shadow Warrior,"),
    ("dir", "M504", "Hiruma Natsuko|My lord Kage? Marry?", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M504", "Hiruma Natsuko|Why me? I'm a scout.", {"emo": "surprised", "act": "shrug"}),
    ("dir", "M504", "Hiruma Natsuko|What does blue mean?", {"emo": "worried", "zoom": True}),
    # ---- Crab Ch2 S04 (M504): the hearing. Takakana must know what she'll say before the Champion hears it; that is
    # the reason the case is laid out, and why "Asako Kuhime" can't be one of the answers.
    ("before", "M504", "The scout's findings, my lord.", [
        ("", "Dusk. The whole Winter Court has come to hear a junior Hiruma name a killer. The Unicorn mats are "
             "empty: Ide Keiyomi's people will not sit in this hall tonight."),
        ("", "At the foot of the dais, Kaiu Takakana leans close. His voice doesn't carry; he makes sure of it."),
        ("Kaiu Takakana", "Before you open your mouth, tell me. Who's on your list?"),
        ("Hiruma Natsuko", "The bride. Fresh Taint at her collar, the morning a girl dies.", "worried", A("think")),
        ("Kaiu Takakana", "The court saw the stain. That's all the court needs to see."),
        IF("G202", [("Hiruma Natsuko", "She laughed at my jokes, Takakana-sama. Nobody laughs at my jokes. "
                                       "She's no killer.", "sad")]),
        ("Hiruma Natsuko", "Then Yogo Shigeru. Scrolls in his room that name him. Neatly.", "neutral"),
        ("Hiruma Natsuko", "He can't forge a love letter neatly. I've read one.", "neutral", A("shrug")),
        IF("G208", [
            ("Hiruma Natsuko", "And the Wall Crabs told me the troll's chains in the donjon were filed. Not "
                               "broken. Filed.", "determined", A("point", True)),
            ("Kaiu Takakana", "...Then someone inside this castle let a monster out. Go on."),
        ]),
        ("Hiruma Natsuko", "And grey Wall mud on Asako Kuhime's hem. At dawn. On the shrine path.", "determined", Z),
        ("Kaiu Takakana", "Kuhime is an Asako, and the bride's dearest friend. Mud is not a culprit."),
        ("Kaiu Takakana", "Say her name in there without proof, and the Phoenix will ask the Champion for your head. "
                          "He will give it to them."),
        ("Hiruma Natsuko", "...Then I'd better not lose it before I have proof.", "worried", A("scratch")),
        ("", "Hida Kisada has not moved since noon. He moves his eyes now, down the length of the hall, to Natsuko."),
    ]),
    ("before", "M504", "Then I demand the right to defend my lady's name.", [
        ("", "A young Phoenix in plain grey steps out from behind the bride: Shiba Noboru, her yojimbo. The Shiba have "
             "guarded the Isawa with their lives for a thousand years.")]),
    ("before", "M504", "Win or lose, Isawa Mutsuye is confined to her rooms.", [
        ("", "First blood, and it is over. Shiba Noboru bows, white to the lips, and goes back to stand behind his lady.")]),
    ("after", "M504", "Win or lose, Isawa Mutsuye is confined to her rooms.", [
        ("Hiruma Natsuko", "(She bowed to me as they led her out. She bowed to me.)", "sad", Z)]),
    ("before", "M504", "Yogo Shigeru is dragged out protesting.", [
        ("", "The scrolls from Yogo Shigeru's room are read aloud. He shouts that he forges love letters, not "
             "confessions. Nobody laughs.")]),
    ("dir", "M504", "Hiruma Natsuko|(He was a creep. He wasn't a killer.", {"emo": "sad", "zoom": True}),
    ("dir", "M504", "Hiruma Natsuko|My lord. I don't have a culprit. I have mud.", {"emo": "worried", "act": "rei", "zoom": True}),
    ("dir", "M504", "Hiruma Natsuko|Give me one night, and I'll give you the hand", {"emo": "determined", "zoom": True}),
    # S07 + Crab Ch4 S01 (M504)
    ("dir", "M504", "Hiruma Natsuko|The puppet didn't do it alone.", {"emo": "determined", "zoom": True}),
    ("dir", "M504", "Hiruma Natsuko|Then why-", {"emo": "surprised", "act": "surprise"}),
    ("dir", "M504", "Hiruma Natsuko|My lady.", {"act": "rei"}),
    ("dir", "M504", "Hiruma Natsuko|...I've seen someone drink sake like that before.", {"emo": "worried", "act": "think", "zoom": True}),
    # ---- Crab Ch2 S02b (M501): the laughed-at line lost its words (a line all in brackets was cut to nothing)
    ("set", "M501", "", {"name": "Hiruma Natsuko", "text": "(Well. The Wall doesn't dance either.)", "emo": "hurt",
                         "act": "scratch"}),
    # ---- Crab Ch2 S05-S06 (M148-M150): the trail
    ("dir", "M148", "Hiruma Natsuko|Filed. Somebody came down here with a rasp.", {"emo": "determined", "act": "think", "zoom": True}),
    ("dir", "M149", "Hiruma Natsuko|Every Crab walks through jade dust", {"emo": "worried", "act": "point", "zoom": True}),
    ("dir", "M150", "Hiruma Natsuko|Who's holding your strings?", {"emo": "angry", "zoom": True}),
    # ---- Crab Ch4 S03 (M153): the barrel. Sachiko and Goro don't know what she knows; they ask, she works it out.
    ("dir", "M153", "Hiruma Natsuko|Two weeks. She's been dead two weeks.", {"emo": "sad", "zoom": True}),
    ("dir", "M153", "Hiruma Natsuko|...Then who did my lord just marry?", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("after", "M153", "Upstairs: laughter. A woman's laughter", [
        ("Hida Sachiko", "Hiruma. Talk to me. Who's in the barrel?"),
        ("Hiruma Natsuko", "Asako Kuhime. The real one. Whatever stood beside Kage today is wearing her face.", "sad"),
        ("Hiruma Goro", "A face-thief. In the Champion's own house. On his wedding day."),
        ("Hida Sachiko", "Then how do we find it? It could be anyone up there. It could be me."),
        ("Hiruma Natsuko", "It drank scalding sake at the wedding without a flicker. Kuhime blew on her tea for a "
                           "full minute.", "determined", A("think", True)),
        ("Hiruma Goro", "A small thing to hang a life on."),
        ("Hiruma Natsuko", "Then here's a bigger one. Jade burns anything the Shadowlands made.", "determined"),
        ("Hiruma Natsuko", "I've got jade dust on my glove from the trap lines. One brush, and it smokes.", "determined",
         A("point")),
        ("Hida Sachiko", "And if it's careful? Keeps its sleeves down?"),
        ("Hiruma Natsuko", "Then hand it a smooth river stone and call it jade. Something that's never touched jade "
                           "won't know the difference.", "neutral"),
        ("Hiruma Goro", "And if you grab the wrong one?"),
        ("Hiruma Natsuko", "Then I've jumped a frightened servant in the dark, she's laughing at us, and she gets "
                           "closer. So we test first.", "worried"),
        ("Hiruma Natsuko", "One more thing. At court she only ever watched one of us at a time. If we split at a "
                           "junction, she has to pick who to follow.", "determined", A("crossarms")),
        ("Hida Sachiko", "...I hate this castle."),
    ]),
    # ---- Crab Ch4 S04 (M503): unmasked, she names herself (the Crab road never hears her name otherwise)
    ("dir", "M503", "Hiruma Natsuko|Here. Jade. For luck.", {"emo": "happy", "zoom": True}),
    ("before", "M503", "...You little Crab.", [
        ("", "The servant's face slides like wet paint. Under it: a woman in a white wedding kimono four centuries out "
             "of fashion, smiling with far too many teeth.")]),
    ("after", "M503", "...You little Crab.", [
        ("Nashiko", "Nashiko. Remember it, scout. Your Hiruma lord already said it to me once today. 'Wife.'"),
        ("Hiruma Natsuko", "You wore her for two weeks. You sat at her table. You let him grieve beside you.", "angry", Z),
        ("Nashiko", "I was a bride once. Nobody let me keep it. I'm only borrowing it back."),
    ]),
    ("dir", "M503", "Hiruma Natsuko|...No. Not without proof.", {"emo": "worried", "act": "crossarms"}),
    ("dir", "M502", "Hiruma Natsuko|Akiko. Go to the cellars.", {"emo": "determined", "zoom": True}),
    ("dir", "M157", "Hiruma Natsuko|Like a goblin. Goats are smarter.", {"emo": "happy", "act": "laugh"}),
    ("dir", "M157", "Hiruma Natsuko|\"Something none of us has seen before.\"", {"emo": "worried", "act": "think", "zoom": True}),
] + [
    # =============================================================== CRANE (Kakita Rensei), read in full 2026-11-22
    # ---- Ch1. Sanae told a Kakita graduate who Morishu was ("as you know"): she asks; he betrays the silence.
    ("set", "M201", "A Kakita prodigy named Kakita Morishu shamed his house a year ago and vanished.",
     {"name": "Doji Sanae", "text": "You were at the Academy when Kakita Morishu left it, Rensei-san."}),
    ("after", "M201", "You were at the Academy when Kakita Morishu left it", [
        ("Kakita Rensei", "Everyone was, my lady. His name came off the board in one night. Nobody has said it since.",
         "worried", A("rei")),
        ("Doji Sanae", "You just did."),
    ]),
    ("dir", "M201", "Kakita Rensei|...Keep it, my lady?", {"emo": "worried", "act": "scratch"}),
    ("dir", "M201", "Kakita Rensei|(...What if what \"never happened\" did happen?)", {"emo": "worried", "zoom": True}),
    ("dir", "M200", "Kakita Rensei|Yes, Father.", {"emo": "neutral", "act": "rei"}),
    ("dir", "M200", "Kakita Rensei|...Adequate.", {"emo": "sad", "zoom": True}),
    ("dir", "M202", "Kakita Rensei|...Heaven's Glory Reflected in the Soul's Steel.", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M202", "Kakita Rensei|To Kakita Morihoshi's house. To his son.", {"emo": "worried", "zoom": True}),
    ("before", "M202", "Tripled. In three years.", [
        ("", "The Lion's rice tax on Pleasant Eaves, in the headman's neat hand, year by year.")]),
    ("dir", "M202", "Kakita Rensei|Tripled. In three years.", {"emo": "surprised", "act": "think"}),
    ("after", "M202", "Tripled. In three years.", [
        ("Kakita Rensei", "No wonder half the village is living in the forest.", "worried")]),
    # the inro: a letter that exists is not a beat; what it says is
    ("before", "M203", "A letter to his mother. He never sent it.", [
        ("", "Folded small inside the inro: \"Mother. I am well. I have friends here, and a wife. Please do not let "
             "Father send anyone.\"")]),
    ("dir", "M203", "Kakita Rensei|A letter to his mother. He never sent it.", {"emo": "sad", "zoom": True}),
    ("dir", "M203", "Kakita Rensei|How can you tell?", {"emo": "surprised", "act": "think"}),
    ("dir", "M204", "Kakita Rensei|My lady-", {"emo": "surprised", "act": "surprise"}),
    # the Green Ronin's village: who Sariko is, before she asks where he is
    ("before", "M205", "Where is he? He went into the forest at dawn and didn't come back.", [
        ("Imuro", "That's Sariko. His wife, Crane. The child is his."),
        ("Imuro", "Whatever your lady came here to make disappear, it has a family now."),
    ]),
    ("dir", "M205", "Kakita Rensei|Is... tea an option?", {"emo": "surprised", "act": "scratch"}),
    ("dir", "M205", "Kakita Rensei|...I understand the second part.", {"emo": "sad", "zoom": True}),
    ("dir", "M207", "Kakita Rensei|(...He looked straight at me and didn't see me.)", {"emo": "surprised", "zoom": True}),
    # the four ways: four options read out in a row is a menu, not a conversation. He answers two of them.
    ("after", "M207", "One. A blade slipped into his cell.", [
        ("Kakita Rensei", "He would have to hold it steady, my lady.", "worried")]),
    ("after", "M207", "Three. His bandit friends strike from the crowd.", [
        ("Kakita Rensei", "Imuro would come. All of them would come. Not all of them would go home.", "worried",
         A("crossarms"))]),
    ("dir", "M207", "Kakita Rensei|He can't hold a cup without shaking.", {"emo": "worried"}),
    ("dir", "M207", "Kakita Rensei|...You're deciding what kind of Crane I am.", {"emo": "determined", "act": "think", "zoom": True}),
    # the cells: why Yasurugi is there, and why Rensei - who brought a blade himself - stands in his way
    ("before", "M208", "Kakita Yasurugi says nothing. He only draws.", [
        ("Kakita Rensei", "Kakita-sama. You carried Lord Morihoshi's letter. His son didn't open his belly, so "
                          "you've come to do it for him. Before the Lion executioner can.", "angry", Z),
        ("Kakita Rensei", "Lady Sanae sent me with a blade for him. His own choice, in his own hand. Not yours.",
         "determined", A("point")),
    ]),
    # the yard when the bandits strike: nobody had said why Yasurugi steps out
    ("before", "M209", "Kakita Yasurugi says nothing. He only draws.", [
        IF("G319", [("Kakita Rensei", "His lord's letter. If Morishu won't open his own belly, Yasurugi will do it "
                                      "for him, here, before the Lion can.", "angry", Z)], val=3, op="=="),
    ]),
    ("dir", ("M208", "M209"), "Kakita Rensei|Then I'll stand in your way.", {"emo": "determined", "act": "point", "zoom": True}),
    ("dir", "M209", "Kakita Rensei|My lord. Kakita Morishu names a second.", {"emo": "determined", "act": "rei"}),
    ("dir", "M209", "Kakita Rensei|Me.", {"emo": "determined", "zoom": True}),
    ("dir", ("M208", "M209"), "Kakita Rensei|My lady. The letter. The death poem.", {"emo": "worried", "zoom": True}),
    ("dir", ("M208", "M209"), "Kakita Rensei|...Is that what you'll write in your report?", {"emo": "angry", "act": "crossarms"}),
    # ---- Ch2. Why the border is "a hair from war": the newcomer asks, the Keeper answers.
    ("before", "M211", "The border is a hair from war, Rensei-san. Those men are the hair.", [
        ("Kakita Rensei", "Forgive me, my lady. You said there was a crisis. Why are we at a dinner?", "worried"),
        ("Doji Sanae", "The Daidoji and the Hida have raided each other across that land-bridge twice since spring. "
                       "Each swears the other struck first."),
        ("Doji Sanae", "One more raid, and the Champions must answer it. The word for that is war."),
    ]),
    ("dir", "M211", "Kakita Rensei|They're all looking at her.", {"emo": "worried", "act": "think"}),
    ("dir", "M211", "Kakita Rensei|He was right. She lied. I heard her.", {"emo": "worried", "zoom": True}),
    ("sub", "M219", "Two Hida generals start shoving over a remark.",
     "Two Hida generals start shoving over a remark; the louder is Hida Masakazu, who led last month's raid."),
    # Sanae was beside him when Miyako lied: he tells her only what she didn't see
    ("set", "M217", "Miyako lied about a dead uncle. Miyubi drank sake hot enough to strip paint.",
     {"name": "Kakita Rensei", "text": "And Miyubi drank Crab sake hot enough to strip paint, my lady. Without a "
                                       "flicker. Nobody drinks it like that.", "emo": "neutral"}),
    ("dir", "M217", "Kakita Rensei|...Because they can't be.", {"emo": "surprised", "act": "think", "zoom": True}),
    ("dir", "M214", "Kakita Rensei|Who told you, my lord? A woman? At night?", {"emo": "determined", "act": "point"}),
    ("dir", "M214", "Kakita Rensei|The Lion your general cut down.", {"emo": "determined", "zoom": True}),
    ("dir", "M218", "Kakita Rensei|...Not two women. One.", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M210", "Kakita Rensei|...There was a Scorpion. At Goroso's castle.", {"emo": "surprised", "act": "think"}),
    # ---- Ch3. The fishwife's clue was never followed: Rensei asks, and the four brothers come out of it
    ("after", "M220", "They struck Shimo-ura and Kitahama on the same morning. Forty ri apart!", [
        ("Kakita Rensei", "The same morning? One ship can't sail forty ri before breakfast.", "surprised", A("think")),
        ("Fishwife", "One can't. Four can. Four white ships, my lord, one for each brother. The old men say so."),
        ("Fishwife", "And every pirate aboard wears a charm the White Brother painted. That's why the arrows miss."),
    ]),
    ("dir", "M220", "Kakita Rensei|I've never been on a boat.", {"emo": "worried", "act": "scratch"}),
    ("dir", "M221", "Kakita Rensei|Is it supposed to... move like this?", {"emo": "worried", "act": "surprise", "zoom": True}),
    ("dir", "M222", "Kakita Rensei|\"...Matsu Tadanobu.\" A Lion.", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M224", "Kakita Rensei|...Is it always like this?", {"emo": "worried", "act": "scratch"}),
    ("dir", "M225", "Kakita Rensei|Go. Take your brothers. Leave Katsuo to me.", {"emo": "determined", "act": "nod"}),
    ("after", "M227", "Believing is the only magic left, little Crane.", [
        ("Kakita Rensei", "Asahina Yajinden's ink. The Asahina still remember him.", "angry"),
        ("Katsuo the White Brother", "They remember to forget him. I remember for them."),
    ]),
    ("dir", "M227", "Kakita Rensei|Then believe this.", {"emo": "determined", "zoom": True}),
    ("dir", "M220", "Kakita Rensei|I brought a confession, my lady.", {"emo": "happy", "act": "rei"}),
    ("dir", "M220", "Kakita Rensei|My lady?", {"emo": "surprised", "act": "surprise", "zoom": True}),
    # ---- Ch4
    ("dir", "M228", "Kakita Rensei|(Bury it. She wants me to help bury it.)", {"emo": "worried", "zoom": True}),
    ("dir", "M233", "Kakita Rensei|She's colour-blind.", {"emo": "surprised", "act": "think", "zoom": True}),
    ("dir", "M233", "Kakita Rensei|A terror of disfigurement.", {"emo": "surprised", "act": "think"}),
    ("dir", "M233", "Kakita Rensei|She wants to be called Empress.", {"emo": "determined", "act": "think"}),
    ("dir", "M233", "Kakita Rensei|She doesn't know this play exists.", {"emo": "determined", "zoom": True}),
    ("after", "M232", "Paper stirs on the shelves with no wind to stir it, and stands up.", [
        ("Kakita Rensei", "\"Mind the guardian.\" He might have mentioned it was the library.", "surprised",
         A("surprise"))]),
    ("dir", "M507", "Kakita Rensei|No, Father.", {"emo": "determined", "zoom": True}),
    ("dir", "M507", "Kakita Rensei|...Yes, Father.", {"emo": "sad", "act": "rei"}),
    ("set", "M507", "\"To his son.\" He's never written that before.",
     {"name": "Kakita Rensei", "text": "\"To his son.\" He has never once written that to me.", "emo": "sad",
      "zoom": True}),
    ("set", "M550", "He didn't sign it \"Father\".",
     {"name": "Kakita Rensei", "text": "...He didn't sign it \"Father\".", "emo": "sad", "zoom": True}),
    # the question after the duel was bare: what each answer means
    ("set", "M509", "One question, Rensei-san. The House's honor, or the Empire?",
     {"name": "Doji Sanae", "text": "One question, Rensei-san. Your father wanted that play burned, for the House's "
                                    "honor. It may be the only thing that can finish her, for the Empire. Which?"}),
    ("dir", "M509", "Kakita Rensei|Why help me?", {"emo": "surprised", "act": "think"}),
    ("dir", "M509", "Kakita Rensei|...Father.", {"emo": "sad", "zoom": True}),
    # ---- Doji Sanae travels with her yojimbo (user 2026-11-22: "she keeps popping out of nowhere ... put her as a call
    # in 3rd row"; "she should wait at an inn like togashi does when not in party"; "So you need me now, do you?!").
    # Guest 18, S645 A Quiet Word (unlimited, ATK Down); RokuganBattle guestPresent; G1649 = she is waiting.
    ("after", "M201", "Kitsuki Seigen will answer your call in battle", [
        ("", "Lady Doji Sanae rides with her yojimbo from here on. In battle she stands in the third row: Support, "
             "A Quiet Word, as often as you like.")]),
    ("before", "M212", "Objective: cross to Yasuki Yashiki while the tide is out.", [
        ("", "Lady Sanae stays behind at the castle. A Crane lady does not wade to a Crab dinner. (She waits in her "
             "rooms at Garden Under Shadow.)"),
        SANAE_WAITS]),
    ("before", "M217", "The Crane generals hang on Miyako.", [
        ("Doji Sanae", "So you need me now, do you?!"),
        SANAE_BACK,
        ("Kakita Rensei", "I need you to listen, my lady. Both of them, both sides of the border.", "worried", A("rei")),
    ]),
    ("page", "M217/#6#", [{"lvar": "G1649", "op": "==", "rvar": True}], [
        ("Doji Sanae", "So you need me now, do you?!"), SANAE_BACK,
        ("", "Lady Sanae gathers her fan and her scrolls. (She stands in the third row again.)")]),
    ("after", "M220", "Ship travel unlocked: your ship is moored at the west pier.", [
        ("Doji Sanae", "I'll be in my quarters, Rensei-san. Ships and I disagree. Come and fetch me if you find you "
                       "need me."),
        SANAE_WAITS,
        ("", "(Lady Sanae waits at the Crane port. Talk to her there to bring her along.)")]),
    ("page", "M220/#3#", [{"lvar": "G1649", "op": "==", "rvar": True}], [
        ("Doji Sanae", "So you need me now, do you?!"), SANAE_BACK,
        ("Doji Sanae", "Very well. I shall be seasick with great dignity."),
        ("", "Lady Sanae comes aboard. (She stands in the third row again.)")]),
    ("before", "M220", "Back at port. The Imperial magistrate Otomo Shinken arrives", [
        ("", "Back at port. Lady Sanae is waiting on the pier, which she would deny."), SANAE_BACK]),
] + [
    # =============================================================== LION (Akodo Shizue), read in full 2026-11-22
    # ---- Ch1. The Ashimita duel never ran: the script line "[PA Duel Ashimita] [BATTLE b_duel_ashimita]" doesn't
    # start with [BATTLE, so script_scene dropped it, and "Win or lose" followed no fight. (Every clue branch.)
    ("after", ("M242", "M243", "M245", "M246", "M247"), "If she can stand against me, she's earned her day.", [
        ("", "A duel: first blood, no seconds. (Win or lose, fight it honorably.)"),
        {"cmd": "cmd_battle1", "mapid": "M001", "gid": 52, "losefunc": 1, "bgmid": None, "keeprset": False}]),
    ("after", ("M242", "M243", "M245", "M246", "M247"), "My grandfather. He screams. He has since I was born.", [
        ("Akodo Shizue", "Your grandfather?", "surprised"),
        ("Shiba Ashimita", "Dead before I was born. He didn't leave. Shiba blood keeps its dead close."),
    ]),
    # the clues: the narrator was doing the investigating. Shizue does it now.
    ("set", "M242", "Hojiki's wound-stone, then, is not jade at all.",
     {"name": "Akodo Shizue", "text": "Real jade. Then the stone Hojiki wrapped round his cut was never jade at all. "
                                      "Someone swapped it.", "emo": "determined", "act": "think", "zoom": True}),
    ("after", "M245", "He keeps his left arm very still. Under the sleeve, a fresh bandage.", [
        ("Akodo Shizue", "That's no practice scratch, Ryuzoji. You were meant to ride on that raid.", "worried",
         A("point"))]),
    ("after", "M245", "In Ozaki's room: a looted statue of Isawa, from the broken shrine.", [
        ("Akodo Shizue", "Gusai lit the torch. You gave the order, Ozaki.", "angry", A("point", True))]),
    ("after", "M245", "In a chest: a looted statue of Isawa, from the broken shrine.", [
        ("Akodo Shizue", "Gusai lit the torch. Ozaki gave the order.", "angry", A("think", True))]),
    ("dir", "M242", "Akodo Shizue|A ghost that lies. Then it isn't a peasant.", {"emo": "determined", "act": "think", "zoom": True}),
    ("dir", ("M242", "M243", "M245", "M246", "M247"), "Akodo Shizue|For the truth. You said you followed it here.", {"emo": "determined", "act": "rei", "zoom": True}),
    ("dir", "M245", "Akodo Shizue|If your hands did it, then someone is wearing your hands.", {"emo": "determined", "zoom": True}),
    ("dir", "M240", "Akodo Shizue|Gusai! The shrine is not a warehouse!", {"emo": "angry", "act": "point", "zoom": True}),
    ("dir", "M242", "Akodo Shizue|And if the truth starts a war, uncle?", {"emo": "worried", "zoom": True}),
    ("dir", "M243", "Akodo Shizue|I'll say what I always say.", {"emo": "happy", "act": "nod"}),
    # the hall: who O-Tamai is, and what the three plans are, before the choice
    ("before", "M248", "He's here. In this room. The dead have stopped whispering.", [
        ("Akodo Shizue", "Ijako. What is it? Say it plainly. The whole room is listening.", "worried")]),
    ("after", "M248", "He's here. In this room. The dead have stopped whispering.", [
        ("Akodo Ijako", "The thing Isawa Hoju bound in that skull. A Bloodspeaker: O-Tamai, Iuchiban's beloved. "
                        "Our raid broke his chain, and he has been wearing Hojiki in his sleep."),
        ("Akodo Shizue", "Three moves, then. Give him a body and chain it. Give him a duel to spoil. Or guard the "
                         "stone he wants most: my uncle.", "determined", A("think", True)),
    ]),
    ("dir", "M248", "Akodo Shizue|Uncle! Don't move!", {"emo": "surprised", "act": "point", "zoom": True}),
    ("dir", "M248", "Akodo Shizue|We'll take it in jade.", {"emo": "determined", "zoom": True}),
    ("dir", "M248", "Akodo Shizue|...You noticed.", {"emo": "happy", "act": "rei"}),
    ("dir", "M248", "Akodo Shizue|Good. You see the whole board from the far end.", {"emo": "happy", "zoom": True}),
    # ---- Ch2. Who sits at the head of the hall, and why a Crab is judging the Akodo
    ("sub", "M511", "Far up the hall: Akodo Toturi, quiet, watchful.",
     "Far up the hall: Akodo Toturi, Champion of the Lion Clan, quiet, watchful."),
    ("before", "M511", "The Crab were asked for their opinion of the Akodo.", [
        ("", "A Crab envoy, Kaiu Gesshin, has spent a week walking the Akodo's walls and drill yards at Toturi's own "
             "invitation. The hall waits for his verdict.")]),
    ("dir", "M511", "Akodo Shizue|\"Sufficient.\" From a Crab, that's a love poem.", {"emo": "happy", "act": "laugh"}),
    ("dir", "M511", "Akodo Shizue|Nishi-sama remembers a game from four summers ago?", {"emo": "surprised", "act": "surprise", "zoom": True}),
    # the "Crane spy" is shouted at before the game ever shows her
    ("before", "M511", "The Crane spy! Arrest her!", [
        ("", "Every eye goes to the one Crane at the Lion's court: Daidoji Atsuko, a Daidoji envoy whom everyone "
             "knows is a spy and nobody can prove it.")]),
    ("dir", "M511", "Akodo Shizue|Honor isn't a banner someone can steal from a wall.", {"emo": "determined", "zoom": True}),
    ("dir", "M511", "Akodo Shizue|...They're all Kafu's.", {"emo": "worried", "act": "think", "zoom": True}),
    ("dir", "M511", "Akodo Shizue|Then I'll dance like a siege.", {"emo": "happy", "act": "laugh"}),
    ("dir", "M513", "Akodo Shizue|Something crawled here.", {"emo": "worried", "act": "think", "zoom": True}),
    ("dir", "M513", "Akodo Shizue|Stop.", {"emo": "angry", "act": "point", "zoom": True}),
    ("dir", "M558", "Akodo Shizue|Kafu-sama.", {"emo": "worried", "zoom": True}),
    # ---- Ch3. The return-branch office opened with the wrong scene's narration ("the old sensei ... in the dojo")
    ("set", "M514", "The old sensei waits in the dojo, a bokken across his knees. He knows what the letter said - and that Akodo Shizue carried it anyway.",
     {"name": "", "text": "The karo's office. Akodo Kagehisa does not look up from his brush. He already knows what "
                          "the letter said - and that Akodo Shizue carried it home to ask."}),
    ("dir", "M514", "Akodo Shizue|...That's why it's me.", {"emo": "worried", "zoom": True}),
    ("dir", "M514", "Akodo Shizue|It broke. I read it.", {"emo": "determined", "act": "rei"}),
    ("dir", "M514", "Akodo Shizue|...My lord?", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M268", "Akodo Shizue|\"Kill these messengers.\"", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M270", "Akodo Shizue|The Lion have no such plan.", {"emo": "worried", "act": "think", "zoom": True}),
    ("dir", "M271", "Akodo Shizue|Because if my lord wanted me dead", {"emo": "determined", "zoom": True}),
    # ---- Ch4
    ("dir", "M273", "Akodo Shizue|So I've read, magistrate. In your letters.", {"emo": "determined", "act": "crossarms", "zoom": True}),
    ("dir", "M274", "Akodo Shizue|The wax was lifted and pressed again.", {"emo": "worried", "act": "think", "zoom": True}),
    ("dir", "M274", "Akodo Shizue|Then she swapped our letter too.", {"emo": "worried", "act": "surprise", "zoom": True}),
    ("dir", "M274", "Akodo Shizue|You can't end a war by starting a battle.", {"emo": "angry", "act": "point"}),
    # the Demon: name it, and let it say what it wants before the fight
    ("before", "M276", "You're afraid, little strategist. I can taste it.", [
        ("Akodo Shizue", "That isn't Rokuro. It's the thing riding him. A fear-eater.", "worried")]),
    ("after", "M276", "You're afraid, little strategist. I can taste it.", [
        ("The Demon", "Four hundred years this river has fed me. Every Lion who charges here charges for me.")]),
    ("dir", "M276", "Akodo Shizue|Of course I'm afraid. Only fools and Matsu aren't.", {"emo": "determined", "zoom": True}),
    ("dir", "M276", "Akodo Shizue|No, magistrate. But it's the first time you lost.", {"emo": "determined", "act": "crossarms", "zoom": True}),
    # the river stone: show the mark she reads, before she reads it
    ("before", "M277", "North. And east. Shinomen.", [
        ("", "Scratched into the back of the stone: an arrow, and the old character for the forest of Shinomen.")]),
    ("dir", "M277", "Akodo Shizue|...It isn't jade. It's river stone.", {"emo": "surprised", "act": "think", "zoom": True}),
    ("dir", "M277", "Akodo Shizue|I couldn't stop the war, uncle.", {"emo": "sad", "zoom": True}),
] + [
    # =============================================================== PHOENIX (Isawa Haruki), read in full 2026-11-22
    # ---- Ch1
    ("dir", "M253", "Isawa Haruki|Sensei! Sensei!", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M253", "Isawa Haruki|Please. Please answer. You always answer.", {"emo": "sad", "zoom": True}),
    ("dir", "M253", "Isawa Haruki|Then I start again on the other hand, sensei.", {"emo": "happy", "act": "laugh"}),
    # Hoju's notes: whose words these are, and what they mean to the boy reading them
    ("before", "M253", "\"Kaiki. Fifteen. We had no other way.\"", [
        ("", "Hoju's private notes, in his smallest hand, folded under the tea things.")]),
    ("after", "M253", "\"Kaiki. Fifteen. We had no other way.\"", [
        ("Isawa Haruki", "He killed a boy to make the binding. Sensei did. And then he wrote histories for forty years.",
         "sad", Z)]),
    ("dir", "M253", "Isawa Haruki|...You kept this. Twelve years.", {"emo": "sad", "zoom": True}),
    ("dir", "M253", "Isawa Haruki|You knew, sensei. You knew all along.", {"emo": "sad", "act": "think"}),
    ("dir", "M252", "Isawa Haruki|Could I try to... calm him?", {"emo": "worried", "act": "scratch"}),
    ("dir", "M252", "Isawa Haruki|Oh no. I'm so sorry-", {"emo": "surprised", "act": "facepalm", "zoom": True}),
    ("dir", "M250", "Isawa Haruki|The Phoenix were supplying the Crane army.", {"emo": "worried", "act": "think", "zoom": True}),
    ("dir", "M250", "Isawa Haruki|I'll find what got out. That's the fixing.", {"emo": "determined", "act": "nod"}),
    ("dir", "M250", "Isawa Haruki|...I've never been very good at holding things together.", {"emo": "sad", "zoom": True}),
    # the tower ghost is Ashimita's screaming grandfather: one line ties the two together
    ("after", "M280", "He's screaming. Can't you hear him?", [
        ("Shiba Ashimita", "That's him. Ashimoshi. My grandfather.")]),
    ("dir", "M280", "Isawa Haruki|No. Yes. In the wind.", {"emo": "surprised", "act": "surprise", "zoom": True}),
    # ---- Ch2
    ("after", "M284", "The Tattooed Prophet sees! Kokujin sees! Burn the false monks!", [
        ("Isawa Haruki", "Who is Kokujin?", "worried"),
        ("Shiba Ashimita", "A madman who paints tattoos on peasants and calls it enlightenment. The Dragon want his "
                           "head. So do I, now.")]),
    ("dir", "M282", "Isawa Haruki|I've been silent about something for twelve years", {"emo": "determined", "zoom": True}),
    ("dir", "M282", "Isawa Haruki|You're grieving too, Matsu-sama.", {"emo": "neutral", "act": "rei"}),
    ("dir", "M285", "Isawa Haruki|...Once. A long time ago.", {"emo": "worried", "zoom": True}),
    ("dir", "M285", "Isawa Haruki|...It's Mieko's handwriting.", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M285", "Isawa Haruki|Written in fear. By a gentle hand.", {"emo": "worried", "act": "think"}),
    ("dir", "M285", "Isawa Haruki|I'm the reason she's two people.", {"emo": "sad", "zoom": True}),
    ("dir", "M286", "Isawa Haruki|...Mieko?", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M287", "Isawa Haruki|He refused an order to burn people.", {"emo": "angry", "act": "point", "zoom": True}),
    ("dir", "M287", "Isawa Haruki|It isn't a prophecy. It's a warning.", {"emo": "determined", "zoom": True}),
    ("dir", "M287", "Isawa Haruki|Because you wanted it.", {"emo": "determined", "zoom": True}),
    # ---- Ch3
    ("dir", "M288", "Isawa Haruki|It spreads in a circle, Master.", {"emo": "worried", "act": "think", "zoom": True}),
    ("dir", "M288", "Isawa Haruki|It's where I broke her.", {"emo": "sad", "zoom": True}),
    ("dir", "M288", "Isawa Haruki|My Void lashed out. It split her soul.", {"emo": "worried"}),
    ("dir", "M294", "Isawa Haruki|She remembers you. She was afraid for you.", {"emo": "determined", "zoom": True}),
    ("dir", "M295", "Isawa Haruki|Then I'll close it.", {"emo": "determined", "zoom": True}),
    ("dir", "M295", "Isawa Haruki|Politely.", {"emo": "determined", "act": "rei"}),
    ("dir", "M296", "Isawa Haruki|...A giver.", {"emo": "worried", "act": "think", "zoom": True}),
    ("dir", "M296", "Isawa Haruki|I've been in one report already.", {"emo": "happy", "act": "laugh"}),
    # ---- Ch4
    ("dir", "M297", "Isawa Haruki|Mieko.", {"emo": "surprised", "zoom": True}),
    ("dir", "M297", "Isawa Haruki|She'll do neither. She'll wait for me.", {"emo": "determined", "act": "nod"}),
    ("dir", "M297", "Isawa Haruki|...You were hunting her. Even then.", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M298", "Isawa Haruki|...She's learned everything I can do.", {"emo": "worried", "zoom": True}),
    ("dir", "M300", "Isawa Haruki|Dreamwalker.", {"emo": "surprised", "act": "think", "zoom": True}),
    ("dir", "M301", "Isawa Haruki|I know.", {"emo": "sad", "zoom": True}),
    ("dir", "M302", "Isawa Haruki|...No. Not again. I won't break you again.", {"emo": "determined", "zoom": True}),
    ("dir", "M302", "Isawa Haruki|I would. I took some of you. It's fair.", {"emo": "determined", "act": "nod", "zoom": True}),
    ("dir", "M302", "Isawa Haruki|I don't know. I think you get to decide.", {"emo": "happy", "zoom": True}),
    ("dir", "M302", "Isawa Haruki|...You did take my stone.", {"emo": "happy", "act": "laugh"}),
] + [
    # =============================================================== DRAGON (Kitsuki Gendo), read in full 2026-11-22
    # Akuro's prophecy was quoted at the end ("Gendo writes down Akuro's prophecy") but nobody ever said it: the
    # villain had one line ("You're late") before his fight. He says it on the parley ship now - his motive, his
    # vision - and Gendo the investigator draws out the last line.
    ("after", "M336", "Little clerk. You're late. History usually is.", [
        ("Kitsuki Gendo", "Why? He rode out alone to stop a war. You've just started one.", "angry", Z),
        ("Togashi Akuro", "My last tattoo showed me what comes, clerk. The son will become the dark brother. The jade "
                          "clan goes black. The dead rule."),
        ("Togashi Akuro", "So I walked back four hundred years to break the road before it gets there. One dead "
                          "Crane is cheap."),
        ("Kitsuki Gendo", "Visions have endings. What was the end of yours?", "determined", A("think")),
        ("Togashi Akuro", "\"Out of all hope, seven mortals will rise.\" I stopped believing in the seven. Kill "
                          "him."),
    ]),
    # ---- Ch1
    ("dir", "M303", "Kitsuki Gendo|And you're seasick, Oharu-sama", {"emo": "happy", "act": "laugh"}),
    ("dir", "M303", "Kitsuki Gendo|Rice is heavier than silk, captain.", {"emo": "happy", "act": "point", "zoom": True}),
    ("dir", "M303", "Kitsuki Gendo|I wasn't staring. I was deducing.", {"emo": "neutral", "act": "shrug"}),
    ("dir", "M306", "Kitsuki Gendo|Oharu-sama!", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M306", "Kitsuki Gendo|(Bitter almond... no. Mantis mushroom.", {"emo": "worried", "act": "think", "zoom": True}),
    ("dir", "M306", "Kitsuki Gendo|The case has one.", {"emo": "determined", "zoom": True}),
    ("dir", "M306", "Kitsuki Gendo|Fish wear hats on some islands.", {"emo": "happy", "act": "shrug"}),
    ("dir", "M306", "Kitsuki Gendo|No, Oharu-sama. But they'll remember being wrong about me.", {"emo": "determined", "act": "rei", "zoom": True}),
    ("dir", "M307", "Kitsuki Gendo|...His tattoos are gone. The skin is blank.", {"emo": "surprised", "act": "think", "zoom": True}),
    ("dir", "M308", "Kitsuki Gendo|It isn't scripture. It's a map.", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M308", "Kitsuki Gendo|You said it perfectly wrong, Riichi.", {"emo": "happy", "act": "nod"}),
    ("dir", "M312", "Kitsuki Gendo|I'm a clerk with a Mirumoto sword I rarely draw.", {"emo": "determined", "zoom": True}),
    ("dir", "M313", "Kitsuki Gendo|(Every court in the Empire believes the manners.)", {"emo": "worried", "act": "think"}),
    ("dir", "M313", "Kitsuki Gendo|Men who run go somewhere. I'd like to know where.", {"emo": "determined", "act": "crossarms", "zoom": True}),
    # ---- Ch2
    ("dir", "M316", "Kitsuki Gendo|Dragon work. Tamori-style.", {"emo": "angry", "act": "point", "zoom": True}),
    ("dir", "M316", "Kitsuki Gendo|Akuro.", {"emo": "determined", "zoom": True}),
    ("dir", "M319", "Kitsuki Gendo|The capital. Built backwards in time.", {"emo": "surprised", "act": "think", "zoom": True}),
    ("dir", "M321", "Kitsuki Gendo|Yosai!", {"emo": "surprised", "zoom": True}),
    ("dir", "M322", "Kitsuki Gendo|Year four hundred. No Kitsuki family yet.", {"emo": "worried", "act": "facepalm", "zoom": True}),
    ("dir", "M322", "Kitsuki Gendo|Wonderful.", {"emo": "neutral", "act": "shrug"}),
    ("dir", "M323", "Kitsuki Gendo|...That's the cove. Our cove.", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M323", "Kitsuki Gendo|Akuro kept a spare.", {"emo": "determined", "act": "think"}),
    ("dir", "M324", "Kitsuki Gendo|Don't let them win, Yosai.", {"emo": "worried", "zoom": True}),
    # ---- Ch3
    ("dir", "M326", "Kitsuki Gendo|When people tell you what you want, ask them what they want first.", {"emo": "neutral", "act": "nod", "zoom": True}),
    ("dir", "M326", "Kitsuki Gendo|One hour. Three lords.", {"emo": "worried", "act": "scratch"}),
    ("dir", "M327", "Kitsuki Gendo|...Real gaijin medicine. Real comfort.", {"emo": "angry", "act": "think", "zoom": True}),
    ("dir", "M329", "Kitsuki Gendo|...What have I done.", {"emo": "surprised", "act": "facepalm", "zoom": True}),
    ("dir", "M331", "Kitsuki Gendo|...I think you should write that idea down", {"emo": "happy", "act": "nod"}),
    ("dir", "M335", "Kitsuki Gendo|An invasion plan. Landing points. Dates.", {"emo": "worried", "act": "think", "zoom": True}),
    ("dir", "M336", "Kitsuki Gendo|NO-", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M332", "Kitsuki Gendo|I've studied every recorded habit of the Crane Champion.", {"emo": "determined", "zoom": True}),
    # ---- Ch4
    ("dir", "M337", "Kitsuki Gendo|(I'll keep mine very straight.)", {"emo": "worried", "act": "scratch"}),
    ("dir", "M337", "Kitsuki Gendo|Yosai!", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M337", "Kitsuki Gendo|It's a long story.", {"emo": "happy", "act": "laugh"}),
    ("dir", "M341", "Kitsuki Gendo|Then paint me the year 1122, Kumpei.", {"emo": "determined", "zoom": True}),
    ("dir", "M342", "Kitsuki Gendo|I know exactly how little being remembered is worth.", {"emo": "happy", "zoom": True}),
    ("dir", "M342", "Kitsuki Gendo|That's the only kind that matters, Majesty.", {"emo": "happy", "act": "rei"}),
    ("dir", "M344", "Kitsuki Gendo|Seven. There are eight of us.", {"emo": "surprised", "act": "think", "zoom": True}),
] + [
    # =============================================================== SCORPION (Shosuro Mitsue), read in full 2026-11-22
    # ---- Ch1. Norie's orders: one beat from Mitsue between the town and the job
    ("after", "M346", "The Fox and the Sparrow govern it together and hate it together.", [
        ("Shosuro Mitsue", "Which one is lying, sensei?", "neutral", A("think")),
        ("Shosuro Norie", "Both. That is what makes it a town."),
    ]),
    # Rui's briefing was one line holding four facts: split it with the newcomer's questions
    ("sub", "M353", " Ten days ago: the Miya caravan robbed in the middle of town. A Crane banner, a broken sword, two stone Fortunes, an iron box. All of it back on the riverbank next morning. All but the box.", ""),
    ("after", "M353", "Eleven days ago: the magistrate and three seniors, and the river-men at the port.", [
        ("Shosuro Mitsue", "Sick with what?", "neutral"),
        ("Yoritomo Rui", "Nobody knows. And the next morning, the Miya caravan was robbed in the middle of town."),
        ("Yoritomo Rui", "A Crane banner, a broken sword, two stone Fortunes. All of it dumped on the riverbank by "
                         "dawn. All but one little iron box."),
        ("Shosuro Mitsue", "Nobody robs a caravan to keep a box. Unless the box was the caravan.", "determined",
         A("think", True)),
    ]),
    ("dir", "M345", "Shosuro Mitsue|Yes, my lady. More tea?", {"emo": "neutral", "act": "rei"}),
    ("dir", "M345", "Shosuro Mitsue|Nobody, sensei. Nobody is very easy to be.", {"emo": "happy", "zoom": True}),
    ("dir", "M346", "Shosuro Mitsue|Evening, sir. Mind the step.", {"emo": "happy", "act": "rei"}),
    ("dir", "M348", "Shosuro Mitsue|...Nineteen.", {"emo": "worried", "zoom": True}),
    ("dir", "M349", "Shosuro Mitsue|Lines. Circles. A summoning.", {"emo": "worried", "act": "think", "zoom": True}),
    ("dir", "M352", "Shosuro Mitsue|...That isn't a governor. That isn't a person.", {"emo": "worried", "zoom": True}),
    ("dir", "M351", "Shosuro Mitsue|The Mantis will consider the matter of the step.", {"emo": "happy", "act": "rei"}),
    ("dir", "M356", "Shosuro Mitsue|Then he didn't fail you. Something wore him.", {"emo": "determined", "zoom": True}),
    ("dir", "M358", "Shosuro Mitsue|Hana. Look at me. Not at the box.", {"emo": "worried", "act": "point", "zoom": True}),
    ("dir", "M354", "Shosuro Mitsue|...Again?", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M354", "Shosuro Mitsue|...Especially if I'm nobody.", {"emo": "happy", "zoom": True}),
    # ---- Ch2
    ("dir", "M360", "Shosuro Mitsue|...Still mine.", {"emo": "worried", "zoom": True}),
    ("dir", "M360", "Shosuro Mitsue|Probably.", {"emo": "happy", "act": "shrug"}),
    ("dir", "M361", "Shosuro Mitsue|Who said?", {"emo": "surprised", "zoom": True}),
    ("dir", "M361", "Shosuro Mitsue|Masks don't usually say thank you.", {"emo": "worried", "act": "scratch"}),
    ("dir", "M361", "Shosuro Mitsue|...Still mine.", {"emo": "worried", "zoom": True}),
    ("dir", "M364", "Shosuro Mitsue|...There's no one behind it. Just a body, breathing.", {"emo": "worried", "zoom": True}),
    # Osuko's history lesson, four lines straight: break it where Mitsue realises who is in her sleeve
    ("after", "M363", "and hid the whole city in the Realm of Dreams.", [
        ("Shosuro Mitsue", "Soshi Giseiki. I think he's riding in my sleeve.", "surprised", A("surprise")),
        ("Shosuro Osuko", "Then you're carrying the only man who can end it. Don't drop him."),
    ]),
    ("dir", "M363", "Shosuro Mitsue|...Oh. He's very polite in here.", {"emo": "surprised", "act": "surprise", "zoom": True}),
    # a lead-in written for another scene ("Cornered at last, the man behind the mask") landed on a talking mask
    ("set", "M364", "Cornered at last, the man behind the mask stops pretending.",
     {"name": "", "text": "The mask in Mitsue's sleeve has been very quiet while the whole market gossiped about him. "
                          "She takes it out and looks at it."}),
    ("dir", "M367", "Shosuro Mitsue|Choosing is the only part that's mine.", {"emo": "determined", "zoom": True}),
    # ---- Ch4
    ("dir", "M379", "Shosuro Mitsue|Everyone is exactly the problem.", {"emo": "determined", "act": "crossarms", "zoom": True}),
    ("dir", "M379", "Shosuro Mitsue|...That's an odd thing to write, sensei.", {"emo": "worried", "act": "think"}),
    ("dir", "M381", "Shosuro Mitsue|Rest now. I'll tell them.", {"emo": "sad", "zoom": True}),
    ("dir", "M383", "Shosuro Mitsue|...A family's line will end.", {"emo": "worried", "zoom": True}),
    ("dir", "M383", "Shosuro Mitsue|The Emperor's. He's going to kill the Emperor.", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M385", "Shosuro Mitsue|You'll be ash.", {"emo": "angry", "zoom": True}),
    # the Bloodspeaker "who has hunted the Box since Kudo" had never been seen: it says so itself
    ("after", "M386", "You and I are the same, Shosuro.", [
        ("Bloodspeaker", "I followed that box out of Kudo. Through Shutai, up three mountains, behind you the whole way.")]),
    ("dir", "M386", "Shosuro Mitsue|I always give mine back.", {"emo": "determined", "zoom": True}),
    ("dir", "M386", "Shosuro Mitsue|Don't waste them on dinner.", {"emo": "happy", "act": "laugh"}),
    ("dir", "M386", "Shosuro Mitsue|...You're in his procession.", {"emo": "surprised", "act": "surprise", "zoom": True}),
] + [
    # =============================================================== UNICORN (Ide Tamotsu), read in full 2026-11-22
    # (also Scorpion Ch3, the shared Ojatara tribunal M368-M376). Kurosho had one line before the last fight: he says
    # why now - the woman he sold, the miners he sold - and Tamotsu answers like a trader.
    ("after", "M412", "Come to buy you back, my lord.", [
        ("Iuchi Kurosho", "Buy me? I sold a woman I loved to a geisha house to keep a war going, boy. I sold the "
                          "miners to the dark when they saw too much."),
        ("Iuchi Kurosho", "Twenty years of it. Regret is the only thing I ever kept. So I called it home."),
        ("Ide Tamotsu", "Then let's find out what it costs to send it away.", "determined", Z),
    ]),
    ("dir", "M412", "Ide Tamotsu|Kurosho-sama!", {"emo": "surprised", "zoom": True}),
    ("dir", "M412", "Ide Tamotsu|Come to buy you back, my lord.", {"emo": "happy", "act": "rei"}),
    ("dir", "M412", "Ide Tamotsu|If you want a bridge between your houses, my lords", {"emo": "determined", "act": "point", "zoom": True}),
    ("dir", "M412", "Ide Tamotsu|It's mostly indigestion.", {"emo": "happy", "act": "laugh"}),
    # ---- Ch1
    ("dir", "M388", "Ide Tamotsu|I'm Ide, Tsune-sama. Being liked is our only weapon.", {"emo": "happy", "zoom": True}),
    ("dir", "M388", "Ide Tamotsu|Is that everyone?", {"emo": "hurt", "zoom": True}),
    ("dir", "M388", "Ide Tamotsu|The cat was important.", {"emo": "happy", "act": "laugh"}),
    ("dir", "M388", "Ide Tamotsu|...His name is Naohida.", {"emo": "worried", "zoom": True}),
    ("dir", "M388", "Ide Tamotsu|I sold him rice cakes for a copper when we were nine.", {"emo": "sad", "zoom": True}),
    ("dir", "M389", "Ide Tamotsu|Hate me, grandmother. I'm the one who's late.", {"emo": "sad", "act": "seiza", "zoom": True}),
    ("dir", "M389", "Ide Tamotsu|Go with the Fortunes, my friend.", {"emo": "happy", "act": "rei"}),
    ("dir", "M391", "Ide Tamotsu|My lord is talking to woodchucks so he won't have to", {"emo": "determined", "zoom": True}),
    ("dir", "M392", "Ide Tamotsu|And when the war is over, general, what grows here?", {"emo": "determined", "act": "point"}),
    ("dir", "M393", "Ide Tamotsu|Both sides made a temple a weapon.", {"emo": "worried", "act": "think", "zoom": True}),
    ("dir", "M395", "Ide Tamotsu|I didn't like them either, sensei.", {"emo": "worried"}),
    ("dir", "M398", "Ide Tamotsu|Naohida. You owe me a copper.", {"emo": "happy", "zoom": True}),
    ("dir", "M398", "Ide Tamotsu|Then come and sit in my seat. I'll stand.", {"emo": "determined", "zoom": True}),
    # ---- Ch2 (+ Scorpion Ch3)
    ("dir", "M370", "Ide Tamotsu|I have a pony, a terrible haiku", {"emo": "happy", "act": "laugh"}),
    ("dir", "M370", "Ide Tamotsu|Then I'll need twice the rice cakes.", {"emo": "happy", "act": "shrug"}),
    ("dir", "M368", "Ide Tamotsu|I'll write what happened. All of it.", {"emo": "determined", "act": "nod", "zoom": True}),
    ("dir", "M369", "Ide Tamotsu|A bell that doesn't ring is a bell somebody's paying for.", {"emo": "determined", "zoom": True}),
    ("dir", "M376", "Ide Tamotsu|He told you about me?", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M371", "Ide Tamotsu|Both sides padding their armies.", {"emo": "worried", "act": "think", "zoom": True}),
    ("dir", "M371", "Shosuro Mitsue|\"...the war was set moving from Kyuden Bayushi.", {"emo": "surprised", "zoom": True}),
    ("dir", "M371", "Shosuro Mitsue|To whom, sensei? Who would believe a nobody?", {"emo": "happy", "act": "shrug"}),
    ("dir", "M374", "Ide Tamotsu|Imperial blood.", {"emo": "surprised", "zoom": True}),
    ("dir", "M374", "Shosuro Mitsue|Imperial blood.", {"emo": "surprised", "zoom": True}),
    # ---- Ch3-4
    ("dir", "M399", "Ide Tamotsu|It wasn't you. Because of you.", {"emo": "neutral", "zoom": True}),
    ("dir", "M403", "Ide Tamotsu|Your father summoned a demon, my lord.", {"emo": "worried", "zoom": True}),
    ("dir", "M404", "Ide Tamotsu|I want three thousand Dragons to ride out again, general.", {"emo": "determined", "zoom": True}),
    ("dir", "M408", "Ide Tamotsu|Good. Understanding yourself is overrated.", {"emo": "happy", "act": "shrug"}),
    ("dir", "M408", "Ide Tamotsu|You still owe me a copper.", {"emo": "happy", "act": "laugh"}),
    ("dir", "M413", "Ide Tamotsu|Round, my lord!", {"emo": "happy", "act": "laugh"}),
    # two ward residents shared a name with a real character (Sayo the traveler; Hiro the undertaker, in his own
    # eta quarter): their busts and speaker labels collided
    ("sub", "M756", "Sayo's resident waits", "Sayu's resident waits"),
    ("name", "M756", "Sayo", "Sayu"),
    ("sub", "M756", "Back to the Sayo.", "Back to Sayu."),
    ("sub", "M652", "Hiro's resident waits in the Hearth Lane", "Hiroe's resident waits in the Hearth Lane"),
    ("name", "M652", "Hiro", "Hiroe"),
    ("sub", "M652", "Back to the Hiro.", "Back to Hiroe."),
] + [
    # =============================================================== RONIN (Sayo), read in full 2026-11-22
    # ---- Ch3. At the Castle of the White Snow the narrator explained each ghost. The grandchildren of those
    # champions are standing right there: each realisation belongs to the one whose family it shames.
    ("set", "M434", "There was no oni. A Crab lord had rebel guards kidnap the prince.",
     {"name": "Hida Ren", "text": "...There was no oni. A Crab lord paid his own guards to steal the prince. A Crab."}),
    ("set", "M434", "The champions fought each other. The Lion killed the Crane.",
     {"name": "Sayo", "text": "They fought each other up here. The Lion shot the Crane.", "emo": "surprised",
      "act": "think", "zoom": True}),
    ("set", "M435", "The Bayushi champion blew the gate with gunpowder.",
     {"name": "Bayushi Kei", "text": "\"Clever with fire.\" He blew the gate himself. That's the best line we have?"}),
    ("set", "M435", "The Mirumoto champion fled on Togashi's prophetic order.",
     {"name": "Sayo", "text": "Togashi told him to run when he heard the cry. So he ran.", "emo": "neutral",
      "zoom": True}),
    ("set", "M435", "The child died here.",
     {"name": "Sayo", "text": "...The child died here. The real one.", "emo": "sad", "zoom": True}),
    ("dir", "M435", "Sayo|- a dead baby and a lot of brave men", {"emo": "sad", "zoom": True}),
    ("dir", "M435", "Sayo|He stayed. Whatever else he did", {"emo": "neutral", "act": "rei"}),
    ("dir", "M436", "Sayo|...Thank you, hermit.", {"emo": "neutral", "act": "rei"}),
    ("dir", "M436", "Sayo|You paid me like a porter!", {"emo": "angry", "zoom": True}),
    ("dir", "M436", "Sayo|You're not coming?", {"emo": "surprised", "zoom": True}),
    ("dir", "M433", "Sayo|Armour doesn't lie, my lord. People do.", {"emo": "neutral", "act": "point", "zoom": True}),
    ("dir", "M432", "Sayo|This isn't fire. It's gunpowder.", {"emo": "surprised", "act": "think", "zoom": True}),
    ("dir", "M431", "Sayo|Sayo. My name's Sayo, my lady.", {"emo": "happy", "zoom": True}),
    ("dir", "M430", "Sayo|And I'll be the only one who knows how to tie them.", {"emo": "happy", "act": "shrug"}),
    ("dir", "M430", "Sayo|You weren't punished for anything.", {"emo": "worried", "zoom": True}),
    ("dir", "M430", "Sayo|Every emperor for three hundred years.", {"emo": "surprised", "act": "think", "zoom": True}),
    ("dir", "M430", "Sayo|That's the one thing samurai would kill to stop anyone saying.", {"emo": "worried", "zoom": True}),
    # ---- Ch1
    ("dir", "M415", "Sayo|Nobody in particular. Chew this.", {"emo": "happy", "act": "point"}),
    ("dir", "M416", "Sayo|There. Now you know what you're paying me for.", {"emo": "happy", "act": "point", "zoom": True}),
    ("dir", "M416", "Sayo|Couldn't you do the execution yourself?", {"emo": "neutral", "act": "think"}),
    ("dir", "M417", "Sayo|It's nobody's fight. That's why I'm here.", {"emo": "determined", "zoom": True}),
    ("dir", "M418", "Sayo|Then it's not punishment. It's dinner.", {"emo": "angry", "zoom": True}),
    ("dir", "M418", "Sayo|And I'm going to spoil its appetite.", {"emo": "determined", "act": "crossarms"}),
    ("dir", "M421", "Sayo|They don't. Nobody does.", {"emo": "determined", "zoom": True}),
    ("dir", "M421", "Sayo|I know. It still wasn't theirs to pay for.", {"emo": "determined", "zoom": True}),
    # ---- Ch2
    ("dir", "M422", "Sayo|Which one of you is the criminal again? I'm new.", {"emo": "happy", "act": "shrug"}),
    ("dir", "M422", "Sayo|Make sure they get my good side!", {"emo": "happy", "act": "laugh"}),
    ("dir", "M423", "Sayo|Osano-Wo? The thunder fortune?", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M425", "Sayo|A cult. Under a harbourmaster. Of course.", {"emo": "neutral", "act": "facepalm", "zoom": True}),
    ("dir", "M427", "Sayo|Sayo. Of nowhere in particular.", {"emo": "neutral", "act": "rei", "zoom": True}),
    ("dir", "M428", "Sayo|I'm not a spy. Spies are better dressed.", {"emo": "happy", "act": "shrug"}),
    ("dir", "M424", "Sayo|Will you be all right?", {"emo": "worried", "zoom": True}),
    ("dir", "M424", "Sayo|Oh, you poor fool.", {"emo": "worried", "act": "facepalm"}),
    # ---- Ch4
    ("dir", "M438", "Sayo|Fire's like that. Loud and full of itself.", {"emo": "determined", "zoom": True}),
    ("dir", "M438", "Sayo|...Oh, you didn't.", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M438", "Sayo|They don't care about Akari.", {"emo": "worried", "act": "think"}),
    ("dir", "M438", "Sayo|Sayo's the only one I picked. I'll keep it.", {"emo": "determined", "zoom": True}),
    ("dir", "M440", "Sayo|Poison the well, and the priests say", {"emo": "angry", "zoom": True}),
    ("dir", "M440", "Sayo|...Same smile. Three faces.", {"emo": "worried", "act": "think", "zoom": True}),
    ("dir", "M442", "Sayo|Then shout back! Tell it to wait for us!", {"emo": "determined", "zoom": True}),
    ("dir", "M443", "Sayo|...That's all I ever wanted from fire, honestly.", {"emo": "happy", "zoom": True}),
    ("dir", "M443", "Sayo|I could start a war with one sentence.", {"emo": "determined", "zoom": True}),
    # more ward residents named like real characters (their busts / labels collided; Old Mosuke and Akari even live
    # on those maps): Sanae, Kiyo, Hana, Rin, Mosuke, Akari, Goro. gen_maps renamed too.
] + [
    # =============================================================== CRAB Ch3 + Ch4's Wall (Hiruma Natsuko), read 2026-11-22
    ("dir", "M170", "Hiruma Natsuko|Third stone. Skip the fourth. Never trust the fifth.", {"emo": "neutral", "act": "point"}),
    ("dir", "M170", "Hiruma Natsuko|...It matches. The first leg.", {"emo": "surprised", "act": "think", "zoom": True}),
    ("dir", "M171", "Hiruma Natsuko|\"Tar chasm. Rope bridge.\" ...It's here.", {"emo": "surprised", "zoom": True}),
    ("dir", "M172", "Hiruma Natsuko|It's all here. Every mark.", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M172", "Hiruma Natsuko|I'll tell her, brother.", {"emo": "sad", "act": "rei"}),
    ("dir", "M173", "Hiruma Natsuko|He wasn't a fool. He was right.", {"emo": "sad", "act": "seiza", "zoom": True}),
    ("dir", "M174", "Hiruma Natsuko|Today somebody does.", {"emo": "determined", "zoom": True}),
    ("dir", "M175", "Hiruma Natsuko|There's a road back, my lord. My father found it.", {"emo": "determined", "act": "point", "zoom": True}),
    ("dir", "M175", "Hiruma Natsuko|A road. To home. If you die here, who walks it?", {"emo": "determined", "zoom": True}),
    ("dir", "M175", "Hiruma Natsuko|...I'll keep watch.", {"emo": "neutral", "act": "nod"}),
    ("dir", "M176", "Hiruma Natsuko|Down. Flat. Don't breathe.", {"emo": "worried", "act": "point"}),
    ("dir", "M176", "Hiruma Natsuko|...Ryozo.", {"emo": "surprised", "act": "surprise", "zoom": True}),
    ("dir", "M176", "Hiruma Natsuko|I left him in that tunnel.", {"emo": "worried", "zoom": True}),
    ("dir", "M177", "Hiruma Natsuko|That's not a patrol. That's a costume.", {"emo": "worried", "act": "point", "zoom": True}),
    ("dir", "M158", "Hiruma Natsuko|A bone-cage. Steel won't more than scratch it.", {"emo": "determined", "act": "think"}),
    ("dir", "M158", "Hiruma Natsuko|Try it. My face doesn't fit anyone else.", {"emo": "angry", "zoom": True}),
    ("dir", "M158", "Hiruma Natsuko|My lord. The woman you married wasn't Kuhime.", {"emo": "sad", "zoom": True}),
    ("dir", "M158", "Hiruma Natsuko|Not by dying, my lord.", {"emo": "determined", "act": "rei"}),
    ("dir", "M158", "Hiruma Natsuko|...North. You keep running north.", {"emo": "determined", "zoom": True}),
] + [
    # =============================================================== FINALE (all eight), read 2026-11-22
    ("after", "M451", "Visitors. In my forest.", [
        ("Mamoru", "Mamoru. I was keeping this forest before it had trees.")]),
    ("dir", "M444", "Kitsuki Gendo|\"Seven mortals will rise.\"", {"emo": "worried", "act": "think", "zoom": True}),
    ("dir", "M444", "Sayo|Then one of us is extra. Hope it's me.", {"emo": "happy", "act": "laugh"}),
    ("dir", "M453", "Hiruma Natsuko|It's walking back into the dark every morning because someone has to.", {"emo": "determined", "zoom": True}),
    ("dir", "M453", "Kakita Rensei|It's also the only thing that keeps two enemies at one table", {"emo": "determined", "zoom": True}),
    ("dir", "M453", "Kakita Rensei|And I've read your play, my lady. Every scene.", {"emo": "determined", "act": "rei"}),
    ("dir", "M453", "Kitsuki Gendo|Sincerity isn't never lying.", {"emo": "determined", "zoom": True}),
    ("dir", "M453", "Akodo Shizue|It's what I answer for when no one is watching.", {"emo": "determined", "zoom": True}),
    ("dir", "M453", "Isawa Haruki|And I spent my life setting it right.", {"emo": "determined", "zoom": True}),
    ("dir", "M453", "Shosuro Mitsue|Because duty isn't a leash.", {"emo": "determined", "zoom": True}),
    ("dir", "M453", "Ide Tamotsu|Compassion isn't pretending the world is kind.", {"emo": "determined", "zoom": True}),
    ("dir", "M453", "Sayo|I picked it up anyway.", {"emo": "determined", "zoom": True}),
    ("dir", "M453", "Sayo|And you're not an Empress. You never were.", {"emo": "determined", "act": "point", "zoom": True}),
    ("dir", "M453", "Sayo|That's the whole play.", {"emo": "happy", "act": "shrug"}),
    ("dir", "M453", "Kitsuki Gendo|You were going to be a footnote.", {"emo": "determined", "zoom": True}),
    ("dir", "M453", "Kitsuki Gendo|I've filed a thousand of those.", {"emo": "happy", "act": "shrug"}),
    ("dir", "M453", "Sayo|...Is anyone hungry?", {"emo": "happy", "act": "laugh"}),
    ("dir", "M453", "Hiruma Natsuko|Starving.", {"emo": "happy", "act": "laugh"}),
    ("dir", "M454", "Kitsuki Gendo|Akuro never could count.", {"emo": "happy", "zoom": True}),
    ("dir", "M455", "Sayo|Biggest mistake she ever made.", {"emo": "determined", "zoom": True}),
] + [x for old, new, mid in (("Sanae", "Sanami", "M631"), ("Kiyo", "Kiyoe", "M634"), ("Hana", "Haneko", "M642"),
                              ("Rin", "Rinka", "M647"), ("Mosuke", "Mosaku", "M650"), ("Akari", "Akane", "M651"),
                              ("Goro", "Genzo", "M754"))
     for x in (("sub", mid, old + "'s resident waits", new + "'s resident waits"),
               ("sub", mid, old + ", who lives in the", new + ", who lives in the"),
               ("name", mid, old, new),
               ("sub", mid, "Back to the " + old + ".", "Back to " + new + "."))]
REGEX = [                                                          # (where, pattern, replacement) on every line
    # ward errands (gen_maps FQ_PRE): "Aki's resident waits in the X" read as if Aki owned the resident
    (None, r"^(.+?)'s resident waits in the (.+?), with a small local errand\.$", r"\1, who lives in the \2, has a small local errand."),
    (None, r", who lives in the The ", ", who lives in the "),       # districts named "The Fisher's Cove"
    (None, r"the third brother to die like this this year\.$", "the third brother this year to die like this."),  # ("this this")
    (None, r"^Back to the ([A-Z][a-z]+ [A-Z][a-z]+)\.$", r"Back to \1."),            # "Back to the Hida Teruko."
    (None, r"^Back to the (?!Chandler\.)([A-Z][a-z]+)\.$", r"Back to \1."),            # "Back to the Aki." (a name)
    (None, r"\bSP\b", "MP"),                                       # the spell resource is MP (user, 2026-11-08)
    (None, r"^A beat\.$", "A pause."),
    (None, r"^\(.+ has had enough\. Make amends at the inn\.\)$", "(Word of the Crane with the speeches has got around. Make amends at the inn.)"),
    ("M205", r"^\(.+ thinks a little less of the stiff young Crane\.\)$", "(The Green Ronin's village thinks a little less of the stiff young Crane.)"),
    ("M210", r"^\(.+ thinks a little less of the stiff young Crane\.\)$", "(Garden Under Shadow thinks a little less of the stiff young Crane.)"),
    ("M220", r"^\(.+ thinks a little less of the stiff young Crane\.\)$", "(The Crane port thinks a little less of the stiff young Crane.)"),
    ("M228", r"^\(.+ thinks a little less of the stiff young Crane\.\)$", "(Kyuden Doji thinks a little less of the stiff young Crane.)"),
]
NOT_SERVANT = "M345"                                               # only at the memorial is Mitsue a tea-pouring maid
EAVES = [("Eyes turn to the servant who is standing much too close.", "Eyes turn to the stranger who is standing much too close."),
         ("...Do you mind? Go and pour tea somewhere else.", "...Do you mind? This is a private conversation.")]




def blocks(o):
    """Every command list under o (page cmdblocks, if/choice/battle branches), in order."""
    if isinstance(o, list):
        if o and all(isinstance(c, dict) and "cmd" in c for c in o):
            yield o
        for c in o:
            yield from blocks(c)
    elif isinstance(o, dict):
        for v in o.values():
            yield from blocks(v)


def is_msg(c):
    return isinstance(c, dict) and c.get("cmd") == "cmd_showmsg" and isinstance(c.get("text"), str)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    check = "--check" in sys.argv
    path = os.path.join(DATA, "map.json")
    maps = json.load(open(path, encoding="utf-8"))

    def events(where):
        ws = where if isinstance(where, tuple) else (where,)
        for w in ws:
            mid, _, eid = (w or "").partition("/")
            for m, mp in maps.items():
                if mid and m != mid:
                    continue
                for e, ev in (mp.get("event") or {}).items() if isinstance(mp, dict) else ():
                    if eid and e != eid:
                        continue
                    yield m, ev

    stale, total = [], 0
    for fx in FIXES:
        kind, where, n = fx[0], fx[1], 0
        for m, ev in events(where):
            if kind == "page":
                last = ev["page"][-1]
                if any(is_msg(c) and c["text"] == fx[3][0][1] for b in blocks(ev) for c in b):
                    n += 1                                          # already there
                    continue
                p = dict(last)
                p["reqs"] = fx[2]
                p["cmdblock"] = [x if isinstance(x, dict) else msg(*x) for x in fx[3]]
                ev["page"].append(p)
                n += 1
                continue
            for b in blocks(ev):
                i = 0
                while i < len(b):
                    c = b[i]
                    if not is_msg(c):
                        i += 1
                        continue
                    if kind == "sub" and fx[2] in c["text"]:
                        if not (fx[3] and fx[2] in fx[3] and fx[3] in c["text"]):   # already applied (the new text holds the old)
                            c["text"] = c["text"].replace(fx[2], fx[3])
                        n += 1
                    elif kind == "name" and c.get("name") == fx[2] and (len(fx) < 5 or fx[4] in c["text"]):
                        c["name"] = fx[3]
                        n += 1
                    elif kind == "del" and c["text"] == fx[2]:
                        del b[i]
                        n += 1
                        continue
                    elif kind == "dir" and (fx[2].split("|", 1)[-1] in c["text"]) and (
                            "|" not in fx[2] or c.get("name") == fx[2].split("|", 1)[0]):
                        for k_, v_ in fx[3].items():
                            if v_ is None:
                                c.pop(k_, None)
                            else:
                                c[k_] = v_
                        n += 1
                    elif kind == "set" and c["text"] == fx[2]:
                        c.update(fx[3])
                        n += 1
                    elif kind in ("before", "after") and fx[2] in c["text"]:
                        new = [x if isinstance(x, dict) else msg(*x) for x in fx[3]]
                        at = i if kind == "before" else i + 1
                        near = b[at - 1] if kind == "before" and at else b[at] if at < len(b) else None
                        if is_msg(near) and near["text"] == new[0]["text"]:     # already applied (run twice)
                            n += 1
                            i += 1
                            continue
                        b[at:at] = new
                        n += 1
                        i += len(new)
                    i += 1
        total += n
        if not n:
            stale.append(fx)
    rx = [0] * len(REGEX)
    ea = 0
    for m, mp in maps.items():
        if not isinstance(mp, dict):
            continue
        for b in blocks(mp.get("event")):
            for c in b:
                if not is_msg(c):
                    continue
                for k, (w, pat, rep) in enumerate(REGEX):
                    if w and w != m:
                        continue
                    t = re.sub(pat, rep, c["text"])
                    if t != c["text"]:
                        c["text"] = t
                        rx[k] += 1
                if m != NOT_SERVANT:
                    for old, new in EAVES:
                        if old in c["text"]:
                            c["text"] = c["text"].replace(old, new)
                            ea += 1
    ch = 0                                                          # choice labels never saw the SP -> MP rename
    for mp in maps.values():                                        # (the patterns above run on message text only)
        for b in blocks(mp.get("event") if isinstance(mp, dict) else None):
            for c in b:
                if c.get("cmd") != "cmd_choices":
                    continue
                for k in [k for k in c if k.startswith("text") and isinstance(c[k], str)]:
                    t = re.sub(r"\bSP\b", "MP", c[k])
                    if t != c[k]:
                        c[k] = t
                        ch += 1
    print("choice labels SP -> MP:", ch)
    mv = 0                                                          # commands after a map move never run (checked in the
    for mp in maps.values():                                        # engine, 2026-11-09: three objectives were lost)
        for b in blocks(mp.get("event") if isinstance(mp, dict) else None):
            for i, c in enumerate(b):
                if c.get("cmd") == "cmd_mapmove" and any(x.get("cmd") in ("cmd_showmsg", "cmd_choices") for x in b[i + 1:]):
                    b.append(b.pop(i))
                    mv += 1
                    break
    print("map moves put last:", mv)
    print("dialog fixes: %d lines from %d entries; patterns %s; eavesdrop wording %d" % (total, len(FIXES) - len(stale), rx, ea))
    for fx in stale:
        print("   STALE (no match):", fx[0], fx[1], repr(fx[2])[:70])
    if not check:                                                   # (map.json is sometimes briefly locked by another
        import time                                                 # process: write beside it, swap it in, retry)
        tmp = path + ".tmp"
        json.dump(maps, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
        for _ in range(60):
            try:
                os.replace(tmp, path)
                break
            except OSError:
                time.sleep(1)
        else:
            raise SystemExit("map.json stayed locked; the fixed copy is " + tmp)


if __name__ == "__main__":
    main()
