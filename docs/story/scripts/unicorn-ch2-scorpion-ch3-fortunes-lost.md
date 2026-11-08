# Script — Unicorn Ch2 "The Bell Without a Clapper" = Scorpion Ch3 "Fortunes Lost" (co-owned crossroads) — DRAFT v0.1

**Source:** *Fortune's Lost* Part II (Brandes & Hepler, 1999). **Toned down** (no shown atrocities). Plot facts
only; **all dialogue is original**.
**Owners:** Ide Tamotsu (Unicorn Ch2) **and** Shosuro Mitsue (Scorpion Ch3), the same tribunal from two benches.
- Rank 2, Lv 22–30 · **winter 1122–23** · the Ojatara Valleys.
- **Stand-ins:** without Mitsue, **Shosuro Norie** carries the Scorpion bench. Without Tamotsu, **Shinjo Tsune**
  carries the Unicorn bench.
**Octopath shape:** tribunal town → the bell trap → Perfume Petal Blossom (dungeon-village) → hit-squad boss.
- **Gimmick:** the **silence bubble** in the boss fight (spells disabled on a turn cycle).
- **Choices:** 2 (the verdict; what to tell Naohida's mother).
- **Adaptation:** the stalker's target is the guest **Akodo Rin**. Her Seppun grandmother gives her a drop of royal
  blood, which the sacrifice needs (the source targets "the royal-blooded PC").

---

## Scene 1 — "Votes Are Bought in Silk" (tribunal hub)
**Beat:** The tribunal sits. Three benches: Unicorn (Tsune, Tamotsu), Scorpion (Norie, Mitsue), and a neutral
swing vote. Haggling for votes plays as **Barter** (Tamotsu: gifts, trade concessions) and **Eavesdrop** (Mitsue:
what each judge fears).
- The remaining grievances (`unicorn-ch1` case board):
  - the poisoned well at Jiochi (it was an Iuchi interrogation camp; the Soshi silenced it)
  - a Shosuro acting troupe massacred by Iuchi troops
  - Soshi Katsu's funeral peace, broken by his own 14-year-old son
  - both sides padding their armies
  - the jade mines' silence
- **Mitsue's viewpoint:** a Soshi general commits a hurried **seppuku** the night before he testifies. It buries
  evidence. Mitsue reads his last letter: the war was *nudged* from Kyuden Bayushi, as a distraction. **Her own
  Champion started it.**
SHOSURO NORIE: You will not repeat what you just read.
MITSUE: To whom, sensei? *(she folds the letter very small)* Who would believe a nobody?
`[FLAG mitsue_knows_shoju_war]` → Scorpion Ch4.

## Scene 2 — "The Bell Without a Clapper" (the trap)
**Beat:** Someone stalks **Akodo Rin**. **Gochu**, a starving miner, has been paid 5 koku to "ring" a clapperless
bell whenever she is alone. The "ringing" is a signal: the bell is hung so that it *shows* rather than sounds. Its
movement is a sign to watchers on the ridge.
- **Discern / Eavesdrop / Barter** on Gochu reveal the payer: an Iuchi agent. Gochu's family is in the refugee camp
  (Tamotsu can feed them: `camps_fed` pays off).
GOCHU: *(miserable)* It doesn't even ring, lady. I thought it was a joke. Five koku for a joke.
AKODO RIN: *(gently)* Then let's tell the joke back to whoever's laughing.
`[SYS]` A short field set-piece is *not* used here (the gimmick budget goes to the boss). This scene is talk and
path actions only.

## Scene 3 — "Perfume Petal Blossom" (dungeon-village)
**Where/When:** a flower village, too perfect to be real
**Beat:** Every house is freshly swept. No refugees, though thousands are camped a valley away. Flowers hide the
smell. Beneath the village: the path toward the **jade mines**, and a grave nobody claims.
- **"Waruko"**, an old courtesan in the most beautiful house, is **Soshi Nihime**: a Scorpion daimyo's "dead"
  daughter, sold to a geisha house after her affair with Iuchi Kurosho twenty years ago. She is Naohida's mother.
SOSHI NIHIME: *(serving tea, perfectly)* You're the Ide boy. My son wrote about you. "He smiles while he disagrees."
TAMOTSU: *(quietly)* He told you about me?
SOSHI NIHIME: He tells me everything. He thinks I'm the only person in these valleys who never lied to him.
`[CHOICE 1]` Tell her what her son did at Buried Leaves (truth; she weeps, then helps) · keep it from her (she
helps anyway, but Ch3's curse-break scene is weaker).
`[FLAG nihime_told]`

## Scene 4 — BOSS: "The Iuchi Hit Squad"
**Where/When:** the mountain road out of the village, at dusk
**Beat:** Iuchi shugenja **rise out of the earth** around the party inside a **silence bubble** to take Rin.
`[BATTLE]` **Iuchi hit squad** (3 shugenja + a meishodo amulet-bearer):
- **Gimmick: the silence bubble.** Every other turn, spells and spell-like skills are disabled (an icon warns the
  turn before). Plan weapon turns for the silent rounds.
- The bubble's anchor is the amulet-bearer. **Breaking him (Suki) pops the bubble** for good.
- Shugenja: Resolve 5. Weak: **Yari**, **Yumi**, **Air** (the earth-risers fear the wind). Amulet-bearer: Resolve
  7. Weak: **Tanto**, **Katana**.
MITSUE: *(in the silence, mouthing it to Tamotsu)* "Left." *(she's already moving)*

## Scene 5 — "The Verdict"
**Beat:** Back at the tribunal. The evidence names crimes on **both** sides.
`[CHOICE 2]` The verdict:
- **Name both sides' crimes** (the canonical "best"): Honor +; both courts are furious; a friendship across the line.
- **Shield your own clan's dead** (Tamotsu shields the Iuchi / Mitsue the Soshi): Glory + at home, Honor −.
- *(Mitsue's private beat, either way: she does **not** reveal that her Champion started it. Duty.)*
TAMOTSU: *(after the verdict, offering Mitsue a rice cake)* You wrote half of that verdict.
MITSUE: I wrote *all* of it. You read it beautifully. *(takes the cake)* Don't tell anyone I was kind.
→ **Unicorn Ch3 "The Noblest Blood"** (a maho sacrifice victim is found: *something has been summoned*) ·
**Scorpion Ch4 "The Eve"**.
`[SYS]` **Rewards:**
- Lv ~30.
- Wax earplugs (key item for Unicorn Ch3–4: the Covered Ears status).
- Akodo Rin's side story 2 (her Seppun blood).
- A Mitsue–Tamotsu banter chain.
