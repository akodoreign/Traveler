# PRODUCTION — Unicorn Ch1 · "Fault Lines"

**Traveler:** Ide Tamotsu (Status 3–4) · **Lv** 1–8 · **Outline:** `scripts/unicorn-ch1-fault-lines.md`
**Flags set:** `camps_fed`, `cases_done` (0–3), `naohida_named`, `rin_joined`
**Maps:** `buried_leaves_inn`, `refugee_camps`, `shiro_iuchi_court`, `shiro_soshi_court`, `hafuna_fields`,
`motobu_crater`, `miyahana_cottage`, `yotomo_village`, `pigeon_cave_1–2`
**Battles:** `b_camp_thugs` (tutorial), `b_cave_guerrillas`, `b_boss_naohida` (powder kegs)
**Guest:** Akodo Rin (S05)
**Fit conversions:** the rubble rescue is a short cutscene (the powder kegs are the chapter's one gimmick); the
testimony mechanic is path actions plus one final choice.
**Storyboard:** `storyboards/unicorn-ch1.md` (the valley mini-region; the cave layout follows the Fortune's Lost cave map).

### RECRUIT VARIANT (Tamotsu is not the starter)
**Join point:** `buried_leaves_inn`, the common room. A round, bearded Unicorn presses rice cakes into the party's
hands before anyone speaks.
TAMOTSU: Eat, eat. You've walked a long way, and the inn's rice is terrible. These are mine.
TAMOTSU: Ide Tamotsu, emissary to a tribunal nobody wanted. (beat; quieter) There are thousands of refugees outside.
TAMOTSU: I could use help carrying rice. And people who don't belong to either side.
> CHOICE "Travel with Tamotsu?" → Yes: **Memory** (S01: Tsune, Norie, Persimmon biting the yojimbo, "a dangerous
  man") → resume at S02.
→ No: he keeps handing out rice cakes; his chapter icon appears at the inn.

### Town NPCs — `buried_leaves_inn` / `refugee_camps` (storyboard pass)
| NPC | Info | Path action |
|---|---|---|
| Crane clerk | — | *Charm:* follows ("Ledger Clerk": shows enemy HP for 1 battle) |
| Scorpion yojimbo | *Discern/Eavesdrop:* "Norie sent him to watch Tamotsu, not guard her." | — |
| Iuchi farmer | — | *Sumai:* Jade Dust + a Case 2 lead |
| Orphan (camps) | — | *Bless:* follows ("Small Hands": item-steal chance up, 1 battle) |
| Ronin cook (camps) | — | *Duel:* Glory +1 · *Pilfer:* Rice Ball ×5 (Honor −) |

---

## S01 — A Seat at the Small Table
MAP: `buried_leaves_inn` · TRIGGER: new game, Tamotsu chosen
NARRATION: The Ojatara Valleys, in the Spine of the World. Two shugenja families fought a war here that nobody gave
them permission to fight.
NARRATION: Now the Emerald Champion has sent judges. And one round, bearded Unicorn who likes everybody.
(The Welcome Road inn, the Town of Buried Leaves. Silk and tension. TAMOTSU, round, bright-robed, laughing, hands
out rice cakes to strangers. A pony, PERSIMMON, glares at everyone from the stable door.)
SHINJO TSUNE: (gaunt, haunted, Unicorn magistrate) You'll take the refugees, Tamotsu.
TAMOTSU: The refugees, Tsune-sama?
SHINJO TSUNE: They like you. Everybody likes you. It's unbearable.
TAMOTSU: (laughing) I'm Ide, Tsune-sama. Being liked is our only weapon. I keep it sharp.
(Across the room, the Scorpion magistrate's party: SHOSURO NORIE, cool and courteous, and a Scorpion yojimbo who
reaches past the stable door — and is promptly bitten by Persimmon.)
SCORPION YOJIMBO: Agh! Your *horse*—
TAMOTSU: Pony. Persimmon. She bites everyone she loves. (beat) And everyone she doesn't. Please — (a lacquered
sweet box) — a small apology.
SCORPION YOJIMBO: (holding his hand, accepting the box, somehow charmed) …Thank you.
SHOSURO NORIE: (watching, amused) The Unicorn have sent a dangerous man.
### TUTORIAL — Status
"Tamotsu's **Status** opens doors: he can request audiences with lords and karo that other travelers would be
refused."
[SAVE]

## S02 — The Camps (Barter tutorial)
MAP: `refugee_camps` · TRIGGER: auto
(Mud. Smoke. Thousands of farmers between two castles, belonging to neither.)
### TUTORIAL — Path Action: Barter
"**Barter** — buy what an NPC owns. **Commerce** rank lowers the price. Money can also feed people."
(A merchant hoards rice at triple prices. [PA Barter merchant] → rice ×10)
REFUGEE GRANDMOTHER: The Iuchi burned our village. The Soshi burned the next one.
REFUGEE GRANDMOTHER: Which one shall I hate, my lord?
(Tamotsu kneels in the mud — a samurai shouldn't — and sets a rice sack beside her.)
TAMOTSU: Hate me, grandmother. I'm the one who's late.
> CHOICE "The rice"
  - "Give it all to the camp." → [SET camps_fed] (−rice, Honor +1)
  - "Keep it for the road." → (nothing; the grandmother says nothing)
(Thugs try to steal the rice the moment Tamotsu stands.)
[BATTLE b_camp_thugs] (tutorial: **Barter Coin** — "Spend coin in battle: hire a strike, or bribe an enemy to skip a turn.")
CAMP THUG: (bribed) …Ten zeni? (pocketing it) I'm going home.
TAMOTSU: Go with the Fortunes, my friend. Buy your mother something.

## S03 — The Case Files (hub)
MAP: `shiro_iuchi_court`, `shiro_soshi_court`, `hafuna_fields`, `motobu_crater` · TRIGGER: explore
(A case board in the inn: eight grievances. Three are open this chapter.)
### Case 1 — The assassins (`shiro_iuchi_court`)
(SHIRO IUCHI: a triangular castle built into a wind tunnel. The daimyo, IUCHI DAIYU, sits in a garden talking to a woodchuck.)
IUCHI DAIYU: He's a nice one. He brought you a carrot.
TAMOTSU: (kneeling, producing a carrot) I brought you one too, my lord.
IUCHI DAIYU: (delighted) Nobody brings me carrots. They bring me reports.
IUCHI DAIYU: (beat; quieter) …The reports are lies, aren't they?
(Behind them, a man in a white porcelain mask with faintly glowing eyes: IUCHI KARASU.)
IUCHI KARASU: Mostly. The carrots are real.
TAMOTSU: You're the nephew who came back from the Shadowlands.
IUCHI KARASU: I'm the nephew who came back. The Shadowlands were very rude about it.
TAMOTSU: (Status: emissary) Karasu-sama. I'm asking as the tribunal's emissary. What did the assassins carry?
IUCHI KARASU: (a pause; then he lays a scorched cloth on the table) Soshi shadow-brands. On every one of them.
[PA Discern Karasu] (optional) → "He doubts the Soshi sent them."
→ case 1 [SET cases_done +1]
(The karo, IUCHI HIROICHI, a Shinjo-trained bushi with a gaijin telescope, watches them both with worry.)
IUCHI HIROICHI: My lord doesn't need to hear about the war, Ide-san.
TAMOTSU: (gently) My lord is talking to woodchucks so he won't have to, Hiroichi-sama. That's hearing.
### Case 2 — The salted fields (`hafuna_fields`)
(White crusted earth. A Iuchi general, Shinjo by birth, inspects it without regret: GENERAL TAKANOBU.)
GENERAL TAKANOBU: Wars are for winning, emissary.
TAMOTSU: And when the war is over, general, what grows here?
GENERAL TAKANOBU: (long pause) …Nothing. That was the point.
→ [PA Barter] his supply ledger (shows the order came from the top) → case 2 [SET cases_done +1]
### Case 3 — The Temple of Jizo (`motobu_crater`)
(A crater where a temple stood.)
TAMOTSU: (reading the evidence) The Soshi hid soldiers in the temple. The Iuchi used the Fist of Osano-Wo.
TAMOTSU: (quietly) Both sides made a temple a weapon. Jizo protects children. There were children in the village below.
→ testimony from a surviving monk (**Bless**, if Haruki; or Etiquette) → case 3 [SET cases_done +1]
### Shiro no Soshi court (optional)
(The Soshi daimyo, SOSHI BANTARO — buffoonish, loud — and his wife SHINOBU, quiet, the real power.)
SOSHI BANTARO: The Unicorn are liars! The Iuchi are murderers! More sake!
SOSHI SHINOBU: (pouring) My husband means that the Soshi welcome the tribunal's wisdom.
TAMOTSU: (bowing to her, not him) I'm sure he does, my lady.
SOSHI SHINOBU: (the faintest smile) …The Unicorn really have sent a dangerous man.
[SAVE]

## S04 — Old Miyahana's Cottage
MAP: `miyahana_cottage` · TRIGGER: after 2 cases
(A small mountain cottage. Plum trees. An old woman pouring tea: SHINJO MIYAHANA, Tamotsu's teacher.)
SHINJO MIYAHANA: Little Tamotsu. Rounder than ever.
TAMOTSU: (bowing, beaming) Sensei. Wiser than ever.
SHINJO MIYAHANA: You were always a flatterer. (then, worried) Have you heard from Naohida?
TAMOTSU: Not in a year.
SHINJO MIYAHANA: Nor I. He always asked why. Why must the farmer bow? Why does the lord eat first?
SHINJO MIYAHANA: I told him the answers. He didn't like them.
TAMOTSU: I didn't like them either, sensei.
SHINJO MIYAHANA: No. But you smiled while you disliked them. He never learned to smile.
(She looks out at the hills a long time.)
SHINJO MIYAHANA: If you find him, bring him to tea. Tell him I've stopped giving answers.

## S05 — Buried Leaves (the bombing)
MAP: `buried_leaves_inn` (night) · TRIGGER: after 3 cases
(The tribunal's welcome dinner. Toasts. Tsune almost smiles. Then a thunderclap tears the east wall open.)
(CUTSCENE — fit conversion: the rescue. Fire, beams falling, Tamotsu dragging a Scorpion judge out by the collar,
going back for a Crane clerk, then for a child, then for a cat. Persimmon kicks down a burning stable door.)
TAMOTSU: (coughing, soot-black, the cat under one arm) Is that everyone?
SHINJO TSUNE: (staring) …You went back four times.
TAMOTSU: The cat was important.
(A pigeon lands on a broken beam with a message tube. Tsune reads it, white-faced.)
SHINJO TSUNE: "Stop judging the dead. Judge the living."
(A Lion samurai in Seppun-trimmed armour pushes through the smoke: AKODO RIN, the tribunal's escort.)
AKODO RIN: That was gaijin pepper. Gunpowder. Illegal. Unthinkable.
AKODO RIN: (sniffing the ash) And made fresh. Saltpeter. From bird droppings.
IUCHI HIROICHI: (lowering his telescope) Pigeons. Yotomo — the pigeon breeders' village. North.
AKODO RIN: Then I'm coming with you, emissary. I'm meant to protect the tribunal. (beat) I'd like to protect it from *that*.
[GUEST +Akodo Rin] [SET rin_joined] (skills: Cover — protect an ally, 2 uses; The Clouds Part — first-turn speed buff, 1 use)
[SAVE]

## S06 — The Pigeon Cave (dungeon)
MAP: `yotomo_village` → `pigeon_cave_1–2` · TRIGGER: travel north
(Yotomo: a village of dovecotes. The cliffs above are crusted white. A cave mouth breathes the sharp stink of saltpeter.)
VILLAGE BOY: Don't go up there, lords! The cave men pay us in rice to keep away!
TAMOTSU: (giving him a rice cake) Then I'll pay you in rice to tell me how many.
VILLAGE BOY: (eating) …Twenty. And the angry one.
### GIMMICK preview — powder kegs
"**Powder kegs** stand on the battlefield. Any **Fire** hit sets one off: a huge blast that hits **both sides**."
[BATTLE b_cave_guerrillas] (peasant guerrillas — they surrender easily; Barter Coin's *Settle the Account* pays them off)
GUERRILLA: (hands up) We're farmers! He taught us to make the powder! We just want them to stop!
TAMOTSU: (kindly) So do I. Go home. Take your powder off the shelf when you go.
[SAVE] (before the overhang passage)

## S07 — Naohida (BOSS)
MAP: `pigeon_cave_2` (the vat chamber) · TRIGGER: enter
(Vats. Pigeons. Barrels. A young man in peasant clothes with a curved gaijin blade: NAOHIDA. He stops dead.)
NAOHIDA: …Tamotsu.
TAMOTSU: Naohida. You owe me a copper.
NAOHIDA: What?
TAMOTSU: The rice cakes. When we were nine. You paid in pebbles. I took them. I still have one.
NAOHIDA: (almost laughing; then not) Look at you. Silk and a pony.
NAOHIDA: They gave you a seat at the table, Tamotsu. They gave me a grave to dig.
TAMOTSU: Then come and sit in my seat. I'll stand. I've got good legs.
NAOHIDA: You always talk. (raising the blade) Talk to this.
[BATTLE b_boss_naohida]
### Barks
- Naohida throws a powder bomb: "Burn, then! Burn like Motobu burned!"
- Keg goes off: AKODO RIN: "Water! Something wet — anything!"
- Barter Coin used on the guerrillas: GUERRILLA: "Sorry, Naohida — he pays better than the cause!"
- At low HP Naohida hurls a bomb at the cave mouth.
NAOHIDA: (through the smoke) Judge the living, Tamotsu! Start with them!
(He's gone. The cave mouth burns.)

## S08 — Judge the Living
MAP: `buried_leaves_inn` (half-burned, morning) · TRIGGER: return
(The tribunal reconvenes in the inn's one standing room. Three grievances' worth of testimony on the table.)
SHINJO TSUNE: The bomber. Do you have his name?
> CHOICE "Naohida"
  - "Name him." → [SET naohida_named] (Honor +1; a manhunt begins)
      TAMOTSU: …His name is Naohida. A peasant. Trained by Shinjo Miyahana. (beat) My classmate.
  - "He escaped unidentified." → (Honor −1; Naohida will trust him later)
      TAMOTSU: (meeting Tsune's eyes) He escaped, Tsune-sama. Into the smoke. Unidentified.
      SHINJO TSUNE: (a long look; he knows) …Unidentified.
SHINJO TSUNE: You knew him.
TAMOTSU: (quietly) I sold him rice cakes for a copper when we were nine.
TAMOTSU: He paid in pebbles. I took them.
(He opens his hand: a small grey pebble, smooth from twenty years in a pocket.)
[CHAPTER COMPLETE]
### Chapter complete card
**"Fault Lines" — complete.**
Journal: *A tribunal of grief between two castles. Tamotsu fed the camps, opened three cases, pulled four people and
a cat from a bombed inn — and met the bomber, who once paid him in pebbles.*

---
## Travel Banter unlocked by Unicorn Ch1
### TB-unicorn1-a "Persimmon" (Tamotsu + Natsuko)
NATSUKO: Your pony bit me.
TAMOTSU: She likes you!
NATSUKO: She bit me twice.
TAMOTSU: She *really* likes you.
### TB-unicorn1-b "Carrots" (Tamotsu + Gendo)
GENDO: You brought a daimyo a carrot.
TAMOTSU: He'd been brought reports for twenty years. Nobody had asked what he was hungry for.
GENDO: (pause) That's a very good interrogation technique.
TAMOTSU: (laughing) Gendo, it's a carrot.
GENDO: It's a very good carrot.
