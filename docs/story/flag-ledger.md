# Flag Ledger

Result of the consistency pass (session 3). Checked by a script that reads every `[SET]`, `[IF]`, header flag list and
`[BATTLE]` id in `story/production/` and `story/sidestories/`, and checks battle ids against `rules/bosses.md`.

**Totals:** 38 files · 138 flags set · 134 flags read · 144 battle ids, all covered by bosses.md.

## 1. Fixes made in this pass
| Problem | Fix |
|---|---|
| Lion Ch4 read `hiruto_backing`, which no chapter sets | Changed to `toturi_knows_name` (set in Lion Ch2) |
| Finale title card said the Rooster "begins tomorrow" | "*The fourteenth day of the Rooster is coming.*" |
| Finale header listed `history_final` and `box_destroyed` but the body never used them | Gendo's coda (the darker-1123 vision on the "saviour" route) · Mitsue's debate rebuttal |
| `history_final = history` was a placeholder | `"erased"` if `glory_refused`, else `"saviour"` |
| Dragon Ch4 promised "an epilogue vision of a darker 1123" when Gendo accepts | Written into his E01 coda |
| Crane Ch4 promised "finale debuffs halved" when the play is handed over | F09 phase 3 rule |
| Phoenix Ch1 crate lid was promised to matter "in the Lion/Crane politics later" | Lion Ch4 S07 truce scene → `three_clan_truce` → finale shrine defence buff |
| SS-TEAM and Benjiro SS2 promised finale montage cameos but set no flag | `inquisitors_hunt_done`, `benjiro_father_home` |
| `mieko_answer` had no values | `"yet"` / `"eight"` |
| Many cross-chapter flags were never paid off | The F10 montage and E01 codas now check them (list in the finale header) |

## 2. Flags read but never set (by design)
These aren't real story flags, so the checker's warnings can be ignored:
- **Party checks** (`*_in_party`, plain names such as `rensei`, `daigo`, `haruki`): the engine checks who is in the party at runtime.
- **Flag values** (`honest`, `heir`, `good`, `kept`, `cliff`, `both`, `strong`, `passed`, `lose`, `book`, `swap`,
  `command`, `healer`, `gives`, `barrel`, `gunpowder`, `curse`, `pilgrims`, `phoenix`, `crane`): these are the right-hand
  side of a check like `[IF settlement heir]`.

## 3. Flags set but never read (chapter-local, by design)
Each of these is a record of a choice or a tally. It affects that chapter's dialogue, its reward, or its journal text,
and nothing later. They become variables in the engine, so a later payoff can be added cheaply.

**Tallies (read as `[per x]` or a reward tier inside the chapter):** `dream_keys`, `echoes_blessed`, `fronts_won`,
`crawl_results`, `clues_found`, `cases_done`, `rumours_found`, `masks_got`, `bracket_result`.

**Choice records (journal / chapter-complete card only):** `accusation`, `camp_split`, `city_sealed`, `dinner`,
`duelist_spared`, `ebisu_saved_how`, `giseiki_mask_held`, `gochu_family_fed`, `governor_fake`, `gusai_held`,
`hikaru_spoke`, `hut_burned`, `jumped_first`, `kage_fought`, `katsuo_alive`, `kumpei_accused`,
`memory_ritual_refused`, `message_route`, `mirumoto_school`, `oharu_poisoned`, `painting_answer`, `puppet_spared`,
`quarry_left`, `retainers_spared`, `riichi_trusts`, `ronin_school_first`, `seoko_charmed`, `shrine_broken`,
`shrine_spirit_blessed`, `sick_treated`, `truce_bought`, `uji_won_by`, `vial_saved`, `well_cleansed`, `writ_pilfered`.

**Item-backed (the item carries the effect, see `rules/equipment.md`):** `seppun_tanto_taken`.

### Candidates for later payoffs (optional)
If there's room for polish later, these would make good extra finale montage shots:
- `katsuo_alive`: Katsuo among the Crane scouts.
- `well_cleansed` and `sick_treated`: villagers bringing water to the shrine.
- `puppet_spared`: the Crab Ch2 puppet, now a goblin-scarer at Kyuden Hida.
- `retainers_spared`: the Ronin Ch2 retainers, who are now ronin themselves, holding a path.

## 4. Known limits of the checker
- Flags inside `[per x]` or plain-text conditions such as "if present" aren't parsed.
- Numeric conditions (`≥ 1`) are only checked by name.
- Run it with: `python -E tools/consistency.py docs`
