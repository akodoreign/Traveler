# Script — Crab Ch3 · "Beyond the Wall" — DRAFT v0.1

**Source:** *Mirror, Mirror* Part II (Brandes & Hepler, 1999). **Softened** (the bride's suicide is told, not shown).
Plot facts only; **all dialogue is original**.
**Traveler:** Hiruma Natsuko · Rank 2, Lv 30–35 · **early spring 1123** · the Kaiu Wall → the Shadowlands.
**Octopath shape:** the Wall (town) → the trap tunnels → the Shadowlands (a long dungeon with save shrines) → Toshi
no Kijo → the fake patrol → boss.
- **Gimmick:** the Oni no Kommei **swaps two travelers' commands**.
- **Choices:** 2.
- **Flags paid off:** `nezumi_friends`, `oni_named_ryozo` (Crab Ch1).

---

## Scene 1 — "Told, Not Shown"
**Beat:** Hida Sachiko meets Natsuko at the Wall with the news: Isawa Mutsuye, Tainted and disgraced, took her own
life at the women's shrine. **Hiruma Kage**, grief-mad, walked out through the Wall at dawn, alone, into the
Shadowlands. Takakana can't spare troops.
KAIU TAKAKANA: He's a daimyo, Hiruma. If he dies out there, the Hiruma line dies with him.
NATSUKO: Then I'll bring him back.
KAIU TAKAKANA: *(beat)* I didn't hear you volunteer. Because I didn't order it. Because nobody would be fool enough.
*(hands her jade)* Go.

## Scene 2 — "The Trap Tunnels"
**Beat:** The Wall's trapped tunnels: rollers, spiked pits, jade-dust trip lines. Natsuko knows the safe paths (a
Hunting/Athletics interaction shortcut). **Squeak and the nezumi** (`nezumi_friends`) are waiting at the far end
with a hand-drawn tunnel map. If the flag is off, the hired Hidden Ones take this role instead.
SQUEAK: Scout-who-fights-at-night! We know the dark-ways. Rats always know the dark-ways.

## Scene 3 — "The Upside-Down Forest" (dungeon, part 1)
**Beat:** The Shadowlands. A tar chasm with a rope bridge; the **Lava Trees** (an upside-down forest); fields of
**toothed poppies**; acid bogs.
- **Taint** builds on Shadowlands tiles (status; cleansed by jade items and shrines; `enemies.md`).
- `[BATTLE]` Goblins, onikage demon-horses (weak to **Yari**, **Jade**).
- **Her father's map is real:** landmarks match. A route exists. Natsuko marks it with a charcoal stick, hands
  shaking.
NATSUKO: *(very quietly)* He wasn't a fool. He was *right*. Thirty years, and he was right.

## Scene 4 — "The Broken Guard"
**Beat:** A Hiruma guard, half-Tainted, broken in spirit, in a ruined watchpost.
`[CHOICE 1]` *Mercy* (the Crab way: a clean death; Courage, but grief) · *carry him home* (slower; he survives
half-mad. Ch4: he warns them which traps were sabotaged).
`[FLAG guard_rescued]`

## Scene 5 — "Toshi no Kijo" (talk-down)
**Where/When:** a troll-ruin coliseum
**Beat:** Kage is smashing pottery in the ruin of an old troll city, alone, raging, half-hoping something kills
him. Talk him back (a dialogue sequence; no battle).
HIRUMA KAGE: Fifteen generations of Hiruma without a home. One woman made me forget it for a month. *(smashing a
jar)* I'm done remembering.
NATSUKO: *(holding out her father's map)* Then remember this. There's a road back, my lord. My father found it. If
you die here, who walks it?
*(Long silence. Kage takes the map. He laughs, terribly, and then he sits down in the dust and weeps.)*

## Scene 6 — "Riders Without Faces"
**Beat:** On the way home, **Moto akutsukai** scouts (undead Unicorn riders with skeletal wings) sweep the plain.
Hide from them (a cutscene with one Stealth prompt; failing it starts a hard battle).
- `oni_named_ryozo`: a nameless thing among the riders calls itself **"Ryozo"** in a borrowed voice and wears
  the guardsman's polished armour. Natsuko recognises the armour. A short, chilling exchange; it rides off. (It
  returns in the finale's Act 1.)
"RYOZO": *(the door-creak voice)* I have a name now, scout. A good one. Imperial. *(pleased)* Thank you for leaving it
for me.

## Scene 7 — BOSS: "The Patrol That Isn't" (Oni no Kommei)
**Beat:** A "Crab patrol" meets them on the road back: maho-bujin in Crab armour, led by an **Oni no Kommei** with a
second face on the back of its head.
`[BATTLE]` **Oni no Kommei + maho-bujin**:
- **Gimmick: Body-swap.** Every third turn it swaps **two travelers' command menus** (their skills, not their
  stats) for 2 turns. Plan around it.
- Kommei: Resolve 12. Weak: **Jade**, **Tetsubo**, **Fire**. The face on the back of its head is a separate target
  (breaking it ends the swaps).
- Maho-bujin: Resolve 4. Weak: **Yari**, **Katana**.
`[CHOICE 2]` Kage fights at full fury (a guest for this battle: strong, but he takes huge damage) · Natsuko orders
him to stay back (Command-style dialogue; the battle is harder, and Kage obeys a Hiruma scout for once).

## Scene 8 — Ending
**Beat:** They reach the Wall at dusk. Kage, alive, gives Natsuko back the map, then changes his mind.
HIRUMA KAGE: Keep it. No. *(he takes it back)* I'll keep it. Someone of rank should carry it. *(beat)* You'll walk
beside me when we use it.
→ **Ch4 "The Fairest One of All"** (Kage is to wed Mutsuye's friend **Asako Kuhime** at once…)
`[SYS]` **Rewards:**
- Lv ~35.
- The Map of the Road Home (story key item; the post-game Hiruma Castle side story ties to the canon Hare sword).
- *Stance of the Wall* kata (R3; at the first pick after Lv 41).
- Squeak's tunnel map.
