# Rules index — L5R 3e Core Book Revised (OCR)

File: `_research/books_txt/L5R - 3E - Core Book Revised.ocr.clean.txt` (line numbers below refer to the **raw**
`.ocr.txt`; the clean file has nearly identical numbering — re-grep `^RANK` to confirm). Built at the end of session 1
as a jump-table for the rules translation (DESIGN §4b–4c). ⚠ OCR typos in headers ("BRIIIANT", "TRIUMTHBEEORE").

## Advancement
- **Insight Rank thresholds** (XP-based in 3e) ≈ line 10069: Rank 2 = 50 XP, Rank 3 = 100, Rank 4 = 175,
  Rank 5 = 250 (we replace with the user's level bands: R1 1–20, R2 21–40, R3 41–50, R4 51–60, R5 61+).
- **Skill Mastery Abilities** ≈ lines 10400–11600: most skills grant a bonus at **skill rank 3 and 5** (some 7),
  e.g. Iaijutsu R3 "Focus an additional time in an Iaijutsu duel", Animal Handling R3/R5, Commerce R5 haggle 10%,
  Meditation R5 "recover 4 Void Points", Tea Ceremony R5 "recovers 2 Void Points", weapon skills R5 (spear +3
  Initiative, polearm +1k0 damage, knives no two-weapon penalty), Lockpicking R5 thirty seconds, Forgery/Poison/Traps
  R3/R5 TN increases, "You gain +2 Insight" on many. → **Use these as the skill-rank unlocks** in §4c (every 2 levels
  +1 rank; mastery bonus at ranks 3/5/7).

## School technique blocks (`^RANK n:` headers) — identified schools
| Approx. line | School (identified from technique names) | Traveler relevance |
|---|---|---|
| 13103 | **Hida Bushi** (R2 The Mountain Does Not Move, R4 Fury of Hida) | Natsuko (Hida-style); find Hiruma Scout separately |
| 13271 | Yasuki merchant (Wiles of the Carp, Treasures of the Carp) | guest/NPC |
| 13363 | Kuni shugenja? (Fire and Shadow, Veil of Spirits) — verify | — |
| 13434 | **Kakita Bushi** (R2 The Sudden Strike, R3 Strike from the Void, R4 One Strike Two Cuts) | **Rensei** |
| 13621 | Doji Courtier (R2 A Whisper from the Soul, R3 Test of Honor, R4 The Gift of the Lady) | Doji Chiyo (guest) |
| 13692 | Daidoji Yojimbo? (Wielding the Inner Fire, Shadowed Guardian) — verify | — |
| 13790 | Mirumoto Bushi? (Strong and Swift, The Blood of My Brothers, The Unrighteous Will Fall, Heart of the Dragon) — verify | Gendo's Mirumoto side |
| 13963 | **Kitsuki Investigator** (R2 Wisdom the Wind Brings, R3 Finding the Path, R4 Know the Rhythm of the Heart) | **Gendo** |
| 14287 | **Akodo Bushi** (R3 Strength of My Ancestors, R4 Triumph Before Battle, R5 Akodo's Fist?) | **Shizue** |
| 14462 | Ikoma Bard? (Brilliant Glory) | — |
| 14549 | Matsu Berserker (Matsu's Fury, The Lion's Charge, The Lion's Victory) | Matsu Kiku (guest) |
| 14641 | Yoritomo Bushi (Voice of the Storm, Strike of the Mantis, Rolling Wave, Hand of Osano-Wo) | Kaito (guest) |
| 14778 | Yoritomo Courtier (Storm Heart, Command the Winds, Will of the Storm, Strength in All Things) | — |
| 14872 | Tsuruchi Archer (The Arrow Knows the Way, Flight of No-Mind) | — |
| 14949 | Shiba Bushi (One with the Void, Move with the World) | Shiba guests |
| 15084 | Asako Henshin? (From the Ashes, Voice of the Universe, Asako's Enlightenment) | — |
| 15359 | Bayushi Bushi (Strike at the Tail, Strike from Above Strike from Below) | Bayushi Hideki (guest) |
| 15463 | Bayushi Courtier (R1 Weakness Is My Strength, R2 Shallow Waters, R3 Secrets Are Birthmarks) | Mitsue alt |
| 15576 | **Shosuro Infiltrator** (R2 The Shadow Has No Mercy, R3 No Form, R4 No Substance) | **Mitsue** |
| 16191 | Unicorn bushi? (With Heaven's Speed, The Sun's Light Reveals) — verify (Shinjo/Utaku) | — |
| 16293 / 16385 | Imperial schools (Destiny Has No Secrets…; Eyes/Hand/Glory of the Emperor — Seppun/Otomo?) | year-400 NPCs |
| 16461+ | Minor clans (Hare, Tortoise, Toku's ronin, …) and ronin paths (Way of Sacrifice, To Master the Game…) | **Sayo** (ronin options), minor-clan NPCs |

**Not yet located:** Hiruma Scout (Natsuko), Isawa Shugenja (Haruki; shugenja schools usually have one technique +
spell affinities — check the shugenja chapter), **Ide Emissary** (Tamotsu; line 9636 mentions it — technique block
probably near the Unicorn section, mixed-case "Rank1:" headers), Iuchi. Grep mixed-case `^Rank\s?1` and school names.

## Next steps (session 2)
1. Extract full R1–R5 text for the 8 travelers' schools into `docs/rules/schools.md` (verify against page images).
2. Pull spell lists by element from *Masters of Magic* OCR for Haruki; kata/kiho from Books of Earth/Fire/Water/Air/Void.
3. Turn each school's R1–R5 into the traveler's Talent upgrades at levels 1/21/41/51/61 (DESIGN §4c).
