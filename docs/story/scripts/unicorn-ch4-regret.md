# Script — Unicorn Ch4 · "Regret" — DRAFT v0.1

**Source:** *Fortune's Lost* Part III, ending (Brandes & Hepler, 1999).
- **Softened:** the "stairs of possessed people" become possessed servants frozen on the stairs, who are freed
  when the demon falls.
- **Changed (02-travelers softening):** banishing the Shuten Doji frees its surviving hosts.

Plot facts only; **all dialogue is original**.
**Traveler:** Ide Tamotsu · Rank 3, Lv 41–45 · **summer 1123** · Shiro Iuchi, the triangular castle in its wind
tunnel.
**Octopath shape:** the siege camp (hub) → the wind-tunnel approach → the castle (dungeon) → boss → the brokered
peace.
- **Gimmick:** the **Wail**: in the boss fight, any traveler *without* Covered Ears may be possessed.
- **Choices:** 2.
- **Flags used:** `naohida_named` (Ch1), `nihime_told` (Ch2).

---

## Scene 1 — "Three Thousand Deaf Dragons"
**Beat:** The Mirumoto army (wax in its ears) and the Iuchi survivors surround **Shiro Iuchi**: triangular, built
into a wind tunnel, entrance facing north, storm-wracked. Inside: old **Iuchi Kurosho** and the **Shuten Doji of
Regret**. Naohida arrives under a flag of truce.
- `naohida_named` = true: the Iuchi want him arrested. Tamotsu must **Barter** for one day's truce.
- `naohida_named` = false: Naohida trusts Tamotsu at once.
NAOHIDA: He's my father. Kurosho. *(beat)* I made gunpowder to hurt him. I'll walk in there to save him. I don't
understand myself either.
TAMOTSU: Good. Understanding yourself is overrated. Bring a jade knife.
- **Guest: Naohida** (gaidao; *Powder Charge*, 1 use).

## Scene 2 — "The Wind Tunnel" (dungeon approach)
**Beat:** Gale-force winds through the canyon. Pigeons in the cliffs carry the demon's whispers. Covered Ears is on
(no spoken path actions).
- `[BATTLE]` Possessed Emerald Legion soldiers, chanting a dead woman's name over and over (weak to **Jade**,
  **Yari**).

## Scene 3 — "The Stairs" (castle dungeon)
**Beat:** The castle's great stair: possessed servants frozen kneeling across every step, humming. The party must go
around them through the servants' passages. Karasu's quiet: "Don't step on them. They'll remember it when they wake."
- **Iuchi Shahai**'s secret (softened from the source): the demon *marked* her. As they climb, she hums the same tune.
`[CHOICE 1]` *Send Shahai back with Daiyu* (safe; the mark worsens) · *keep her close* (she is the key: at the boss,
her voice can be used against the demon, but it is risky).

## Scene 4 — BOSS: "Kurosho and Regret"
**Beat:** In the storm-room at the top: **Iuchi Kurosho**, the kanji for Void burned into his skull. Behind him, the
**Shuten Doji of Regret**: a shape made of every apology no one ever made.
`[BATTLE]` **Kurosho (possessed) + the Shuten Doji of Regret**:
- **Gimmick: the Wail.** Every 3 turns, the Doji wails. Any traveler **without Covered Ears** (wax removed: you
  need it off to use spoken skills such as Charm-type and Command shouts) must resist or be **possessed** for 2
  turns (they attack allies). Covered Ears blocks it, but also disables "voice" skills. The fight is a constant
  trade-off.
- Doji: Resolve 18. Weak: **Jade** (the mine jade), **Water**, **Void**. Kurosho: Resolve 10. Weak: **Air**, **Bo**.
- **Soshi Nihime's curse** (`nihime_told` = true: she's here; false: she sends it in a letter) wakes Kurosho for
  **one breath**: his Resolve drops to 0 once, a free Suki.
- If Shahai is present (Choice 1), her humming can be *inverted* (an item: Karasu's tuning fork) to stun the Doji
  for a turn.
KUROSHO *(awake, for one breath)*: Nihime? *(beat)* I'm sorry. I'm so sorry. I should have—
THE SHUTEN DOJI: *(through him)* Yes. Say it again. *Again*.
TAMOTSU: *(Barter Coin: Settle the Account)* He's paid enough. *(throwing gold into the storm)* Here: take
mine instead, and *get out*.

## Scene 5 — "Brokered" (ending)
**Beat:** Regret is banished. Its surviving hosts wake, dazed, freed (the softening). Kurosho dies in Nihime's arms
(or alone, if she wasn't told), at peace.
`[CHOICE 2]` Tamotsu's settlement:
- *Acknowledge Naohida as heir of both blood-lines*: Iuchi through Kurosho, Soshi through Nihime. A bridge between
  the two shattered houses (canonical; Compassion).
- *A plain treaty between the houses*: safer politically, but Naohida stays nameless.
- Then Tamotsu walks a refugee caravan home through the valleys, Persimmon biting everyone who tries to help.
IUCHI DAIYU: *(to a woodchuck at the roadside)* He fixed it. The fat merchant fixed it.
IUCHI KARASU: *(deadpan)* Emissary.
IUCHI DAIYU: The fat *emissary* fixed it.
→ **Finale.**
`[SYS]` **Rewards:**
- Lv ~45.
- Naohida (guest: a finale callback).
- Karasu's tuning fork.
- *The Immovable Hand of Peace* (R5) foreshadowed: Tamotsu's peace-lock skill appears in the finale's last phase.
