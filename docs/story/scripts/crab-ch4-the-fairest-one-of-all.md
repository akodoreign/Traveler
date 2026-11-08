# Script — Crab Ch4 · "The Fairest One of All" — DRAFT v0.1

**Source:** *Mirror, Mirror* Part III (Brandes & Hepler, 1999). **Heavily softened:** the real Kuhime's body is
implied (a sealed barrel, Natsuko's reaction); no child endangerment shown, only the threat. Plot facts only; **all
dialogue is original**.
**Traveler:** Hiruma Natsuko · Rank 3, Lv 41–45 · **summer 1123** · Kyuden Hida and the Kaiu Wall.
**Octopath shape:** the castle under siege (hub) → the cellars → the stalking sequence (set-piece) → the trap
tunnels → the Wall (boss).
- **Set-piece:** **the stalking sequence** (Nashiko can be anyone).
- **Choices:** 2.
- **Flags used:** `guard_rescued` (Ch3), the blue flare (Ch2).

---

## Scene 1 — "A Wedding at Speed"
**Beat:** Kage is wed at once to Mutsuye's friend **Asako Kuhime**: the court needs a Hiruma heir. Kuhime is
radiant. Kage is numb. Natsuko stands at the back and watches the bride's eyes: very blue.
ASAKO KUHIME: *(to Natsuko, warmly)* You brought him home. I'll never forget it. *(beat)* I never forget anything.

## Scene 2 — "Every Trap Is Wrong"
**Beat:** That night the Shadowlands strike the Wall: Oni no Tsume's horde. **Every trap inside the castle and on the
Wall has been sabotaged from within.**
- `guard_rescued`: the half-mad Hiruma guard from Ch3 names the sabotaged sections. Natsuko knows which tunnels are
  safe.
- Takakana splits the defenders: scouts to the Wall, bodyguards to herd the court into the cellars. Natsuko is sent
  to the cellars ("The Champion's guests must live. Most of them.").

## Scene 3 — "The Barrel" (the reveal, softened)
**Beat:** In the cellars, among the pickle barrels, Natsuko finds a sealed barrel no one has opened in weeks. Inside
(not shown; her face is): **the real Asako Kuhime**, dead two weeks. The bride upstairs is someone else.
NATSUKO: *(very quietly, the lid back on)* Two weeks. She's been wearing her face for two weeks. *(beat)* At the
wedding. At my lord's side.
*(Upstairs: the sound of a woman laughing, from everywhere at once.)*
**The bride is Doji Nashiko.** The court's children and the women's quarters are upstairs with her.

## Scene 4 — "She Can Be Anyone" (set-piece: the stalking sequence)
**Beat:** Nashiko, invisible and shifting faces, stalks the dark castle. **No combat** (OCTOPATH-FIT set-piece):
- The party moves room to room. NPCs may be Nashiko wearing their face. **Tells** (from the stories) expose her:
  - she doesn't flinch at scalding sake
  - she mistakes smooth stone for jade (colour-blind)
  - jade burns only her bare skin
  - she can read only one mind at a time (keep two travelers apart, and she loses track of one)
- `[SYS]` Each wrong guess costs a step on a "dread" counter. If it fills, she knocks a party member out (no game
  over).
- **Goal:** lure her away from the children's quarters down into the **trap tunnels**.
NASHIKO *(in a servant's face)*: Lost, scout? Let me light your way. *(the lantern she holds gives no warmth)*
NATSUKO: *(handing her a smooth river stone)* Here: jade, for luck.
NASHIKO: *(taking it, pleased; then the jade-dust on Natsuko's glove brushes her wrist and smokes)* …You little
*Crab*.

## Scene 5 — "Through the Teeth" (dungeon)
**Beat:** The trap tunnels: jade-dust trip line, rollers, spiked pit. Natsuko leads Nashiko through them *on
purpose*, springing the traps the saboteurs missed. Nashiko pursues, laughing, wounded by each trap.
`[CHOICE 1]` *Fire the blue flare* (the signal nobody has seen before: the Crab army rings the tunnel exit, and Ch4's
boss gets +1 turn of army support) · *keep it* (it stays for the finale callback).

## Scene 6 — BOSS: "Oni no Tsukakoro at the Wall"
**Beat:** At the tunnel's end, on the Wall, Nashiko summons **Oni no Tsukakoro** (a bouncing bone-cage) to cover her
escape, while the army closes in.
`[BATTLE]` **Oni no Tsukakoro**:
- Resolve 14. Weak: **Tetsubo**, **Jade**, **Earth**. **Multi-target bounce** (the source's bouncing attack hits 2–4
  targets in a chain; Natsuko's Razor's Edge redirects bounces to herself).
- No extra gimmick (the stalking was the set-piece).
- Natsuko's R3 *Fire and Shadow* (+damage vs. Shadowlands) applies.

## Scene 7 — "Smoke and Laughter" (ending)
**Beat:** The oni falls. Nashiko, cornered by the whole Crab army, laughs and **flies north on smoke**. She never
risks herself.
NASHIKO: *(from the smoke)* Tell Kage I enjoyed the wedding! Such a *sad* little man. I'll wear someone he loves next
time. Maybe *you*.
NATSUKO: *(yari raised)* Try it. My face doesn't fit anyone else.
`[CHOICE 2]` What Natsuko tells Kage: *the whole truth* (he breaks, then swears to keep the Hiruma line alive; it's
the canonical line) · *a kinder version* (he never learns his bride was a demon; Honor −).
- Kage swears, either way, to keep the Hiruma alive. He gives her his father's tanto.
HIRUMA KAGE: Someday we'll walk your father's road. *(beat)* Not by dying.
- **Hand-off:** Natsuko follows Nashiko's trail north → the **finale**.
`[SYS]` **Rewards:**
- Lv ~45.
- Kage's tanto (a Jade-element Tanto).
- *Shards of Earth* kata at Lv 51.
- `nashiko_unmasked` (a finale debuff: one of her shields starts revealed).
