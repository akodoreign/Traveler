# Rules - Progression v2 (user, 2026-11-11)

Replaces the rank thresholds in schools.md and the "Kata Stance" activation in kata.md. Everything else in those
files (the technique lists, the per-traveler kata picks, the kiho menu) stays the source for content.

User's report that started it (Crab path): Goro's dojo called it "the Hida technique" though Natsuko is a Hiruma,
it never gave a technique, and it left no pointer of where to go next. "Each school should follow its progression,
min levels for each rank should be 0, 15, 30, 45, 60."

## 1. School ranks (Insight Rank)
- **R1 Lv 1 (0), R2 Lv 15, R3 Lv 30, R4 Lv 45, R5 Lv 60.** Chapter bands: Ch2 starts ~18, Ch3 ~28, Ch4 ~40, the
  finale ~54, so R2 lands early in Ch2, R3 in Ch3, R4 in Ch4, R5 in the finale or the post-game.
- **Automatic** at level-up (user's choice 1): the player data's lvoption gives the rank's technique skill at that
  level, and a banner says "Insight Rank N: <technique>". Nobody can get stuck waiting for a teacher.
- The technique is the traveler's **own school** (Hiruma for Natsuko, Kakita for Rensei, ...), per schools.md.
- Techniques are passive skills S700-S739 (not in the battle list) that the plugin checks with hasSkill; the few
  that are commands (e.g. Mitsue R3 Vanish) are school commands.
- Sayo keeps her story choices (Ronin Ch2 R2, Ch4 R3) and picks R4/R5 the same way when she reaches the level.
- Old story narrations of a rank ("Kakita Rensei reaches Rank 2", G369, Mitsue's "Insight Rank 2") are removed or
  reworded so they don't contradict the level rule.

## 2. Dojos give kata (user: "change the dojo to give out a Kata appropriate to crab clan like Earth instead of
school rank. if you have other dojos for other members do the same. that way its still a reward.")
- Goro's Hida dojo (M164, Crab Ch2): teaches **Striking as Earth** and tells Natsuko where to go next.
- Every other path's training dojo gives one clan-appropriate kata as a reward the same way (Gendo's ridge dojo
  M317 keeps the Mirumoto Daisho Technique and adds nothing else).

## 3. Jobs (user approved the list)
- Slot 1 "Job": **Traveler** (everyone) or the traveler's personal job. Slot 2 "Trait": a trait unlocked by a job.
- **Traveler**: +5% EXP and money per job level, 0% at JLv 1 up to **+50% at JLv 10** (user: "0-50% extra exp and
  money").
- Personal jobs (MAXLV 10). Traits unlock at job levels 2 / 5 / 8 and stay learned (perma), so they can be worn in
  the Trait slot while another job is equipped:

| Traveler | Job | Traits (JLv 2 / 5 / 8) |
|---|---|---|
| Natsuko | Scout | Surprise Round (chance to act before the enemy; crit up in that round at higher JLv) / Sneak (fewer encounters) / Tracker (see enemy level and HP) |
| Rensei | Duelist | Strike First / Measure the Foe (+crit vs a lone enemy) / Ready Blade (Iaijutsu starts with 1 Focus) |
| Gendo | Magistrate | Read the Foe (one weakness shown at battle start) / Honest Eyes (resist charm, confuse) / Bounty (+money) |
| Shizue | Tactician | Vanguard (party speed up on turn 1) / Rally (+1 VP at battle start) / Banner (party ATK up while she is under 50% HP) |
| Haruki | Scholar | Learned (+max SP) / Meditation (SP regen each turn) / Ward (status resist) |
| Mitsue | Shinobi | Sneak / Light Fingers (steal up) / Ambush (surprise round; back-attack crit) |
| Tamotsu | Merchant | Haggle (shop prices -10%) / Golden Purse (+money) / Connections (hirelings +1 charge) |
| Sayo | Herbalist | Forager (items after battle) / Strong Brew (Remedy stronger) / Wave-woman (escape always works) |

- Job EXP comes from battles (enemy jxp). Scout's Surprise Round crit bonus grows with job level.

## 4. Kata and kiho (user's choice: "Bushi learn kata, Shugenja and Monks get Kiho, monks get more as that's their
skill")
- A kata or kiho is an **attack that also puts its effect on the user for X turns** (some last the whole battle).
  One active kata at a time per traveler (a new one replaces the old).
- **Learned on level-up** from the per-traveler lists in kata.md (bushi: Natsuko, Rensei, Gendo via Mirumoto,
  Shizue, Mitsue, Sayo) and kiho.md (Haruki, the shugenja). Tamotsu (courtier) learns neither.
- **Monks** (Togashi Yosai) get the most kiho, at more levels than Haruki.
- **Togashi tattoos at the school levels** (user: "the togashi should get a new tattoo at the school levels, like
  Tiger, Raven, and something at 5th"): R2 Lv 15 **Tiger**, R3 Lv 30 **Raven**, R4 Lv 45 **Centipede**, R5 Lv 60
  **Phoenix**. His existing Dragon and Arrowroot tattoos stay as the R1 set.

## 5. Battle commands (user)
- **Boost -> Void**: spending 1 / 2 / 3 VP multiplies the action's damage (or healing) **and** hit chance by
  **x2 / x3 / x5**. No more extra hits. (Done 2026-11-11.)
- **Call -> Support** (guests, hirelings, the finale's exploits). (Done 2026-11-11.)

## IDs
- Skills S700-S739 rank techniques, S740-S799 kata / kiho / tattoos. Jobs J010-J017 personal, J110-J139 traits.
  Conditions K070+ for kata effects.
