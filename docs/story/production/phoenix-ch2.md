# PRODUCTION — Phoenix Ch2 · "The Silent Court"

**Traveler:** Isawa Haruki · **Lv** 20–25 · **Outline:** `scripts/phoenix-ch2-the-silent-court.md`
**Flags read:** `apology_note_found` · **Flags set:** `memory_ritual_refused`, `mieko_midnight_seen`, `told_keiki`,
`torii_saved`, `consumer_scroll_kept`
**Maps:** `zumiki_village` (3 inns), `snow_pass_1–2`, `treaty_city` (memorial halls, lake, guest houses),
`snow_garden_night`, `traitors_torii`
**Battles:** `b_pass_cultists`, `b_boss_hioninmaru`
**Set-piece:** the torii debate (UI shared with the finale) · **Storyboard:** `storyboards/phoenix-ch2.md`

---

## S01 — A Court Where No One Speaks
MAP: `zumiki_village` · TRIGGER: arrive
NARRATION: A Silent Court. Grief spoken only in ritual. Every clan sends envoys — and every envoy has a second errand.
(A snowbound village below an old Otomo watchtower. Three inns: the White Songbird, the Yellow Lantern, and the
Hidden Poem geisha house. ASAKO KEIKI — an idealist monk, round-faced, serene — greets arrivals.)
ASAKO KEIKI: Haruki-san. Hoju's apprentice. Thank you for coming.
ASAKO KEIKI: Here, we speak with the ritual, not with our tongues.
ASAKO KEIKI: Grief that shouts is only anger wearing a mourning robe.
HARUKI: (bowing) Yes, Keiki-sama.
### The drunk Matsu (test of manners)
(In the Yellow Lantern a Matsu bushi, MATSU HISAE, sways and shouts insults at the Phoenix.)
MATSU HISAE: Phoenix! You hide behind prayers while the Lion bleed! You — boy! Fight me!
> CHOICE "Respond"
  - [PA Bless] "You're grieving too, Matsu-sama. Sit. Let me pour." → (best)
      MATSU HISAE: (instantly sober, sitting) …Good. The last three envoys threw sake at me. (to Keiki) He passes.
  - "Walk away." → (neutral)
  - "Accept the duel." → (she laughs and declines: "You fail. Politely.")
### The magistrates
(Two Imperial magistrates in the White Songbird, accusing the Phoenix of harbouring road bandits.)
IMPERIAL MAGISTRATE: Bandits on the pass, Isawa-sama. Phoenix bandits.
ISAWA KAMASARI: Absurd. (to Keiki) We'll perform the Ritual of Forgetting tonight. Everyone sleeps; no one remembers this insult.
HARUKI: (before he can stop himself) No.
(Everyone looks at him.)
HARUKI: (pale, but steady) Forgive me. I don't think… we should make people forget things.
HARUKI: I've been silent about something for twelve years, Keiki-sama. It doesn't get quieter.
ASAKO KEIKI: (a long look) …Then we won't make it quieter. No ritual.
[SET memory_ritual_refused]
[SAVE]

## S02 — The Pass (dungeon)
MAP: `snow_pass_1–2` · TRIGGER: travel with the caravan
(A narrow white pass. The caravan crawls. Then shapes on the slopes: peasants with crude tattoos painted on their
skin, chanting, running down through the snow.)
CULTIST: The Tattooed Prophet sees! Kokujin sees! Burn the false monks!
[IF dragon_ch2_not_done]
(A familiar shaved head pops up from behind a snowdrift.)
TOGASHI YOSAI: Kokujin's children! They copied our tattoos and got the ink wrong. It's *embarrassing*.
HARUKI: Who are—
TOGASHI YOSAI: Yosai. Togashi. Seventeen. Shall we?
[GUEST +Togashi Yosai (this chapter only)]
[END]
[BATTLE b_pass_cultists]
(A thin man in red at the back of the mob, gesturing, sweating: HIONINMARU. He sees the battle turning and runs.)
HIONINMARU: Fools! Hold them! (already fleeing) Hold them while I — while I *think*!
(Unicorn riders and a Mantis envoy's guards gallop up the pass — uninvited, cheerful — and scatter the rest.)
MANTIS ENVOY: Nobody invited us! We came anyway! It's a Mantis tradition!

## S03 — Honored Treaty City (hub)
MAP: `treaty_city` · TRIGGER: arrive
NARRATION: Honored Treaty City. Built to celebrate a peace between the Lion and the Phoenix. Most of the peace has worn off.
### Town sub-stories (Octopath side-story icons; written in the storyboard pass)
| Sub-story | Solve with | Reward |
|---|---|---|
| "The Same Dojo" — a Hida and a Shiba bushi keep "accidentally" meeting | Eavesdrop (each wants a go-between) → Charm or Bless carries the message | Kabuto (T2) |
| "The Archive at Night" — a Crane yojimbo by the spell-scroll archive | Discern: he guards a young Asahina reading forbidden history; let it be | **Scroll: Tremor** (Haruki field spell) |
| "Sober by Dusk" — the Shiba commander must lead the procession | Remedy (Sayo) or Bless (lead him to the shrine) | Shugenja's Haori · Honor +1 |
| "Ice Duel" — a children's blood-feud duel on the lake ice | Duel (take one child's place, non-lethal) or Charm the parents | Rattan Yumi · Honor +2 |
| "The Burned Stall" — Mantis stall arson | Discern the soot (Yasuki lamp oil) → Sumai or Pilfer the rival's ledger → Barter restocks | Pearl ×2 · Fine Sake ×2 |
### Isawa Mieko (the camellia garden)
(A gentle priest, arranging winter camellias: ISAWA MIEKO. The second ceremony master.)
ISAWA MIEKO: Haruki-san? What a lovely name.
ISAWA MIEKO: Have we met? You look at me as though we have.
HARUKI: (his hand closing on the note in his sleeve) …Once. A long time ago.
HARUKI: You wouldn't remember.
ISAWA MIEKO: (smiling, puzzled) I don't remember much from when I was small. The healers say I was very ill.
ISAWA MIEKO: But I remember a boy who counted on his fingers. (laughing) Isn't that silly?
HARUKI: (not laughing) …No. Not silly.
### The murder
(Night. A cry from the scholars' house. A Lion historian, IKOMA SADAHISA, lies dead at his desk. An old scroll is
missing from his hands.)
ASAKO KEIKI: He'd found something in the archives. He wouldn't say what. He said only: "the Consumer".
[PA Discern / Eavesdrop / Bless (the historian's ghost)] →
- HISTORIAN'S GHOST (Bless): "A darkness that lives in the best of the Phoenix… reborn… the scroll says… the scroll says…"
- (The scroll, recovered from a hiding place under the scholars' house floor — a search spot.) HARUKI (Speak to the Soul on it): "Written in fear. By a gentle hand."
- HARUKI: (comparing the brushwork with a camellia label in the garden) …It's Mieko's handwriting.
[SAVE]

## S04 — Midnight
MAP: `snow_garden_night` · TRIGGER: rest at the guest house
(Midnight. Haruki can't sleep. Through the window: Mieko in the snow garden, barefoot, humming, unbothered by the cold.)
(He goes out. She turns. Her eyes are black glass.)
MIEKO (???): Hello, little Void.
HARUKI: (frozen) …Mieko?
MIEKO (???): You broke my toy. (tilting her head) I've been looking for you.
(A blink — and she's herself again, shivering, confused, looking at her bare feet.)
ISAWA MIEKO: Haruki-san? Why — why am I outside? Did I sleepwalk? How embarrassing.
[SET mieko_midnight_seen]
> CHOICE "Tell anyone?"
  - "Tell Keiki." → [SET told_keiki]
      ASAKO KEIKI: (grave) Then I'll watch her. Quietly. You did right, Haruki-san.
  - "Say nothing." → (Haruki carries it alone)
      HARUKI: (internal) It's my fault she's two people. It's my job to fix it. Nobody else's.

## S05 — The Traitor's Torii (set-piece: debate)
MAP: `traitors_torii` · TRIGGER: the next day
(A hidden mountain torii honouring SHIBA MITSUHIDE, a Phoenix Champion branded a traitor centuries ago — he refused
an order to burn a village. A mob of grieving envoys and townsfolk with torches.)
MOB LEADER: A shrine to a traitor! At a memorial for our dead! Burn it!
HARUKI: (stepping in front of the torii, shaking) Please. Let me speak.
### DEBATE (the shared UI) — 3 claims
- **Claim 1:** "He disobeyed his lord." → evidence choices:
  - "So did the boy who ran into a burning house to save his sister. Do we burn *his* memory?" → strong
  - "He had his reasons." → weak
- **Claim 2:** "Honouring a traitor insults the loyal dead." → (party members may answer; e.g. SHIZUE: "The loyal
  dead died *for* something. Ask what.") → strong
- **Claim 3 (Haruki's key):** "There is no righteousness in disobedience."
  HARUKI: (strong) He refused an order to burn people. You'd burn his shrine for it.
  HARUKI: Which of those is the insult to the dead?
(Silence. A torch lowers. Then another.)
[IF 2+ strong] [SET torii_saved] MOB LEADER: (quietly) …Leave it. Leave it standing. [END]
[ELSE] (The torii burns. Haruki stands in the smoke until it's gone.) [END]
(The guest house. Prompt: "Rest until night." [SAVE])

## S06 — Hioninmaru (BOSS)
MAP: `traitors_torii` (night) · TRIGGER: after S05
(Night. Torches again — fewer, brighter. Hioninmaru and the last of Kokujin's cultists, and in his hands the
"Consumer" scroll, stolen back.)
HIONINMARU: The Consumer! Isn't it beautiful? A darkness that never dies — that lives inside the very best of you!
HIONINMARU: Read it to me, boy. Read me how to *become* it!
HARUKI: (Attune: Water) It isn't a prophecy. It's a warning.
HARUKI: And you can't even read the difference.
[BATTLE b_boss_hioninmaru]
### Barks
- Maho cast (pays HP): HIONINMARU: "My blood — for power — gladly—" (he winces) "…less gladly—"
- Cultists all down → coward rule: HIONINMARU: "Wait! Wait! I have *gold*! I have *secrets*!"
- Defeat: HIONINMARU: (on his knees in the snow) "It said the best of you… the very best… why not *me*?"
- HARUKI: "Because you wanted it."
> CHOICE "The Consumer scroll"
  - "Give it to the Council." → (locked away)
  - "Keep it." → [SET consumer_scroll_kept] [ITEM +"The Consumer" scroll (Ch3/Ch4 key)]

## S07 — Ending
MAP: `treaty_city` (lake, lanterns) · TRIGGER: auto
(The memorial closes. Lanterns drift across the black lake — one for each of the dead. Haruki sets down one for Hoju.)
(By morning two envoys are found dead in their beds. Both were last seen walking with Mieko. The Council's
investigators look at her. Mieko, bewildered, looks at Haruki.)
ASAKO KEIKI: You know her, don't you, Haruki-san.
HARUKI: (looking at the eclipse calendar on the temple wall) I'm the reason she's two people.
[CHAPTER COMPLETE]
### Chapter complete card
**"The Silent Court" — complete.**
Journal: *At Hoju's memorial, Haruki refused a ritual of forgetting, defended a traitor's shrine with words — and
met Mieko, who remembers a boy who counted on his fingers. At midnight, she remembers more.*
[UNLOCK] Rank 2: Attune can be changed once per battle for free; Mastery 2–3 spells.

---
## Travel Banter unlocked by Phoenix Ch2
### TB-phoenix2-a "The Torii" (Haruki + Shizue)
SHIZUE: You argued down a mob. With your hands shaking.
HARUKI: They were shaking the whole time.
SHIZUE: That's what made them listen. Nobody fakes shaking hands.
### TB-phoenix2-b "Midnight" (Haruki + Mitsue)
MITSUE: I saw you in the snow garden at midnight. With her.
HARUKI: (alarmed) You—
MITSUE: Don't worry. I'm very good at not having seen things.
MITSUE: (lightly, then not) She has two faces, Haruki. Believe me — I know what that looks like from inside.
