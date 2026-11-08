# PRODUCTION — Unicorn Ch2 "The Bell Without a Clapper" = Scorpion Ch3 "Fortunes Lost" (co-owned crossroads)

**Owners:** Ide Tamotsu **and** Shosuro Mitsue · **Lv** 22–30 · **Outline:**
`scripts/unicorn-ch2-scorpion-ch3-fortunes-lost.md`
**Viewpoint:** the chapter is started from whichever owner's chapter list. `[IF owner tamotsu]` /
`[IF owner mitsue]` mark scenes that differ. When the other owner is absent, **Shinjo Tsune** (Unicorn bench) or
**Shosuro Norie** (Scorpion bench) speaks their lines.
**Flags read:** `camps_fed`, `naohida_named`, `rin_joined`, `iron_box_held` · **Flags set:**
`mitsue_knows_shoju_war`, `gochu_family_fed`, `nihime_told`, `verdict` (both / iuchi / soshi)
**Maps:** `tribunal_hall` (Buried Leaves, rebuilt), `soshi_camp`, `yotomo_bell_hill`, `perfume_petal_blossom`,
`mountain_road_dusk`
**Battles:** `b_boss_iuchi_hit_squad` (silence-bubble gimmick)
**Storyboard:** `storyboards/unicorn-ch2-scorpion-ch3.md`
**Co-owned rule (C-1):** both owners in the active party → plays once and counts as **both** chapters. One owner only
→ plays from that owner's view; the other owner's chapter is later a flashback ("That season at the tribunal")
from their view, with `verdict` locked to the first choice. **Mitsue's view scales enemies to Lv 30–35** (her Ch3
band).

---

## S01 — Votes Are Bought in Silk (tribunal hub)
MAP: `tribunal_hall` · TRIGGER: start
NARRATION: The tribunal sits. Three benches: Unicorn, Scorpion, and the neutral swing vote. Five grievances left.
Every judge has a price.
### Bench intros
[IF owner tamotsu]
SHINJO TSUNE: The swing judge likes horses, poetry and cheap scandal.
TAMOTSU: I have a pony, a terrible haiku, and a very expensive scandal. I'll bring all three.
[ELSE]
SHOSURO NORIE: The swing judge likes horses, poetry and cheap scandal. The Unicorn have the horses. We have the scandal.
MITSUE: And the poetry?
SHOSURO NORIE: Nobody has the poetry. That's why it's the swing vote.
[END]
### The remaining grievances (case board) — each needs a path action + testimony
| Grievance | Tamotsu's path | Mitsue's path |
|---|---|---|
| The poisoned well at Jiochi (750 dead) | *Barter* with a surviving water-carrier: it was the Iuchi interrogation camp | *Eavesdrop* on Soshi officers: they silenced it with oleander |
| The massacred Shosuro acting troupe | *Barter* the troupe's surviving props: Iuchi arrows | *Many Faces* as an Iuchi soldier: "We were ordered to. They were spies." |
| Soshi Katsu's funeral peace broken | testimony from the Iuchi side | the culprit: Katsu's own 14-year-old son, Ichihito |
| Both sides padding their armies | trade ledgers | Scorpion rolls |
| The jade mines' silence | (deferred to Unicorn Ch3) | (deferred) |
### The seppuku (MAP: `soshi_camp`; Mitsue's viewpoint)
[IF owner tamotsu AND NOT mitsue_in_party]
(Morning. News runs through the tribunal: a Soshi general opened his belly in the night, before he could testify.)
SHINJO TSUNE: (grim) One less witness. Somebody wanted it that way.
(The rest of this scene, and `mitsue_knows_shoju_war`, play only in Mitsue's view.)
[ELSE]
(Night. A Soshi general kneels in his tent and opens his belly before he can testify. Mitsue, in a servant's face,
slips in before the guards.)
MITSUE: (finding his last letter under the mat; reading) "…the war was set moving from Kyuden Bayushi. By the
Champion's own hand. A distraction."
MITSUE: (very still) …A distraction from what?
SHOSURO NORIE: (in the doorway) You will not repeat what you just read.
MITSUE: (folding it very small) To whom, sensei? Who would believe a nobody?
[SET mitsue_knows_shoju_war]
[IF owner tamotsu AND mitsue_in_party]
(Later, Tamotsu notices Mitsue not eating.)
TAMOTSU: You look like you swallowed a stone.
MITSUE: (bright) I *love* stones. Very filling.
[END]
[END]
[SAVE]

## S02 — The Bell Without a Clapper
MAP: `yotomo_bell_hill` · TRIGGER: Akodo Rin reports being followed
AKODO RIN: Someone's following me. Every time I'm alone, a bell on the hill moves.
AKODO RIN: It doesn't ring. It has no clapper. It just… swings.
(A starving miner sits under the bell frame: GOCHU.)
GOCHU: (miserable) Five koku, lady. Five koku to swing it when you're alone.
GOCHU: It doesn't even ring. I thought it was a joke.
AKODO RIN: (gently) Then let's tell the joke back to whoever's laughing.
### Path actions on Gochu
- *Discern / Eavesdrop:* "Paid by an Iuchi agent with a meishodo amulet."
- **Barter** (Tamotsu): "Your family's in the camp? (handing over rice) Here. Now tell me who paid."
  [IF camps_fed] GOCHU: "…You're the one who fed the camp. My daughter ate your rice." (he tells everything) [END]
  [SET gochu_family_fed]
GOCHU: The signal's for watchers on the ridge. They want her. Something about her blood.
AKODO RIN: (going pale) …My grandmother was Seppun.
TAMOTSU: Imperial blood.
AKODO RIN: (quietly) A drop. Enough to be useful to someone, apparently.

## S03 — Perfume Petal Blossom (dungeon-village)
MAP: `perfume_petal_blossom` · TRIGGER: follow the agent's trail
NARRATION: A flower village. Every house freshly swept. Every path lined with blossom. No refugees, though thousands
are camped one valley away.
[IF sayo_in_party] SAYO: Flowers this thick are hiding a smell. Every herbalist knows that. [END]
(The most beautiful house. An old courtesan serving tea with perfect hands: "WARUKO" — SOSHI NIHIME.)
SOSHI NIHIME: You're the Ide boy. My son wrote about you.
SOSHI NIHIME: "He smiles while he disagrees."
TAMOTSU: (quietly) He told you about me?
SOSHI NIHIME: He tells me everything. He thinks I'm the only person in these valleys who never lied to him.
SOSHI NIHIME: (pouring) I was a Soshi daimyo's daughter, once. I loved an Iuchi. They sold me to a geisha house and
told my family I'd died.
SOSHI NIHIME: My son is the child of that war. Naohida.
[IF owner mitsue] MITSUE: (to herself) A Scorpion lady sold and declared dead. The family files say "drowned". I've read them. [END]
> CHOICE "Tell her what her son did?"
  - "Tell her about the bombing." → [SET nihime_told]
      SOSHI NIHIME: (a long silence; then, steadily) …Then he's become his father after all.
      SOSHI NIHIME: (setting down the cup) I'll help you. Not for the Iuchi. For him.
  - "Keep it from her." → (she helps anyway, less)
### Beneath the village
(A path down behind the houses toward the jade mines. A grave nobody has claimed: low mounds, prayer strips, flowers
planted over them. Karasu, if present, stops and says nothing for a long time.)
(The grave path is a short dungeon — encounters: Gaki, Mountain Wolf; uncommon Blood-Hungry Acolyte — ending at the
sealed mine gate. Back at the village shrine: [SAVE])

## S04 — The Iuchi Hit Squad (BOSS)
MAP: `mountain_road_dusk` · TRIGGER: leave the village
(Dusk on the mountain road. The ground ripples. Iuchi shugenja rise out of the earth around the party — and the world
goes utterly silent.)
[BATTLE b_boss_iuchi_hit_squad]
### GIMMICK — the silence bubble
"Every other turn, a **silence bubble** seals all **spells and spell-like skills** (an icon warns you a turn early).
The **amulet-bearer** anchors the bubble — **break him (Suki)** to pop it for good."
### Barks (silence turns are shown as mouthed lines in grey)
- Silence: MITSUE (mouthing to Tamotsu): "Left." (she's already moving)
- Silence: TAMOTSU (mouthing): "…Did you say 'lunch'?"
- Bubble pops: AKODO RIN: "I can hear again! Gods, I can hear the *birds*."
- Amulet-bearer down: IUCHI AGENT: "The old master needs her! He needs royal blood! You don't understand what's coming!"

## S05 — The Verdict
MAP: `tribunal_hall` · TRIGGER: return
(The tribunal. Evidence on every table. The swing judge looks at both owners.)
SWING JUDGE: The evidence names crimes on *both* sides.
> CHOICE "The verdict"
  - "Name both sides' crimes." → [SET verdict both] (recommended; Honor +1; both courts furious)
  - [IF owner tamotsu] "Shield the Iuchi dead." → [SET verdict iuchi] (Glory + at home; Honor −1)
  - [IF owner mitsue] "Shield the Soshi dead." → [SET verdict soshi] (Glory + at home; Honor −1)
[IF verdict both]
SHINJO TSUNE: (stunned) …Both. You named both.
SHOSURO NORIE: (to Mitsue, very low) You've made enemies in two clans today.
MITSUE: Only two, sensei? I'm losing my touch.
[END]
(Mitsue's private beat, either way: she does not reveal the Champion's letter. Her hand rests on her sash where it's folded.)
(Afterwards. A balcony. Tamotsu offers Mitsue a rice cake.)
TAMOTSU: You wrote half of that verdict.
MITSUE: I wrote *all* of it. You read it beautifully.
MITSUE: (taking the cake) Don't tell anyone I was kind.
TAMOTSU: (laughing) I'd never. Nobody would believe me.
[ITEM +Wax Earplugs (key item: Covered Ears status, Unicorn Ch3–4)]
(A messenger runs up the stairs, white-faced.)
MESSENGER: A body — in a field near Shiro Iuchi — in a star burned into the grass.
MESSENGER: A Seppun courier. Drained.
AKODO RIN: (very quiet) …That was meant to be me.
[CHAPTER COMPLETE]
### Chapter complete card (shown per owner)
**Unicorn — "The Bell Without a Clapper"** / **Scorpion — "Fortunes Lost"** — complete.
Journal (Tamotsu): *A bell that never rang, a mother sold and declared drowned, and a verdict that named everyone's dead.*
Journal (Mitsue): *A general opened his belly to hide a letter. Mitsue read it anyway. Her own Champion started this
war — and she can tell no one.*

---
## Travel Banter unlocked
### TB-crossroads3 "Rice Cakes" (Tamotsu + Mitsue)
TAMOTSU: I have a theory about you.
MITSUE: Everyone does.
TAMOTSU: You're kind, and you hide it the way other people hide cruelty.
MITSUE: (long pause) …That's a very dangerous theory, Ide.
TAMOTSU: I'm a very dangerous man. Ask your sensei.
