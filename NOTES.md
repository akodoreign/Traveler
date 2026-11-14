# Rokugan Traveler — Working Notes

Fan-made, **never-for-profit** Octopath Traveler–style RPG set in Legend of the Five Rings' Rokugan, built with
RPG-Cobo. L5R © Fantasy Flight Games; Octopath Traveler © Square Enix (inspiration only).

**Read this file first every session.** Then read the memory index, then `docs/story/00-synthesis.md`.

---

## ▶ RESUME POINT (2026-10-29, latest; details in the dated log at the end)
**Crab path (Ch1-4): done. Crane path (Ch1-4): done. Lion path (Ch1-4): done. Phoenix Ch1: done. Togashi Yosai on every path: done. Phoenix path (Ch1-4): done. Dragon Ch1-3: done (2026-10-30). Soundtrack v1 (Japanese, generated): done, needs the user's ears. Dragon path (Ch1-4): done (2026-10-30). Scorpion path (Ch1-4): done (2026-10-31; Ch3 from Mitsue's view). Battle music: light rock + biwa (user liked it; check the faster tempo). Arrowroot capped at 50% max HP (user). Unicorn Ch1: done (2026-10-31). Unicorn Ch2 (Tamotsu's view of Fortunes Lost): done. Unicorn Ch3 "The Noblest Blood": done. Unicorn Ch4 "Regret": done (2026-10-31). The Unicorn path (Ch1-4) is complete. Ronin Ch1 "What's Eating the Eta": done (2026-10-31). Ronin Ch2 "The Noble and the Ronin": done (2026-11-01). Ronin Ch3 "The Village of the Wounded Lion": done (2026-11-01). Ronin Ch4 "The Oracle's Choice": done (2026-11-02). The Ronin path (Ch1-4) is complete: all eight paths are built. The finale: Slices A-E built and tested (A-D 2026-11-04; E, the flight, her death, the eight codas, the final image and the post-game return, 2026-11-05). THE GAME CAN BE PLAYED TO THE END. The post-game P1-P3 are built (P4 the teachers left). The user is now PLAYING the alpha and reporting bugs: see "START HERE after Saturday" at the end of the log.** (see "Now:" below).
Every chapter was verified slice by slice in-engine; none has been played as one continuous run. The sections below
("Open for Crane Ch2" etc.) are kept as history.
**Rebuild with `python -E tools/regen.py [--maps]`** (gen_maps, gen_data, gen_render LAST).

**Open for Crane Ch2:**
1. ~~The chain~~ Every link was run in-engine, and a static check confirms every portal in map.json resolves to a
   real event (0 problems).
2. ~~Boss art~~ DONE: redesigned with Miyako looming as an untargetable watcher and the generals as regular
   sprites (see the log).
3. Waiting on other travelers:
   - path actions in the port: the tea-house Duel, the dock porter's Pilfer, the sailor's Sumai;
   - Miyako / Miyubi blanking Discern and Eavesdrop (rule N-1);
   - the TB-crossroads1 banter (needs Natsuko).
   The Yasuki "+10% sell" isn't built (it would need an engine shop override).
4. Rank system: only a flag (G369) and narration so far.
5. **Defaults the user may overrule:** Goro is a short-term companion during the chapter, then a guest; Rank 2 is
   flag-only.

**Now:** Crane Ch3 "The White Squid" (Lv 30-35), **slice A in progress** (see "Crane Ch3 slice A (part 1)" at the
end of the log for what is done and the exact next steps).
**Crane Ch3 progress:** **built end to end, slices A-H, every scene and fight run in-engine** (see "Crane Ch3
slices" at the end of the log). Not yet played as one continuous run. Open: the path actions that wait for other
travelers; the travel banter (TB-crane3-a needs Natsuko, TB-crane3-b needs Shizue).
**Crane Ch4 "The Play No One Performs": built end to end too** (2026-10-29; see "Crane Ch4" at the end of the log).
**The Crane path (Ch1-Ch4) is complete.** The finale (Nashiko; reads play_known_scenes G421, rehearsal_quality
G427, play_handed_over G429) is the shared ending, not part of the path.
**Now: the Lion path (Akodo Shizue).** Lion Ch1 "The Blood of Family" and **Lion Ch2 "Shadow of a Doubt" are built
end to end** (2026-10-29; every scene, both Ch2 epilogues and every fight run in-engine; see "Lion Ch2" at the end of
the log). **Lion Ch3 "The Deadly Message" is built end to end too** (2026-10-29; both routes, every scene and fight
run in-engine; see "Lion Ch3" at the end of the log). **Next: Lion Ch4** (`docs/story/production/lion-ch4.md`, its
storyboard, script and bosses.md rows). **Lion Ch4 "Sorrow's Path": built end to end** (2026-10-30; see "Lion
Ch4" at the end of the log). **The Lion path (Ch1-Ch4) is complete.** Next: pick the next path (one at a time) and
read its sources in full first.
**Phoenix path started (2026-10-30): Phoenix Ch1 "The Silent Kami" is built end to end** (see "Phoenix Ch1" at the
end of the log). **User directions the same day (memory files):** shugenja never travel alone (a yojimbo companion,
lean on spells); Togashi Yosai as an optional companion on every path until the join-up, with regeneration, never
serious; Ide Tamotsu is a non-combat buffing diplomat with a Shinjo guardian companion.

## ▶ RESUME POINT (2026-10-20, long session; the user's meter was ~70%+ near the end)
**State:** Crab Ch1 is complete and verified. Crab Ch2 "Winter Court at Kyuden Hida" is built end to end, plus
this session's extras. Only Natsuko is playable (memory solo-with-companions). Details are in the dated log
entries at the end of this file.

**This session, in order:**
1. **Art.**
   - Arm/weapon pass, legs pass, faces/necks pass (short neck stub).
   - Shoulders lowered and sloped (no shrug).
   - Side-view heads in profile, facing where the feet point (user correction: not "looking down").
   - Nezumi in the Splinter style; a campfire for the river camp.
2. **Stats.**
   - Per-traveler growth: `tools/traits.py` reads the stats.md trait schedules.
   - Clan battle roles (memory clan-battle-roles):
     - Crab most HP; Lion hardest hitter.
     - Mirumoto double strike; shugenja +1 VP.
     - Crane and Scorpion fastest; Scorpion denial.
   - Spell and heal formulas scale with MATK.
3. **Crab Ch2.**
   - Built and verified:
     - all hub talk pages (`tools/runevent.py`);
     - boss barks;
     - the Unicorn Dance Ribbon return (Keiyomi → O-Shito, Honor +1);
     - Mutsuye's repeat line and family-name-first labels fixed.
   - The battle AI attacks the puppet once the troll proves immune and throws Jade.
4. **Water + invisible walls** (user: "falling through the floor... water tiles").
   - RokuganMapGen gives water a solid bed. Open water is walled off with the engine's barrier bitmap.
   - Followers snap only onto real floor. The player has a fall-rescue safety net.
5. **Guests.**
   - Octopath II "Call Guest": battle command slot 7 "Guest", replacing Formation.
   - Four Crab Ch2 guest side stories with "?" icon sprites: Kitsu Takeo, Yogo Mai, Ide Fujio, Daidoji Sakura.
     All verified in-engine.

**Test tooling added this session** (all no-keys):
- `tools/runevent.py MAP ID PAGE [--vars] [--choice] [--lv N] [--party P123]` and `--list MAP`.
  `--lv` drives `-debuglv`, which sets the party's level.
- Game flags (plugin RokuganField / RokuganAI):
  - `-rtwalk cdir,ms[,delay[,jump]]` holds the stick and logs positions.
  - `-rtparty P123,...` adds companions at the leader's level.
  - `-rtlv N`.
  - `-rtguest`: auto battle calls the current guest.
- **Gotcha:** `-debuglv N` sets the party's level *after* launch hooks, so `-rtlv` loses to it.

**NEXT (in order):**
1. ~~Trees blocking the view~~ DONE (it was in combat, not the field):
   - gen_maps `clear_arena()` runs on every M8xx backdrop: no trees at z 40-75 (between the battle camera and the
     road behind the fighters at z 64), no rocks in the arena box x 40-90 / z 46-74.
   - The Hida road backdrop's tree row moved behind the road (z 80-87).
   - New `tools/snapbattles.py [gid ...]` screenshots one battle per backdrop into
     _art/preview/battle_backdrops.png. All 8 backdrops in use are clear.
2. ~~Scandalous Letter~~ DONE: K025 is no longer `uncommandable` (in RPG-Cobo that means "acts on its own",
   i.e. confused, so it hit its ally). RokuganBattle `onSkillChange` swaps a Scandalized enemy's action for S000
   Wait (pop "Scandalized!"), like Suki. Verified: the target loses its action on turns 1 and 2.
3. ~~Crab Ch3 "Beyond the Wall"~~ BUILT and verified end to end (2026-10-21; details in the log entry at the end).
   Open: Squeak's field skill *Dark-ways* (chests show on the map) isn't implemented. The Kaiu Tetsubo Blueprint
   trade-in isn't either. Balance is set for Natsuko + 1 companion (see CH3_LV_SHIFT).
4. Travel Banter needs 2+ travelers in the party, so it waits for the first crossover. The guest SS2s come in
   later chapters.
5. Mitsue's Misdirection, Vanish and Mask Change (plugin mechanics) when her chapter is built. Other travelers'
   path actions in the court (Kuhime blanks Discern/Eavesdrop).
6. ~~Crab Ch4~~ BUILT (2026-10-21; log entry at the end). The Crab path (Ch1-Ch4) is complete.
   Next: decide with the user which traveler's Ch1 comes next, or the finale prerequisites.

## (older) ▶ RESUME POINT (session 3, later): DESIGN DOCS ARE COMPLETE. NEXT IS THE ENGINE OR THE ART.
- Done: all story, dialogue, side stories, boss sheets, plus:
  - ✅ `docs/rules/bestiary.md`: every regular foe.
    - Human foes A1–A7: bandits, ronin, contentious samurai, ashigaru, pirates, cultists, ninja.
    - Beasts B1–B5: wolves, snakes, bears and boars, birds and insects, sea creatures.
    - Also: the Shadowlands (C), spirits and the dead (D), the past (E).
    - Tiers I–V, regional encounter tables (F), and non-violent exits (surrender, bribe, scare off, Bless, talk-down).
  - ✅ `docs/rules/equipment.md`: shop tiers T1–T5 for the 6 weapon types, named weapons, armour, accessories,
    consumables, key items and sell items, and shops by region.
  - ✅ The consistency pass: `docs/story/flag-ledger.md` records the fixes and which flags are chapter-local.
    The checker is `tools/consistency.py`; run it with `python -E tools/consistency.py docs`.
    - The finale's F10 montage and E01 codas now check about 35 cross-chapter flags.
    - New flags: `three_clan_truce` (Lion Ch4, from the Phoenix Ch1 crate lid), `inquisitors_hunt_done`,
      `benjiro_father_home`.
- **NOW (session 3, latest): STORYBOARD PASS** (user: "go chapter by chapter and do a branching storyboard… imagine
  going to each of the locations in Octopath style… you have rokugan maps"; "you don't have to tell me all the
  results, just simulate it").
  - Folder: `docs/story/storyboards/`. README = legend, Octopath map conventions, overworld (built from the user's
    two maps: *Emerald Empire* p.14 and the Mahn political map), recruit rule R-1, guest rule G-1, findings log.
  - Each chapter file: a mermaid flow, ASCII maps with placements (NPCs, path actions, shops, chests, `*` prompts,
    saves), a simulated playthrough, and findings. **Fixes go straight into `production/`**, `bestiary.md`,
    `bosses.md` and `equipment.md` §H (the new-items list).
  - ✅ **STORYBOARD PASS COMPLETE (session 3):** all 32 chapter storyboards + README (33 files). Every Ch1 has a
    RECRUIT VARIANT block. Consistency check clean (148 battles; the remaining "read but never set" entries are flag
    values, party checks, or chapter-progress checks).
  - Big structural fixes (see storyboards README §6):
    - R-1 recruit Join points; G-1 one active guest, with story-locked guests and story companions.
    - P-1 the Lion/Phoenix Ch1 pair rule; C-1 the co-owned Unicorn Ch2 / Scorpion Ch3 rule (the second view is a
      flashback with locked choices).
    - D-1 the Ink Door (Dragon Ch2–4); Y-1 the Yosai gate (Tamori Haku stands in for Scorpion Ch4).
    - §3c non-fatal Duels and fronts; S-1 a save before every boss; T-1 path-action coverage in every town.
    - Finale: the `thunder_plain_road` level bridge (50–56); the post-game clear-save rule.
  - Blockers fixed: Scorpion Ch1 boss (Crystal Shards in the marsh); Unicorn Ch1 Case 1 (Status instead of Discern);
    Lion Ch3/Ch4 "Interrogate" misused as a path action; Phoenix Ch1 Jade Chains were optional; Crane Ch4 `duel_won`
    was set on a loss; Ronin Ch4's Hiro beat was gated on a later side story.
  - New items are in `equipment.md` §H; new mobs and areas in bestiary F (Fear Shade, Singing Servant, Stitched-face
    Monk, Blood Leech, Ink-pot/Lantern Spirits; several region rows); new battles `b_siege_breach_a/b`,
    `b_lion_checkpoint`.
  - **For every remaining Ch1:** add the RECRUIT VARIANT block (Join point + Memory), as in crab-ch1 / crane-ch1.
- ✅ **ENGINE STARTED (session 3, user: "start messing with the engine… procedurally generate anything you need"):**
  see **`docs/ENGINE.md`**. Template installed; battle plugin `plugin/rokugan` (Suki + Void Points + Boost) written and
  **verified in a test battle**; procedural art: 8 traveler models (clan recolours) + 6 Crab Ch1 enemy sprites;
  data generator `tools/gen_data.py`; `.mcp.json` registers the engine MCP (next session; editor must be open).
  **Next:** ENGINE.md §5 (turn-order bar, talents, Rumble meter, then the Crab Ch1 vertical slice).
- **Rule:** after editing any production file, re-run the checker.

## (older) RESUME POINT (end of session 2, user hit 90%)
- **Current task:** the production dialogue pass (work item 1 of 3; the user wants all dialogue done before side
  stories and boss sheets).
- **Done:** 21 production files in `docs/story/production/`:
  - all 8 Ch1s
  - all 8 Ch2s (the unicorn-ch2-scorpion-ch3 file covers Scorpion Ch3)
  - Ch3: crab, crane, dragon, lion, phoenix
- **Update (session 3):** all chapter production files + the finale are DONE. Next:
  4. work item 2: guest side stories (27 guests × 2 stories; `story/04` B3)
  5. then work item 3: `docs/rules/bosses.md` stat sheets for every `b_*` battle id used in production files
- **Format:** `production/README.md`, and copy the style of any finished file (e.g. `phoenix-ch3.md`).
  - Keep: original dialogue only; voices per README; ASCII terms (Bo, Suki, VP).
  - Keep: ≤2 choices per chapter, one gimmick, fake choices allowed.
  - Each file ends with a chapter-complete card and 2 Travel Banters.
- **Flags:** each production header lists flags read and set. Later chapters must read the right ones. Key
  cross-chapter flags:
  - Crab: `nezumi_friends`, `oni_named_ryozo`, `guard_rescued`, `blue_flare_held`
  - Crane: `depura_seen`, `same_woman_proven`, `tadanobu_letters`
  - Lion: `atsuko_promise`, `shogen_joined`, `yachiko_letters`
  - Phoenix: `consumer_scroll_kept`, `showed_scroll`, `mieko_midnight_seen`
  - Dragon: `tsuhime_helped`, `history`
  - Unicorn: `naohida_named`, `nihime_told`, `camps_fed`
  - Ronin: `sono_link`
  - Scorpion: `mitsue_knows_shoju_war`, `mitsue_wore_giseiki`, `iron_box_held`

## HANDOFF — current state (session 2, 2026-10-16)

**Phase:** story bible + rules translation. Both are at a detailed draft, waiting on the user's review: start with
`docs/rules/README.md` and the open questions below. Engine work has not started.

**Done:**
- Every adventure in `Adventures In Rokugan/` read (most in full) → one research note each in `docs/research/` (14 files).
- Story bible v0.1–0.2 in `docs/story/`:
  - `00-synthesis.md` — era, recurring threads, user decisions, canon-event arc options (§5b)
  - `01-world-and-timeline.md` — winter 1122 → summer 1123, **canon dates verified**, regions, antagonist layers, tone
  - `02-travelers.md` — 8 travelers × 4 chapters, talents, path actions, finale virtues, **Rank 1 / low-status rules**
  - `03-crossroads-and-finale.md` — 4 crossroads chapters + 4-act finale "The Empress of Nothing" + epilogue
  - `04-supporting-cast-and-hireables.md` (v0.2) — Octopath II–style guests, followers, hired help; per-traveler casts;
    25 guests (pregens renamed; mapping §B4)
- `docs/DESIGN.md` — mechanics mapping (§2), L5R→Octopath rules translation draft (§4b), **Rank↔level bands and per-level
  gains (§4c)**, technical plan (§5), milestones (§6).
- All 31 Drive sourcebooks downloaded and text-extracted (see Sources).

**OCR — DONE:** all 4 scanned books (874 pages) → `_research/books_txt/*.ocr.txt` (raw) and **`*.ocr.clean.txt`
(use these)**: re-spaced with `wordninja` (long runs + short lowercase runs; L5R terms protected; hyphenated line
breaks rejoined). Readable for research, but some joined words/OCR slips remain ("Atthedawnof", "touma ment") →
**verify exact numbers against the page image** before using them in rules. Books: 3e Core Book Revised (340 pp),
Masters of Magic (162), The Four Winds (194), The Vacant Throne (178).
Re-run (only if ever needed; resumes via `[[PAGE` markers):
  `python -E <scratchpad>/ocr_books.py "D:\RokuganTraveler\_sources\drive" "D:\RokuganTraveler\_research\books_txt" "L5R - 3E - Core Book Revised.pdf" "L5R - 3E - Masters of Magic.pdf" "L5R - 3E - The Four Winds.pdf" "L5R - 3E - The Vacant Throne.pdf"`
  (The scratchpad is session-specific — if gone, rewrite the script: render each page at 170 dpi with `pymupdf`,
  OCR with `rapidocr_onnxruntime.RapidOCR()`, find the column gutter as the widest box-free vertical strip between 30%
  and 70% of page width (ignore boxes wider than 60% = headers), output full-width lines, then left column, then right
  column, each sorted by y; append `[[PAGE n]]` per page so reruns resume.)

**Rules work started (end of session 1):** `docs/research/rules-index-3e-core.md` — jump table into the OCR'd 3e
Core: Insight XP thresholds, **skill mastery abilities at skill ranks 3/5(/7)** (→ use as the skill-rank unlocks in
DESIGN §4c), and line numbers of each school's technique block (Kakita, Kitsuki, Akodo, Shosuro located; Hiruma Scout,
Isawa, Ide Emissary still to find). Start session 2 there.

**Schools extracted:** `docs/rules/schools.md` — all 8 travelers' 3e schools (Hiruma Scout, Kakita Bushi, Kitsuki
Courtier [+Mirumoto secondary at R2], Akodo Bushi, Isawa Shugenja [single technique → spell tiers per Rank], Shosuro
Shinobi, Ide Emissary, Ronin Warrior/Duelist/Yojimbo **mix-and-match** for Sayo) with R1–R5 → Octopath translation
at Lv 1/21/41/51/61. Changed Natsuko to an **evasion tank** (talent "Razor's Edge") to match canon Hiruma techniques.

**Spell & kata index:** `docs/rules/spell-and-kata-index-3e-core.md` — **complete list of 143 core spells** by element
× Mastery Level (cross-checked against the book's own index; all "name lost" entries recovered), plus the *Masters of
Magic* spells (only 16: 6 multi-element + 10 Phoenix First Tier secrets).

**Session 2 rules work (2026-10-16, after the user's reset):**
- `docs/rules/kata.md` — the **Kata Stance system**: 1 slot, set at inns or camps; a free toggle in battle; VP
  "Void clause" on first activation; melee only; Striking as Void = 3 slots.
  - A **3e→Octopath conversion table** (TN ±5 = Evasion ±10%, etc.); **reuse it for all future rules work.**
  - Per-traveler kata with level unlocks: Natsuko, Rensei, Gendo (from Lv 21 via Mirumoto), Shizue, Mitsue, and Sayo
    (all 5 common kata — her niche).
  - Haruki and Tamotsu get no kata. Kata out of the travelers' reach are assigned to guests and enemies.
- `docs/rules/kiho.md` — 49 core kiho indexed. In 3e only monks and shugenja may learn kiho.
  - **Haruki: up to 5**, as Brotherhood story rewards (Self No Self recommended first).
  - Martial and atemi kiho → enemy kit for Kokujin's tattooed cultists and Togashi Akuro.
  - Open question: should a monk guest be added (Jinnai?).
- `docs/rules/haruki-spells.md` — the full spell → skill design:
  - SP by Mastery Level; Special Raises = Boost.
  - **Kami Weapons**: Haruki can break Yari/Tetsubo/Katana/Bo shields, and the Yumi via *Yumi of the Void*.
  - **Concentration** spells; Harmony (multi-element) skills; field spells come from scrolls.
  - Starting kit, per-element tables, recommended pick curve.
  - Proposed **Water Affinity**, with Void latent (unlocks at R3, in line with Ch3).

**Also drafted in session 2:**
- `stats.md`:
  - Family and school trait bonuses (from the OCR).
  - Trait→stat mapping and formulas.
  - Lv 1 traits plus a per-level **trait schedule** for each traveler. The schedules are verified by
    `scratchpad/traits.py`, and every kata/kiho ring gate passes.
- `skills.md`:
  - **Skill cap per Rank (3/5/7/9/10)**, aligned with the 3e mastery tiers.
  - Path actions are gated by skills (Duel→Iaijutsu, Sumai→Jiujutsu, Charm→Etiquette, Bless→Theology,
    Discern→Investigation, Eavesdrop→Stealth, Barter→Commerce, Pilfer→Sleight of Hand). Low Skills cost Honor.
  - Skill lists per traveler and mastery effects.
- `weapons.md`: 3e DR → power and traits; arrow types → Yumi shot skills; Light/Heavy armour tags.
- `battle-skills.md`: 3e maneuvers as universal skills, plus 6–7 signature skills per traveler, gated by skill rank.
- `schools.md`: Sayo's three ronin trees translated (Warrior / Duelist / Yojimbo).

## NEXT (in order)
1. Rules translation, remaining:
   - (a) ✅ The ⚠ OCR entries are checked against the page images, using
     `scratchpad/render_page.py <pdf> <ocr.txt> <line> <outdir> [full|top|bottom|left|right] [dpi]`. It finds the
     `[[PAGE n]]` marker before a line, renders that page, and the PNG can then be read. Corrections were made to
     My Brother's Soul, Death of Flame, Heart of Stone, Parting the Waves and Shosuro R4/R5. (A future engine step
     should check numbers the same way.)
   - (b) ✅ `sayo-remedy.md`: base + catalyst concoctions from setting herbs.
   - (c) ✅ Tamotsu got 5 more signature skills (battle-skills.md).
   - (d) ✅ `enemies.md`: Suki rules; 13 enemy families with L5R weaknesses; crystal and obsidian as *material*
     weaknesses hit by items; statuses (Terror/Shaken/Taint); boss rules.
   - (e) Equipment list (nemuranai, named blades). **Not started.**
   - ✅ **`docs/rules/README.md`** is a one-page overview of the whole system plus the 8 decisions for the user to
     approve. **Show it to the user.**
2. ✅ **Weak chapters expanded to scene level** → `docs/story/05-chapter-outlines.md`: Lion Ch3–4, Phoenix Ch1 and
   **Ch3 (rewritten as "The Darkfever")**, Ronin Ch2 and Ch4, Crane Ch4, Scorpion Ch4. Each scene lists the systems
   it uses.
   - Canon anchors: the Darkfever oni = **Oni no Kuzushi**, freed by an eclipse from a forgotten Isawa forest estate;
     the Oracle of Fire's eta successor (the Scorpion foiled "by travelling samurai"); Shoju's visit to Togashi.
   - Story additions:
     - The Darkfever estate is Mieko's family house, and Haruki's childhood Void cracked its seal.
     - The Sorrow's Path battle in Lion Ch4 ties to the Crane banner from Ch2.
     - Mitsue overhears Togashi's answer in Ch4.
     - Crane Ch4: the forbidden play becomes a key item that reveals Nashiko's shields in the finale.
   - ✅ **Template scene script written:** `docs/story/scripts/lion-ch2-shadow-of-a-doubt.md`. It has 11 scenes,
     original sample dialogue, `[CHOICE]/[BATTLE]/[FLAG]/[SYS]` markup and the format notes at the end.
     ✅ **Format approved by the user.**
   - ✅ **All 8 Chapter 1 scripts written** (`docs/story/scripts/`):
     - crab-ch1-eggs-and-shadows · crane-ch1-heavens-glory · dragon-ch1-under-the-skin
     - lion-ch1-the-blood-of-family + phoenix-ch1-the-silent-kami (they share the O-Tamai climax)
     - scorpion-ch1-blood-and-iron · unicorn-ch1-fault-lines · ronin-ch1-whats-eating-the-eta
     - Each Ch1 introduces its traveler's Talent and path action and seeds flags for later chapters (e.g.
       `oni_named_ryozo`, `depura_seen`, `yachiko_suspected`, `naohida_named`, `sono_link`).
   - ✅ User: "story-wise it looks good; fit it to Octopath mechanics" → **`docs/OCTOPATH-FIT.md`**. It covers:
     - the Octopath skeleton we adopt, and the deviations
     - an audit of every written script, with the conversions needed
     - the gimmick budget: **1 battle gimmick OR 1 field set-piece per chapter; max 2 choices; same boss on every
       route**
     - the world map and recruitment order, and engine notes
     **All new scripts must follow it.**
   - ✅ **Crossroads = shared chapters** (each owned by one traveler; partner bonus; NPC stand-in;
     OCTOPATH-FIT §2, story/03). Scripts written in the new shape:
     - `crane-ch2-the-iron-cranes` (+Natsuko / Hiruma Goro)
     - `unicorn-ch2-scorpion-ch3-fortunes-lost` (co-owned; Akodo Rin is the stalker's royal-blood target)
     - `scorpion-ch4-the-eve` (+Gendo / Togashi Yosai)
     - The Lion/Phoenix crossroads is their shared Ch1 (already written).
   - ✅ **All 8 Ch2s scripted:**
     - crab-ch2-winter-court-at-kyuden-hida · crane-ch2-the-iron-cranes · dragon-ch2-the-painting
     - lion-ch2 (the template) · phoenix-ch2-the-silent-court · scorpion-ch2-city-of-masks
     - unicorn-ch2 (= scorpion-ch3, shared) · ronin-ch2-the-noble-and-the-ronin
     - Each follows OCTOPATH-FIT (1 gimmick or set-piece, ≤2 choices). Notable:
       - Dragon Ch2 takes Gendo into the year 400; the Mirumoto secondary school unlocks; Yosai is "lost in the
         ink" until Ch4.
       - Phoenix Ch2's torii debate rehearses the finale's debate.
       - Scorpion Ch2 uses the mask gate.
   - ✅ **All 8 Ch3s scripted:**
     - crab-ch3-beyond-the-wall (pays off `nezumi_friends` and `oni_named_ryozo`)
     - crane-ch3-the-white-squid (re-dated; the canon 1123 Lion patron becomes Matsu Tadanobu, orig.)
     - dragon-ch3-past-mistakes (History meter)
     - lion-ch3-the-deadly-message (fit fix: same boss on both routes)
     - phoenix-ch3-the-darkfever (triage → path actions)
     - scorpion-ch3 (= unicorn-ch2)
     - unicorn-ch3-the-noblest-blood (Covered Ears set-piece)
     - ronin-ch3-the-village-of-the-wounded-lion (re-scaled: the Hantei line descends from a peasant)
   - ✅ **All 8 Ch4s + the finale scripted.** **THE WHOLE GAME IS NOW SCRIPTED at scene level: 32 chapters + the
     finale.** Files in `docs/story/scripts/`:
     - crab-ch4-the-fairest-one-of-all (the stalking set-piece)
     - crane-ch4-the-play-no-one-performs (the rehearsal; father duel)
     - dragon-ch4-the-battle-of-the-white-stag (three-front chain; refuse the glory)
     - lion-ch4-sorrows-path (hold the ford; obsidian temptation)
     - phoenix-ch4-howl (Dreamwalker; join the halves → "Whole"; a fake choice)
     - unicorn-ch4-regret (the Wail vs. Covered Ears; Naohida as the heir of both houses)
     - ronin-ch4-the-oracles-choice (the night race; Akari becomes the Oracle)
     - finale-the-empress-of-nothing:
       - 4 acts, with **two parties of four** in the final boss (OT1 model)
       - a debate with the "doubt" twist
       - a table of the chapter flags that weaken Nashiko
       - the 8-traveler epilogue
   - OCTOPATH-FIT gained the **fake choice** rule.
   - ✅ **User: "want all the dialog and script done first: 1, 2, 3."** Order:
     1. Full production dialogue for all chapters.
     2. Guest side stories.
     3. Boss stat sheets.
     Format spec: `docs/story/production/README.md`. It covers the box size, flags, battles, the NPC table, Travel
     Banter, and the chapter-complete card.
   - **PRODUCTION TRACKER** (`docs/story/production/`):
     - Ch1 ✅ crab · crane · dragon · lion · phoenix · scorpion · unicorn · ronin
     - Ch2 ✅ crab · crane · dragon · lion · phoenix · scorpion · unicorn(=scorpion3) · ronin
     - Ch3 ✅ crab · crane · dragon · lion · phoenix · unicorn · ronin
     - Ch4 ✅ crab · crane · dragon · lion · phoenix · scorpion · unicorn · ronin
     - Finale ✅
     - ✅ **WORK ITEM 1 COMPLETE: full production dialogue for every chapter + the finale (34 files).**
     - ✅ **WORK ITEM 2 COMPLETE:** 27 guests × 2 side stories in `docs/story/sidestories/`:
       - guests-01-06 · 07-12 (the Inquisitor team + SS-TEAM) · 13-18 · 19-23 · 24-27
       - Each SS2 upgrades a guest skill. Several feed the finale's callback montage.
     - ✅ **WORK ITEM 3 COMPLETE:** `docs/rules/bosses.md`:
       - a stat formula
       - a table row for every common battle
       - full sheets for every boss and mid-boss (L, HPx, Resolve, weak/resist, skills, gimmick, phases,
         drop/steal)
       - finale phases and the side-story battles
     - **ALL DIALOGUE + SCRIPT WORK IS DONE** (the user's priority). Suggested next steps (ask the user):
       - (a) ✅ `rules/equipment.md` (and ✅ `rules/bestiary.md`)
       - (b) ✅ The consistency pass: `story/flag-ledger.md` and `tools/consistency.py`
       - (c) **Start the engine:**
         - install the RPG-Cobo template
         - register the MCP server (`rpgcobo.exe -mcp-stdio`)
         - build the battle-prototype plugins (`rt_suki`, `rt_void`, kata toggle) and test against
           `bosses.md` numbers
       - (d) AI-art planning (the user's tools are still unknown).
     - (Old note:) work item 2: guest side stories. Files: `docs/story/sidestories/guests-NN-MM.md` (batches of
       ~5 guests). Each guest has 2 side stories:
       - **SS1 "recruit"**: offered in their "joins via" chapter
       - **SS2 "secret"**: unlocks after a later chapter; resolves their B3 secret; upgrades a guest skill
       Production format, Octopath side-story style (an icon, a request, a short task, a payoff).
     - Battle ids used in production files must later appear in `rules/bosses.md` (work item 3).
   - **NEXT (suggested):**
     - (1) the production pass: apply the OCTOPATH-FIT §3 conversions to the early scripts
     - (2) side stories for the 27 guests
     - (3) per-boss stat sheets
     - (4) start the engine (template install, MCP, battle prototype)
     Ask the user which. (Lion Ch2 already exists as the template), Ch3s, Ch4s and the
     finale.
   - Guardrail I applied there: lines that echoed the source too closely were reworded. Keep doing this; never
     reuse adventure text.
3. ✅ **Weapon coverage:** every weapon type now has ≥2 users, thanks to Haruki's Kami Weapons (02-travelers.md).
4. **Per-chapter scene scripts** for all 32 chapters + crossroads + finale (start with one complete chapter as the
   voice/format template and get user approval).
5. Optional reads: Blood and Iron middle (Kudo town NPCs); targeted searches of the Gozoku/Triumvirate books
   (year-400 detail for Dragon Ch3); Emerald Empire for customs/flavour.
6. **Then engine:** install template on first `rpgcobo.exe` launch, register the RPG-Cobo MCP server
   (`rpgcobo.exe -mcp-stdio`) with Claude Code, build battle prototype plugins (Suki, Void Points, turn order).

## Open questions to raise with the user
- Which **AI art tools** do they have (they chose AI-assisted art)?
- Approval of the per-level gain scheme (DESIGN §4c) once numbers exist.
- ✅ Haruki's Ch4: −1 Void stat + passive **"Whole"** (Water heals cleanse 1 debuff; Drawing the Void twice per
  battle). Approved. ✅ "Void Points as AP" = Void spells are *paid* in VP: confirmed.
- (Answered in session 2: see the "Session 2 user decisions" block below.)

### Session 2 user decisions (2026-10-16), all applied to the docs
1. The **template script format is approved** → write the remaining chapter scripts in the same format.
2. Natsuko as a **dodge/evasion tank**: OK.
3. Haruki is **Water + Void** with **Ishiken-do** (cheap for Phoenix); **Void Points act like AP**: Void spells cost
   VP and *Drawing the Void* fuels them.
4. **Mass Path to Inner Peace** (VP 3 = party heal): approved.
5. Monk guests: **Jinnai** (Osano-Wo lay brother, Ronin arc) and a **tattooed Togashi** in the Dragon stories with
   dark humour → **Togashi Yosai** (orig.; guests 26–27).
6. The Break mechanic is **renamed "Suki"** (opening). The canon oni **Oni no Kuzushi** keeps its name.
7. **Calendar:** October Coup (3e months). The game spans winter 1122 → early autumn 1123.
8. "The courtier" = **Ide Tamotsu**, starting at **Status 3–4** (the Ide are loved by everyone).
9. **Obsidian is used by the corrupted: using it inflicts Taint.**
10. Spelling: write **"Bo"**, not "Bō" (renamed everywhere; saved to memory).
- Also told to the user: 5 adventure-NPC guests got their source names back (Iuchi Karasu, Moto Benjiro, Shiba
  Ashimita, Akodo Ijako, Hiro). The *Endless Strike* holder was fixed to Mirumoto Hikaru, because Mirumoto Daigo is a
  shugenja.

---

## Standing requirements (from the user)
- Fan-only, never for profit. Story bible first, then engine. **Depth over speed** — research thoroughly.
- **Original arcs are expected** where sources are thin/off-era.
- **Translate L5R rules into Octopath-style gameplay** (DESIGN §4b–4c).
- **Travelers start Insight Rank 1, low Status** (Tamotsu starts at Status 3–4); big names treat them as nobodies.
- **Rank bands:** R1 = Lv 1–20, R2 = 21–40, R3 = 41–50, R4 = 51–60, R5 = 61+; per-level gains from kata, skills, kiho,
  spells, school techniques.
- **Static characters stay static:** adventure/canon NPCs keep their names; only pregen-derived guests are renamed.
- Guests work **like Octopath Traveler II**.
- "Stop at 90%" = the user's **claude.ai usage meter** (Claude can't see it) — keep working, keep this file current,
  ask the user to say when it's near 90%.

## Key decisions log
| Decision | Notes |
|---|---|
| Era: winter 1122 → summer 1123; ends on the **eve of the Coup** (14th of the Rooster 1123) | verified in *Imperial Histories* ch.5 |
| Cast: 8 original travelers (see table below) | Unicorn = Ide diplomat-trader; Ronin = born wave-woman herbalist |
| Final antagonist: **Doji Nashiko** — destroyed at the end | villain of Mirror, Mirror and Of Family and Honor |
| Finale virtue debate uses canon clan tenets (5e core ch.7) | Crab Courage, Crane Courtesy, Dragon Sincerity, Lion Honor, Phoenix Righteousness, Scorpion Duty & Loyalty, Unicorn Compassion; Ronin answers last |
| Sayo Ch4 = The Oracle's Choice | she protects the eta woman Akari; gains no Oracle powers |
| Don't install/decompile `OctopathTraveler/` (scene-group installer) | design from public knowledge |
| Custom systems as RPG-Cobo **plugins**, not engine edits | engine is pre-1.0 |

**Travelers:** Hiruma Natsuko (Crab, 20, scout, Sumai) · Kakita Rensei (Crane, 17, duelist, Charm) · Kitsuki Gendo
(Dragon, 28, junior yoriki, Discern) · Akodo Shizue (Lion, 18, tactician, Duel) · Isawa Haruki (Phoenix, 20, shugenja
healer, Bless) · Shosuro Mitsue (Scorpion, 23, actress-agent, Eavesdrop) · Ide Tamotsu (Unicorn, 29, courtier-trader,
Barter) · Sayo (Ronin, 18, herbalist, Pilfer).

---

## Folder layout
| Path | What it is |
|---|---|
| `Adventures In Rokugan/` | User's adventure PDFs (29 + 2 maps) |
| `OctopathTraveler/` | Installer — **not used** |
| `_tools/rpgcobo-tool/` | Clone of github.com/akodoreign/rpgcobo-tool (HEAD `4b9cb08`) — engine/editor |
| `_sources/drive/` | 31 sourcebook PDFs from the user's Drive (2.1 GB). `drive_files.tsv` = names/IDs/keys |
| `_research/adventures_txt/` | Text of every adventure PDF |
| `_research/books_txt/` | Text of the sourcebooks (`*.ocr.txt` = OCR of scanned ones) |
| `docs/research/` | One research note per adventure |
| `docs/story/` | Story bible (00–04) |
| `docs/DESIGN.md` | Game design + rules translation |
| `docs/rules/` | schools · stats · skills · kata · kiho · haruki-spells · battle-skills · weapons · spell-and-kata-index-3e-core |

## Sources
- **Drive books with usable text:** Emerald Empire, Enemies of the Empire, Imperial Histories 1 & 2 (has the
  year-by-year 1119–1123 timeline, pp. 128–132), L5R 5e Core Rulebook, Fealty & Freedom, Masters of Court, Prayers and
  Treasures, Legacy of Disaster, Burning Sands 4E conversion, Kyuden Soyokaze, Naishou Province, Strongholds of the
  Empire, Sword and Fan, Books of Air/Earth/Fire/Void/Water, The Great Clans, The Imperial Archives, Topaz Championship.
- **Scanned (OCR):** 3e Core Revised, Masters of Magic, The Four Winds, The Vacant Throne.
- **Broken on Drive (truncated, unreadable):** "Legend of the Five Rings.pdf", "Secrets of the Empire.pdf".
- Download method (if ever needed again): Drive `embeddedfolderview?id=…&resourcekey=…` → file IDs + per-file
  resourcekeys → `https://drive.usercontent.google.com/download?id=…&export=download&confirm=t&resourcekey=…`.
  `gdown --folder` returns 401 for this folder.
- l5r.fandom.com blocks automated fetching (HTTP 402).
- Use sources for **facts**; never copy book text or art into the game.

## Tooling notes
- Python 3.11; pip packages (`pypdf`, `gdown`, `pymupdf`, `rapidocr-onnxruntime`, `wordninja`) are in the **user** site →
  run scripts with `python -E` (`-I` hides user-site packages). Keep scripts outside the folders holding downloaded files.
- git 2.52 + git-lfs 3.7.1 installed (needed by RPG-Cobo's template installer). `gh` CLI not installed.

## RPG-Cobo engine — key facts (details in DESIGN §5)
- Apache-2.0 HD-2D voxel RPG maker; scripting in "Sakana" (`.sk`, Squirrel-like; globals `::x <- v`; `obj["k"]` safe
  lookup; blocking cooperative threads). Docs Japanese-only (`docs/ja/`).
- First launch installs the template from github.com/djkotori/rpgcobo-assets via git-lfs.
- Data = JSON in `project/data/`; battle code `project/src/rpg/battle/` (TurnBattleRunner; hooks `prebattle`,
  `preturn`, `turn`, `precommand`, `postcommand`, `postturn`, `dying`; attribute bitmask defence) → Break/Boost doable
  as plugins.
- Built-in **MCP server** (`rpgcobo.exe -mcp-stdio`): database get/set/search, debug start/stop/screenshot, runtime
  execute — lets Claude build and playtest directly once registered.
- Roadmap: action-order battle (beta), front-view battle (fall 2026), Japanese-style asset pack (winter 2026).

---

## Session log (compact)
**Session 1 — 2026-10-16.** Explored workspace & engine; extracted and read all adventures (14 research notes);
user chose era, original cast, story-bible-first, AI art; drafted story bible 00–04 and DESIGN; user revised Unicorn
(Ide trader) and Ronin (born wave-woman), ending (eve of Coup), Nashiko destroyed; downloaded all Drive books (user
approved), verified Coup date and clan tenets, added canon 1120–23 events; supporting cast & guests (OT2 model,
pregens renamed, static NPCs keep names); Rank 1 / low-status rule applied; Rank↔level bands and per-level gains
drafted. OCR of 4 scanned books left running (resumable).
**Session 2 — 2026-10-16 (after the user's usage reset).** OCR finished and cleaned. Built the rules index and
schools.md. Wrote kata.md, kiho.md and haruki-spells.md; completed the 143-spell index; indexed *Masters of Magic*.
The Hida and Mirumoto technique blocks were read (Hida ≈ line 13041, Mirumoto ≈ 13729) and used for secondary-school
kata eligibility. Scratchpad scripts: `kiho.py`, `mom_spells.py`, `spells2.py`, `spell_xref.py`; each anchors on stat
lines (MASTERY / AREA OF EFFECT) because the OCR mangles the labels.
Later in session 2:
- Rules: stats.md, skills.md, weapons.md, battle-skills.md, sayo-remedy.md, enemies.md, and the rules README
  (overview + 8 decisions for the user).
- OCR spot-checks against the page images (render_page.py).
- Story: 05-chapter-outlines.md (7 thin chapters at scene level; Phoenix Ch3 → the canon Darkfever).
- Fixes: restored 5 static-NPC names; 3e calendar correction (Rooster ≈ October).
Late session 2:
- User decisions applied: Suki, Water/Void + VP-cost Void spells, the mass heal, monk guests (Jinnai, Togashi Yosai),
  the October Coup, Tamotsu at Status 3–4, obsidian Taints, "Bo".
- OCTOPATH-FIT.md written.
- All 32 chapters + the finale scripted at scene level.
- The production dialogue pass started: 21 files done (see the RESUME POINT at the top). Paused at the user's 90%.
**Session 3 — 2026-10-17 (engine work).** Built the Rokugan battle plugin (Suki shields/break, Void Points + Boost),
data generator, enemy sprite animator and HD-2D render presets — see docs/ENGINE.md. Art direction (user): HD-2D /
Octopath, not voxel, and NOT the tilt-shift "miniature diorama" look (user finds it unsettling — Fantasian-like).
- Party sprites: `tools/gen_sprites3d.py` (replaces gen_sprites.py): SDF figures raymarched to 64x80 pixel frames,
  chibi proportions (HEAD_S/BODY_SQ), 3/4 frontal (YAW -62), cel ramps with hue-shifted shadows, hair strands/pleats,
  pixel-placed eyes. Writes EP200-207 into enemy_pic.json (scale 1.1, flipx). Still below Octopath reference quality
  (next: hand-placed hair silhouettes, more cloth detail, better attack poses, per-character props).
- `tools/gen_render.py`: deep focus (far-only DOF), matte IBL (iblspec 250), crisp shadows, PBR fog type 3.
  Fog colour's low byte is an EXPONENT (intensity 1.1^(A-128)), not alpha — 0xFF whites out the screen; use ~0xC0.
- Regen order: restore _tools/enemy_pic.orig.json -> gen_enemy_art -> gen_sprites3d -> gen_data -> gen_render.
- **Sprites v3 (current): `tools/gen_sprites2d.py`** — true 2D pixel-rule art (user rejected the 3D-rendered v2 as
  "Playmobil"). 64x60 frames, distinct weapon/prop per traveler (Natsuko yari+map case, Rensei katana+saya, Gendo
  Bo+jitte+glasses, Shizue katana+gunbai [data now W100], Haruki shakujo+ofuda, Mitsue tanto+mask, Tamotsu yumi+quiver,
  Sayo katana+basket+jingasa). gen_sprites.py / gen_sprites3d.py are superseded.
- **Two engine animation bugs fixed:** (1) stock `atk_normal` skips attack anims for picture models (`if(ispic)
  return`) -> overridden in RokuganBattle.sk; (2) battle calls anime2("stand") every frame and `replay:true` restarted
  loops at frame 0 -> loops now `replay:false` (gen_sprites2d + gen_enemy_art). Party = "fight"/"stand" frames 0-3.
- **Ground texture:** `tools/gen_terrain_tex.py` paints 4-tone leafy grass into floor1.vox tiles (+ ramps in
  map_vox.json) and strata on terrain1.vox cliffs. Lighting moodier (ibldiff 800, sun 1600 warm).
- Regen order now: restore enemy_pic.orig.json -> gen_enemy_art -> gen_sprites2d -> gen_data -> gen_render
  (gen_terrain_tex is independent). Auto Battle setting persists (toggle V).
- **RESUME POINT (session 3 end, user at 93%):** next = per-character hair polish (silhouettes per style), Octopath
  lighting (dark surroundings + light pools; no vignette param in renderset, consider a UI overlay), verify goblin
  idle loop in-engine (Auto Battle off first), then ENGINE.md update + Crab Ch1 slice. Preview: _art/preview/sprites2d.png
- **Side-cast sprites (preview only): `tools/gen_sidecast.py` -> _art/preview/sidecast.png (27 chars).** User: look up
  each canon NPC's appearance on the L5R wiki (l5r.fandom.com) before redrawing — e.g. Hida Kisada must be a very
  heavily armoured giant (needs a heavy-armour build + tetsubo). Add per-character look notes to CAST, then new
  builds/props as needed (heavy armour, kabuto, porcelain mask for Karasu, monk tattoos for Yosai/Hikaru).
- **Session 3b (2026-10-17 11:24–, user asked for 1.5 h on character detail/uniqueness):** wiki research (MediaWiki
  API via curl works; WebFetch is blocked with 402) -> docs/art/cast-looks.md. gen_sprites2d grew a full spec
  vocabulary (see docs/ENGINE.md §2), 80x68 frames, weapon-style attack/idle/victory animations (thrust/slash/smash/
  shoot/iai). Side cast written to the engine as EP300-EP326. New: 28 human enemies (bestiary A1-A7) as EP400-EP427 /
  E200-E227, test groups M001 gid 4 and 5, verified in-engine.
  Also: HD-2D screen layer in the plugin (colour grade via drawpass.setColorMatrix, vignette SKImageView between
  stage3d and stageui — RPGStage.launch is a coroutine, wrap it by storing the original as a class member, not
  .call()); weather layers (field cloud shadows, battle motes); title M000 moved off the tilt-shift preset; field
  placeholders on M001 swapped to sprites (villager = Hiruma Ryoichi EP304, symbol enemies = goblins). Expressions
  (hurt/cast/victory), clan mon shapes, element-coloured cast glows, body-type variety, better walk cycle.
- **RESUME POINT (after session 3b):** art pass done for travelers / 27 side cast / 28 human enemies (previews:
  _art/preview/travelers_final.png, sidecast_final.png, human_enemies_final.png). Next: user feedback on the cast;
  side-cast sprites are in enemy_pic (EP300+) but only Ryoichi is placed on a map; turn-order bar; traveler talents;
  Crab Ch1 maps (docs/ENGINE.md §5).
- Localisation started: gen_data.LOCAL (jobs/items/conds; plain-string names — a {ja,en} dict shows "table:...")
  and tools/patch_ui.py for labels baked into binary .ui layouts (level-up "Learned Arts"). Regen order adds
  patch_ui (independent). Side-cast NPCs on M001: Ryoichi, Kaiu Takakana (EP302), Hida Sachiko (EP303) with lines.
- Late 3b: KO is now a kneeling collapse pose (weapon dropped) instead of a rotated sprite; new evade frames 27-28
  ("avoid" anim no longer reuses the pain frames); per-character idle tempo (idle_spd); sleeve linings + obijime;
  pale-colour ramps get cool lavender shadows. Turn-order bar: engine sorts cmdqueue by cmd.order only after all
  commands are chosen (TurnBattleRunner.battleTurn) -> a bar needs an AGI-based prediction + a new UI label.
- Turn order: #n ranks in party/enemy labels = the real action order (factor pre-rolled at preturn; SkillCommand.
  calcCommandOrder overridden). Verified in-engine. Next: graphical portrait bar.
- Suki look: broken enemies desaturate/darken (tintBroken; colour matrices saved in ::Rokugan.savedcm because class
  instances can't take new slots) and restore on recovery — verified break -> recover -> break cycle.
- Hair/helmet pass (2026-10-18): clump shading (smooth crown + shine band, clumps toward ends), tufted outlines,
  zigzag hem tips, sidelocks, ahoge, new bang sets (swept/parted/heavy/messy), bangs cast a forehead shadow;
  kabuto rebuilt (ridged riveted bowl + tehen ring, visor, laced shikoro, fukigaeshi with mon, crest on base plate).
- Turn-order portrait bar done (THIS TURN + NEXT, pre-rolled factors; tools/gen_portraits.py makes 131 framed
  portraits + row tags). Run gen_portraits after any sprite regeneration.
- Talents v1 (all 8) as a Talent battle command; verified in-engine (party swap test via setting.json, then
  gen_data restores). Fixed S111 Jade Strike: magic formula needs atkform (spell power) or it throws "pow".
- **Crab Ch1 slice started (2026-10-18):** procedural map pipeline (gen_maps.py + RokuganMapGen.sk) — Rokugani
  building kit (gabled kawara roofs; stepped pyramids read as ziggurats), M100 watchtower (night) with the S01
  opening + goblin raid on the new Wall battle backdrop M810, M101 garrison, M102 coast road (encounters on M811
  beach backdrop), M103 Hoshi-no-Ichi with the Crab Ch1 townsfolk (EP327-336) and their barks; portals verified
  M100->M101->M102->M103. Gotchas: portal "back": true ignores dest (returns to previous portal); battle floors must
  be at y=1 like M800; run gen_render after any map registration. Start party is still the 4-traveler test party.
  Next: S02 Tomoe scene + S03 arrival cutscene, inn/shop functions, quarry M104, Egg Caves D1, solo-start decision.
- User rules (2026-10-18): **simulate what is actually there** — party = who is present in the scene (Natsuko starts
  solo; S01 raid adds guests P120 Sachiko / P121 Ryoichi via cmd_memberop, removed after). Cast proportions: heads
  x0.75 (gen_sprites2d HEAD_SCALE, box-downscale + palette snap + re-stamped eyes), necks ~50% SHORTER (NECK_UP=-1).
  Battle floors: top block y=0 (feet at y=1 like M800 markers). Battle tests via -battle now use the solo party.
- **RESUME POINT (2026-10-18, user hit 99% — wrapped mid-task):**
  DONE this stretch: heads x0.75 / necks ~50% shorter; 4-way field sprites (gen_sprites2d front/back views: fidle,
  fwalk, bidle, bwalk -> animap stand_f/walk_f/stand_b/walk_b..., sheets now 8x8 / 57 frames) + plugin facing system
  (RPG3DPicture.updateSRT/anime2 overrides: dir 0=back, PI=front, +-PI/2 = east/west mirror; battle unchanged) —
  verified walking 4 ways and NPCs facing the camera. Spell cast poses cast_bolt/area/heal/ward/summon/void.
  IN PROGRESS: tools/gen_spellfx.py — 92 spells parsed from haruki-spells.md, classified (cat/motif/kind/tgt), pixel
  FX strips + .ptd written to resource/efx/rt/FX400+, efx.json caps raised to 999, manifest data/rt_spells.json.
  TODO next: (1) fix leftover misclassifications (Whirlpool -> water cyclone attack all enemies; Tempest of Fire ->
  fire cyclone attack; Tremor ok as curse); (2) gen_data: build skills S300+ from rt_spells.json (skill.json caps
  -> 999; useani cast_<cat>, hitefx = FX id, elembits by elem, SP cost, attack=magic dmgform 1 with atkform, heal
  dmgform 2, buff/debuff putconds where mappable) and give Haruki the starting kit + §4 curve via lvoption;
  (3) test FX in-engine (never rendered yet — .ptd syntax untested); (4) look at _art/preview/spellfx.png;
  (5) S02/S03 cutscenes, inn/shops, quarry, Egg Caves. Regen order: sprites -> gen_portraits -> gen_spellfx ->
  gen_data -> (gen_maps if designs changed) -> gen_render LAST.
- **Spells live (2026-10-19):** gen_spellfx.py (92 spells: motif + 46 distinct motif/sub-motif looks + a unique
  sigil per spell; overrides table for terse ultimates) -> gen_data spell_skills() makes S300-S391 (cast pose
  useani cast_<cat>, hitefx FX400+, magic dmg formula, mapped status conds, Void spells cost VP via plugin rt_vp,
  Drawing the Void +1 VP) and Haruki learns the starting kit + §4 curve (lvoption). Verified in-engine: Fury of
  Osano-wo cast pose -> lightning FX -> 203 dmg + Suki break; Path to Inner Peace runs. Gotchas: use_charge needs
  useact.usesnd; heredoc-in-python writes turned "\b" into backspace chars (write patch files instead).
- **S02 + S03 scripted (2026-10-19):** S01 ends with "Dawn." + cmd_mapmove (dest pos with null y) to the garrison;
  S02 (Tomoe's leave order) autoplays there once (G011, requires G010); S03 (arrival, drop soup, Kiyo's rumour) on
  M103 (G012, requires G011). Verified S01 -> raid -> aftermath -> dawn -> S02 in a real New Game run.
  tools/autoplay.py = scripted playtest driver ("z14;wait:3000;shot:name"). Cart escort NPC not built yet.
- **Dialogue now generated from the production script (2026-10-19):** gen_maps.script_scene(chapter, "Sxx",
  battles=..., start_at/stop_at) turns `NAME: line` into dialogue, `(stage direction)` into narration (camera words
  trimmed, ALL-CAPS names title-cased, technical notes skipped), `[BATTLE id]` into commands, and drops inline acting
  cues. Fixes the user-reported missing connective lines (hand-typed scenes had dropped the hat falling, Ryoichi
  wrapping her arm, merchants mobbing the cart, the "You always have the watch / Someone has to" close).
  S03 split: S03A on entering town (G012), S03B drop-soup when walking past the noodle stall (touch trigger, G013);
  Taneo moved to the stall. Verified S03A/S03B in-engine. Barks match the script's NPC table.
  Recurring hazard: writing patches via heredocs turned "\b" into a literal backspace (0x08) in regexes —
  scratchpad/fix_bs.py repairs tools/*.py; run it after any heredoc patch.
- **Services (2026-10-19):** items I100 Rice Ball, I101 Herbal Salve, I102 Salt Herring, I103 Eye Drops, I104 Jade
  Dust (Jade damage), I018 Antidote; armour A100 Travelling Clothes, A101 Ashigaru Lamellar, A102 Jingasa; stores
  R100 Garrison Armoury, R101 Jade Store, R102 Hoshi Arms, R103 Hoshi Goods; inns: barracks (free), Hoshi inn
  (10 zeni). Service NPC sprites EP337-341 (quartermaster, jade clerk, innkeeper, merchant, cart driver); cart prop
  EP350 (tools/gen_props.py) at the garrison exit and the town gate. English for template macros X004/X013-X017
  (gen_data.MACRO_TEXT, path-addressed) and dict.json terms (currency " zeni", steal messages). Weapon/armour
  descriptions written. Verified: armoury buy list, inn stay (price prompt -> rest fade).
  Next: the cart actually following on the Coast Road (escort), quarry M104 + Gonta (S04 Sumai), inn S05 night theft,
  Egg Caves.
- **Escort + quarry (2026-10-19, later):**
  - New plugin file `plugin/rokugan/RokuganField.sk`:
    - moveaction **`rt_follow`**: breadcrumb-trail follower. `data.lead` = the leader's event id NUMBER (runtime evids
      are ints, not "#n#"); `gap` in metres; always spawned; passes through the party (collision mask minus 0x100);
      snaps behind the leader when more than 9 m away.
    - The cart escort on M102 (driver follows Natsuko, cart follows the driver; reqs G011 && !G012) is verified.
    - `-rtvar G010,G011` test switch sets flags before the first stage launch, e.g.
      `rpgcobo.exe -testplay -map M104 "[31.5,3.5,3.5,0.0]" -rtvar G010,G011,G012,G013 -debuglv 3`.
    - **Sumai helpers** `::Rokugan.sumaiBegin/sumaiEnd(pid)`: swap the weapon for W106 Bare Hands (skill S106 Throw =
      the new 13th attack type **Unarmed**; EDR has 16 slots) and restore it after the bout.
  - **S04 quarry M104 verified:**
    - Arrival scene G014; Natsuko walks down to the fire, and the script's 3-way choice follows.
    - Sumai = M001 gid 6 vs E120 Gonta (EP342; Unarmed weakness) on the new backdrop M812, with losefunc 1.
    - A loss gives a taunt and a retry (G020 counts losses); the 2nd loss is "a little too slowly" and counts as a win.
    - Win sets G015 `hidden_ones_cleared`; Leave sets G016 `quarry_left`.
    - Hint spots: pots, Gonta's boy, prints. The ledge chest has 100 zeni.
    - Tents are straw-mat A-frames (`tent()`, MATTING = S(26)); the campfire is lamp #2 torch2.
  - Townsfolk talks are counted (G030-37 → G019). The 3rd talk opens the quarry trail (M103 north portal; a stop
    event walks the player back before that).
  - Satomi S03b (talk twice → G017 `talked_satomi`).
  - New sprites (gen_sidecast): EP342-347 Gonta, 2 Hidden Ones, Gonta's boy, guard sergeant, town guard.
  - Event helpers in gen_maps: talk (pages; the engine runs the LAST page whose reqs pass), if_, choices, script,
    setf, step_back, after_line. script_scene now drops any lowercase inline cue.
  - **autoplay.py focus guard:** keys are global (keybd_event). autoplay now re-fronts the game before each key and
    exits (code 2) rather than type into another app. Dialogue needs ~2 Z presses per line (hold:z:150; wait ~1.2 s).
  - Balance: E120 Lv5 HP300 ATK17. A Lv1 Natsuko loses; Lv3 should be close.
  - Next: S05 (the first inn rest after S04 → night theft → chase cutscene → road_coast night follow-walk P1-P3 →
    the cave mouth + Squeak), then the Egg Caves D1 + Rumble meter.
- **S05 verified (2026-10-19):**
  - The Hoshi inn keeper (M120) is now a talk event. Page 0 is the normal stay (W = price, macro X014).
  - Page 1 applies after S04 (G021) and before S05 (G022). Choosing "Stay the night" runs:
    - the fade to blue, then black (DARK), and a heal;
    - the S05 night text up to the follow-walk;
    - a mapmove to **M105**, the night copy of the Coast Road (`road_coast(night=True)`). It has no exits, chests or
      encounters.
  - On M105, touch prompts P1-P3 (G025-27; text parsed from the script's FOLLOW-WALK bullets) are spaced 124 → 78.
    Squeak (EP351, new gen_props sprite) waits ahead at each step.
  - The cave-mouth scene (G024) plays at the new Egg Caves mouth (exterior #21 dungeon entrance at CAVE = (68,25) on
    both M102 and M105). On M102, examining the cave says "Not my business. I'm on leave." until G024.
    CAVE_ENTER is a placeholder until the caves exist.
  - The inn stove moved to the corner; it used to block the innkeeper.
  - Mapmove world pos for padded maps = ((x + PAD_X)/2, None, (z + PAD_BOTTOM)/2, dir).
  - Next: the Egg Caves D1 (3 caves + the altar), the Rumble meter, S06-S09, then S10.
- **Egg Caves built (2026-10-19, later):**
  - Maps:
    - M130 nests: stolen-things circles → Kite Mirror / Wooden Fish / Pearl Hairpin (I110-112); chests Rice Ball ×2
      and Scroll: Summon Fog (I113); fixed fight b_cave_nezumi_a = gid 7 (G041).
    - M131 painted eggs: baskets; cracked Tremor wall (text only until Haruki); pool dead end with Eye Drops ×2 and
      150 zeni; b_cave_beetles = gid 8 (G042).
    - M132 armour: the stand (S06 C3 lines; the talked_satomi lines G017); Seppun Guard's Jingasa A103 + 300 zeni;
      b_cave_nezumi_b = gid 9 (G044); save shrine (statue: heal + menu_save).
    - M133 altar: Ryozo, young nezumi (EP354), Squeak, egg heaps (EP352), candles.
  - Cave generator `cave_map()`: carved wobbly rooms and tunnels, floor y=2, STONE walls. **Cut-away rule:** a wall
    with floor within 9 blocks to its north drops to a 2-block rim, or the 38° camera can't see the rooms.
  - Backdrop M813; render preset `rt_hd2d_cave` (gen_render CAVE_MAPS, dust motes).
  - **Rumble meter** (`plugin/rokugan/RokuganRumble.sk`): active on M813. Area actions +30, Boost +15 per level.
    At 100 a cave-in after that action: -20% max HP to all (travelers floor at 1); the Nezumi Shaman goes Suki.
    The UI bar top right uses gen_portraits images (_rumble, _rumble_bar, _rumble_fill). Verified with TEST group
    gid 12 (dummy on M813): fills 45/90/100 → CAVE-IN! → resets.
  - S07 (G045) "Reach Ryozo": up to 3 rounds with short choice labels; Natsuko then says the script's full line.
    G046/G047 → G048 `ryozo_talked_down`. Without talked_satomi only 2 options, so the talk-down can't succeed
    (as designed).
  - S08: boss gid 10 (+ guest Squeak P122, Pocket Sand S132) or gid 11 (+ Ryozo E121, Egg Rite S131). The shaman
    E106 (HP 900) uses Name-Magic S130 (Silence); drop Nezumi Bone Charm A105; steal Painted Egg I114.
  - S09: the oni scene (G050) when not talked down; the roof collapses; mapmove to the M102 cave mouth.
    - Dawn scene there (G051 nezumi_friends; the Ryozo dawn line if G048) → Squeak's Charm (A104).
    - Tea house M123 scene (G053): the reunion + Seppun Tanto choice (W107, G052), or Satomi packing.
    - S10 at the garrison (touch near the east arrival, G054) + the chapter-complete card.
  - All flags are declared; gen_data now WARNS about any G### an event uses that gvar.json lacks.
  - Production fix: "Satomi's nephew." moved inside [IF talked_satomi] (crab-ch1.md S06).
  - Verified in-engine: cave 1 walk, circles pickup, nezumi fight on M813 with the meter shown, boss gid 10 win +
    drop, cave-in on the dummy, S07 intro + choice round 1-2.
  - **NOT yet verified:** S07 rounds 2-3 → S08 boss from the scene → S09 mapmove/dawn → tea house → S10. Testing
    stopped because the user was using the desktop (autoplay steals focus; it now exits instead of typing into
    other apps).
  - TODO: template "Pebble" drops on every enemy (set real drops from the bestiary); post-chapter item returns
    (mirror/fish/hairpin); Honor for the gift refusal; consider quest.json for objectives instead of narration.
- **Arm + weapon rig, side views (2026-10-19; user: "arms and weapons, should be dynamic; particularly east/west"):**
  - gen_sprites2d `rig_arms()` runs after build_pose.
    - **IK:** both arms are fixed-length 2-bone chains (ARM_UP 5.8, ARM_FORE 5.6) solved toward the pose's hand
      target. The elbow uses the anatomical fold: shoulder→hand direction turned 90° clockwise (a forward reach bends
      down, a hanging arm bends back, a raised arm bends forward). The pose's elbow coordinates are ignored.
    - **Dynamic grip:** the weapon hangs off the near fist at wang. For TWO_HAND weapons (katana -3.6, nodachi -5,
      yari/naginata/bo -9, tetsubo -5.5), the far fist IK-snaps to that offset along the shaft. If the far shoulder
      can't reach, the near fist and the weapon slide back toward it.
    - Pose flag `grip2`: idle (chudan/spear), ready, all attack frames, guard.
  - Drawing:
    - `draw_fist` wraps across the weapon axis, with a knuckle highlight and thumb shadow.
    - The near arm is drawn on its own layer (`arm_layer`): an additive +10 lift, a rim light on the top/right
      edges, and a dark contact line where it crosses the body.
    - When gripping, the far forearm is drawn in front of the chest (upper arm hidden), darkened.
  - `forge_blade`: a polygon blade with sori, a tapering kissaki, a bright edge, a polished face and a darkest-tone
    mune. Used for katana, nodachi and naginata.
    - Canvas.keep marks metal so outline_outer no longer darkens blades (the old "dotted stick" look); the spear and
      tanto heads are kept too.
    - A habaki collar sits at the tsuba.
  - Walk: a bigger arm swing; the weapon rocks ±6°. Swords are carried low (tip forward-down), pole arms upright
    (wfront: always drawn in front, so weapons no longer vanish on some frames), and a club rides on the shoulder.
  - Tools: `tools/preview_arms.py` (cast close-up across poses). Before/after compare script lives in the session
    scratchpad (gen_sprites2d.before_arms.py backup there).
  - Regenerated: gen_sprites2d, gen_sidecast, gen_human_enemies, gen_portraits, gen_data, gen_render. Checked
    in-engine (M001 gid 4 battle).
  - Front/back (field) views are unchanged: still hanging arms (draw_fb_body/draw_fb_weapon).
- **Unattended playtests (2026-10-19):** RokuganField.sk flags.
  - `-rtfast`: messages are logged as `[RT] MSG name: text` instead of waiting, and the battle result's level-up and
    click waits are skipped.
  - `-rtchoice 0,1,...`: choice menus are answered in order.
  - `-rtauto`: every battle starts in Auto Battle.
  - With `-rtvar` and a `-map` spawn on (or next to) a scene trigger, a whole branch runs with **no keypresses**
    (the game keeps running unfocused). Grep the log. Spawn off exit portals (the tea house door is at world z 6.0;
    use 7.5).
  - Example: `rpgcobo.exe -testplay -map M133 "[29.0,1.5,6.5,0.0]" -rtvar G010,...,G044 -rtfast -rtauto
    -rtchoice 0,1 -debuglv 9 > log` and wait for a log line with a `timeout ... until grep` loop.
  - **Crab Ch1 is verified end to end in-engine:**
    - S07 talk-down (choices 0,1) → boss gid 10 + Squeak → collapse → dawn → nezumi_friends + Squeak's Charm.
    - Oni branch (no talked_satomi; 3 failed rounds) → gid 11 + Ryozo → oni scene → dawn.
    - Tea house A (reunion, accept → Seppun Tanto) and B (Satomi packing).
    - S10 at the garrison → the chapter-complete card.
  - Squeak's sprite scale ×0.62 (he was drawn as big as Natsuko in battle).
  - A known harmless engine error on window resize: `index "link" does not exist in null` in SKRootView.updateLayout.
    The game carries on.
- **Legs, nezumi, campfire, names (2026-10-19, user pass):**
  - **Side-view leg rig** (gen_sprites2d `rig_legs`, `leg_layer`, `draw_foot_side`):
    - Thigh and shin of fixed length (LEG_BASE 13.6 + height). Knees fold forward.
    - If a stance puts a foot out of reach, the body crouches (whole-pixel hip drop) instead of the foot lifting.
    - Real walk: contact → passing (swing foot lifted 3 px, toe down) → contact → passing, with heel strike and
      toe push-off pitch.
    - Hakama drawn through the knee (mitred polygon): pleats follow the shin, the hem darkens, and a contact line
      sits between the legs.
    - Shaped feet: tabi with the split toe and waraji sole + thongs; bare feet on straw for peasants; dark kogake for
      armoured builds.
    - The robe's front edge follows the forward knee. KO uses `kneel` (pose knees kept).
  - **Front/back walk:** lift 3 px with the knee coming toward the camera (raised hem, narrower shin, knee light);
    `draw_foot_fb` (toe cap / heel / sandal sole when lifted from behind); robe hems lean with the stride.
  - Previews: `tools/preview_legs.py`, `tools/preview_arms.py`.
  - **Nezumi redesign** (`tools/gen_nezumi.py`): upright ratfolk in the Master Splinter mould (the user found the old
    Squeak too Tom & Jerry).
    - Long tapered snout, set-back ears (big on the young), beady eyes, light whiskers, chibi head ×1.35, neck,
      digitigrade pink feet, clawed hands, a long bare ringed tail (kept out of the outline pass).
    - Outfits: rags (Squeak EP351), loincloth (young EP354), hide + red headband + spear (warrior EP101), robe + sash +
      bone charms + bone headdress + skull staff, old and grey (shaman EP105).
    - Squeak uses the travelers' sheet layout (party guest); enemies use gen_enemy_art.animate.
    - Regen order: gen_props → gen_nezumi → gen_portraits. The old cartoon Squeak was removed from gen_props.
  - **Campfire** (gen_props EP355, 4 flicker frames: stone ring, crossed logs, layered flame, sparks) +
    `Events.light` (role "light", warm ARGB) via `Events.campfire()`.
    - Replaces the torch in the quarry camp M104 and on its battle backdrop M812. Battle maps run events: the
      backdrop builder may return (m, Events) with ids from 100; register() merges them into the M800 copy.
  - **Names, family name first, often:**
    - gen_data player names (Hiruma Natsuko, Kakita Rensei, …; Sayo/Squeak single).
    - gen_maps `FULL_NAMES`: say() labels are always full; `full_first()` names a samurai in full at the first
      narration mention per scene.
    - The plugin matches talents and barks by given name (`::Rokugan.given`).
    - The production README has the naming rule; memory `family-name-first`.
  - Verified in-engine (no keypresses; wincap without focus): the quarry campfire, the boss fight with the new nezumi
    and the full names in the battle list. Field walking legs aren't seen in-engine yet (needs key input).
- **Face + neck pass (2026-10-19, user: "faces and necks, give each of them uniqueness"):**
  - Cause of the samey faces: the head is box-scaled to HEAD_SCALE 0.75, and one-pixel features blurred away. Only
    the eyes were re-stamped.
  - **Face kit** (gen_sprites2d `face_kit` / `stamp_face`): eyes, brows, nose, mouth and marks are stamped crisply at
    sprite resolution after scaling, in the side 3/4 view (near + foreshortened far eye) and the front view.
    - The design-layer versions step aside (`kit_ok`). Masks (porcelain, reed, noh, death, stitched) and glowing eyes
      keep the old path.
    - Vocabulary:
      - eye: round, sharp, gentle, half, wide, smile, tired
      - brow: straight, angled, worried, arched, thick, skeptical, none
      - mouth: neutral, set, smile, smirk, frown, grin, open, pout, toothless
      - nose: dot, strong
      - marks: scar_cheek, scar_nose, scar_brow, freckles, mole_eye, mole_chin, beauty, bags, laugh, wrinkles, blush,
        drunk, paint_red, paint_white
    - Expressions override the kit (pain → > < + open mouth; focus → shut; grin → smile eyes + grin).
    - Travelers have explicit kits (personality from the voice notes): Natsuko sharp/angled/smirk + nose scar + bags,
      Rensei half/set + mole, Gendo half/skeptical + bags behind glasses, Shizue round/smile + blush, Haruki
      gentle/worried/pout, Mitsue sharp + red lid paint, Tamotsu smile-eyes/grin + laugh lines, Sayo wide/smile +
      freckles.
    - Side cast: `gen_sidecast.KITS` for all 47 named NPCs. Anyone else gets a seeded default from their spec (old →
      wrinkles + bags, peasant women → freckles, etc.).
  - **Neck:** width by sex/build, jaw shadow, lit throat edge / shadowed nape, Adam's apple on grown men, laced nodowa
    on heavy armour; a front-view variant.
  - Preview: `tools/preview_faces.py [travelers|side|all]` (FZ/FCOLS env for zoom/columns).
- **Drops, path actions, Honor, returns (2026-10-19):**
  - `gen_data.bestiary_drops`: parses every bestiary row (Drop / Steal) and attaches them to matching enemies
    (34: Crab Ch1 beasts + all human foes).
    - Known consumables are reused; food heals; everything else becomes a sell item I200+ priced by tier.
    - Nezumi drop Rice Balls and carry a Shiny Trinket to steal. No loot from Gonta, Ryozo or the dummy.
    - The template "Pebble" is gone.
  - **Path actions** (gen_maps): `with_sumai()` wraps an NPC's talk page into Talk / Sumai (n%) / Leave while P100
    is in the party.
    - `sumai()`: a refusal, or `::Rokugan.roll(pct)` → a win reward, or a loss (standing −1 + taunt).
    - Wall veteran 55% → Old Jade Bead A106 (G062). Kanbe refuses.
    - **Town standing** G061 (Hoshi-no-Ichi, starts 3). At 0 townsfolk refuse; amends at the inn cost 100 zeni and
      reset it to 3 (money checked).
    - **Honor** G060: refusing Satomi's gift +1, Gonta letting you win −1 (`honor(n)` shows "(Honor ±n)").
  - **RNG gotcha:** ::rnd is clock-seeded at boot, so the first draws are nearly identical every launch (r≈34.36 five
    times). `::Rokugan.roll` skips ahead by skGetTime()%97 first.
  - **Post-chapter returns** (after G054), via `returned(item, flag, lines, reward)` pages:
    - mirror → the kite child (Crow Feather I117, G063)
    - fish → Gonta's boy (Hidden Ones' Thanks I116, G064; only if the camp was spared)
    - hairpin → Kiyo (Drop Soup I115, G065)
  - Test tooling:
    - `-rtvar` takes values (`G061=0`).
    - `-event MAP ID PAGE` (testplay built-in) force-triggers a talk page, so talk NPCs can be tested with no keys.
    - Verified: veteran win and loss → town refusal → amends; kite mirror return.
  - Heredoc hazard is worse than noted: the Bash tool also turns `\` into `\`. Write patch scripts with the Write
    tool.
- **World map fast travel (2026-10-19):**
  - `tools/gen_worldmap.py` paints the world map from the README §4a ASCII sketch:
    - mountains ^, forest %, sea ~ (noisy coast), roads = (dotted), the Kaiu Wall # (crenellated)
    - soft clan-coloured regions from the clan labels, a darkened Shadowlands, region labels, 43 node pins + names
      (Georgia), a vignette and a frame
    - writes enemy_pic EP360 (1280×720) + data/rt_worldmap.json
  - The travel itself: plugin `::Rokugan.travel(runner, here, nodes)` shows EP360 (showPicture idx 0) and offers
    every *visited* node except this one (+ "Stay here."), then moveMap.
  - gen_maps `TRAVEL` table (code, name, visited flag G1xx, map, arrival block) + `signpost(m, ev, x, z, code)`:
    exterior post1 + an examine event + a silent arrival scene that sets the visited flag.
    - Current nodes: KW (garrison road gate, G100), HI (west gate, G101).
    - gen_data declares the flags from TRAVEL.
  - Verified: a real playthrough of the signpost → map + menu → travel KW→HI.
  - Note: screenshots from a `-event` launch can stay black (that launch path's own fade); test pictures via
    `-map` + autoplay.
  - **Next nodes** need their maps: KH Kyuden Hida (Crab Ch2), etc.
- **Crab Ch2 "Winter Court at Kyuden Hida" built (2026-10-20):**
  - **Maps:**
    - M140 Hida road: winter; the Wall on the far side; a waystation shrine; the Wall-stair Crab Plate chest;
      encounters on M814.
    - M141 castle town: snow; the black stone keep and castle gate; inn M160, Kaiu forge M161 (R110), Hida armoury
      M162 (R111), jade merchant M163 (R112), dojo M164 (Hiruma Goro; the Hida school after the chapter), tea house
      M165; KH travel signpost.
    - Castle floors: `castle_floor()`; event 1 = the way down, 2 = the way up.
      - M142 1F: barracks (free inn, Sachiko's Sumai → G208), the outer-yard archery (Kurako), the basement stair
        (Shigeru & Taira), the donjon door ev3 (after S04), the rear gate ev5 to the shrine.
      - M143 2F winter garden: Mutsuye, Kuhime, Keiyomi, Akiko, O-Shito; a frozen pond.
      - M144 3F guest wings: Shiko, Kage, Shigeru's room, Kuhime's empty room + the Blue-Silk Veil Thread.
      - M145 4F great hall: Kurako, the kitchen servant; the S02b dance trigger.
      - M146 5F/6F: the window over the Wall + the audience hall (Kisada, Takakana). S01, S04 and S07 autoplay.
    - M147 the women's shrine (dawn, S03). M148 donjon cells (S05 entry, goblin experiments gid 13, Squeak's
      rat-way if nezumi_friends, cells). M149 trap catacombs (roller and jade-line beats, caltrops cache, save
      shrine). M150 deepest cell (S06 boss gid 14 → spare/end → S07).
    - Battle backdrops: M814 road, M815 donjon, M816 castle hall (duel gid 15).
  - **Flow (flags G200-G230):** the castle-gate guard is the chapter icon (needs Crab Ch1 complete G054) → S01 → the
    hub (G202-G205 required; optional G206-G208, G221, G222) → S02b dance → dawn → S03 → S04 (3 accusations; "one
    more night" needs G208 + G210) → night → donjon → boss → S07 → the chapter-complete card.
    - The garrison's west exit to the Hida road opens after Crab Ch1.
  - **New art:**
    - Side cast EP370+ (`gen_sidecast.epid`: the first 50 entries are EP300+, later ones EP370+, avoiding the props
      at EP350-369): Kuhime (very blue eyes), Akiko, Keiyomi, Shiko, Shigeru, Taira (Tainted pallor), Kurako,
      O-Shito, Noboru, the servant, Goro. Mutsuye is EP349.
    - Monsters (`tools/gen_monsters.py`): EP110 Goblin Warmonger, EP111 Cave Bat Swarm, EP112 Yurei, EP113 Troll;
      EP114/115 tinted copies.
    - Human enemies EP428 Shiba Noboru, EP429 Maho Puppet.
  - **Enemy stats now come from the player curve** (`gen_data.player_curve` / `foe_stats`).
    - Fitted to measured Lv5 and Lv22 travelers: a regular hit ≈ 14% HP; a regular foe ≈ 2 party actions.
      Damage = 2.1 × PATK − PDEF.
    - Applies to human foes E200+ and all Ch2 foes (they were far too weak: 0-1 damage at Lv22). The hand-tuned Ch1
      foes match it at L1.
  - **Bug fixed:** status-attack skills were cloned from template S101 "mine-uchi", which barely scratches. They're
    now based on S003 Strike (Name-Magic, Pocket Sand, Veil Lash, No Pure Breaths, Screech, Grief Wail, Troll
    Smash).
  - **Troll hazard** (`plugin/rokugan/RokuganHazard.sk`):
    - Untouchable while the Maho Puppet stands ("HAZARD"), except **Jade gets through** (user).
    - It smashes the highest-attention traveler; Razor's Edge draws it.
    - It attacks the puppet while the puppet is open (Suki), and sits down when the puppet falls.
  - **Party Auto Battle AI** (`RokuganAI.sk`, user request):
    - heals anyone under 50% (Haruki: Path to Inner Peace);
    - Natsuko keeps Razor's Edge up against a hazard;
    - picks the best (skill, target): weakness ×2, Suki ×1.5, spells ×1.3, jade preferred on ties;
    - skips foes learned to be untouchable.
    - Boss on auto with Lv22 Natsuko/Rensei/Shizue/Haruki: 3/3 wins in 7-9 turns.
  - **Test tooling:**
    - `-rtshot tmp/rt_shot/x.raw <ms>`: the game screenshots ITSELF (rootview.capture → PixelBuffer.readPixels
      async → isDone → getData). It works while the window is behind other apps (wincap gives black then).
      Writes must stay under the tool folder; set pos = 0 before save.
    - `tools/snapmaps.py "MAP:x,z" ... --vars ...` snapshots maps unattended.
    - Battle stat/damage log lines: `[RT] stat ...`, `[RT] dmg ...`, `[RT] X hit Y`.
  - Verified unattended: chapter start → S01; dance → S03 → S04 (one more night) → the cellar; boss → spare → S07
    → the card; the gid 13/15 fights; map snapshots of all new maps (no errors).
  - **Not yet:**
    - (Done 2026-10-20: all 2F-4F hub talk pages run in-engine via tools/runevent.py, 0 errors.)
    - Other travelers' path actions in the court (Bless, Discern, Eavesdrop, Barter, Charm, Duel, Pilfer; Kuhime
      blanks Discern/Eavesdrop).
    - The 6 guest side-story icons, Travel Banter. (Boss barks and the Dance Ribbon return are done, 2026-10-20.)
    - The chapter is designed for 4 travelers at Lv 18-25; only Natsuko exists as a playable chapter so far.
  - User link (2026-10-20): github.com/Kirat-Singh2006/16-Bit-Style-Pixel-Art-Converter is a downscale + 64-colour
    quantize + nearest-upscale script. Not needed for the drawn sprites; maybe useful later to turn painted art
    (title, stills, the world map) into matching pixel art.
- **Companions + magic scaling (2026-10-20, user):**
  - **Rule (memory solo-with-companions):** only Natsuko is playable; each path uses short-term companions until the
    travelers meet (crossover chapters excepted).
  - **Crab Ch2 companions** (gen_maps `join(pid, name, lines, lv=18)` sets level max(18, Natsuko's), `leave(pid)`):
    - P123 Hiruma Goro (Kage's bodyguard, joins at the end of S01; Troll-Breaker S139, 2 uses);
    - P120 Hida Sachiko (joins on the barracks Sumai win);
    - P124 Isawa Michio (Phoenix Inquisitor, joins at the shrine S03; Amaterasu's Fire S138 2 uses, Jade Strike,
      Path to Inner Peace, Earth's Touch; sprite EP380, Goro now EP381).
    - All three leave at S07. The Noboru duel removes them and puts them back (a 1v1 duel).
  - **Guest uses per battle:** skill field `rt_uses` (RokuganAI.sk): a spent skill falls back to the weapon; auto
    battle skips it.
  - **Spells were flat:** a skill's atkform REPLACES the dmgform's atk formula, so "48" = 48 at every level.
    - `gen_data.spell_atk(p)` = "src.MATK*2.0+p" (dmgform 1, minus MDEF).
    - `heal_atk(p)` = "src.MATK*0.9+p+dst.MAXHP*p/300.0" (new dmgform 7, def 0).
    - Path to Inner Peace now heals ~52% at Lv20 (user: "not healing enough, more dynamic per level").
    - Enemy MDEF = 0.55 × player PATK curve (foe_stats).
  - **All travelers share one stat curve** (the template's). Stopgap: shugenja (P104 Haruki, P124 Michio) swap
    ATK↔MATK growth. **TODO:** wire in docs/rules/stats.md per-traveler trait schedules.
  - The boss with the real Ch2 party (Natsuko, Goro, Sachiko, Michio) at Lv20 on auto: 3/3 wins, 5-9 turns, 0 KOs.
  - Castle stairs: the up-portal is now at the stair foot (the mid-flight portal was unreachable); the 1F archery
    butts moved off the stair.
    - Walk-tested with keys: 1F → stairs → 2F garden → talk to Kuhime (hub scene, then her repeat line).
- **Necks + per-traveler growth + clan roles (2026-10-20, user):**
  - Necks: heads now sit on the collar (gen_sprites2d NECK_SIDE −2, NECK_FB −3, set per view in compose /
    compose_fb); the neck is a 3-row stub under the jaw (user: "look like E.T. from the front").
  - **Per-traveler growth** (`tools/traits.py`): parses the stats.md Lv 1 traits + schedules → traits/rings by level.
    - Each stat = the template curve (= the "average traveler" the enemy formula is fitted to) × the traveler's
      trait formula / the 8-traveler mean.
    - MATK = the template ATK curve × Int / Haruki's Int, × 0.55 for non-shugenja.
    - gen_data applies it to P100-P107. The companion Michio keeps the ATK↔MATK swap.
  - **Clan roles** (memory clan-battle-roles; traits.ROLE + plugin):
    - Crab most HP ×1.12, Lion HP ×1.18 + PATK ×1.12 (the hardest hitter), shugenja PATK ×0.8, Crane/Scorpion
      AGI ×1.16/1.17 (they vie for first).
    - Lv20: Natsuko HP 561; Shizue 468 and PATK 147; Haruki MATK 116 and SP 148; Mitsue AGI 100, Rensei 99.
    - Plugin: shugenja (Haruki, Michio) start with 2 VP and hold max+1 (`isShugenja`, `vpMax`).
    - Mirumoto: Gendo from Lv 22 strikes twice at 65% (verified on the dummy).
    - Scorpion denial: Mitsue's hits push the enemy to the end of next turn's order, and 20% "lose the thread"
      (their queued action is cancelled).
    - Mitsue skills: S142 Shuriken Fan (Lv8), S140 Poisoned Edge (Lv14), S141 Metsubishi (Lv22, Blind all).
      **TODO:** Misdirection, Vanish, Mask Change (need plugin mechanics).
- **Shoulders + side heads (2026-10-20, user: "faces should face more toward the feet... shoulders too high, shrugging"):**
  - "Toward the feet" = the way the feet point, not down (user correction). A lowered gaze (GAZE_DOWN) and a 1 px
    feature drop (LOOK_DOWN) were tried and are left off.
  - **Side views are now profiles** (gen_sprites2d `PROFILE`):
    - one eye moved forward (design x 17.5), no far eye;
    - the nose juts 1 px past the face's edge; the mouth sits forward (x 21.2);
    - an ear shade at the back of the cheek (when skin shows there).
    - The non-kit path (porcelain/reed/noh/death/stitched masks, glowing eyes) still draws the 3/4 eyes.
  - **Shoulders lowered and sloped:**
    - base_pose shoulder joints y 31 → 34 (elbows 36 → 37).
    - The torso tapers from the collar, anchored to the neck (`neck_top(P)`: side +2, front +3 rows), down to the
      shoulder line, so the collar stays under the chin while the shoulders drop about 3 rows.
    - Front arms, haori and cloak hang from the lowered line.
  - Regenerated: sprites, sidecast, human enemies, portraits, data, render. Snapshots M141/M142: 0 errors.
- **Water + invisible walls (2026-10-20, user: "they keep falling through the floor... a lot with water tiles"):**
  - **Cause:** liquid blocks aren't floor in RPG-Cobo; ground checks see only SOLID/PLANT/BARRIER blocks. Our water
    cells were water columns down to y 0, so anything that got onto water fell out of the world. The engine's own
    water "fin" stops a *walking or jumping* player at the edge (tested), but nothing else.
    - The real faller: `rt_follow` escorts. `snapBehind` teleported them 1.6 m behind the player's heading with no
      ground check, which after walking up from a bank is the river.
  - **Fixes:**
    - **RokuganMapGen:** water cells get a solid bed (spec `bed`, SAND); only the top block is water. Every open
      water cell is a no-entry barrier: `BlockWorld.bmp`, the engine's invisible-wall bitmap (BLK_BARRIOR fin mode
      1, always on). Cells with something solid over the water (the M103 pier) stay open. Spec `walls: [[x, z]]`
      (MapSpec.walls) adds hand-placed invisible walls; `barrier: false` turns the automatic ones off.
    - Water at y 0 has no room for a bed: the 2F garden pond moved to y 1. Only the M811 battle backdrop keeps
      y 0 water.
    - **RokuganField:** `::Rokugan.floorAt` (a floor sweep that rejects water and barrier cells) and
      `::Rokugan.nearestFloor`.
      - Followers snap only onto real floor near the leader's height: behind, then ±45°, ±90°, ±135°, in front,
        else the leader's spot. They also re-snap if they ever fall 3 m below the leader.
      - Player safety net: the last safe spot (checked 5×/s) is restored if she drops below y −1; with none, the
        nearest floor within 16 m (`[RT] RESCUE`).
  - **Test flag** `-rtwalk cdir,ms[,delay[,jump]]`: holds the stick (cdir 1-16, camera-relative; 9 = toward the
    camera) and logs `[RT] POS x y z landed` every 250 ms, jumping every `jump` ms.
  - Verified:
    - M103 quay and M102 tidepool: the player stops at the edge, walking and jumping.
    - M102 escort spawned facing inland: the cart and driver step sideways onto the sand instead of into the sea.
    - Drop into bedless water (M811): rescued to the closest shore.
    - Rebuilt all 44 maps; water counts M102/M105 2698, M103 2268 (35 under the pier left open), M141 1620,
      M143 32, M131 48.
- **Hub check (2026-10-20):** new `tools/runevent.py MAP ID PAGE [--vars ..] [--choice ..]` (`--list MAP` prints
  event ids/models/reqs) runs one event page via `-event` + `-rtfast` and prints its lines.
  - All Ch2 2F-4F hub pages run clean.
  - Fixed: Mutsuye's repeat line had her quoting Natsuko's own line. Kuhime/Akiko/Mutsuye repeat-line speaker
    labels now use family name first.
- **Ch2 boss barks + the Dance Ribbon (2026-10-20):**
  - **Barks** (RokuganHazard.sk; `::Rokugan.bark(key, chr, text)` floats the line once per battle, via `barkOnce`;
    `::Rokugan.member(given)`):
    - Natsuko's "Over here, you ugly heap of moss!" when the troll targets an ally;
    - the puppet's "Hush now. Hush." on No Pure Breaths;
    - Natsuko's "That's right. He's the one you want." when the open puppet draws the troll.
    - Verified 2/2 boss runs on auto with the real Ch2 party (all three barks fire once, troll sits down).
  - **Test flag** `-rtparty P123,P120,P124` (RokuganField launch wrapper): those players join at the leader's level,
    so `-battle M001 14` fights with the chapter's party (the test party is solo Natsuko now).
  - **Unicorn Dance Ribbon** (I123):
    - The storyboard has Keiyomi Barter it (Tamotsu's path action). Solo adaptation: talk to Keiyomi again during
      the hub; she gives it to the one who watched (new flag G231).
    - After S03, Shinjo O-Shito (2F, now a talk event) takes it home to the Ide: item removed, Honor +1, G228,
      then an after-line.
    - All pages run in-engine.
- **Guests: Octopath II "Call Guest" + four Crab Ch2 side stories (2026-10-20):**
  - **Why not party members:** the party cap is 4. In the hub Natsuko + Goro (+ Sachiko) already sit there, and
    Michio joins at S03. A 4th member would make Michio's memberop fail silently (ERROR 13126 "full").
  - **System:**
    - Battle command "guest" (RokuganBattle.sk, setting battlecmd7; it replaces Formation, which Octopath has no
      use for).
    - It fires the current guest's call skill: G232 is the guest number (a numeric gvar, type 2; as a bool it read
      every value as 1). `::Rokugan.GUEST_SKILLS` = [_, S143, S144, S145, S146].
    - Uses are shared by the whole party per battle: skill fields `rt_uses` + `rt_guest`
      (`::Rokugan.usesState`, RokuganAI.sk). The command greys out at 0 uses. Auto battle never calls guests
      (except `-rtguest`).
  - **Call skills** (gen_data `guest_skill`):
    - S143 Kitsu Takeo: Charge (all enemies, Yari, x1.3-1.4, 2 uses);
    - S144 Yogo Mai: Ward (party K022 DEF Up, 2);
    - S145 Ide Fujio: Scandalous Letter (K025 Scandalized, 1; see NEXT 2);
    - S146 Daidoji Sakura: Blank Scroll (party K024 Void Guard = MDEF +30%, new; 2).
  - **Side stories** (gen_maps `GUESTS`, `guest_npc`, `guest_join`; texts from sidestories/guests-07-12.md SS1,
    adapted for solo Natsuko):
    - Takeo (1F yard): a race → fight with 2 Matsu Braggarts (E239, EP431, gid 17 on M814).
    - Mai (1F cellar stair): the goblin prisoner confesses ("sky-eyes lady"; third stone safe). The catacombs'
      roller-trap scene echoes it if G234.
    - Fujio (3F): an ink/paper deduction among three suspects. The Yogo scribe is right; wrong picks can be retried
      by talking again.
    - Sakura (2F): a fight with 2 Daidoji Agents (E238, EP430, gid 16 on M816).
    - Losses use losefunc 1 (recover); talk again to retry. Done flags G233-G236.
    - Afterwards, talking to a guest again offers "Ask X to come along" (one guest at a time).
  - **Sprites:**
    - Guests EP382-385 (gen_sidecast CAST).
    - Side-story icon copies EP386-389 (`SS_ICON`, `badge()` stamps a gold "?" tablet over the head in every
      frame; the engine has no event balloons). Each guest is two talk events on one tile with opposite done-flag
      reqs.
    - Verified: all four stories (win and loss branches, Fujio's wrong pick); all four call skills fire with
      shared uses that stop at 0.
  - Goro and Michio (guests #7 and #12) already join through the main story, so they have no icons. Their SS1
    beats are covered by S01 and S03.
- **Crab Ch3 "Beyond the Wall" (2026-10-21):** production/crab-ch3.md + storyboard, all 8 scenes.
  - **Maps** (gen_maps "Crab Ch3" section):
    - M101 gate events (`ch3_gate`): Sachiko's chapter start (after G216), the quartermaster R113 (T3 stock,
      Jade Finger, Jade Pouch), the open gate, and S08 at dusk.
    - M170 trap tunnels (cave): the trap line; Squeak (G051) or Gonta (G015) joins at the far mouth; the point of
      no return.
    - M171 tar chasm (rope bridge over tar); M172 lava trees (b_sl_goblins, the hanging root → Fine Katana, a
      scout's bones → Hiruma Scout's Jingasa); M173 poppy fields (b_sl_onikage, the ridge, waystone 1).
    - M174 watchpost (the broken guard: mercy / carry → G248 follower); M175 Toshi no Kijo (Kage, S05; waystone
      2 after).
    - M176 the plain (hide roll 70%, 45% carrying the guard → b_sl_akutsukai; the Ryozo rider if G050); M177 road
      home (boss, Kage's choice → join P126 for the fight).
    - Backdrops M817 (Shadowlands) and M818 (the road home, the Wall behind).
    - Liquids: map_vox water #0 blue, #1 teal, #2 lava, #3 purple bog, #4 black tar (only 0-4 exist: #5+ crashes
      the game). The terrain catalog M094 is a dev map.
    - Render preset `rt_hd2d_shadow` (blood-orange sun, crimson haze, falling ash) for M171-M177, M817, M818.
  - **Taint** (memory: user wants it "known and available"):
    - Condition K026: stacks to 5, -6% max HP per stack, persists after battle, Jade weakness at 4.
    - Taint tiles: map.json `rt_taint` {blocks, pct} from gen_maps `TAINT_TILES` (stained earth T(3,7), scorched
      T(0), poppy floor T(5,3)); plugin `taintStep` rolls per step.
    - Cleansed by Jade Pouch (I130; 5 from Takakana; R113 sells) and Hiruma waystones (`::Rokugan.cleanseTaint`).
    - **Jade Finger** (A115, accessory, 1500 zeni at R113; user): its wearer can't be Tainted by anything
      (RPGPlayer.putCondition wrapper). Takakana tells you about it in S01, and the tutorial text names it.
    - Scout's Jingasa (A113) and Old Jade Bead (A106) halve the tile chance.
    - Verified: stacks 561 → 527 → 493 → 460 max HP at Lv20; the finger blocks tiles and Command the Taint.
  - **Boss: Oni no Kommei** (RokuganHazard.sk):
    - Every 3rd round it swaps two members' menus (skills via `hasSkill`, Attack via `getAttackSkill`, Talent) for
      2 rounds; auto battle follows the swap.
    - "The Other Face" (E248) is a separate target: Suki or kill it and the swaps stop. The Kommei Mask (A114, its
      drop) makes the wearer unswappable. The face falls with the Kommei.
    - Barks: "Which of you is which?" / "I'm the one hitting you." / "My other self!".
    - Command the Taint uses atkform `dst.PDEF+30+src.PATK*0.4` (at x0.35 its damage rounded to 0 = MISS = no
      status).
  - **Balance** (CH3_LV_SHIFT = -5 in gen_data; HPx tuned for Natsuko + 1 companion at ~Lv 26):
    - Kommei HPx 5.5 (design 10), face 0.8, maho-bujin 0.9, Ch3 warmongers 0.6.
    - Kage: Berserk Smash x1.5-1.6, 1 use, PATK +15%, PDEF -50%.
    - Lv26 auto: with Kage 7 rounds; without Kage (Natsuko + Squeak) a 13-14 round win with Natsuko at about half
      HP.
  - **New art:**
    - Kage without armour (sidecast kage_ch3, EP386; the guest badges moved to EP387-390).
    - Zombie / Maho-bujin / Moto Akutsukai / Oni no Kommei (EP432-435).
    - Onikage, Toothed Poppy, The Other Face (gen_monsters EP116, EP117, EP119); Ogre = troll tint EP118.
  - **Data:**
    - Flags G240-G261; players P125 Gonta, P126 Kage; enemies E240-E248; groups gid 18-21; skills S147-S153.
    - Items I130-I137, armour A112-A115, weapons W120-W123, store R113.
  - Verified unattended, 0 errors: every scene (Squeak / Gonta / nobody at the tunnel mouth, mercy / carry, hide
    fail + Ryozo rider, boss with Kage → S08 with the "Uncle?" line).
  - `say()` now runs `_clean()`: hand-written lines drop acting cues like the production-parsed ones.
- **See-through bubble (2026-10-21, user: "a cutout effect like a bubble around the player when they are behind
  things"):**
  - src/shader/vox.skfx (original in _tools/data_orig/vox.skfx): `rt_cut()` in the main block pass and a new
    `depthcut` program for the depth pre-pass (shadows keep the full geometry).
  - It discards dithered pixels that are nearer the camera than the player, above her feet (+0.35), and inside an
    ellipse round her on screen.
  - Data path: the plugin writes the player's feet to `env.worldpos` (uniform id WORLDPOS) every field frame in an
    `RPGStage.updateStageBody` wrapper; zero (battle, `-rtnocut`) turns it off. `ENV3MAT` = inverse view,
    `VMAT` = view.
  - Verified: the M101 gate strip behind Tomoe's office (the roof opens round her); no artefacts in open fields;
    the Toshi no Kijo ring wall opens.
- **Engine gotcha: at most 13 command-line arguments reach the game** (the rest are silently dropped).
  - Pack test flags: `-rt "walk 5,3500,3000;equip P100+4+A115;taint100;party P122"` expands to -rtwalk,
    -rtequip, -rttaint100, -rtparty (plugin.sk).
  - Test flags added: `-rtequip PID+slot+ITEM` (slot 4 = accessory), `-rttaint100`, `-rtnocut`.
  - `-debuglv N` sets the party level (runevent `--lv`).
- **Grinding, Squeak's sticks, Octopath bosses (2026-10-21, user):**
  - **Grinding:** enemy EXP was a flat 6+3*LV (a Ch3 foe gave 84 while Lv 24 → 25 needs 26,766). Now a foe pays
    4% of the EXP a traveler of its own level needs for the next level (RPGSystem.getExpByLV, expcurv [50, 40]).
    - A 2-3 foe fight at your level is about 10% of a level, so about 10 fights per level.
    - Bosses get x BOSS_EXP. Gold scales too. The engine key is lowercase `exp` (an uppercase `EXP` key is
      ignored).
  - **Squeak's memory sticks** (Enemies of the Empire, "Rememberers and Memory Sticks" p.113-117 + the shaman's Mend
    Name p.120). Any nezumi can use a stick, so no shugenja/MATK: heals scale with the target's max HP and Squeak's
    level. SP cost doubled (user):
    - Mend-Name Stick (heal 35%, Lv1, 44 SP); Armor Stick (DEF up, Lv8, 32); Warrior's Stick (ATK up, Lv12, 32);
      Sunlit Stick (party Blind cure, Lv16, 28); Life Stick (70% heal + Poison cure, Lv22, 80); Evil Stick
      (party DEF + E.DEF, Lv26, 96).
    - Squeak's SP: 55 at Lv10, 127 at Lv26 (he can't afford Mend-Name in Ch1 at Lv6).
    - AI heals rank by the skill field `rt_heal` (share of max HP) instead of parsing atkform.
    - Kommei swap bark "I don't know how to heal! ...Oh. Oh, that's nice." when a swap gives Natsuko a heal
      (verified: she healed with Squeak's Life Stick mid-swap).
  - **Octopath bosses** (`tools/gen_bossart.py`):
    - L5R wiki art (MediaWiki API; originals in _sources/wiki_art) is cut out, tinted (line art) or keyed (paint),
      pixelated like the user's 16-Bit-Style-Pixel-Art-Converter (_sources/pixelconv, MIT: downscale + ADAPTIVE
      palette), outlined, and animated with gen_enemy_art.animate.
    - Drawn at the cast's pixel density, about 3x a traveler.
    - EP120 Nezumi Shaman (Nezumi_Shaman_2.jpg, sepia), EP121 Troll (Troll_2.jpg, moss green), EP122 Moto
      Akutsukai (Onikage.jpg painted rider, GrabCut + hint boxes + smooth-sky filter + "keep" polygons for the
      hat, mirrored to face the party), EP123 Oni no Kommei (the two-headed Oni no Megada Diskwars art,
      green-keyed: the wiki's only Kommei image is a crowd scene).
    - Layout (gen_data BOSS_LAYOUT): the boss at back-left (x about -2.3, z +0.7), minions in front (x -0.4, z
      -0.7).
    - b_sl_akutsukai is now one big rider (HPx 3.2, EXP x2) + a zombie.
- **Crab Ch4 "The Fairest One of All" (2026-10-21):** production/crab-ch4.md + storyboard, all 7 scenes.
  - **Flow:**
    - M101: Hiruma Ryoichi brings the call after G255 (CHAPTER 4 card).
    - M146: the 6F hall hosts the wedding (S01, `ch4_wedding` hooked from castle_6f).
    - M151: the summer castle town, last free roam. It is kh_town with SNOW → GRASS2, T4 stall R114, the jade
      merchant, an inn, and the gate prompt "Night will fall".
    - M152: the siege yard at night.
      - S02: Takakana's orders; the guard's lines if G248. Sachiko (P120) and Goro (P123) join.
      - Six tampered trap tiles (-8% party HP each) are chalk-marked and harmless if G248.
      - b_siege_breach_a (gid 22: wolf-riders + warmongers); random encounters on the M810 backdrop.
    - M153: the cellars.
      - b_siege_breach_b (gid 23): the Cellar Ogre mini-boss + maho-bujin.
      - Plugin rule: undrawn by Razor's Edge, 60% of its swings hit the courtiers (G291). None hurt → Honor +1.
      - S03 the barrel, the stalk tutorial, a save shrine.
    - M154-M156: the dark castle (castle_floor rooms, cave render) — the stalk (`stalk_npc`):
      - Test with hot sake / a smooth "jade" stone / the jade-dust glove, then Accuse or Let pass.
      - A wrong or untested accusation, or letting Nashiko pass: Dread (G282) +1. At 3, Sachiko then Goro are
        knocked out (G283). They rejoin for the boss.
      - `split_up` junctions: Dread -1 once per floor (G287-G289), needs a companion.
      - Order: maid F1 → guard + Akiko F2 (Squeak in the vent if G051) → the lantern servant = Nashiko F3
        (G279 nashiko_unmasked).
    - M157: the deep tunnels (S05 chase; the blue flare choice if G217 → G281 flare_fired).
    - M158: the Wall top (S06 boss gid 24 Oni no Tsukakoro, S07 smoke north, the Kage choice → G285
      kage_told_truth or Honor -1; W124 Kage's Father's Tanto, a jade tanto). Then dawn in the summer town.
  - **Plugin** (RokuganHazard.sk):
    - Bounce Chain: 2-4 hits on different travelers; Razor's Edge pulls every bounce onto Natsuko (barks).
    - flare_fired: Crab archers volley the oni every round (3% max HP, bark).
    - The Cellar Ogre courtier rule.
  - **Data:**
    - CH4_LV_SHIFT -8 (foes Lv 34-37).
    - E250 Bakemono Wolf-rider (new gen_monsters sprite EP436), E251-E252, E253 Cellar Ogre (boss art EP124,
      Ogre.jpg mirrored), E254 Ogre, E255 Oni no Tsukakoro (boss art EP125, Tsukakoro_no_Oni.jpg, the victim's
      katana inpainted out).
    - Skills S160-S163; T4 gear W124-W128, A116, store R114; I138 Bone-cage Fragment; flags G270-G291.
  - **Boss art pipeline** now runs the user's converter itself: gen_bossart loads
    convert_to_16bit_style_pixel_art() from _sources/pixelconv/asciiartist.py (its demo call is skipped and
    .show() is silenced). Squares are padded, edge colours bled, palette 32, PIX = 1.4 (chunkier pixels, drawn
    1.4x).
- **Crab Ch4 finished + Octopath boss rules (2026-10-21, after the 99% stop):**
  - **Boss rules** (RokuganHazard.sk; user):
    - Bosses respawn minions: MINIONS table (Nezumi Shaman → Nezumi Warrior/Seppun Ryozo; Moto Akutsukai →
      Zombie; Oni no Kommei → Maho-bujin; Cellar Ogre → Maho-bujin). When every minion is down, the boss stands
      alone one round (the window), then raises them (HP, Resolve, Suki cleared, the dissolve run backwards).
    - Minion tricks: skills flagged rt_minion (S164 Blood Ward, S165 Shield the Master, S166 War Chant, S167 Grave
      Feast, S168 Rally) are aimed at the boss (or the most wounded ally).
    - Minionless bosses get a WARD (user: the condition must be something the player can actually do). Tsukakoro:
      non-Jade hits do exactly 1 (::Damage.finishDamage wrapper) until a Jade hit opens it for the round.
      - Jade is guaranteed: Jade Dust x4 cache in M157, R114 sells Jade Dust and jade spears, and Natsuko says so
        before the fight.
      - Auto battle now throws Jade Dust at a warded foe (polish pass below), but a jade weapon is still what wins.
  - **Balance** (auto, party of 3 at Lv 34 unless noted):
    - Tsukakoro HPx 24: 9-round win with a jade spear.
    - Cellar Ogre HPx 7 (atkx 1.6): 6 rounds; the bujin heal and shield, then respawn.
    - Nezumi Shaman Lv8 + Squeak: 5 rounds.
    - Kommei HPx 4.0, Natsuko + Squeak at Lv 27 without Kage: a 21-round win (was a loss at 5.5).
  - **Verified unattended** (tools/runevent.py, 0 errors): the call → wedding → summer town; S02 + Sachiko/Goro
    join; yard and cellar fights; courtiers hurt; S03; the stalk (pass, wrong accusation → knockout at Dread 3,
    split → Dread -1, Akiko + Squeak); unmasking → chase → flare fired → boss (volleys) → S07 → the whole truth →
    tanto → complete → M151.
  - **Tools:**
    - `tools/testbattle.py GID [--lv] [--rt] [--vars]` runs a -battle on auto and summarises it.
    - runevent now packs vars/choices/party/extras into `-rt` (13-arg limit).
  - Script fixes: the duplicate "toward the tunnels" line; "Oni No" → "Oni no" in narration; `(to X, ...)` cues
    stripped.
  - **The Crab path (Ch1-Ch4) is complete.** Next (ask the user): another traveler's chapter, or polish.
- **Crab polish pass (2026-10-21, user: "polish"):**
  - **Soft-lock fixed:** after Ch4 (G286) the summer town M151 was a dead end.
    - The M151 west road now leads to the Hida road M140 (115, 15).
    - The Hida road's east end goes to M151 instead of the winter town M141.
    - M151 got a KH signpost.
    - Fast travel: TRAVEL_ALT {"KH": G286 → M151}, read by `::Rokugan.travel` (altflag/altmap/altpos).
  - **Storyboard trades:**
    - Kaiu smith at the Wall gate (M101, after G216): trade the Kaiu Tetsubo Blueprint (I124) for a Kaiu Tetsubo
      (W120).
    - Kaiu smith in M151 (after G286): trade the Bone-cage Fragment (I138) for the new W129 Bone-cage Tetsubo (ATK
      138, price 0).
  - **Auto battle throws Jade Dust:** when a foe is warded (learned "immune") and the traveler has no Jade skill or
    weapon, one traveler per round throws I104.
  - **Companions fell too fast** (user). Sachiko and Goro used the sample curve (610 HP vs Natsuko's 868).
    - COMPANION_CURVES: both use Natsuko's trait curve, scaled. Sachiko: HP x1.35, PDEF x1.15, AGI x0.8 (1172 HP at
      Lv 34). Goro: HP x1.15 (998).
    - Sachiko learns **S169 The Mountain Does Not Move** (Hida Bushi R2, 3e core; self, 16 SP): puts K027 "The
      Mountain", which halves hits taken (RokuganHazard finishDamage).
    - The AI keeps any skill with an `rt_guard` field up against a boss (a foe with 4x its MAXHP) or when under 70%
      HP.
  - **Gear matters (user OK'd forcing the right gear):**
    - Tsukakoro with no jade weapon and 6 Dust: a loss after 28 rounds. Sachiko is last standing now (was 13
      rounds).
    - With the jade spear: a 9-round win, both companions above 75% HP.
    - M151 veteran (before the wedding night): "Steel just bounces off the big ones. Spend your zeni on jade."
  - Test flag `-rtitem I104x5,...` puts items in the bag.
  - runevent can't run villager NPCs (no pages); that's expected, not a bug.
  - **Rider art:** gen_bossart LIFT gamma per painted boss (akutsukai 0.62, ogre 0.85). The rider went from mean
    47/255 to 80.
  - **Squeak's Dark-ways** (Ch3 storyboard: reveals the map's chests). While P122 is in the party:
    - Arriving on a map pops "Squeak: N shiny-boxes here!" (unopened itemchest events only).
    - Spawned chests glint (FX020) every 2 s.
    - Code: RokuganField `darkwaysChests` / `darkwaysArrive` (called from the launch wrapper in RokuganBattle) /
      `darkwaysGlint` (from updateStageBody).
  - **Masked / glowing-eyed enemies in profile:** the gen_sprites2d draw_face fallback (non-kit faces) now draws one
    forward eye at ox+16 and drops the far eye. Reed holes, noh brows and mouths moved with it (`mo` offset). Cast
    faces are unchanged.
  - **Boss intro (Octopath):**
    - The boss enters with a white flash, a vertical quake, the SE111 thud, and a brush-ink name banner with an
      epithet (EP391-396, gen_bossart `banner()`, Georgia).
    - It shows over the battle stance and fades as turn 1 starts.
    - RokuganBattle wraps TurnBattleRunner.battleStart (BOSS_BANNER, by enemy name).
    - Previews: _art/preview/boss_banners.png, boss_intro_1500.png.
  - **Noticed, not fixed:** battle lighting darkens the big boss sprites in night or cellar arenas (the ogre reads
    muddy). They could be drawn unlit if it bothers the user.
- **Goro SS2 "The Bent Sword" + the rescue fix (2026-10-21):**
  - **The side story** (sidestories/guests-07-12.md #7). Goro's SS1 isn't used: he joins through the main story,
    as Kage's bodyguard.
    - M101 barracks (28, 40), with a "?" badge (gen_sidecast SS_ICON += goro, EP391).
    - Shown after Ch3 (G255) except while Ch4 runs (G270 to G286), and again after G286.
    - Goro joins at Lv 32 for b_ss_goro_troll (gid 25, M810).
    - E256 Wall Troll: Lv 32, HPx 6, weak to Jade/Fire/Katana; uses the wiki troll art EP121 (a mini-boss) and the
      banner EP456.
    - Reward: S172 Troll-Breaker (Katana, 3 uses, ignores armour: atkform adds dst.PDEF back), granted with
      `::Rokugan.learn("P123", "S172")`. That pushes an opt_getskill own option; the UPGRADES table in RokuganField
      makes RPGPlayer.udpateOwnLists drop S139.
    - G292 marks it done; his brother Hiruma Kenzo is new.
    - Verified unattended: the story, a won battle, learn, and "replaces S139: gone".
  - **Boss banners moved** to EP450-456 (EP391 is now Goro's badge). gen_bossart removes old banner entries.
    EXTRA_BANNERS covers mini-bosses that reuse a boss's art.
  - **The rescue loop** (user saw "falling into a tree with grey around him"):
    - The cause: safepos was global. After a battle, the spot saved in the M810 arena was used on M101: a tree,
      so a fall, a rescue to the same spot, forever.
    - safepos now belongs to its stage, and battle stages skip the net.
    - A second rescue within 3 s drops the spot and searches.
    - nearestFloor now wants **open ground**: the hit must be the column's top map block (not a tree or prop
      object) with solid blocks below. It also prefers floor within 1 m of the last walking height (lastgy), so
      not a roof beside the road.
    - Test flag `-rtdrop` (runevent `--rt "drop 1"`): verified on M101, M151, M157 and M154; each lands on ground
      next to the drop.
- **Hireables (2026-10-21; user: OT0/OT2-style limited-use followers; memory hireables).**
  The user also said to finish all the Crab content before other travelers.
  - **Roster:** `tools/hirelings.py`, shared by gen_sidecast (sprites EP387-392; the side-story badges moved to
    EP393-397), gen_data and gen_maps.

    | Hireling | Where | Price | Sumai | Charges | Action |
    |---|---|---|---|---|---|
    | Ashigaru Archer | M101 | 200 | 45% | 3 | Arrow Volley: Yumi, all enemies, ignores DEF |
    | **Kuni Shugenja** | M101 | 900 | refuses | 3 | **Earth Becomes Sky** |
    | Kaiu Engineer | M141 / M151 | 500 | 50% | 3 | Barricade: DEF + E.DEF, party |
    | Village Herbalist | M103 | 120 | refuses | 3 | Ginseng Tea: heal all 30%, cure Poison |
    | Hoshi Fisherman | M103 | 80 | 55% | 2 | Throw Net: K028 Netted, loses its next action |
    | Hida Veteran | M141 / M151 | 800 | 30% | 2 | Tetsubo Smash |

  - **Earth Becomes Sky / Jade:**
    - From 3e Prayers & Treasures, 5e core and Legacy of Disaster ("make boulders Jade with 2 Raises", the user's
      pointer).
    - The boulder never misses (hitform 999), ignores half of DEF, and puts K029 Prone (DEF down). A Prone target
      takes double.
    - **Boost 2+ = the 2 Raises:** the Jade element is added and the skill is renamed "Earth Becomes Jade"
      (`rt_jade_raise`, in RokuganBattle's boost code).
    - Verified: it opens Oni no Tsukakoro's ward, 3 hits for 1626 each.
  - **Flags:** G293 = the current hireling, G294 = charges left (both numeric). Charges are per hire, not per
    battle.
  - **Hiring:** pay zeni, or win Sumai (a loss costs Honor -1). Hiring someone new sends the current one home.
  - **Battle:**
    - Slot 7 "Guest" became **"Call"**: it lists the guest's action and the hireling's, with uses left.
    - The hireling stands in the back row (visual only: create3DObject behind *memberloc).
    - When a call runs, a charge is spent and the hireling pops its name. A call queued after the last charge
      fizzles.
  - **Field:**
    - One rt_follow event per hireling on every M100-M799 map, added in gen_maps make().
    - At 0 charges, the next field arrival pops "<name> heads back to <home>" and sets G293 = 0. The hire NPC is
      shown again (reqs G293 != n), and events re-check conditions every frame.
  - **Test flags:** `-rtmoney N`; `-rthire` (Natsuko on auto calls the hireling and Boosts 2 when she can).
  - Verified: hiring, the follower on M101/M103, going home, the back-row screenshot (_art/preview/hire_backrow.png),
    the fight.
- **Crab path completion pass, Ch1 (2026-10-21; user: "lets do one complete everything on a path at a time").**
  Checked against storyboards/crab-ch1.md. Path actions for travelers not yet playable (Charm, Bless, Pilfer, Duel,
  Discern, Eavesdrop) wait for those travelers.
  - **New monsters** (gen_monsters; bestiary names, so bestiary_drops gives the drops):
    - E107 Carrion Crow EP437 (Peck Eyes S179, Blind).
    - E108 Will-o'-wisp EP438 (Lure S180, Confuse; half damage from physical weapons).
    - E109 Wild Boar EP439 (Charge S181).
    - The Mamushi Viper got Venom Fang S182 (Poison).
  - **Encounters:**
    - M102 now matches bestiary F: goblins, tide crabs, crows, uncommon road bandit, rare wisp.
    - The **Egg Caves M130-M132 had no random encounters**; now beetles, vipers and goblins (M813, the Rumble
      meter applies).
    - The donjon M148 got its uncommon Yurei.
    - `tools/testbattle.py --map M102 GID` tests a map's own groups.
  - **Coast road** (`coast_extras`, day only):
    - The road sign.
    - The Athletics beach ledge: Bamboo Yumi W104 (G296).
    - The Hunting boar tracks: b_hunt_boars, gid 26, 2 Wild Boars; then 150 zeni and Herbal Salve x2 (G295).
  - **Hoshi-no-Ichi:**
    - The under-pier chest is now the Jingasa A102 (was a Tonic).
    - The storehouse lacquer box after Ch1: 200 zeni + Painted Egg I114 (G297).
    - The henhouse Herbal Salve x2 after Ch1 (reqs G054).
    - The cart driver no longer stands on the magistrate's door.
  - **Garrison shrine** (M101, 63, 10): Pray (cleanse Taint) and Meditate (MP).
  - **Gonta = hireling #7** at his fire (M104) once the camp is cleared (G015, not burned).
    - The fish reward I116 "Hidden Ones' Thanks" pays one free hire; then 600 zeni or Sumai 35%.
    - Landslide S183 (Earth, all enemies). The old "ask for Gonta" line is replaced.
  - **Event overlap scan** (any two events on one tile with a portal or touch trigger): only the intended M140
    pair remains.
- **Session end (2026-10-21), the last items:**
  - **Every chapter has back-row recruitables** (user): Ch3 Hiruma Scout #8 (M172, Jade Arrows), Kuni
    Witch-hunter #9 (M175, Purify: cleanses Taint, heals), Ch4 Kaiu Sapper #10 (M152 siege night, Trap Roller +
    Prone). New sidecast sprites.
  - **Hirelings don't scale with Natsuko** (user): `lv` per roster entry (the area's level) replaces src.LV in their
    atkform.
  - **Sprite id overflow bug:** sidecast entries 80+ had spilled into EP400, so the Road Bandit showed Goro's badge
    ("facing the wrong way"). `gen_sidecast.epid()` now continues at EP460+. EP400-436 humans/monsters, 437-439
    beasts, 450-456 banners.
  - New `tools/balance_encounters.py` (per-map party table, rounds, outcome, HP left).
  - Ch1 regular foes put on the foe_stats curve (see the RESUME POINT for the open follow-ups).
- **Balance pass, continued (2026-10-24):**
  - **Coast:** Tide Crab E105 to Lv 2, HPx 0.7. All five M102 groups now land in 3-4 rounds with 56-86% HP left.
  - **`foe_stats(..., vs=)` defender profiles** (gen_data `DEFENDER`). "avg" is the old curve. "crab" targets
    Natsuko as measured in-engine: HP 1.6x and PDEF 1.5x the average traveler, a hit taking ~10% of her HP.
    - Damage is subtractive, so from Lv 5 the "avg" foes did 0-4 to her. The cave fights and the boss were
      non-events.
    - The caves' E102/E103/E104 and the boss E106 (L7 HPx 7) / E121 Ryozo (L7 HPx 3) now use "crab". Before, they
      had hand stats from the first tutorial build: PATK 17, 900 HP.
    - The coast foes stay "avg". E100 also runs the Lv 1 tutorial beside a fragile Ryoichi.
  - **Enemy AI weights were never applied (game-wide).**
    - In RPG-Cobo, an AI cmd's `rate` picks the action and `rndwgt` is only target randomness. gen_data wrote the
      weights into `rndwgt` with every `rate` = 50, so all foes picked uniformly. It now writes `rate`.
    - The engine's `rate x rnd(0.3..1)` ordering also skews shares (60 vs 40 gives ~88%). RokuganAI overrides
      `TurnBattleRunner.chooseAICommand` with a weighted draw (key = rnd^(1/rate)).
    - Enemy heals go to the most wounded ally under 80%, or aren't chosen. RokuganHazard's minion retarget no
      longer heals a full-HP boss.
  - **Ch1 scripted fights re-verified** (testbattle now prints party HP left; balance_encounters shares its
    parser):

    | Fight | Result |
    |---|---|
    | gid 1 tutorial, Lv 1 | 3 rounds; Ryoichi 27/50 |
    | gid 7 nezumi, Lv 5 | 5 rounds; Natsuko 102/221 |
    | gid 8 beetles, Lv 6 | 5 rounds; 160/255 |
    | gid 9 nezumi, Lv 7 | 5 rounds; 261/288 |
    | gid 10 boss, Lv 7 + Squeak | 8 rounds; Squeak 125/182 |
    | gid 11 boss + Ryozo, Lv 8 | 9 rounds; Squeak 78/202 |
  - **Crab completion audit, Ch2-Ch4** (storyboards vs gen_maps). Ch3 and Ch4 match their storyboards. The
    blueprint trade is built: the Kaiu smith at the M101 gate, from G216. The older note calling it open was stale.
    Ch2 fixes (gen_maps):
    - New `shrine_rites(ev, x, z, intro, meditate, extra, reqs)`: Pray (cleanse Taint) and Meditate. It is the old
      garrison event, now shared.
      - Added to the Hida road waystation (M140) and the town's Hachiman shrine (M141); both were decoration only.
      - Added to the women's shrine (M147) after the chapter (G216), with "Light a lantern for Ide Keiyomi".
      - Keiyomi's body prop is now hidden once S03 has played (G229). Before, it stayed forever.
    - The deepest cell's post-boss chest is the **Troll Hide**, as in the storyboard; it was 400 zeni. New
      `item_named()` looks up bestiary-drop ids by name, since gen_data numbers them in table order.
    - Ch2 path actions for travelers not yet playable (Bless, Discern, Eavesdrop, Pilfer, Barter, Charm, Duel) wait
      for those travelers, as in Ch1.
  - **Full balance run (all chapter maps) after the AI fix:**
    - Ch1 is ok: caves 53-97% HP left; a few goblin groups are easy.
    - **Ch2 and Ch4 were trivial:** 1-2 rounds, 100% HP. The curve assumes a foe falls to ~2 party actions, so
      2-4 travelers wipe a group in a round. The Ch2/Ch4 parties are Crab tanks, too.
    - Ch3 (Natsuko + Squeak) was ok to easy.
  - **Area tuning** (gen_data `AREA`, after the AI table): eid -> (HP x, defender profile, ATK x). Values are
    re-measured with balance_encounters.

    | Area | Tuning |
    |---|---|
    | Hida road | 1.7 / crab / 1.3 |
    | Donjon | 3.0 / crab / 1.4 |
    | Shadowlands | 1.3 / avg / 1.3 |
    | Siege | 2.4 / crab / 1.3 |

    - `hum()` and the generic-humans loop record each foe's designed HPx in `HPX`.
    - Shared generic foes get **area copies** instead of global changes: E257 Mountain Bandit, E258 Border Patrol
      and E259 Yurei for the Hida road. Same names, so the same drops. M140's ENCOUNTERS use them. Other paths will
      reuse E201/E213 with their own parties.
  - **Measurement bug:** in `[RT] dmg ... N (HP a/b)`, a/b is the HP *before* the hit. `party_hp` took it as the
    result, so every HP-left figure before this point was optimistic by one hit per member. Fixed in
    testbattle.party_hp, which now applies N (heals are negative; MISS counts as 0). Re-measured: the siege
    wolf-riders leave ~87% (it read 100%), Ch1 gid 7 leaves 42% (it read 46%).
  - Groups for 3-4 member areas now have 3-4 foes (donjon, catacombs, siege, some Shadowlands). gen_maps has a 4th
    formation spot, (-2.4, 0.25), as in the M001 raid.
    - AREA HP: donjon 2.2, siege 1.8, Shadowlands zombies 1.0 (Grave Feast dragged fights to 9 rounds).
    - Road yurei come in a pair; the coast bandit is alone.
  - S047 (the warmongers' buff) still had its sample-data Japanese name, アタックアップ, on screen. It is now
    "War Cry". A scan of skills used by our foes and travelers, conditions and shop stock found no other Japanese
    names.
  - **Second measurement bug (engine quirk):** `emitOption` stops at the first handler that returns true, and
    `opt_putcond` returns true from "condchk".
    - So a hit that puts a condition (Prone, Poison, Blind, Terror...) never reached the `[RT] dmg` logger on
      condchk. Damage and conditions applied; only the log line was lost.
    - The logger now runs on "recoil", emitted right after; HP is still the pre-hit value there.
    - This also explains the "silent" Kaiu Sapper roller: it was hitting (448, then 593 on the Prone target).
    - Gotcha for future options: anything else hooked on condchk is skipped after a putcond, too.
  - **Hireling tests:**
    - Kuni Witch-hunter (M175): hired; Purify heals the party, 3 -> 0 charges.
    - Kaiu Sapper (M152): hired; Trap Roller deals damage and knocks Prone, 2 -> 0 charges.
    - Hida Veteran: Tetsubo Smash ok.
    - runevent takes money through the packed `-rt`: `--rt "money 2000"`.
  - **Ch2 events verified in-engine (runevent):**
    - M140 #7 Pray; M141 #19 Meditate; M147 #8 (G216) the lantern.
    - The M150 chest is I260 Troll Hide.
  - Scripted fights after area tuning (testbattle, storyboard levels):

    | Fight | Result |
    |---|---|
    | gid 1 tutorial, Lv 1 | Natsuko 37/79, Ryoichi 26/50 |
    | gid 13 donjon goblins | Michio 226/431 |
    | gid 18 SL goblins | Squeak 322/491 |
    | gid 22 breach A | Sachiko 855/1172 |
    | gid 23 cellar breach | 6 rounds; Goro 720/1020 |
- **Crane Ch1 "Heaven's Glory" build plan (2026-10-24; Kakita Rensei).**
  - Sources, read in full:
    - production/crane-ch1.md and storyboards/crane-ch1.md;
    - research/and-does-not-descend.md;
    - bosses.md §2 b_boss_yasurugi (L8 HPx 7, Resolve 8, duel phase then a skirmish);
    - bestiary F "Crane coast & Beiden forest": Road Bandit I, Grey Wolf, Wild Boar; uncommon Hungry Ronin; rare
      Will-o'-wisp.
  - **Structure (OCTOPATH-FIT §1, choose 1 of 8 starters; memory solo-with-companions):** a new game opens on a
    starter-choice prologue map, M099.
    - Natsuko leads to M100 as before.
    - Rensei swaps P100 for P101 and goes to M200. The field avatar is the first living member.
    - The recruit variant waits for a world map that joins the regions.
  - **Id ranges:**

    | Kind | Ids |
    |---|---|
    | Maps | M200-M219, backdrops M820-M822 |
    | Flags | G300-G339 |
    | Enemies | E300+ |
    | Skills | S400+ |
    | Items | I140-I159 |
    | Gear | W130+ / A117+ |
    | Shop | R115 (peddler, Lion T1) |
    | Guests | 5 Kitsuki Seigen "Evidence" (2 uses), 6 Matsu Kiku "Battle-Joy" (1 use); G-1 one active guest |

  - **Slices** (each one playable and tested before the next):
    1. The prologue choice, M200 Kakita Academy, S01 and the b_bokken_bout tutorial.
    2. M201 road_west (S02, Seigen joins; the Hunting boar).
    3. M202 Pleasant Eaves: S03 Ebisu (Charm / steel / coin), the town NPCs, the peddler, the inn, Kiku, a
       hireling.
    4. M203/M204 the forest: rope points R1-R3, b_forest_bandits_a with surrender, the clearing, save.
    5. M205 the bandit village: b_forest_bandits_b unless spared, S05 tea, the inn mat banter TB-crane1-a.
    6. M206-M209 the castle: S06 Depura, the Seoko / Tatanko Charms, S07 the dawn choice.
    7. b_boss_yasurugi: the duel phase plus wiki boss art; S09 and the endings.
    8. Encounters and balance (Rensei + guest + hireling), hirelings, the completion audit.
  - **Slice 1 DONE (verified in-engine):**
    - **M099 prologue:** the starter choice. Natsuko goes to M100 (START_NATSUKO). Rensei adds P101, drops P100,
      sets G300 and goes to M200. START is now M099. gen_maps builds every map except DEBUG_MAPS, and M099 is
      padded.
    - **M200 Kakita Academy:**
      - S01 from the production text, with the bout tutorial lines and battle gid 27 b_bokken_bout on the M820
        courtyard backdrop.
      - Rensei's chests (Rice Ball x3, Travelling Clothes); the closed smith; the gate portal to M201 (G301).
    - **Iaijutsu stacks** (RokuganBattle):
      - Focus +1, up to IAI_MAX 3.
      - Strike x(1 + 0.75 per stack), critical only at full Focus.
      - The Talent command lists Focus / Strike between 1 and 2 stacks.
      - `::Rokugan.iaitutor` pops "Patience." on an early Strike.
      - S121 is now a 1.0x base.
    - **Bout:** Focus x3, Strike x3.25 crit 367, won in 4 rounds; Rensei 25/47.
    - **Sprites:**
      - 17 Crane Ch1 cast entries (the sensei to the twin girl). Imuro is a big peasant, not "heavy", which draws
        armour.
      - Human enemies Senior Student and Forest Bandit at EP500/501. gen_human_enemies `epid()` continues at
        EP500 after 36 entries, and its `EP` key map is used by gen_data.
      - gen_sprites2d has a `bokken` weapon.
    - **Test flags:** `-rtlead P101` (another starter leads; `--rt "lead P101"`) and `-rtiai` (auto Focus to full,
      then Strike). testbattle PARTY_NAMES covers Kakita / Matsu / Kitsuki.
    - TRIM_DIR also trims "Montage:". The M001 scripted groups are labelled "Scripted (...)".
  - **Slice 2 DONE (verified in-engine):**
    - **M201 road_west:**
      - S02 runs on arrival (G333): Sanae, then Seigen rides up and joins as guest 5 (GUESTS[5], G302).
      - The palanquin EP356 follows Rensei until S03 (G303). A new gen_props `palanquin()`, black lacquer, also
        waits at the academy gate after S01.
      - The "Four days of road" fade (G334); Rice Ball x2; 60 zeni.
      - The Hunting hollow: gid 28 b_hunt_boar_west, Boar Meat x2, G323.
      - The east portal goes to M202, event 1 (slice 3).
    - **M821** is the Beiden road / forest battle backdrop.
    - **Guests:**
      - S400 Kitsuki Seigen: Evidence (2 uses, no damage). The plugin marks every foe's weaknesses known and pops
        each foe's queued move ("NEXT: Pack Bite"); the enemy's turn pick is in `.skill`.
      - S401 Matsu Kiku: Battle-Joy (1 use, Bo, x3.0-3.2).
      - Plugin GUEST_SKILLS has slots 5 and 6.
    - **New foes:**
      - E302 Grey Wolf, EP440: a gen_monsters `grey_wolf`, the wolf-rider's wolf without the rider.
      - S402 Pack Bite: the plugin's enemy pre-command branch adds +25% per other same-named wolf alive.
    - **Rensei solo balance:**
      - A new DEFENDER "crane" = (HP 0.8, PDEF 0.83, a hit takes 8%), measured at Lv 2.
      - road_west has its own Lv 2-4 copies via gen_data `relevel(src, dst, lv)`, which keeps the shape ratios,
        with AREA (0.65, crane, 1.0): E303 wolf Lv 2, E304 bandit Lv 2, E305 boar Lv 3, E306 ronin Lv 4,
        E307 wisp Lv 3.
      - Without them a Lv 2 Rensei died to two Lv 4 wolves in 2 rounds.
      - Result: all ok (60-92% left, 2-3 rounds). The boar hollow leaves 86/90.
    - balance_encounters PARTY entries can be (lv, rt string, rtvars); M201 = (2, "lead P101", "G232=5").
    - `say()` strips a trailing capitalised stage direction ("Yes, my lady. (He does not stop.)").
  - **Slice 3 DONE (verified in-engine):**
    - **M202 Pleasant Eaves.** S03 (G335) plays as:
      - the production head;
      - the Ebisu choice: Charm, steel (Honor -1) or coin (-50), setting G304 to 1/2/3;
      - the tail: Heaven's Glory I140 (key);
      - Kiku joins as guest 6 under the G-1 pick, and the other guest waits at the inn (`inn_guest`, swap by
        talking);
      - G303 set; objective: the forest.
    - **Rensei's Charm:**
      - Talk / Charm (n%) / Leave with `with_charm`; `::Rokugan.roll`.
      - A failure costs village standing (G330, starts at 3). At 0 the village refuses until "Buy the room a
        round" (50 zeni) at the inn.
      - Ebisu at 70% marks the waterfall glade (G322). Torishigawa's Charm always fails, a story hint.
    - **Hirelings:**
      - The roster takes `charm`, `leader`, `town`, `charm_line` and `won`. `hire_npc` offers Charm instead of
        Sumai for Rensei; the "Coin first, X-sama" line uses the leader's family name.
      - #11 Old woman: Green Ronin's Blessing, heal all, 2 uses, 100 zeni or Charm 45%, M202.
      - #12 Ronin Yojimbo: Desperate Cut, 3 uses, 300 zeni or Charm 25%, M202 inn. New sidecast `h_yojimbo`.
      - #13 Lantern Twins: Lantern Lure, blind all, 3 uses, 150 zeni or Charm 60%, M205 after G313.
      - Skills S187-S189.
    - **Places:**
      - R115 peddler (Lion T1).
      - The inn (30 zeni).
      - The woodpile chest (Antidote x2).
      - The headman's storehouse after S03 (tax ledger I141 + 150 zeni, G324).
      - The shrine rites.
      - The Lion checkpoint east turns you back. The north portal goes to M203 (G303).
    - The sidecast spilled past 80 entries, so Ebisu and later cast are EP460+. All ids are recomputed by the
      generators.
  - **Slice 4 DONE (verified in-engine): Mountains' Cloak Forest.**
    - **M203 (night):**
      - The S04 intro (G338). Ropes R1 (G307) and R2 (G308), the cut revealing the pit.
      - Walking into the pit without cutting R2 costs 10% HP and drops into the pit chamber (Eye Drops x2, G328),
        with a rope back up.
      - R3: the ghost lantern starts b_forest_bandits_a (gid 29, M822). Then G310, and G311 spared unless G336.
      - The waterfall glade (G322 from Ebisu's Charm): Morishu's Inro I142 + Old Whetstone (G337).
      - Chests: Rice Ball x2, Jingasa.
    - **M204:** the clearing scene (G339 then G312: Adoru, Yasurugi, the letter), a save shrine, 120 zeni, a Bamboo
      Yumi, and the old Kakita training post (Kozuka, G340). The trail goes to M205 after G312.
    - **M822** is the forest-at-night backdrop. The forests use RSET night.
    - **Surrender** (RokuganHazard; enemy field `rt_surrender` = 30%):
      - A foe at or under 30% gives up: escaped, the plugin dissolve, the production barks "Mercy! We're
        farmers!" / "...Then put the sticks down."
      - Follow-up hits on him are STAYED (Boost multi-hits).
      - The engine's "dying" option event (return true = no death) stays any lethal blow except the
        KILLING_BLOWS: "Iaijutsu: Strike" and "Battle-Joy". Killing one sets G336.
      - The "victory" event clears `escaped` on surrendered foes, so mercy still pays exp.
      - Result: plain fighting spares all three; full Iaijutsu kills.
      - E301 Forest Bandit: Lv 5, AREA (1.6, crane, 0.7).
    - **Crane profile:** DEF factor 0.83 became 0.95. Rensei's PDEF is 0.93x the average by Lv 5, and the
      subtractive formula zeroed the hits.
    - **Forest copies:** E308 bandit Lv 5, E309 boar Lv 6, E310 ronin Lv 6, E311 wisp Lv 6 (HP 1.0, ATK 1.4);
      E312 wolf Lv 5 (HP 1.0, ATK 1.0; Pack Bite already stacks).
    - **Final forest balance:** 3-5 rounds, 50-95% HP left, all ok. The road is still ok (68-92%) after the
      profile change.
    - Script fixes:
      - "(tiny cough)" becomes "-cough-": it's heard, and Seigen's "Ghosts don't cough" needs it.
      - Event scripts use `Math`, not `::Math`.
  - **Slice 5 DONE (verified in-engine): M205, the Green Ronin's village.**
    - **S05 (G341):** the head, then the gate. If spared (G311), the bandit lets them through. Otherwise spears and
      b_forest_bandits_b (gid 30): they surrender, G314.
    - Then the tea with Imuro and Sariko, the runner's news, G313, objective: the castle.
    - **TB-crane1-a "Spilled Tea"** at the inn mat, while Kiku is the active guest (G232 = 6), once (G327).
    - Terraced paddies, the palisade gate, the granary (Rice Ball x4 + Imuro's line), shrine rites, a free inn mat,
      both guests' swap spots, and the Lantern Twins hireling (#13, after G313).
    - The road down goes to M206 (slice 6).
  - **Slices 6-7 DONE (verified in-engine): the castle, the boss, the endings.**
    - **M206 hall** (castle_floor, an interior): the S06 hall scene (G343), then to M207.
    - **M207 corridor:**
      - The Depura / Tama scene (G344, then G316 depura_seen).
      - Seoko Charm 55%: G317 seoko_charmed, opens the side gate on route 3.
      - Tatanko Charm 45%: G318. Castle standing is G342; `with_charm` takes `place`.
      - The guest room runs S07 (the four routes set G319, G329), then a rest-and-save.
    - **Routes:** route 1 goes to M208 cells (gid 32, backdrop M824); routes 2-4 go to M209 yard (gid 31,
      backdrop M823).
    - **S08:**
      - Route 4 plays the production duel text. Routes 2-3: Yasurugi steps out of the crowd. Route 2 adds the
        present guest's "He means to kill him..." line.
      - All routes get DUEL_RULE, which also hints the tanto: "A Kakita turns katana aside...".
    - **S09:**
      - Route 4: Goroso's settlement and Heaven's Glory, which answers his hand at Rank 2 (not built yet).
      - Routes 1-2: Morishu dies, the sword goes to the vaults.
      - Route 3: Morishu escapes with the sword.
      - Then the road east, the chapter card, the guests leaving (G232 = 0) and G321. The player lands on M201
        at (100, 15).
    - **Boss E313 Kakita Yasurugi:**
      - L8, HPx 4.5 (7 was a slog for a solo Ch1), Resolve 8, weak Yari/Tanto/Air, Katana EDR 50.
      - Steal A117 Yasurugi's Spare Hilt-wrap (+10 CRI).
      - Wiki art: the generic "Kakita Duelist" line art, cropped to the upper body. gen_bossart has `CLEAN` to
        drop specks. EP126, banner EP457 "The Silent Blade".
    - **The duel** (RokuganHazard):
      - He Focuses 1/3, 2/3, then turn 3 Kakita Iaijutsu S403 at ~70% of Rensei's HP. Kiku cries "Rensei!".
      - If Rensei's Iaijutsu Strike lands first, "DUEL WON" and his strike is lost.
      - Then S404 First Stance (~28% HP, atkform) and S405 Way of the Crane (acts first next turn).
      - At 25%, Seigen's "His left side, boy" (reveals weaknesses if he's the guest).
      - Engine gotcha: `dmgrate` multiplies *after* DEF is subtracted, so signature blows need `atkform`
        (dst.PDEF + dst.MAXHP*k). The formula roughly halves it, so k is about twice the share wanted.
    - **Balance:** at Lv 8 with the Kozuka, Kiku and the old woman hireling (iai 2): won in 9 rounds, 129/186 HP.
      Plain auto-katana loses, as intended.
    - **Test hooks now play sensibly:**
      - `-rtguest` calls the guest from turn 4.
      - `-rthire` works for any leader; a healing hireling is called only under 50%.
      - `-rtiai [n]` Focuses to n stacks, only during turns 1-3.
    - Peddler R115 also sells the Kozuka (W102): the counter to the boss's Katana resist, told and buyable.
    - In-engine screenshots: _art/preview/battle_backdrops.png (gids 31, 27, 29).
- **User feedback (2026-10-24): the duelist art looked horrible (redo from scratch); the buildings don't scale with
  the cast. Both done.**
  - **Building scale:**
    - Measured in-engine: the doorway was 3 blocks (1.5 m), shorter than a character, the walls 2 m, and the
      roofs about twice the wall height.
    - `building()` now adds STOREY_EXTRA = 2 blocks to every storey; doorway 4 blocks (2 m); shoji 3 tall; the
      upper storey on two-storey buildings is 4; torii h 7 became 9.
    - Every chapter shares the kit, so Crab and Crane match by construction.
    - Screenshots of M101, M103, M141, M147, M200 and M202 look right, with no misaligned gates.
  - **Yasurugi's art:**
    - Thin ink line art never survives pixelation. He now wears the wiki's painted "Kakita Bushi": white-haired,
      calm, Kakita blue, on a white ground.
    - New gen_bossart mode "white": flood the paper from the edges at a stricter threshold (240) and keep the
      painting's colours. ERASE paints out the "Crane Bushi" caption.
    - Height 190 px, about 2.7x the cast. Candidates are kept in _sources/wiki_art/cand_crane2.
  - **gen_render was never run this session.** gen_data re-registers every map, which drops gen_render's battle
    camera, markers, lighting presets and weather.
    - Fixed: `tools/regen.py [--maps] [MAP ...]` runs gen_maps (optional), then gen_data, then gen_render. **Use it
      instead of calling gen_data alone.**
    - gen_render's lists now include the Crane maps:
      - field M200-M202, M205, M209;
      - night M099, M203, M204;
      - caves M208, M824;
      - battle M820-M824;
      - night battle M822.
    - gen_maps register() also applies RSET to battle backdrops that have an entry.
    - Screenshots after the fix: the night forest has mist, and the battle camera framing is right.
- **Crane Ch2 "The Iron Cranes" build plan (2026-10-24, next session; user said "continue").**
  - Sources, all read in full:
    - production/crane-ch2.md and storyboards/crane-ch2.md;
    - scripts/crane-ch2-the-iron-cranes.md;
    - research/of-family-and-honor.md (Round One).
  - **Defaults chosen (the user may overrule):**
    - Goro, the stand-in, is a short-term party member (P123) during the chapter, so the camp split has a cost.
      At the end he becomes a Call guest ("+Goro joins the roster", if not recruited).
    - Rank 2 is a per-traveler unlock at chapter end. Heaven's Glory becomes an equippable weapon then.
  - **Canon looks** (wiki API wikitext; WebFetch gets HTTP 402, so use curl on api.php):
    - Hida Yakamo: "a huge brute of a man with rough shoulder-length hair and a mustache"; tetsubo + katana;
      young in 1122.
    - Daidoji Uji: "slight but wiry, dark complexion, black hair and brown eyes, a short topknot never dyed white;
      rarely wore his armour".
  - **Ids:**

    | Kind | Ids |
    |---|---|
    | Maps | M210 GS port town, M211 the castle's lantern garden, M212 land_bridge, M213 Yasuki Yashiki, M214/M215 border camp 1/2, M216 coast road (academy to GS), M217 Sanae's rooms, M218 Miyako's chamber, M219 Yasuki hall |
    | Backdrops | M825 border meadow, M826 causeway |
    | Flags | G346+ |
    | Enemies | E314+ |
    | Skills | S406+ |
    | Hirelings | #14+ (skills S190 is taken; use S191-S199) |

  - **Slices:**
    - A: cast and enemy sprites, the boss art (Daidoji generals), flags.
    - B: the coast road + the GS port town + S01 in the garden.
    - C: land_bridge (tide rule) + Yasuki Yashiki (S02 Sumai/Charm).
    - D: S03 split / together.
    - E: the camp (sentries, Uji, Yakamo).
    - F: the boss (charmed generals freed by Suki).
    - G: S06-S07, banter, Rank 2, balance, hirelings, audit.
  - **Crane Ch2 slice A DONE: cast, foes, boss art, mechanics.**
    - **14 cast sprites:** Miyako, Kakita Yumi, Eriko, Ikoma Tadaka, the Daidoji general (field), Kuni Miyubi,
      Masakazu, Kuni Akuja, Uji (canon look), Yakamo (canon look), Chuto, a Daidoji sailor, a Suitengu priest.
    - **Generals' boss art** (EP127, banner EP458 "The Iron Cranes"):
      - The wiki's painted bust "Daidoji Kikaze 2": white topknot, sword raised, Crane blue, on a pale wall.
      - Tried and rejected: the dark "Daidoji Iron Warrior" (mush) and the busy "Iron Warrior (TCG)"
        (holes and junk).
      - gen_bossart paint hints can take `redkey` (red, warm-wood and green keys). Hint boxes are in crop
        coordinates. `CLEAN` has iron_crane.
    - **Foes:**
      - E314 Seduced Sentry: Lv 22, rt_charmed 1, sprite EP502.
      - E315 Daidoji General: Lv 25, HPx 3, Resolve 4, weak Yari/Tanto/Water, PATK x0.85, rt_charmed 2.
      - Groups: 33/34 b_camp_sentries_a/b and 35 b_boss_iron_cranes (BOSS_LAYOUT of three), on the new M825
        border-meadow backdrop.
    - **Plugin (RokuganHazard):**
      - `onBroken` (called from breakEnemy): a charmed foe is FREED on Suki and leaves alive, still giving exp.
        Production barks for each freed general, including "Eriko: Right here, you fool." if eriko_close.
      - Miyako's hold heals each charmed general 10% a turn ("Don't let them hurt you, my love").
      - Killing a general sets G359 (the worse epilogue). G360 counts the freed.
    - **Flags:** G346-G370 (numeric: G353 camp_split, G356 uji_won_by, G360 freed count, G370 GS standing).
    - **Test:** Lv 22, Rensei with the Kozuka + Goro: won in 9 rounds, 2 freed and 1 killed (Goro's katana has no
      weakness). **TODO:** a port-town Yari or Water hireling as the told-and-buyable counter (e.g. a Daidoji marine
      with a boarding pike).
  - **Crane Ch2 slice B DONE (verified in-engine):**
    - **The way in:** the Kakita Academy's south gate (DOOR_EV ("M200", "south"), after G321) leads to M216, the
      Crane coast road (border encounters; chests: Ginseng Tonic x2, 300 zeni), then to M210.
    - **M210 Garden Under Shadow City:**
      - The harbour and piers; the inn (60).
      - R116 Daidoji Armoury (Crane T2); R117 fish market.
      - Kakita Yumi's studio: Charm after the dinner. Charm standing here is G370.
      - The harbour master gives the Tide Chart I143 (G363); the harbour office box (Fine Sake, G372); the docks'
        chests; Suitengu shrine rites.
      - Hirelings: #14 Daidoji Marine (Boarding Pike: **Yari**, the told-and-buyable counter to the generals;
        700 zeni or Charm 40%) and #15 Suitengu Priest (Tide Blessing: heal all, cure Poison). Skills S191/S192.
      - **The chapter icon:** the castle gate guard (after G321) sets G346 and goes to the garden.
    - **M211 the lantern garden:**
      - The S01 intro (G371).
      - Free mingling: Charm Yumi (G350) or Eriko (G349, eriko_close).
      - Talking to Tadaka plays his question, Miyako's staged assault and his death, then "Next day" (G348
        tadaka_lie_heard, G347). Back to the port by the land-bridge road.
    - **Border row** (the coast road; Rensei alone, Lv 20): E316 patrol 21, E317 tide crab 21 (HP 0.75),
      E318 glory-hungry bushi 22, E319 sword-for-hire 23, E320 yurei 23 (HP 0.7, ATK 0.8), all with the crane
      profile.
      - Balance: patrol 58%, crabs 73%, bushi 65%, sword 78%, yurei 65%.
      - Backdrop M826 is the Crane coast.
    - **Parser bug fixed** (affects every chapter): `script_scene` dropped wrapped dialogue/narration lines (35 across
      the production files; 7 in Crab Ch2, e.g. "...nobody climbs there twice | by choice."). A wrapped line now
      joins the previous NAME:/NARRATION: message unless it looks like a speaker, a direction or a list item.
      Everything was rebuilt with `regen.py --maps`.
  - **Crane Ch2 slice C DONE (verified in-engine):**
    - **M212 the land-bridge:**
      - S02 at the GS bridgehead (G377): Natsuko's branch if she's in the party, else Goro joins (P123, levelled to
        the leader) with a recruited / not-recruited line.
      - **Tide rule:** the first bridgehead asks "Wait for low tide?" (G376); the far one resets it. The Tide Chart
        changes the wait text.
      - The tide pool: Crab Shell x3 + Pearl (via `item_named`, G364); Herbal Salve.
    - **M213 Yasuki Yashiki:** the inn, R118 (Crab T2), the Kuni shrine rites, the warehouse (Jade Dust x4 +
      500, G366); the Crab road north is turned back. **M219 the Yasuki hall:** S02 (G378, then G351).
    - **Encounters:** the bridge has its own two-traveler copies E321-E325 (HP 1.3-1.8, ATK 1.3): 80-94% left,
      3-5 rounds. The coast road keeps E316-E320 (solo Rensei).
    - **Bug fixed (affects the whole game):** `in_party()` always returned true. The engine's `array.find` returns
      false, not null, when nothing matches, and the old test was `!= null`. It now uses `!!`. The Crab chapters
      were unaffected only because Natsuko is always in the party.
    - `join()` levels the companion to the party leader (it used P100's level).
    - `-rtlead` logs the member list.
  - **Crane Ch2 slices D-F DONE (verified in-engine):**
    - **M217 Lady Sanae's rooms** (castle_floor, a door from the garden: DOOR_EV ("M211", "rooms")):
      - S03 (G379, then G352). Goro, who travelled with Rensei, says the "same trick" line himself.
      - The split / together choice sets G353 (1/2). The story then cuts to the night camp.
      - A rest-and-save at the writing table.
    - **`partner_says(text % name)`** names the Crab partner (Hiruma Natsuko if she's in the party, else Hiruma
      Goro) in narration. `natsuko_here(then, else)` branches dialogue the same way.
    - **M214 the night camp:**
      - Entry (G380): on split, Goro leaves (leave P123) and returns at dawn.
      - b_camp_sentries_a (G354). A Charm prompt (55%) on a Crane sentry skips b_camp_sentries_b (G355).
      - Uji's tent: argument, or Tadaka (needs G348), sets G356. Then Yakamo: live if together, Goro's report if
        split (G357).
      - The quartermaster's wagon chests. Encounters from the solo border copies.
    - **M215 the ridge at dawn:** a save shrine at the foot (F-7). S05 (G381) runs b_boss_iron_cranes, then G358
      and the freed-count epilogue line. The Daidoji War Fan A118 only if all 3 are freed (G382).
    - **Sentries:** AREA E314 (0.6, crane, 0.85), since after a split Rensei walks the camp alone. Fights: 3 rounds,
      54-60% left.
      - Charmed sentries (rt_charmed 1) are woken, not killed, by any non-signature lethal blow, with the
        "The lady said..." bark. Generals (2) stay killable, which is the worse epilogue.
    - **Bug fixed (since Ch1's surrender):** escaped (freed or surrendered) foes were still targetable and soaked
      attacks. A global `isCommandTarget` wrapper excludes `escaped`, and the auto AI's foe list skips them.
      Fights got 2 rounds shorter.
    - Camp balance: patrol 47%, bushi 82%, sword 68%.
    - Boss scene with Goro + the Marine hireling + the Kozuka: won, 1 freed / 2 killed by auto-battle.
  - **Crane Ch2 slice G DONE (verified in-engine): S06, S07, Rank 2, Goro as a guest.**
    - **The boss's end:** the scene cuts to M218, Doji Miyako's chamber (castle_floor).
    - **S06 (G383, then G361):** Rensei's door, plus Natsuko's (Squeak if G051 nezumi_friends, else Sachiko and
      Ryoichi) if she's in the party. The refusal has both partner versions; then Miyako flies off as a white bird.
    - **S07** (an autorun in the port by the bridge road, G384): the reports, then either Natsuko's gift exchange
      or Goro's farewell.
      - Goro leaves the party and joins the **guest roster** (GUESTS 7, G368): S406 "Hiruma Goro:
        Troll-Breaker", 2 uses. Plugin GUEST_SKILLS slot 7.
    - **Chapter card, then G362.**
    - **Rank 2 (G369):** narration only (no Rank system yet).
    - **Heaven's Glory:** the key item I140, if still held after Ch1's route 4, becomes **W130 Heaven's Glory**
      (Katana, PATK 96, CRI +15).
    - S07's trigger sits at the END of the port's events (the castle gate must stay event 5; an assert guards it).
  - **Iron Cranes fight redesigned after an in-engine check.** Three identical general busts stacked at the top-left,
    heads cut off by the screen, square-cut like cards. Now Octopath-style:
    - **Doji Miyako** looms at the back-left. Art EP127 is the wiki's painted "Doji Ayano": white hair, **blue
      eyes** (Nashiko's tell), pale teal robe. Banner EP458 "The Woman in White".
    - **E326** (rt_watcher): untargetable for players (an isCommandTarget wrapper), and the auto AI skips her. She
      only Waits; her hold heals the generals ("Don't let them hurt you, my love" now comes from her). Once no other
      foe is left fighting she leaves ("How tiresome."), which ends the battle.
    - **The generals:** E315 uses a new human-enemy sprite "charmed_general" (iron-grey Daidoji armour, glazed pink
      eyes), regular size, in front. BOSS_LAYOUT 35: Miyako (-2.3, 0.5), generals in front.
    - **New gen_bossart mode "coolkey"** (COOLKEY per boss) for a cool figure on a warm, saturated ground. The ground
      is warm and over a saturation threshold, plus dark wood, plus skin-toned wood outside the face/hands column
      and above the shoulders. Then the largest blob, closed and hole-filled.
      - Why: GrabCut's smooth-sky filter deleted her smooth robe and hair. Measured HSV: walls hue 6-15 / sat
        175-219; skin, hands and scroll sat 132-152.
    - The rejected Kikaze-bust entry is gone from BOSSES; the Nashiko true-form painting is kept for the finale
      (_sources/wiki_art/cand_crane5).
    - Test: won in 9 rounds (Rensei 270/371, Goro 600/716), 1 freed / 2 killed, and Miyako left the ridge.
- **Crane Ch3 "The White Squid" build plan (2026-10-24).**
  - Sources, all read in full: storyboard, production, scripts/crane-ch3-the-white-squid.md and
    research/the-edge-of-treachery.md.
  - **Party:** Rensei solo, plus a Call guest (Seigen, Kiku or Goro, swapped at inns and the ship's cabin) and a
    hireling. No story companion: Tessai helps with his ship (the storm broadside) and Ryohei is an enemy or
    released.
  - **Ids:**

    | Kind | Ids |
    |---|---|
    | Maps | M220 crane_port, M221 ship_deck (hub: the cabin is an inn/save/swap; ship's master shop; sea chart), M222 cove_fort, M223 temples_of_sun, M224 storm_sea, M225 heavenly_sheen_isle, M226/M227 squid_shrine_1/2 |
    | Backdrops | M827 ship deck, M828 cove/beach, M829 sea-cave shrine |
    | Flags | G385+ |
    | Enemies | E327+ |
    | Skills | S407+ |
    | Items | I144+ |
    | Conditions | new K044 "Charm: Evasion" (PEVA +30); charms also use K020 ATK Up and K040 Regen |

  - **Route:** the Crane coast road M216 gets a side exit to the Crane port (after G362).
  - **Sailing:** the sea chart lists nodes the story has revealed (Cove Fort, then Temples of the Sun, then the
    south isles via the storm). Each leg runs 1-2 roll-picked sea encounters, then arrival.
  - **Sea row:** Wako Raider (E217), Sea Serpent Eel (new beast), Tide Crab; uncommon Mantis Corsair (E218); rare
    Umibozu Shade (storm).
  - **Gimmick, the fake charms** (plugin):
    - Chihaya starts with one (evasion).
    - Katsuo hands one per turn to a pirate or himself: ATK / evasion / regen.
    - Breaking the wearer (Suki) shatters the charm and stuns them for a turn. Stealing waits for Mitsue.
    - The Asahina Ward-paper accessory (A119) halves charm buffs on enemies.
  - **Bosses with wiki art:** Chihaya (mid-boss), Yosuke (storm, + pirates x2), Katsuo (boss), Ryohei (with Katsuo
    if refused; boss art or a big sprite).
  - **Slices:**
    - A: cast, foes, art, conditions, flags.
    - B: the port (S01 + S02 Tessai choice, shops, path actions, hirelings).
    - C: the ship hub + sailing + the sea table.
    - D: Cove Fort + Chihaya.
    - E: the temples (S04, ward-paper).
    - F: storm + Yosuke.
    - G: the isle (S06 Ryohei choice, tribute screen) + the shrine 1-2 (Tessai's chests, the back door, the save) +
      Katsuo.
    - H: S09 + balance + audit.
  - **Crane Ch3 boss art DONE** (gen_bossart):
    - **Chihaya EP128:** the wiki's painted "Shinjo Bushi" on white; the new `HUE_SHIFT` turns Unicorn purple into
      sea teal.
    - **Yosuke EP129:** "Ronin_3" (the painted "Ronin Bushi" plate); ERASE removes the caption.
    - **Katsuo EP130:** "Iuchiban 2" (white robes, bloody blade). coolkey katsuo (warm, sat > 70, val < 150) keeps
      his skin and hair against the skull wall. The new `WHITEN` (pale_skin) makes him the albino.
    - Banners EP520-522: "Who Walks on Oars", "Captain in the Storm", "Maker of True Lies". (EP459 is free;
      EP460+ is the cast.)
    - Candidates are in _sources/wiki_art/cand_crane7-9. Ryohei gets a regular-size sprite (he fights beside
      Katsuo).
- **Crane Ch3 slice A (part 1) DONE (2026-10-24); wrapped up mid-slice at the user's request.**
  - **Sources re-read in full:** production/crane-ch3.md, storyboards/crane-ch3.md, scripts/crane-ch3-the-white-squid.md,
    research/the-edge-of-treachery.md, plus the Ch3 rows of rules/bosses.md and rules/bestiary.md.
  - **Spec numbers from bosses.md and the bestiary:**

    | Battle | Level | HPx | Resolve | Weak | Drop / Steal |
    |---|---|---|---|---|---|
    | Chihaya (mid-boss) | 31 | 5 | 7 | Yumi, Air | Tadanobu's Letters / Pirate Charm (+evasion) |
    | Yosuke + pirates x2 | 33 | - | 7 / 3 | Katana, Water | - |
    | Katsuo (boss) | 35 | 10 | 12 | Jade, Katana, Fire | White Squid Pearl (Water accessory) / Blood-ink Brush (E.Atk+) |
    | Ryohei (with Katsuo if refused) | 34 | 5 | 8 | Katana, Bo | - |

    Katsuo's maho pays 5% HP per cast and Taints on hit.
  - **Sea beasts** (gen_monsters, after grey_wolf): EP441 `sea_eel` (Sea Serpent Eel: a curved body with a dorsal
    fin, rising from a splash) and EP442 `umibozu` (Umibozu Shade: a dark head and shoulders, pale eyes, mist).
  - **Ch3 cast** (gen_sidecast, 14 sprites + face kits):
    - tessai, shipmaster, shinken, clerk, asahina (priest), netmender, charmseller, courtier (Doji), porter,
      drunksailor;
    - field sprites for chihaya, yosuke, katsuo (white hair, coral eyes) and ryohei (Mantis green, nunchaku).
    - The Daidoji marine reuses `sailor` and the fishwife reuses `fishwife`.
    - The porter uses the peasant build, because "heavy" draws armour.
  - **EP id fix (gen_sidecast.epid):** side-cast index 120+ now goes to EP540+. Without it, the cast overflowed into
    the human enemies (EP500+) and banners (EP520+).
    - The side-story "?" icons moved from EP488-492 to EP542-546. `regen.py --maps` was run, so the maps use the new
      ids.
    - Free id ranges: EP505-519 for human enemies, EP523-539 for banners.
  - **Sprite kit:** new weapon "nunchaku" (side view: two sticks on a chain; front/back: one stick hanging); its
    STYLE is "slash".
  - **Human enemy** "ryohei" = EP504 (gen_human_enemies), for the refused-offer boss fight.
  - **Next, in order:**
    1. The exp-loop fix above.
    2. **gen_data, the rest of slice A** (all of these ids are confirmed free):
       - **Conditions:** charms K044 Evasion (PEVA +30, valtype "supply"; PEVA is a 0-100 score), K045 Fury (PATK
         +30 totalrate), K046 Mending (regen 8, copied from K040). Warded halves K047-K049 (+15 / +15 / 4). K050
         "Shattered" (skips actions, rem_turn 3, so one turn past Suki's 2). K051 "Slowed" (AGI down, for Umibozu's
         Wave Wall). COND_BIT goes up to bit 51; keep below 53.
       - **Skills S407+:**
         - S407 Boarding Hook (wako);
         - S408 Strike of the Cliff's Edge (corsair);
         - S409 Electric Coil (eel; K006 Paralysis);
         - S410 Wave Wall (umibozu; all players, Water, K051);
         - S411 Oar Dance (Chihaya; `atknum` 2);
         - S412 Rally the Crew (Yosuke; K020 on all allies);
         - S413 Captain's Cut (atkform signature);
         - S414 Blood Ink (Katsuo; K026 Taint, `rt_maho` 5% HP cost);
         - S415 Nunchaku Flurry (Ryohei; `atknum` 3);
         - S416 Cover the Brother (Ryohei; rt_minion K022).
         E217 and E218 have no skills yet.
       - **Enemies:**
         - bosses: E327 Chihaya (EP128, rt_charm K044), E328 Yosuke (EP129, rt_broadside), E329 Yosuke's pirates
           (rt_charm), E330 Katsuo (EP130, rt_charmer), E331 Ryohei (EP504), E332 shrine pirates;
         - sea row: relevel copies E333 wako L30, E335 tide crab, E336 corsair L32; new E334 eel (EP441) and E337
           umibozu (EP442; physical half, weak Fire/Void);
         - shrine row: E338-E341.
         Solo Rensei, so bosses and copies use the "crane" AREA profile. Start with HPx: Chihaya 4, Yosuke 4,
         Katsuo 6, Ryohei 3.5, then tune.
       - **Items:**
         - keys I144 Tadanobu's Letters, I145 the Emperor's Lacquered Screen;
         - I146 Ward-paper Strip (a caltrop-style item on all enemies, remconds = the charm bits);
         - after `bestiary_drops`, turn I237 "Sea Salt" into a Taint cleanse (by name; a new item with the same
           name would renumber the I2xx drops).
       - **Gear:**
         - A119 Asahina Ward-paper;
         - A120 Scorpion Silk Armour (body, T3);
         - A121 Chihaya's Charm (PEVA +10);
         - A122 White Squid Pearl (Water resist);
         - A123 Blood-ink Brush (MATK);
         - A124 Asahina Robes;
         - A125 Sailor's Oilskin;
         - W131 Kakita Masterwork Katana (108);
         - W132 Daikyu-pattern Yumi.
       - **Stores:** R119 port armoury (Crane T3), R120 port chandler, R121 ship's master (Oilskin, Sea Salt), R122
         Asahina charm-house (Robes, Ward-paper Strip, Jade Pouch = the told-and-buyable Taint counter).
       - **Battle groups:** 36 b_midboss_chihaya (M828), 37 b_storm_yosuke (M827), 38 b_boss_katsuo (M829: Katsuo +
         2 pirates, Ryohei released), 39 b_boss_katsuo_ryohei (Katsuo + Ryohei + 1 pirate). Add BOSS_LAYOUT and
         BOSS_EXP entries for them.
       - **Flags:** G385+.
    3. **Plugin (RokuganHazard, the same pattern as Miyako's hold):**
       - start charms from `rt_charm`;
       - Katsuo gives one charm per new turn: to a foe without one, preferring the others over himself, random type,
         the warded version if anyone wears A119. Bark: "Here, brother...";
       - a break with a charm removes it and puts K050, with the "My charm!" or "How rude" bark;
       - `rt_maho` HP cost with the "very good ink" bark;
       - Katsuo's 25% barks;
       - Tessai's broadside on turn 2 if `tessai_ally`;
       - the K050 skip in RokuganBattle.onSkillChange;
       - BOSS_BANNER entries for Chihaya (EP520), Yosuke (EP521) and Katsuo (EP522).
    4. Slices B-H as planned above.
- **Crane Ch3 slices A-C DONE (2026-10-29, verified in-engine).**
  - **Exp bug fixed:** the gen_data scaling loop covers E100-E399 and skips `rt_watcher`. Crane foes now pay like
    the rest of the game: the border Patrol E316 pays 791 exp (was 69), a Daidoji general 2,329.
  - **Data (gen_data):**
    - **Conditions:**
      - Charms K044 Evasion (PEVA +30, "supply"), K045 Fury (PATK +16), K046 Mending (regen 8); warded halves
        K047-K049.
      - K050 Shattered: skips actions for 3 turns, one past Suki.
      - K051 Slowed: AGI -30%.
      - Fury is small on purpose: damage is 2.1×ATK − DEF, so +30% ATK had roughly doubled the pirates' hits.
    - **Skills:**
      - S407 Boarding Hook (E217 and its copies);
      - S408 Strike of the Cliff's Edge (E218);
      - S409 Electric Coil;
      - S410 Wave Wall;
      - S411 Oar Dance (atknum [2, 2]; atknum is a [min, max] pair);
      - S412 Rally the Crew (DEF up: ATK up stacked with Fury broke the fight);
      - S413 Captain's Cut;
      - S414 Blood Ink (rt_maho 5);
      - S415 Nunchaku Flurry;
      - S416 Cover the Brother (rt_minion);
      - hirelings S193 Daikyu Shot (hitform 999: it never misses, even against the evasion charm) and S194 Storm
        Gust (Air, all enemies).
    - **Enemies:**
      - bosses E327 Chihaya (L31, HPx4, AGI x1.5, rt_charm K044, steal A121), E328 Yosuke (L33, HPx4,
        rt_broadside), E330 Katsuo (L35, HPx6, rt_charmer, drop A122 / steal A123), E331 Ryohei (L34, HPx3.5,
        ATK x0.75);
      - crews: E329 Yosuke's pirates (L32, hpm 0.7, atm 0.6, rt_charm K045) and E332 Katsuo's (L34, 0.6 / 0.55),
        renamed "White Squid Pirate", given Wako loot after bestiary_drops;
      - sea row: E333 Wako L30, E334 Eel L31 (EP441), E335 Tide Crab L30, E336 Corsair L32, E337 Umibozu L34
        (EP442; physical half);
      - shrine row: E338-E341.
    - **Items and gear:**
      - I144 Tadanobu's Letters, I145 the Emperor's Screen, I146 Ward-paper Strip (all enemies, strips charms);
      - I237 Sea Salt is now a Taint cleanse;
      - A119-A125, W131 Kakita Masterwork (108), W132 Daikyu-pattern Yumi.
    - **Stores:** R119 port armoury, R120 chandler, R121 ship's master, R122 Asahina charm-house (Jade Pouch).
    - **Flags:** G385-G407 (G404 = Crane port Charm standing, numeric).
    - **Battle groups:**

      | Groups | Fights | Backdrop |
      |---|---|---|
      | 36-39 | Chihaya, Yosuke, Katsuo, Katsuo with Ryohei | Yosuke on M830; the rest on M826 until M828/M829 exist (auto-fallback) |
      | 40-43 | sea fights | M827 |
      | 44 | Umibozu | M830 |

      Fallback rule: a group keeps its backdrop if gen_maps has a builder for it, otherwise it uses M826. (map.json is
      rebuilt from the template inside gen_data, so checking map.json there doesn't work.)
  - **Plugin:**
    - **RokuganHazard, the false charms:**
      - starting charms from rt_charm;
      - Katsuo gives one charm per turn to a foe without one, his crew first and himself last, never to a foe
        that is broken or Shattered. Anyone wearing A119 means the warded version;
      - a break removes the charm and puts K050;
      - rt_maho costs HP;
      - Tessai's archers loose on turn 2 when G387 ("broadside": no ship's guns in Rokugan);
      - barks: Chihaya's taunt and "Paintings don't miss"; Katsuo's 25% line plus Rensei's "Then I won't kill
        you" (on the hit, via the new onRecoil hook, because one Boost can take him from half to dead);
      - "How rude" comes from Katsuo only; other wearers say "The charm - it was supposed to-!".
    - **RokuganBattle:** the K050 skip in onSkillChange; BOSS_BANNER entries for Chihaya (EP520), Yosuke (EP521) and
      Katsuo (EP522); the recoil case calls ::Rokugan.onRecoil.
  - **Tests** (solo Rensei with Heaven's Glory, auto-battle, no guest, hireling or items):

    | Fight | Lv | Result |
    |---|---|---|
    | Chihaya | 31 | won, 9 rounds, 91/522 left (her charm makes most cuts miss; she never broke without Yumi/Air) |
    | Yosuke | 35 | won, 5 rounds, 118/557 left |
    | Katsuo | 35 | won 41/456 in one run, lost narrowly in another (he was at 2 HP) |
    | Katsuo + Ryohei | 35 | lost (the harder branch, by design) |

    - Verified: the shatter (forced with Resolve 1: SUKI, then "shattered", then "loses its action (Shattered)"),
      Tessai's volley, and the per-turn charms.
    - Still to test: the Ward-paper halving.
  - **Slice B, M220 the Crane port** (from the coast road M216's shore path at (60, 9), after G362):
    - **Chapter start:** the Doji servant at Sanae's door plays the chapter card and S01, then the save prompt and
      the docks objective.
    - **Docks** (after G385): the fishwife, drunk sailor, net-mender and charm-seller give the production lines. The
      Daidoji marine tells the counter: "Arrows, though. Or a good wind."
    - **Tessai:** S02 plus the choice (G387 ally, G388 done, G389 Cove Fort revealed).
    - **Shinken's clerk:** Charm 55% (G405; standing G404; amends at the inn, 80 zeni).
    - **Services and loot:** inn (80) with guest swaps 5-7; R119, R120; chests (1000 zeni, Eel x2, Pearl x2,
      W132); Suitengu shrine rites.
    - **The ship's master** at the west pier boards you (after G388).
    - **Hirelings:** #16 Tsuruchi Archer (on the docks; 900 zeni or Charm 45%) and #17 Moshi Wind-caller (by the
      shrine; 800 zeni or Charm 50%). Both are told counters to Chihaya (weak Yumi, Air).
    - **Ships are built from blocks** (`ship()`): hull, deck, mast, sail furled on its yard. A raised sail had
      hidden the docks.
    - **Parser:** "SHIP'S" now becomes "Ship's", not "Ship'S" (all chapters).
  - **Slice C, M221 the ship (the hub):**
    - S01's "On deck" banter on the first visit (G386);
    - R121 from the ship's master;
    - the cabin: rest and save;
    - guest swaps 5-7 on deck;
    - the chart table: one menu per story stage, listing only nodes whose maps exist (SEA_NODES). Each leg is one
      roll-picked fight plus a second at 50% (Corsair 15%, crabs 30%, else Wako or Eel + Wako), then landfall.
    - Measured at Lv 30 solo: 63% HP left after a Wako pair, 68% after two crab fights.
    - Backdrops M827 (ship deck) and M830 (the deck in the storm, a night backdrop).
  - **Bug found and fixed (my own new code):** `battle(mapid, gid)` looks the group up in the encounter list of
    `mapid`. A missing group counts as an instant win (RPGMain.enterBattle), so scripted fights must say "M001"; the
    backdrop comes from the group's own mapid. Every older call already used M001.
  - **Waiting on other travelers:** Discern (fishwife, charm-seller), Eavesdrop (drunk sailor), Barter (net-mender:
    Storm Kama), Pilfer (charm-seller: the real White Squid charm), Duel (Daidoji marine: War Fan), Bless (Doji
    courtier: Courtly Grace), Sumai (porter: the decoy ship).
  - **User report, fixed:** in the ship-deck battles the combatants were sunk into the floor. Battle backdrops put
    fighters at height 0, and I had raised the deck to 2. **Rule for every backdrop: the floor the fighters stand on is
    height 0;** only scenery rises above it. The storm deck M830 is also off the night-lighting list, because the fog
    hid Yosuke's boss art. Re-checked with snapbattles 40 and 37: everyone is visible on the deck.
- **Crane Ch3 slice D DONE (2026-10-29, verified in-engine): M222 Cove Fort and b_midboss_chihaya.**
  - **The map:**
    - the landing (west), where the ship's master takes you back aboard;
    - the white ship moored on the mooring rope, with Chihaya standing there;
    - the palisade with its gate, the pirate store (Ginseng Tonic x2), and the lookout (Athletics: Pirate Charm x2,
      G408);
    - a drag-marks sign (Danger 30-33).
  - **S03:** walking up to the rope plays the scene (touch, G390). The intro, then a tutorial line (break her to
    shatter the charm; weak Yumi, Air), the battle (group 36, backdrop M828), the aftermath, Tadanobu's Letters
    (G391), then Temples revealed (G392) and the objective.
  - **Encounters** (backdrop M828; Lv 30 solo): Wako pair 87%, tide crabs 86%, eel + wako 71%, corsair 85%.
  - **Tutorial fix:** Chihaya is Resolve 4, not bosses.md's 7. One hireling could never break 7 shields: 3 charges
    is 3 weak hits, and Rensei alone has no Yumi or Air. Daikyu Shot and Storm Gust now hit twice per call.
    Measured: either hireling breaks her on the 2nd call (shatter, then "Shattered") and Rensei ends at about 72% HP.
  - **Bug fixed:** Electric Coil used K006 Paralysis, which is deadtype 1 (counts as defeated) and never wears off.
    On a solo traveler that is an instant game over (the measured "LOST at 91% HP"). It now puts K052 "Shocked", a
    Sleep copy that lasts 1 turn. **Rule: no enemy skill may put K006 or K011 while a chapter is solo.**
  - The "index link does not exist in null" exception in snapmaps logs is the engine's window-resize code. It also
    appears in old Crab logs; harmless.
- **Crane Ch3 slice E DONE (2026-10-29, verified in-engine): M223 the Temples of the Sun.**
  - **The map:** sea steps and the boat (back aboard); the white temple; R122 the Asahina charm-house (the jadeclerk
    sprite); the pilgrim inn (60); the sun shrine rites; the Bless-locked offering box (waiting for Haruki).
  - **S04** (the priest, after G391): the production text, then A119 Asahina Ward-paper plus an explanation line,
    then G393 and G394 (the south isles are revealed).
  - **After S04 the priest names the Taint counters:** jade from the charm-house, sea salt from the ship's master,
    and the ward-paper.
  - **Ward-paper verified:** in Katsuo's fight with A119 in accessory slot 4, the crew got K047 (the warded charm),
    and Rensei won with 142/490 HP (41/456 without it).
  - The test equip hook takes a list: `equip P101+0+W130,P101+4+A119`.
  - The sea chart's third entry sails there: fight(s), then landfall at block (6, 16).
- **Crane Ch3 slices F-H DONE (2026-10-29, verified in-engine). The chapter is complete.**
  - **M224 the storm (night field map):**
    - The first sail to the isle goes through it (sea_chart `leg`, until G395). S05 plays as an autorun (G413):
      the Orochi beat, Yosuke, a counter hint, group 37 on M830, then dawn and on to the isle.
    - The rare Umibozu was moved off this leg. A 30% roll had put a full fight right before the boss with no heal,
      and Rensei died. It is now a 10% roll on later trips to the isle.
  - **M225 the Isle of the Heavenly Sheen:**
    - Ryohei under the white flag. S06 plays on touch (G396), with Accept (G397) or Refuse.
    - The wrecked Doji crate gives I145 the Emperor's Screen (G398; F-7).
    - The hidden cove (68, 22): with G397, Ryohei's back door goes straight to M227's inner door (F-2).
    - The cliff path leads to M226. Encounters: shrine-row copies on M828.
  - **M226 the shrine, front (cave):**
    - S07 at the outer gate (G399), then a save prompt; the tide-pool beat (G409).
    - Tessai's two chests (G410-411, F-1): his men already have them open if allied (G387, and Tessai is standing
      there: "My cook's knives!"), otherwise Fine Katana / 1500 zeni.
    - Other chests: Ginseng x2, Sea Salt x3, and in the drowned-shrine dead end Eel x3 + Pearl.
    - Encounters on M829 (with umibozu 6%).
  - **M227 the inner shrine:**
    - The inner-door save (F-4).
    - Katsuo; Ryohei too if he was refused.
    - S08 (touch, G414): the tutorial line, then group 38 (released) or 39 (refused), then G400. S09's first beat
      (binding Katsuo, G401) follows, then to the port.
    - Katsuo's paint box after the boss (Fine Sake x2, Poison Kit; G412).
  - **S09 at the port** (autorun after G401, G415): Shinken takes the credit; "Adequate"; the screen line (in the hold
    if G398, else still on the island); the brothers' line if released; the chapter card (G402, G403).
  - **New rule (plugin, `rt_captain` on Yosuke and Katsuo):** when the captain falls, the rest of his side surrender
    and leave, and still count for exp. Before this, Katsuo's charmed crew kept fighting on their Mending charms and
    killed a Rensei who had already beaten the boss.
  - **Fixes:**
    - Narration doubled epithets ("Yosuke the Bold The Bold"). full_first now treats a name already written out in
      full (any case) as named, and fixes its case.
    - Captain's Cut dropped from 22% to 18% of max HP; Ryohei's ATK multiplier from 0.75 to 0.65; the isle's eel copy
      E340 HP x0.85.
  - **Boss results (Lv 35, Ward-paper, Tsuruchi hireling, auto-battle, no items):**

    | Fight | Result |
    |---|---|
    | Katsuo, Ryohei released | won 85/456 |
    | Katsuo, Ryohei refused | lost (Katsuo at 620), so harder by design; won 118/490 with Kiku's guest Call and 208/490 with Goro's |
    | Yosuke (Lv 33) | won 52/535 and 33/535 with the archer; 244/535 with Moshi |

  - **Encounters (Lv 33 solo, HP left):**
    - isle: wako 68%, corsair 85%, eels 48% (before the trim);
    - shrine: wako 76%, corsair + wako 63%, eels 60%, umibozu 64%.
  - **Static check:** 0 problems. The check now also covers every scripted battle group, in every chapter.
  - **Audit against the storyboard:** every scene, map, chest and finding (F-1 to F-7) is in. Two deviations:
    - Chihaya's Resolve is 4, not 7 (so the tutorial can be won).
    - The Umibozu is in the shrine's encounter table generally, not only in a "flooded hall".
  - Waiting, as listed in slice B. The Asahina offering box waits for Bless (Haruki).
- **Crane Ch4 "The Play No One Performs" DONE (2026-10-29, every scene and fight run in-engine).**
  - **Sources, all read in full:** production/crane-ch4.md, storyboards/crane-ch4.md,
    scripts/crane-ch4-the-play-no-one-performs.md, 05-chapter-outlines (Ch4), kata.md (Watchful Falcon), bosses.md,
    bestiary D.
  - **Route:** a new sea-chart node, Kyuden Doji (SEA_NODES, revealed by G403 = Crane Ch3 complete). The ship's boat
    lands at the harbour steps.
  - **Maps:**
    - **M228 the castle town.** The castle gate guard plays the chapter card and S01, then the save prompt, then on to
      Sanae's rooms. The castle-approach lane (x 47-61) must stay open.
      - Shops: R123 Doji silk house, R124 Kakita sword gallery, R125 apothecary (Oni Ichor = Fire).
      - Inn (120, amends 150; standing G416) with guest swaps; Amaterasu shrine rites; chests (Ginseng x3, Fine Sake
        x3, Doji Mon Charm).
      - Path-action NPCs just talk until their travelers exist.
      - The rehearsal hall door (after G425); the east road to the dueling ground (after G430).
    - **M229 the court:** S06 autorun after G430 (G439). Its stair leads to the archives; a door to M230.
    - **M230 Sanae's rooms:** a save table; S04 autorun after G426 (G440).
    - **M231-M233 the archives** (castle floors with shelf runs, wall=DARKWOOD):
      - M231: the censor-monk gate (Charm line, or Watchful Falcon; G418 opens the way down).
      - M232: the fixed b_archive_spirits fight (touch, G419); A128 mantle, Kansen Mist x2, the steward's diary
        dead end (I149, G436); a save alcove.
      - M233: lectern 1 (plain), lectern 2 (cipher: Watchful Falcon), shelf nine (touch) with b_archive_guardian
        then the play I147 (G425), lectern 3 + margin note (after G420). Each reading is G422/G423/G424 plus
        G421 += 1 (play_known_scenes, numeric).
    - **M234 the rehearsal hall (S03, G426):** Mitsue's lines if P105 is in the party; 3 timing cues and 2 picks
      score G438 (0-5); G427 (good) at 4 or more; then morning and S04.
    - **M235 the dueling ground:** the court on the veranda. S05 is an autorun (G430) with battle 47 (losefunc 1).
      - Win (G431): "the foot didn't hesitate".
      - Loss: "...Adequate", and if the play wasn't handed over, Masanori takes it (G429, F-2).
      - Then the court and S06: Sanae's question (G432; G433 = the Empire), the blank scroll, the real play back if
        Rensei lost it, A126 Father's Hilt-wrap, the card, G434.
  - **Timing cue (plugin RokuganField):** cueStart() / cueEnd(ms) on a frame clock (the sum of updateSteps dt, in ms;
    a 700 ms wait logs about 716). `Date().getTime()` only has whole seconds. `::Date` doesn't exist in event threads,
    so plugins must capture it at load (`local DATE = Date`). A cue = the actor's line, a 700 ms wait, "NOW!", then
    closing it within 900 ms lands. Under -rtfast every cue lands.
  - **Masanori (plugin RokuganHazard, rt_firstblood):**
    - A formal duel: `callables` returns nothing, so Call is greyed. (The test hooks bypass the menu.)
    - Phase 1: he starts at Focus 2/4, Focuses twice more with One Strike Blade (he moves first), then makes his own
      iaijutsu (S423). Rensei's Iaijutsu Strike landing first wins the exchange.
    - First blood: a break, then an Iaijutsu Strike while he's open or any crit. A killing blow is stayed at 1 HP
      and counts. He then yields (escaped).
    - Resolve 8, not 14 (solo; Rensei duels alone). He resists Katana.
    - The counter, told by Sanae the night before and in the item text: W133 Kakita Wakizashi (Tanto) from R124.
    - Measured at Lv 45:

      | Rensei's weapon | Result |
      |---|---|
      | wakizashi, auto | won with 529/692 and 449/692 |
      | wakizashi, a guest set (the hook used Goro anyway) | won 571/692 |
      | katana | lost: no break is possible; the story continues |

  - **Art (gen_bossart):**
    - Masanori EP131: "Kakita Toshimoko 5" (a full-figure old master in Kakita blue) via the new mode `inkflood`:
      flood the ground in from the edges, stopped by the dilated black ink. Inside the head keep-box, anything that
      isn't the saturated cyan ground is figure, because the thin grey hair strokes leak the flood.
    - The Shelf Kami EP132: the wiki's "Shiryo" (an ancestor spirit, line art, a ghost-blue ramp, CLEAN 60).
      Rejected: "Tsukumogami" (a semi-transparent ghost made a broken mesh) and a stone kami (it merges into its
      rocks).
    - Banners EP523 "First Blood at Dawn" and EP524 "Keeper of Shelf Nine".
    - Candidates are in _sources/wiki_art/cand_crane10-12, downloaded through the fandom API with curl (WebFetch gets
      HTTP 402).
  - **Monsters:** EP443 paper_spirit, EP444 inkpot, EP445 lantern.
  - **Cast:** actors a/b/c, censormonk, censorclerk, dojipoet, smithboy, craneguard, drunkactor, h_lamplighter.
  - **Hirelings:** #18 Doji Poet (Verse of Reproach: ATK down on all enemies, 2 charges, Charm 55%) and #19
    Lamplighter (Lamp Oil: Fire on all enemies; his hello line tells you paper fears fire).
  - **Data:**
    - Conditions: K053 Watchful Falcon (PHIT +15, CRI +15, 3 turns); K054 Dazed (a 1-2 turn Confuse); K055
      Bleeding (5% a turn for 3 turns, ends with the battle).
    - Rensei learns S426 Watchful Falcon at Lv 25 (P101 lvoption). It's the first kata; the kata system is otherwise
      unbuilt.
    - Skills S417-S428; enemies E342-E344, E346, E347; gear A126-A128, W133-W135; items I147-I149.
    - Groups 45-47 (M831 archive, M832 dueling ground; floors at height 0, snapped); flags G416-G440.
  - **Solo balance fixes (rule):** no enemy skill puts K001 Poison on a solo traveler. It takes 10% of max HP a turn,
    forever, and even lasts after the battle (the "LOST with HP left" runs were poison ticks). Paper Cut uses K055
    instead.
    - Archives at Lv 41-43 with a katana: 47-88% HP left.
    - The fixed four-spirit fight: 71-252 HP left with a katana, 218 with the wakizashi, 452 with the Lamplighter.
    - The guardian: 310/681.
  - **Waiting on other travelers:**
    - Eavesdrop (the censor's clerk), Charm-follow already built (the poet = hireling #18), Barter (the smith's boy:
      Fine Katana Fragment), Bless (the Asahina pilgrim), Duel (the Daidoji guard), Sumai (the drunk actor), Pilfer
      (the poet's purse);
    - Discern on the misfiled box (Gendo);
    - Calligraphy on lectern 2 (Haruki/Gendo; Rensei's Falcon already covers it);
    - TB-crane4-a (Gendo), TB-crane4-b (Sayo);
    - the master-forged katana (3 Fine Katana Fragments).
- **Lion Ch1 "The Blood of Family": plan + slices 1-2 (2026-10-29).**
  - **Sources, all read in full:** production/lion-ch1.md, storyboards/lion-ch1.md,
    scripts/lion-ch1-the-blood-of-family.md, research/the-blood-of-family.md, bosses.md §3 (b_warehouse_raid,
    b_nagai_possessed L6 HPx4 Res6, b_duel_ashimita L6 Res5, b_boss_otamai L9 HPx8 Res8 + red-shadow oni), bestiary F
    (Lion plains & border, Phoenix roads & Kamatori: Lv 1-8).
  - **Pair rule P-1:** Lion is played first, so it plays as written. Haruki is a silent NPC in the embassy ("a young
    Isawa carrying too many scrolls"; G445 = Haruki recruited hides him). Phoenix Ch1, played later, is the flashback
    with climax_route locked.
  - **Ids:**

    | Kind | Ids |
    |---|---|
    | Maps | M240 Magonojo river (night), M241 castle town, M242 castle courtyard, M243-M249 castle interiors (chapel, bathhouse, barracks, guest wing, Ozaki's room, hall, Hiruto's chamber), M250/M251 road_west_phoenix (the 4 shrines), M252 Shiro no Kamatori, M253 Hoju's study |
    | Backdrops | M833 (Magonojo at night), M834+ |
    | Flags | G441+ |
    | Enemies | E348+ |
    | Skills | S429+ |
    | Items | I150+ |
    | Stores | R126+ |
    | Companions | P127 Akodo Gusai, P128 Lion rider (S01 only) |
    | Guests | 8 Ijako (Call the Dead, Mask Rite in the field), 9 Ashimita |

  - **Slices:**
    1. The prologue + S01 raid.
    2. The courtyard + S02.
    3. The castle hub: interiors, Ijako, clues C1-C6 (5 of 6), the escalations at 2/3/4 (b_nagai_possessed, the
       Ashimita Duel), the town M241 (Lion T1, inn, path-action NPCs, hirelings).
    4. S05 Hojiki's custody, then the road M250/M251 with the colder/warmer compass, Kamatori, Hoju's study (S06).
    5. S07 the three routes, S08 b_boss_otamai (jade chains on Suki, 3 = win; the oni's soul damage; boss art).
    6. S09, rewards (Hiruto's Go Stones: +1 Command), the spirit wasteland lifted, balance, audit.
  - **Slice 1 DONE:**
    - The M099 prologue has a third road, Akodo Shizue: add P103, drop P100, set G441, go to M240.
    - M240 the Magonojo at night: S01 from the production text. Gusai (P127) and a Lion rider (P128) join for
      b_warehouse_raid (gid 48: Phoenix Guard E348 x3, L1, Res 2, weak Katana/Yari; backdrop M833, night) with the
      Command tutorial lines, then leave.
    - After the raid: Hojiki and the skull, G443 shrine_broken, a save, "A week later".
    - Verified from the prologue: the party ends the tutorial at full HP.
  - **Slice 2 DONE:** M242 the castle courtyard.
    - The hall, chapel, bathhouse, barracks, guest wing, west tower and the water barrel. Interiors come in slice 3.
    - S02 autorun (G446, then G444): the embassy props, the family scene, a save. The silent Haruki NPC.
  - **New sprites:**
    - side cast: gusai, lionrider, hojiki, kamasari, hojato, ozaki, ryuzoji, togawa, nagai, ukita, acolyte,
      mizochi (hiruto, ijako, ashimita, yachiko and hoju already existed);
    - human enemy phoenix_guard = EP504 (Ryohei moved to EP505; gen_data reads sprite ids by key).
  - **Parser fix (all chapters):** a removed acting cue left a space before punctuation ("Hojato , the sullen").
  - testbattle PARTY_NAMES now includes Akodo, Lion and Shiba.
  - **Slice 3 DONE (verified in-engine): the castle hub.**
    - **M241 the castle town:**
      - R126 Lion armoury (yari for the Lion duelists, who are weak to Yari) and R127 rice merchant; the inn (20)
        with guest swaps 8/9 (`inn_guest(..., path="G444")`).
      - The silent shrine (no rites until S08); chests (80 zeni, the tea house's Fine Sake + I151 Crane Spy's Note).
      - Path-action NPCs; hirelings #20 Lion Ashigaru (Yari) and #21 Kitsu Acolyte (heal).
      - The east gate is held until S05 (G467; its portal exists once M250 does).
    - **M242 the courtyard:** doors are events 2-5 (chapel, barracks, guest wing, hall). C3 is the bathhouse
      search (I150 Hojiki's Jade Stone, a Jade item). C2: Ukita "Wait for night" (G458), then the ghost at the
      barrel, with Mask Rite.
    - **M243 the chapel:** S03a Ijako (guest 8, G456/G464); C1 Hoju's ghost through Mask Rite.
    - **M245 the barracks:**
      - C5 Ryuzoji.
      - C4 at Ozaki's door: Duel (b_duel_ozaki gid 50) or "come back at dinner".
      - Gusai's Duel (gid 51): "Ozaki did."
    - **M246 the guest wing:** C6 through Ijako's fallback after C1-C3 (F-4).
    - **M248 the hall:** S07 comes later.
    - **The clue board:** `clue(n, text)` sets G446+n and G453 += 1 (clues_found), then the escalation that count
      opens:

      | Count | What happens |
      |---|---|
      | 2 | Ukita's Crane banners |
      | 3 | Togawa found choked |
      | 4 | b_nagai_possessed (gid 49, M834), then the S04 lines, the b_duel_ashimita Duel (gid 52, losefunc 1), Ashimita becomes guest 9, save |
      | 5 | Objective: Hojiki |

    - **Duels (plugin, enemy field `rt_duel`):** no seconds (Call is empty), and a lethal blow makes them yield
      (escaped, counted as the win). `duel_pa(name, gid, win, lose, flag)` is Shizue's path action.
    - **Lion guests:** S429 Ijako "Call the Dead" (Void, 1 use) and S430 Ashimita "Yojimbo's Cut" (Katana, 2 uses);
      GUEST_SKILLS slots 8 and 9.
    - **Solo tuning:** Nagai AREA (0.55, avg, 0.8); duelists (0.6, avg, 0.8).

      | Fight (Lv 5) | HP left |
      |---|---|
      | Nagai, solo | 72/155 |
      | Nagai, with hireling + guest | 60/155 |
      | Ozaki | 143/155 |
      | Ashimita | 98/155 |

    - The parser now trims a leading "Victory:" from stage directions.
  - **Slice 4 DONE (verified in-engine):**
    - **S05 at Hojiki** (barracks, after G463): the production text, then the custody choice (G469 = phoenix),
      G468, G467 (the east gate opens), objective Kamatori.
    - **M250/M251 the shrine road** (shared with Phoenix Ch1, F-3):
      - 4 despoiled shrines. After the Jade Chains (G470) they read in order on the way back: S1 "cool" (G471), S2
        "Colder" (G472), S3 "Cold. Frost..." (G473).
      - S4 is the courtyard spot facing the west tower: "Ice" (G474), Ijako's line, objective the hall, save.
      - Chests and an Athletics ledge.
      - Encounters (relevel copies, vs="avg": E353 ashigaru, E354 wolf, E355 bandit, E356 wisp, backdrop M835):
        68-96% HP left at Lv 5-6.
      - `relevel()` takes a `vs` profile now; it used to be hard-wired to "crane".
    - **M252 Shiro no Kamatori:** R128 Phoenix T1, an inn with guest swaps, the NPC table (cook, scroll-copier, old
      nun), Shrine rites (Kamatori's kami never left). The Shiba guard is a Duel (gid 53, E357): an Oak Bo and Glory.
    - **M253 Hoju's study (S06, G479):** the Haruki branch (P104 in the party) or the acolyte reads; I152 the Jade
      Chains (G470); I153 Hoju's Tea Set (sell); save.
  - **Slice 5 (half), 2026-10-29: data, plugin and art are in; the maps aren't.**
    - **Boss art (gen_bossart):**
      - O-Tamai EP133: the painted "Bloodspeaker" via GrabCut, with PAINT_HINTS (the robe is close to the purple
        mountains; the hints keep it).
      - Red-shadow Oni EP134: "Akeru no Oni" (line art with a blood-red ramp; caption and signature erased).
      - Possessed Matsu Nagai EP135: the painted "Lion Bushi" (white mode, caption erased). E349 now wears it.
      - Banners EP525-527: "Beloved of Iuchiban", "It Eats the Breath", "Many Voices, One Sword".
      - Candidates are in _sources/wiki_art/cand_lion1. The wiki has no O-Tamai art.
    - **Data:**
      - E358 O-Tamai (L9, HPx6, Resolve 4 not 8, because three breaks solo at 8 would be 24 weak hits; rt_chains 3;
        rt_captain; drop I154 Jade Chain Fragment, steal I155 Bloodspeaker's Ring).
      - E360, the harder copy (Hojiki given to the Phoenix: no host ready).
      - E359 Red-shadow Oni.
      - Skills S435 Blood Bolt and S436 Breath-eater (rt_soul).
      - Groups 54-57; A129 Hiruto's Go Stones; flags G480-G488.
    - **Plugin (RokuganHazard):**
      - `rt_chains`: each Suki on O-Tamai binds a chain (the chain barks); the last one binds him (escaped). His
        oni leaves too (rt_captain).
      - He can't die before that: a killing blow leaves 1 HP, with "Then we chain him" from Shizue.
      - `rt_soul` skills drain SP (1/6 of max) and 1 VP, with Ijako's bark.
      - Verified working: "jade chain 1/3" fires on his first break.
    - **Balance problem:** see the RESUME POINT.
  - **Slices 5-6 DONE (2026-10-29, verified in-engine). Lion Ch1 is complete.**
    - **b_boss_otamai retuned** (solo Shizue at Lv 8, with a guest and a hireling):
      - Resolve 2 (bosses.md says 8). Each chain is a break followed by 2 turns of Suki, so at Resolve 8 three
        chains took about 15 rounds. Now about 10.
      - Damage: AREA E358 (0.6, avg, 0.5), E360 0.55, the oni 0.4; Blood Bolt dmgrate 1.05.
      - Results:

        | Setup | Result |
        |---|---|
        | Ijako + Kitsu Acolyte (heal) | won, 9-10 rounds, 87-90/219 |
        | Ijako only | won 31/219 |
        | Spear hireling | lost (the -rthire test hook wastes turns calling a hireling he isn't weak to; a player wouldn't) |
        | E360, no host (Hojiki with the Phoenix) | won 95-120/219 |

      - Layout: O-Tamai (-2.5, 1.0), the oni (-0.4, -1.0). The oni's art is height 125, because the 170 version
        overlapped O-Tamai and was clipped at the top (snapbattles).
    - **S07-S09** (M248 hall autorun after G474, G487): the production text and the 3 routes.
      - A: Hojiki volunteers, plus Kamasari's line if G469.
      - B: Mizochi, the whisper refused.
      - C: a 2-choice chase to Hiruto's doorway.
      - S08: the pre-battle lines (the Haruki branch with P104), then the battle: routes A/C use 54/56 on the M836
        hall, route B 55/57 on the M834 yard; 56/57 when G469.
      - G484; the spirit wasteland clears; S09 in full; G485 yachiko_suspected; A129 Hiruto's Go Stones (AGI +10%);
        the chapter card; G486; back to the courtyard.
      - All three routes were run through to the card.
    - **Spirit wasteland:** the town shrine gives no rites until G484, then full rites (Kamatori's never stopped).
      Spells aren't actually weakened (no Lion Ch1 caster needs it); it's flavour.
    - **Fixes:**
      - shrine_rites said "Nothing in Natsuko for it to take" on every path. It now says "There is nothing in you for
        it to take".
      - NAME_FIX "O-tamai" becomes "O-Tamai".
  - **Lion Ch1 audit against the storyboard:**
    - **In:** every scene; all 6 clue spots and the F-4 fallback; the escalations; the custody choice; the merged
      road (F-3); the compass; the town screen (F-2: Lion T1, inn, NPCs); the 3 routes; the S-1 saves (the S06 study,
      the west-tower compass spot).
    - **Waiting on other travelers:** the farmer (Bless), the Crane trader (Barter/Eavesdrop), the Kitsu child
      (Charm), the ronin guard (Sumai/Pilfer), the Discern lines (Hojato, Gusai, Nagai, Ukita), the Kamatori table's
      other actions, TB-lion1-a/b, and the recruit variant (non-starter Join point).
    - **Phoenix Ch1** is the flashback version later (P-1): climax_route is stored in G481-G483 and custody in G469.
- **Lion Ch2 "Shadow of a Doubt" DONE (2026-10-29, verified in-engine scene by scene).**
  - **Sources, all read in full:** production/lion-ch2.md, storyboards/lion-ch2.md,
    scripts/lion-ch2-shadow-of-a-doubt.md, research/shadow-of-a-doubt.md, bosses.md, bestiary (Fear Shade, the Shiro
    Akodo rows).
  - **Maps:**
    - **M254 the winter road:** from Hiruto's town (west exit, after G486). The frozen ford, the waystation rites, a
      wolf den (Hunting: gid 63, Ginseng x2). Encounters: Mountain Wolf, Glory-Hungry Bushi, Border Patrol, Yurei;
      backdrop M837; 58-86% HP left.
    - **M255 Shiro Akodo town:**
      - R129 Lion T2, R130 apothecary (Calming Tea = the Terror cure); the inn with guest swaps 8/9/10.
      - The swordsmith's shed (Beat 3's sword clue, G500); Hachiman shrine; chests.
      - Path-action NPCs waiting: the Matsu bushi Sumai, the widow Bless, the Ikoma bard Barter.
      - Hirelings #22 Kitsu Jade-priest (Jade, all enemies: the told-and-buyable counter to the shades) and #23 Ikoma
        Herald (heal + cure Terror).
    - **M256 the grounds:** the garden; the stables (Benjiro, S08); the kitchen girl; Yutaka; Mami; Kafu (no sword
      after Beat 3). Doors are events 2-8; the South Dojo opens after Beat 3, the cells after the arrest.
    - **M257 Hall of Honors:** S01 (G489/G490) and the hostess, who starts every beat (F-1):

      | Beat | What happens | Prize | Flags |
      |---|---|---|---|
      | 1 | painting choice (G492); the bracket of 3 Duels (gids 58-60, losefunc 1; a loss ends the bracket, F-5) | W137 Jade Tanto, whether won or lost | G494 won |
      | 2 | Kafu's history, Shizue's history | I156 Jade Flesh-cutter Arrow | G496 |
      | 3 | the debate, then Toturi's "Who is that?" | A130 Akodo's Leadership | G499; then the sword |
      | 4 (after S06) | the dance | A131 Jade-inlaid War Fans | G503 |

      After Beat 4: the seal, Atsuko arrested, the clue chain "everything Kafu loves".
    - **Escalations:** the Duty plaque (M258 Central Dojo, after G491) and the banner (M262 Hall of Akodo, after
      G495).
    - **M259 North Dojo:** Nishi's go game (a 3-move choice; "Kafu taught me to play").
    - **M263 library:** Atsuko. **M264 cells:** atsuko_promise (G505: 0/1/2).
    - **M260 South Dojo (night):**
      - S06: the trail, then b_fear_shades (gid 61), the Terror tutorial, the loose board down to M261 (the
        crawlspace: the scarf glimpse, Jade Dust, an Old Jade Bead dead end), back up the hatch, the voices (G513 →
        G501), save.
      - S09 after G507: the talk-down. Option 3 works only with met_nishi + heard_history (G490 + G496), giving G508
        kafu_joins and P129 Kafu as a companion for the fight. Then b_boss_ianwa (gid 62).
      - S10: both epilogue branches, Atsuko's line if honest, "Akodo Shizue. Again.", the card, G510.
  - **Ianwa (plugin):**
    - Its turn is "Coward's Whisper" (S440). A bare Wait (S000) has no target, so the AI never acted: no turn, no
      hooks. (Miyako's Wait in Crane Ch2 never ran either; harmless there.)
    - `rt_charmer_ally`: each turn it charms one traveler: 70%, or 35% with jade (W137/A131), never under K056. A
      charmed traveler hits another one, or alone loses the action.
    - `rt_coward`: the first Suki, or a lethal blow, makes it flee. The captain rule now fires on escaped captains
      too, so the shades leave. (This also covers a bound O-Tamai.)
    - Boss shades are softer copies (E371). Results at Lv 24 with the Jade Tanto + Death Trance: 30-73% HP left.
      Without jade it can't be broken and you lose (every prize is jade, and the tanto is always given).
  - **Terror now works, game-wide:** K007 "Terror" used to do nothing.
    - A Terrified traveler freezes 30% of the time and can't Boost.
    - The War Fans resist it 60%; Death Trance (K056) blocks it and charm.
    - The older yurei, Tsukakoro and Nagai skills now really terrify.
  - **Engine rule (found the hard way):** `putconds`/`remconds` bits must stay under about 50. Death Trance used
    COND_BIT("K056") and the engine read it as a defeat condition ("DEFEATED" with HP left). Conditions K050 and up
    now go through `PUT_BY_ID` (an opt_putcond option by id). Watchful Falcon (K053, Masanori's and Rensei's) was
    fixed the same way. A scan confirms no skill or item uses a bit above 50.
  - **Art:**
    - Oni no Ianwa EP136: the wiki's painted "Ianwa no Oni" via GrabCut. The fg boxes must stay inside the body;
      boxes over its edge kept rectangles of sky. Banner EP528 "The Coward's Feast".
    - Fear Shade EP446 (gen_monsters).
    - Cast: nishi, kafu (+ kafu_nosword), gesshin, yutaka, mami, hostess, ikomabard, matsuduel, widow, kitchengirl,
      swordsmith (peasant build), karo.
  - **Data:**
    - Enemies E361-E371; skills S437-S442; gear W137, A130-A132; items I156-I158.
    - Groups 58-63; flags G489-G518 (numeric G492/G494/G505); guest 10 Moto Benjiro (S439 Death Trance, 2 uses);
      P129 Kafu.
  - **Visual fixes after snapbattles:** M839 is off the night list (the fog hid the shades and Ianwa); the garden's
    trees moved to the corners (they hid the player).
  - **Waiting on other travelers:** Discern (Nishi, Kafu, Yutaka, Atsuko, Benjiro), Eavesdrop (the kitchen girl),
    Charm (Atsuko: Rensei), Sumai/Bless/Barter/Pilfer (the town), TB-lion2-a/b.

- **Lion Ch3 "The Deadly Message" (2026-10-29): built end to end.** Sources: production/lion-ch3.md, storyboards/lion-ch3.md,
  scripts/lion-ch3-the-deadly-message.md, bosses.md (b_boss_miya_killers), bestiary F (Lion west road / mountains).
  - **Maps:**
    | Map | What |
    |---|---|
    | M265 the karo's office | castle_floor; door = M256 grounds event 9 (after G510). S01 (start), S05B (route B), S07 (both routes) |
    | M266 the west road | from the M255 town's east gate (event 3, after G519). Granary loft (Fine Katana), cairn shrine. Encounters on M840 |
    | M267 the Burned Bridge | S02: the ford Duel (gid 64, losefunc 1; losing = pay 100 zeni), Ijako (guest 8), the inspector; toll box choice; R131 market, inn; hirelings #24-#26 |
    | M268 the sleet waystation (night) | S03 on resting: the tube cracks; G527 message_route (1 deliver, 2 ask the karo) |
    | M269-M270 the pass (cave_map, snow) | S04 the pass ronin (gid 65, rt_surrender), Miya Letters (I160); frozen courier; route B's boss + coda on M270 |
    | M271 Kaze-no-Tani | route A: S05A Shogen's Duel (gid 66, losefunc 1), Shogen's tea (full heal), then S06 the boss; plum wine; the road home |
    | M840 battle: the thaw road | new backdrop (height 0); also the ford duel |
  - **Routes:** A = deliver -> pass -> hermitage (Shogen joins, A133 Strategist's Eye in S07). B = back to the karo (S05B)
    -> pass -> the boss on M270 -> the hermitage coda (G535) -> home. The boss (gid 67) needs G530 (the letters) on both.
  - **Data:** E372-E380 (E377-E380 = west road/pass relevels); S443-S448; I159-I161, A133; R131; groups 64-67;
    flags G519-G546 (numeric G527).
  - **Boss:** Seppun-trained Duelist E375 (HPx 6.5, Res 10, rt_captain: the archers give up when he falls) + 2 Miya
    Archers E376 (HPx 2, atk 0.7). Volley from the Rocks: light all-target damage, ATK down only 10% (it used to
    cripple Shizue). Seppun Iaijutsu = PDEF + 12% max HP.
    - Results at Lv 28-30 with Ijako + the Refugee Herbalist (#26, heal): won in 5 rounds, 5-50% HP left (the
      autopilot uses no items). With the archer or spear hireling instead: lost in round 6. So the village sells a
      healer.
  - **Duels:** Bandit Chief HPx 6 atk 1.25 (5 rounds, 29-50% left); Shogen HPx 10 Res 8 atk 1.5 (5 rounds, 34-41% left).
  - **Encounters (balance_encounters):** road Lv 27 and pass Lv 29 all "ok" (50-79%, the captain 36-70% by RNG).
    Winter Wolf HPx 0.55 and atk 0.7; 2 wolves on the road, 3 on the pass.
  - **Plugin fixes (game-wide):**
    - **Escaped enemies kept acting.** Surrendered, freed or captain-routed foes stayed in the turn order and
      attacked. `chooseAICommand` now returns no action for an escaped enemy (RokuganAI.sk). This affected Crane
      Ch1's bandits and the Crane Ch2/Ch3 crews too.
    - The surrender bark is per foe: `rt_mercy` in the enemy data (the old farmers' line is the fallback).
  - **Art:** EP137 the Duelist (Harue, paint): the hint boxes no longer cut the hakama, and the katana hilt and
    wakizashi are back. Shogen (side cast), Miya Archer (human enemy). Snapbattles 64-67: all fighters visible.
  - **Waiting on other travelers:** the party reactions in S03 (wired, gated by in_party), PA Discern/Eavesdrop on
    the letters, TB-lion3-a/b.

- **Lion Ch4 "Sorrow's Path" (2026-10-30): built end to end.** Sources: production/lion-ch4.md, storyboards/lion-ch4.md,
  scripts/lion-ch4-sorrows-path.md, bosses.md (b_gusai_duel, b_ford_waves_1-5, b_boss_rokuro_demon), bestiary F.
  - **Maps:**
    | Map | What |
    |---|---|
    | M272 Sorrow's Path road | from the M255 town's north gate (event 4, after G537). Victory stone (History: wave 1 Resolve -1, G549), watchtower (Matsu War Yari W138), encounters on M841. Events 2-5 = the camp by day / night / the ford / day again |
    | M273 the Lion camp (day) | S01 (Shogen's Old Lion's Counsel if G532: +10% party damage, rpgvar G548) -> dusk -> M274. After the chapter: Hiruto, Gusai, Rokuro |
    | M274 the camp (night) | S02; clues: courier + sentry -> "same method twice" (G555; Tadanobu's letters if G391). Yachiko's tent (Mitsue only), her baggage (3,000 zeni + Miya Seal Wax, Honor -1), the berserker's Duel (gid 76, W138), Gusai S04 (Duel gid 68, or Command if toturi_knows_name G499), the obsidian choice, dawn |
    | M275 the riverbank | S03: who crosses (G556: 1 Rensei if G557, 2 Atsuko if G505 = 1, 3 herself); the scout's kit (Tsuruchi Longbow) |
    | M276 the ford (dawn) | five wave triggers along the causeway (gids 69/70-74), "Hold" walks between (no save), the mist lifts (save), the boss (gid 75), S07, the report choice |
    | M277 the courtier's tent | the river stone, the complete card -> M273 |
    | M841 / M842 | battle backdrops: the old battlefield; the ford at dawn (both height 0) |
  - **Go-between "herself" (G556 = 3):** at dawn Shizue leaves the party and Lord Hiruto (P130, Lv 44) holds the ford
    alone; she rejoins after wave 5. Hiruto alone ends waves with 20-66% HP (Shizue: 52-75%): the hardest way, as the
    script says. (Gusai + Hiruto together was easier than Shizue, so Gusai "holds his own men back".)
  - **Data:** E381-E393 (E386/E387/E391-E393 relevels); S449-S456; I162 Obsidian Blade (reusable battle item),
    I163 Miya Seal Wax, I164 Rokuro's Gratitude; W138 Matsu War Yari; A134 Demon's Shadow (Terror immunity, max HP
    -10%), A135 Matsu Lamellar; R132-R133; groups 68-76; flags G547-G584 (numeric G556); P130 Akodo Hiruto;
    hirelings #27 Kitsu Field-priest (heal), #28 Ikoma War-herald (cures Terror), #29 Matsu Spearman (Yari).
  - **Plugin:** Old Lion's Counsel (+10% when G548); the Obsidian Blade (`rt_obsidian`) strips 3 shields from a foe
    with `rt_obsidian_weak` and Taints the user each hit (Jade Finger wards it); Demon's Shadow blocks Terror;
    surrender kills set `rt_killflag` (berserkers: G577; Honor +1 after wave 1 if none died). **Not yet tested with a
    real item use in battle** (the test autopilot doesn't use items).
  - **Balance (Lv 42-44, Matsu War Yari, Counsel):** waves 3-4 rounds, 52-75% HP left each, solo; the boss (Rokuro HPx 9,
    Res 8, weak Jade/Yari/Water) with Ijako + a camp hireling: won in 6-8 rounds, 25-52% left. Gusai's duel 3 rounds,
    73% left; the berserker's 3 rounds, 67%. Road (Lv 41): all "ok", 45-76%.
  - **Art:** EP138 Matsu Rokuro = the wiki's painted "Matsu Gohei 3" (paint mode on a 40% copy), banner EP530 "Only
    Fools and Matsu"; Rokuro side cast; Matsu Berserker and Crane Archer human enemies; EP447 Burning Bridge.
  - **User fix (2026-10-30): duel opponents faced away.** "Gusai in that battle is backwards ... not facing the
    character", and "the characters for lion are still looking over their shoulder". Side-cast sprites carry
    flipx (they face the enemy side like party members), so every side-cast character fought as an enemy stood with
    its back to the party: Ozaki, Gusai, Ashimita (Lion Ch1), the Ch2 bracket (Ikoma bard, Matsu duellist, Yutaka),
    Shogen, Gusai (Ch4), and on the Crab path Gonta and Seppun Ryozo. Fix: gen_sidecast writes a foe copy of every
    side-cast sprite (`foe_epid(n)` = EP700 + n, flipx False, same scale) and gen_data repoints any enemy using a
    side-cast sprite to it. Snapbattles 59/66/68: all face the party.
    - Also: Akodo Ijako's reed mask was the same brown as her hair, so in profile her head read as the back of a
      head. The mask is now pale straw.
    - **Ask the user** if "looking over their shoulder" meant something else (field walking?). The field facing code
      and every Lion side frame looked right on inspection.
  - **Waiting on other travelers:** the Rensei go-between (needs the crossroads recruit, G557), Haruki's three-clan
    truce (G571, Phoenix Ch1), path actions in camp (Sumai, Charm, Pilfer, Bless, Barter, Eavesdrop), TB-lion4-a/b,
    the Gentle Blade of Winter kata (kata system).

- **Phoenix Ch1 "The Silent Kami" (2026-10-30): built end to end.** Sources: production/phoenix-ch1.md,
  storyboards/phoenix-ch1.md, scripts/phoenix-ch1-the-silent-kami.md, bosses.md (b_shrine_guardian_shards,
  b_ashimoshi), bestiary F (Phoenix roads & Kamatori), production/lion-ch1.md S07-S08 (the shared climax).
  - **Start:** the prologue has a fourth road, Isawa Haruki (P104, G585). Haruki is the starter, so P-1 applies:
    Shizue is a silent NPC at Lord Hiruto's side; the climax is route A with Akodo Ijako standing in (an actor, not a
    guest, F-4).
  - **Shared Lion Ch1 maps, gated by path:** G585 (Phoenix) / G441 (Lion).
    - M253 Hoju's study: S01 (start), Sense at the reading stand, the futon (-> S02), the chest (S04: the Jade Chains
      G470 required; the folded note optional, G587 + I167), S09 (the note). It now has a door to M281 the inner
      garden (Commune at the shrine, Summon at the candle hall; silent after S02, humming after G484).
    - M252 Kamatori: S03 the muster (props); the study door is always open (Shizue only reaches Kamatori after S05);
      the gate holds Haruki until the chains (Ashimita's line); the old nun (Bless: 2 Rejuvenating Tea); the shrine is
      silent for Haruki until O-Tamai is bound; the Lion Duel guard is Shizue's only.
    - M250 the shrine road: S05 the Magonojo ruins (crate lid -> G571 phoenix_supply_proof, the flag Lion Ch4's
      truce scene reads) and S06 the broken shrine (Bless the keeper's ghost G589, b_shrine_guardian_shards gid 77,
      the Void tutorial, save). The compass text is traveler-neutral now.
    - M241 the east gate is open for the Phoenix too (blocker page, not a hidden portal: a hidden portal can't be
      arrived at). M242: the arrival (G600), Shizue silent, the west-tower door, the hall door (after G601); the Lion
      compass spot is Shizue's only (G441).
    - M278-M280 the west tower (F-3): wisps, a blade rack (Ironwood Bo), a save on 2F, Ashimoshi on top (gid 78,
      backdrop M843). M248 the hall: S08 (gid 79), then home for S09.
  - **User: "shugenja should never travel alone ... always at least a Yojimbo companion ... lean heavy on spells."**
    Shiba Ashimita is a front-row companion (P131, a weaker Crab curve: HP 0.75, PATK 0.45, PDEF 0.55) from the S03
    muster to S09; then he becomes guest 9. Fights are balanced for Haruki + Ashimita (+ a hireling); Haruki's spells
    carry the damage.
  - **Plugin:**
    - Spirit wasteland (G588, from S02 until O-Tamai is bound): the travelers' spells (MATK formulas) at 75%.
    - Ashimoshi's Silent Wind (`rt_silentwind`): each of his actions toggles a seal; sealed spells fizzle; "Now -
      while he breathes!" when it lifts.
    - **This Squirrel's strings use `indexOf`, not `find`** (the first version never matched).
    - Encounter groups can carry `rt_if` / `rt_ifnot` (a 4th ENCOUNTERS field; RPGStage.raiseEncounter override), so
      the shared shrine road rolls Lv 2-3 Phoenix groups for Haruki and Lv 5-6 groups for Shizue.
      balance_encounters takes "M251:phx" keys.
  - **Data:** E394 Guardian-stone (EP448), E395 Ashimoshi (EP139, physical halved, drop A136 Hurricane Bead), E396-E398
    young road foes, E399 O-Tamai at Resolve 4 for a shugenja + yojimbo (group 79; Lion keeps 54-57); S457-S459;
    I165-I168; **I125 Fine Sake now really restores SP** (it was an Antidote copy) and I168 Rejuvenating Tea (SP 25%);
    hirelings #30 Isawa Fire-acolyte, #31 Shiba Staff-guard at Kamatori; flags G585-G606.
  - **Balance:** shards Lv 4-5: 3 rounds, 74-96% left; Ashimoshi Lv 6-7: 5-7 rounds, 50-78%; O-Tamai Lv 7-8: 7-9
    rounds, 46-69%; roads: "ok".
  - **Art:** EP139 Ashimoshi = the wiki's painted "Daidoji Yurei" (paint mode; height 150, because 200 clipped his head
    in battle); banner EP531 "The Silent Hurricane"; EP448 Guardian-stone (gen_monsters).
  - **Waiting:** the cook/scroll-copier/pilgrim/stable-boy path actions of other travelers, TB-phoenix1-a/b, the recruit
    variant (Join point at the muster), Ashimita's Guardian / Grandfather's Storm skills (he uses Yojimbo's Cut).
- **Togashi Yosai, a companion on every path (user, 2026-10-30): BUILT.** Optional front-row companion until the
  travelers join up; regeneration; never serious; talks in cryptic, story-relevant parables. User choices: met in each
  path's Ch1 town, then for the whole path; he travels only when no other companion does.
  - **P132 Togashi Yosai** (cast #27; Crab-curve copy: HP 0.9, PATK 0.8, PDEF 0.75, AGI 1.1; bare hands):
    - S460 Dragon's Breath: Fire on all enemies; costs him 10% HP.
    - S461 Arrowroot: heals an ally (40% of max HP); costs him 15%.
    - Plugin: `rt_selfburn` on the skills; `REGEN` (P132: 7% max HP at the start of each of his turns); Crow tattoo
      (no Taint).
  - **Where:** `Events.inn` records each inn, and `make()` adds `yosai_inn()` beside every inn on every map (after the
    map is built, so no event ids shift; interiors get the inn's embed offset).
    - YOSAI_MEET = the Ch1 inns M111 (Crab garrison barracks), M202 (Pleasant Eaves), M241 (Hiruto's town), M252
      (Kamatori): the first meeting (G607).
    - Elsewhere he appears once met, while not in the party (G608).
    - "Travel with me" only when the party is the traveler alone (`length(members) <= 1`; this Squirrel uses
      length(), not len()).
  - **Lines:** YOSAI_SAYS is a parable per inn map, hinting at that chapter's mystery and at the blue-eyed hand (user:
    "cryptic things, relevant to the story, in parable or roundabout ways"). YOSAI_ANY is the fallback.
  - **Steps out:** join() (and the raw joins of Squeak and Goro) run YOSAI_STEPS_OUT first: he leaves with a joke and
    waits at the inns.
  - **Duels are one on one:** make() wraps every duel battle (groups whose enemies have rt_duel / rt_firstblood, read
    from the last generated data) with YOSAI_ASIDE / YOSAI_BACK (G609). Verified: the Matsu berserker's duel had only
    Shizue.
  - **Verified in-engine:** meet + join at M241; Dragon's Breath, self-burn and regen in battle; Yosai steps out when
    Ashimita joins (Phoenix S03); the static check finds 0 problems.
  - **Not done:** his Shadowlands taunt (Crow: Tainted foes always target him); join-up removal (no join-up yet);
    fights weren't retuned for him (he's optional, so they get easier). **Ide Tamotsu:** support/buff diplomat, never alone (a Shinjo guardian companion on the Unicorn path).

- **Phoenix Ch2 "The Silent Court" (2026-10-30): DONE. Every scene was run in-engine (S01, Hisae, the magistrates,
  S02 + Yosai, S03, Mieko, the murder, ghost, floor, label, midnight, the debate, nightfall, S06, S07 to the card).**
  Fixes from the run:
  - Yosai's pass cameo has a "we meet again" version when he was met at Kamatori (G607).
  - The black-glass lines are labelled "Mieko (???)".
  - The mob leader's label is now consistent.
  - Hioninmaru's art is now height 125 (170 clipped his head).
  - Snapbattles 80/81/82: every fighter faces the party and is visible. Field snaps M282/M285 OK.
  Sources read in full: production/phoenix-ch2.md, storyboards/phoenix-ch2.md, scripts/phoenix-ch2-the-silent-court.md,
  bosses.md (b_pass_cultists, b_boss_hioninmaru).
  - **NEXT STEP (resume here):** run each scene with tools/runevent.py and fix what breaks:
    - M282: S01 (G610, after G604), Hisae, the magistrates;
    - M284: S02 (touch, G614);
    - M285: S03 (G645), Mieko, the guest-house rest page (murder -> midnight -> nightfall), ghost, floor, label, the
      3 sub-stories;
    - M286: S04;
    - M287: S05 debate, S06 boss;
    - M285: S07 (G642).
    Then snapbattles 80/81/82 (backdrops M844/M845: check facing, height, visibility), and a field snap of M282/M285.
  - **Maps:**
    | Map | What |
    |---|---|
    | M282 Zumiki | from Kamatori's east gate (M252 event 21, after G604). S01 Keiki; Ashimita joins as yojimbo (P131, Lv 20, user rule); Hisae in the Yellow Lantern (Bless best / walk / duel); the magistrates (G613 memory_ritual_refused, save); R134 Phoenix T2; inn; watchtower chest; hireling #32 |
    | M283-M284 the snowbound pass | cave maps, snow; the wolf den (gid 82); S02: cultists; Yosai's cameo joins him as P132 (allowed beside Haruki's yojimbo, user) unless already along; b_pass_cultists gid 80 (Hioninmaru E401 is a coward + captain: he runs, the cultists give up); the Unicorn rider |
    | M285 Honored Treaty City | S03; Mieko (camellia garden); the guest-house page drives the night beats (murder G618 -> midnight -> nightfall G627); Bless the historian's ghost (G619), the floor (G620, Speak to the Soul), the camellia label (G621, save); sub-stories 1 (dojo: Bless, Kabuto), 2 (archive: Sense, Scroll: Tremor I171), 3 (sober: Bless, Haori, Honor); 4-5 wait for other travelers; R135; hireling #33 |
    | M286 the snow garden (night) | S04, the tell-Keiki choice (G623), back to M285 |
    | M287 the traitor's torii | S05 the debate (3 claims, G626 strong count; Ashimita answers claim 2 since he's there; 2+ = torii_saved G625, Honor +1); S06 at night: b_boss_hioninmaru gid 81, the scroll choice (G629 + I169), then S07 at M285: Courage of the Seven Thunders taught (G638 + I172), Ashimita leaves, G630 |
    | M844 / M845 | battle backdrops: the pass; the torii |
  - **Hioninmaru (E402, EP140):**
    - Boss art: the wiki's "Bloodspeaker 3" line art in a blood-red ramp (a thin man cutting his arm in a candle circle).
    - His maho (S462) costs him 3% HP and can Taint.
    - **User: "he should spawn more minions when he says I have gold".** rt_gold 2: when his cultists are all down he
      buys them back (raise) twice; then he's broke ("I have secrets!") and loses 1 Resolve per turn (rt_fearful).
    - Balance at Lv 23-25 with Ashimita: 5-8 rounds, 35-70% HP left.
    - Pass: 3-4 rounds. Roads: ok / easy.
  - **Plugin lessons:**
    - **Never override RPGPlayer.udpateOwnLists** (even a pass-through stops every battle from starting).
      Story-taught skills (STORY_SKILLS, P104: G638 -> S368) set the skill bit in onPreTurn instead.
    - Enemy skills can carry rt_selfburn too.
  - **Data:** E400-E404; S462-S465; I169-I172; R134-R135; groups 80-82; flags G610-G646 (numeric G626); new side
    cast keiki, hisae, mieko, magistrate, mobleader; hirelings #32 Zumiki Porter, #33 Asako Lorekeeper.
  - **Bug found and fixed:** a full `regen.py --maps` once finished without writing the new maps' .bw files (no error
    shown), and every test battle then failed at load. Rebuilding those maps by name fixed it. **After a full build,
    check that mapdata/<new map>.bw exists.**
- **Battle presentation (user, 2026-10-30):** "not clear what is happening when the aoe attack goes off; it's clear
  when Path to Inner Peace is cast" and "I like it when spells show up at the top and show what element they are
  using".
  - gen_data: every area skill (cmdtgt 3/7) that isn't one of Haruki's spells gets a cast (use_charge, cast_area, cast
    sound) and a spell effect on each target by element: Fire FX422, Air FX404, Yumi FX458, Water FX452, Jade FX463,
    Earth FX479, Void FX485, Terror FX485, otherwise FX418.
  - Plugin (RokuganField): every special skill whose flags bit 0 is set (the engine shows a banner only when it's
    off) shows the engine's top banner "icon name - Element". Plain weapon strikes and "Strike" are skipped.
    Verified: "Bo of Water (Water)", "Howling Silence (Air)", "Blood Bolt (maho)".

- **Phoenix Ch3 "The Darkfever" (2026-10-30): DONE, every scene run in-engine** (S01, a treatment, the dying healer,
  the leave choice, S03, S04, the forest fight, dark Mieko + the scroll, Kuzushi, S07 to the card).
  Sources read in full: production/phoenix-ch3.md, storyboards/phoenix-ch3.md, scripts/phoenix-ch3-the-darkfever.md,
  bosses.md (b_forest_fever_spirits, b_mieko_dark_mid, b_boss_oni_no_kuzushi).
  - **Maps:**
    | Map | What |
    |---|---|
    | M288 Kyuden Isawa | from Treaty City's south road (M285 event, after G630). S01 the eclipse; Ashimita joins again (Kamasari lends him; user rule); S03 the Council (after the leave choice G660); S04 Hayato's circle (G664: the forest opens) + the Mountain's-Feet Charm hint; R136 Phoenix T3 (sells A137); inn; the refugee (Bless G663 -> hireling #35); the sealed library door (after G671) |
    | M289 / M291 the fever road | 8 sick NPCs (`sick()`): Path to Inner Peace 6 SP, Boosted 12 SP, Hand of Jurojin 4 SP (after the healer), Bless; the ferryman needs Remedy (waits for Sayo). G650 counts the treated; at 5 the west exit asks the leave choice (stay: +2, G661 -> the boss gets +1 Resolve); no inns (F-1) |
    | M290 the temple hospital | the dying healer (I173, G656: Hand of Jurojin S316 as a story skill); one rest (G674) |
    | M292-M293 the Isawa Mori | b_forest_fever_spirits (gid 83); the deer trail; the Tremor web shrine (needs the archive sub-story G632; Jade Dust x4); the fever shrine |
    | M294 the estate | 3 flashback points; b_mieko_dark_mid (gid 84, she flees at 50%: rt_flee_pct); the scroll choice (G670 if G629); Mieko's room (I176 Child's Go Stone); the cellar door |
    | M295 the cellar | b_boss_oni_no_kuzushi (gid 85, or 86 with Resolve +1 when G661) |
    | M296 the sealed library | S07: I174 Scroll: Dreamwalker (no Dreamwalker skill yet: Ch4 decides its use), the saved count, Ashimita leaves |
  - **Plugin:**
    - Unbalancing Breath (`rt_unbalance`): every 2nd oni turn, K052 Off-Balance on a random traveler and +2 Resolve.
      The **Mountain's-Feet Charm (A137)** prevents it (the "counters known and available" rule: Hayato names it,
      the temple-smith sells it).
    - Darkfever aura (`rt_fever` 6% HP per oni turn).
    - Flee (`rt_flee_pct`).
    - STORY_SKILLS adds G656 -> S316.
  - **Balance (Haruki + Ashimita):** forest spirits 3-4 rounds; dark Mieko 3 rounds (flees); Kuzushi Lv 33-35: 5-9
    rounds, 10-90% left, one autopilot loss at Lv 33 (no items/charm/hireling). Roads: ok / easy (triage pressure).
  - **Art:**
    - EP141 Kuzushi: the wiki's own "Kuzushi no Oni". New gen_bossart options: `INVERT` (white line work on a black
      ground), `DROP` (enclosed ground, dark pixels only), `DROP_ALL` (whole regions), `DESAT`.
    - EP142 dark Mieko: "Bloodspeaker 2" (painted).
    - Battle heights 135 / 130 (the first versions clipped at the top).
    - Monsters EP449 Fever Spirit (scale x2.0), EP450 Gaki, EP451 Tsuchigumo.
    - Side cast hayato, rujo, uona, healer.
  - **Data:** E405-E411; S466-S470; I173-I176; A137-A138; R136; groups 83-86; flags G650-G682 (numeric G650);
    hirelings #34 Temple Bo-monk, #35 Village Survivor.
  - **Waiting:** Remedy (the ferryman, Goemon), Charm/Eavesdrop/Pilfer/Discern/Barter/Duel/Sumai in Kyuden Isawa,
    TB-phoenix3-a/b, the Dreamwalker spell itself.

- **Phoenix Ch4 "Howl" (2026-10-30): DONE, every scene run in-engine. The Phoenix path (Ch1-4) is complete.**
  Sources read in full: production/phoenix-ch4.md, storyboards/phoenix-ch4.md, scripts/phoenix-ch4-howl.md,
  bosses.md (b_mieko_shadows_a/b, b_boss_mieko_dark).
  - **Yojimbo (user rule):** Doji Hayato (P133, Crane yoriki; the same weaker curve as Ashimita) joins at S01 and
    leaves at S06.
  - **Maps:**
    | Map | What |
    |---|---|
    | M297 the coast temple town | from Kyuden Isawa's north road (after G673). S01 (Keiki's lines by told_keiki / mieko_midnight_seen); R137 Phoenix T4; inn; the drowned sailor (Bless -> A139 Orochi Scale); hirelings #36/#37; S06 at dawn |
    | M298-M299 the cliff path | b_mieko_shadows_a/b (gids 87/88); 3 echoes of the gentle Mieko (Bless, G684 += 1 each); the wrecked shrine-boat (Pearl x3) |
    | M300 the last shrine | save; S03 Dreamwalker -> M301 |
    | M301 the dream | the garden / the crack (VOID, a plank bridge) / the ash. Key 1 (G629 or G670), Key 2 (G587), Key 3 (the frozen child, ends the dream; the Child's Go Stone line). **User fix:** the arrival and the child had been placed in the black crack: now the garden and the bridge's edge |
    | M302 the red torii | S04 the boss: gid 89-92 by dream keys (Resolve 12/10/8/6); S05 the fake choice (strike -> join), Whole (G696), the answer (G697) |
  - **Plugin:**
    - `rt_echo_block`: each blessed echo cancels one Void Drain (S473, an rt_soul copy).
    - "Whole" (G696): Haruki's Water heals cleanse one debuff; Drawing the Void twice per battle. **Drawing the Void
      is now once per battle** (Ch1's tutorial said so; it was unlimited).
    - Void -1: Haruki loses the shugenja +1 VP cap.
  - **Balance (Haruki + Hayato, Lv 41-45):** shadows 5-9 rounds; the dark half 5-10 rounds, 35-90% left (keys and
    echoes shorten it).
  - **Data:** E412-E420 (E418-E420 cliff relevels from E404/E217/E356); S471-S475; I177 "Against the Bloodspeakers"
    (finale key item); A139; R137; groups 87-92; flags G683-G705 (numeric G684, G691, G697); hirelings #36, #37;
    EP452 Mieko's Shadow.
  - **Build lessons:**
    - A failed gen_data leaves item.json without the bestiary drops. gen_maps' `item_named` now falls back to a
      placeholder instead of crashing, and the next full build fixes it, so **run regen.py --maps twice after a
      gen_data failure**.
    - New relevels must come after their source enemy exists in gen_data (E338, E404 ordering).
  - **Waiting:** the town's other path actions, TB-phoenix4-a/b, the Dreamwalker field spell beyond this scene.
- **Dragon Ch1 "Under the Skin" (2026-10-30): DONE, every scene run in-engine (S01-S08, the Momo guest, the boss).**
  Sources read in full: production/dragon-ch1.md, storyboards/dragon-ch1.md, scripts/dragon-ch1-under-the-skin.md,
  battle-skills.md (Gendo).
  - **Start:** the prologue now offers 5 starters; Kitsuki Gendo (P102) sets G706 and opens on the Mantis ship
    (M303). He is alone until Togashi Yosai joins at the dump (S03, his story home; sets G607/G608/G712). The
    Ch1-town Yosai meeting does not apply on this path.
  - **Maps:**
    | Map | What |
    |---|---|
    | M303 the Mantis ship | S01; Discern the captain (G708) -> the dock brawl (gid 93, the Deduce tutorial) |
    | M304 the Isle of Silk | the waterfront hub; Discern table (net-mender G728, Kosai G729, the Storm Legion thug G731); R138 Silk Chandler; hirelings #38/#39 (after G712); the tax shed (Fine Sake). Gates: hill path G713, boathouse G722, beach G723 |
    | M305 Yoritomo's hall / M306 the guest house | S02 (the poisoned tea, Oharu's Seal I178); inn; S08 ending (G727) |
    | M307 the dump | S03: Muika (Discern G730), Yosai on the heap; stepped refuse mounds, the tarp |
    | M308 the Rakusho school | S04: Riichi; "slowly" (G714) makes the chant hints plain in the ruins; Momo (guest 11, G715) |
    | M309 the silk hill path | field encounters (E426-E429) |
    | M310-M312 Kyuden Gusai | the code is the layout: the fourth step (G716) -> three stones (G717-G719) -> twenty up the wall (I180 the Monks' Notes, G722); thugs a/b (gids 94/95) |
    | M313 the boathouse | S06 Kumpei: Discern 2 layers; accuse (G724) / watch (G725); Rare Blue Pigment I181 |
    | M314 Tortoise beach | S07 the boss: the tide (gid 96); I179 Tortoise Ferry Token |
    | M850-M852 | backdrops: the docks, the ruins, the beach (height 0, snapped, foes face the party) |
  - **Plugin:**
    - The tide (`rt_tidecaller`) now rises on rounds 3, 6, 9 (it had been rounds 4, 7).
    - Interrogate (`rt_interrogate` / `rt_hypno`).
    - Momo's Perfect Recall (S478).
  - **User change, Arrowroot (S461, all paths):** the heal is doubled and scales with Yosai's level: dst.MAXHP*0.6 + src.LV*8 (was *0.4 + LV*2). The 15% HP cost is unchanged. It heals Gendo for 139 at Lv 6.
  - **Side cast:** sidecast has a new "mantis" clan palette (green, dark teal, gold).
  - **Balance (Gendo + Yosai):**
    - Field encounters on M309-M312 (Lv 3-5): 2-4 rounds, 72-96% HP left. The ruins groups were stiffened with a third foe or a ronin.
    - Dock tutorial (Lv 1): 2 rounds.
    - Thugs a/b (Lv 5): 3-4 rounds.
    - Tide boss (Lv 6): 7-12 rounds when the duo fights alone, with every run won by a thin margin. 7-9 rounds with Momo and a hireling.
    - AREA: E422 (1.1, 0.85), E423 (1.1, 1.05), E424 (0.9, 0.95).
  - **Data:**
    - Enemies E421-E429.
    - Skills S476 Interrogate (P102 Lv 5), S478, S479, S480.
    - Items I178-I181. Store R138.
    - Groups 93-96. Flags G706-G739.
  - **Not built yet:**
    - The RECRUIT VARIANT (Gendo met as a non-starter); it waits for the travelers to meet.
    - Kumpei's "Glory -1" (narration only).
    - Banters TB-dragon1-a/b/c.
    - The Yosai-hit bark "Eighteen and a half!".
- **Dragon Ch2 "The Painting" (2026-10-30): DONE. Every scene was run in-engine, S01-S06, including the boss and the Ink Door.**
  Sources read in full: production/dragon-ch2.md, storyboards/dragon-ch2.md, scripts/dragon-ch2-the-painting.md.
  - **Route:**
    - The Isle of Silk ferryman (M304 pier; needs G727 and the I179 token) takes Gendo to Tortoise Island.
    - The Ch1 ending now says "Next: The Painting ... (Recommended level 20)".
  - **Maps:**
    | Map | What |
    |---|---|
    | M315 Tortoise Island | S01 (with the kumpei_watched line); inn; R139 net shop; Discern the villager (G753); hirelings #40 Old Diver (Yari) and #41 Shrine-keeper (heal); the boat-shed chest. Gates: house -> rubble and a cat (G741/G758); cove after G741 |
    | M316 the new house | the study autorun (G768); lore chests I182/I183 before the cellar (F-3); the cellar and the quake (G741) |
    | M317 the ridge dojo | S02, optional: Koshi; I187; mirumoto_school (G742) -> Daisho Technique |
    | M318-M320 the cove | Yosai teaches the Bow (G757); b_cove_crabs (gid 97); the clay city (a grid of miniature houses, tile roofs -> thatch; Discern G756); b_cove_guards (gid 98, rt_hypno); Kumpei's Ink Pot I184; a save shrine before the portal (F-4); the portal (S03) |
    | M321 outside time | S04 limbo |
    | M322 the winter orchard | History tutorial and HUD (G747); b_boss_ushimo (gid 99); the ushimo_lead choice (G750); S06 Kusada |
    | M323 the year-400 south gate | R140 Antique Market (W139 Tachi-pattern Katana); the painting = the Ink Door (G752) |
    | M324 the guest house | S06 invitations (I188); TB-dragon2-b at the window (G764) |
    | M853 / M854 | backdrops (snapped): the cove; the winter orchard (winter cherries made of blocks) |
  - **Portal (S03):**
    - Only Gendo crosses. Momo crosses as the active guest if G715 is set.
    - The hireling stays behind (G293 = 0).
    - Yosai is lost in the ink: P132 leaves, G608 = false, G759 = true.
    - yosai_inn now also requires G759 false, so he does not reappear at inns until he returns in Ch4.
  - **Plugin:**
    - **The History meter:** G748 (numeric; starts at 100), shown as a stage-UI label top-left. It appears on the year-400 maps (HISTORY_MAPS M321-M324; add the Ch3-4 maps to that table) once G747 is set. Event scripts refresh it with `::Rokugan.historyHUD()`.
    - **Ushimo** (rt_ushimo):
      - He Focuses twice, then draws (S484) at Gendo.
      - Daisho Technique (rt_daisho) landing first answers the draw.
      - Below 25% HP he kneels: shields drop to 1 and he stops acting.
      - A killing blow is refused: 1 HP, History -10, "History shudders".
      - A Suki or a Subdue (rt_subdue) while he kneels makes him yield (G749).
    - **The Bow** (rt_bow vs rt_kappa): the kappa breaks at once (Suki).
    - **The auto-battle AI** now bows to kappa, answers Ushimo's draw with Daisho, and Subdues him once he kneels.
    - STORY_SKILLS P102: S482 Subdue (G740), S483 Bow (G757), S481 Daisho Technique (G742).
    - TRIM_DIR now also trims "CUTSCENE:" from narration.
  - **Art:**
    - Ushimo: boss art EP143 and banner EP535, from cand_dragon2/Seppun_Ishikawa_2.jpg in a Seppun green line ramp. That art was fetched through the wiki API with curl into _sources/wiki_art/cand_dragon2.
    - Kappa: EP459, drawn in gen_monsters.
    - Side cast: a new "mantis" clan palette; new characters koshi, kusada, ushimo, seppunguard, akuro (in his fisherman disguise), diver, crabboy, shrinekeeper, mbushi.
  - **Bug fixed (all paths):** the grinding-EXP formula only covered E100-E399, so Lion, Phoenix and Dragon foes (E4xx) paid hand-set EXP. For example, a Lv 42 Frost Spirit gave 132 EXP while a Lv 22 Wako Raider gave 883. The range is now E100-E499, with E435 and E423 added to BOSS_EXP. **The Lion and Phoenix paths now level faster; their balance tests were run before this fix.**
  - **Balance:**
    - Cove encounters (Gendo + Yosai, Lv 21-22): 2-3 rounds, 62-96% HP left.
    - Crabs and guards: 3 rounds each.
    - Ushimo (Gendo alone, Lv 23; HP x0.45, ATK x0.85; the draw does PDEF + 30% of max HP):
      - with Daisho: 9 rounds, won with 4-50% HP left;
      - without the dojo: 9-10 rounds, won 3 of 3.
      - Auto-battle wastes Momo's Perfect Recall.
  - **Data:**
    - Enemies E430-E435.
    - Skills S481-S488.
    - Items I182-I184, I187, I188. Kappa drops come automatically from bestiary.md.
    - Weapon W139. Stores R139/R140.
    - Groups 97-99. Flags G740-G768.
  - **Not built / not tested:**
    - The ferry's item gate was not run (runevent can't put items in the bag).
    - Ch2 village path actions (Barter, Charm, Eavesdrop, Bless, Sumai, Pilfer, Duel) and banters TB-dragon2-a/b are waiting on other travelers; TB-dragon2-b is in as Gendo's window scene.
    - Party swaps at the Tortoise inn.
    - The Bow banner shows "(-)" as its element.
    - Water/Path to Inner Peace healing Ushimo applies only if Haruki is in the party.
- **Dragon Ch3 "Past Mistakes" (2026-10-30): DONE. Every scene was run in-engine, S01-S07, including the boss.**
  Sources read in full: production/dragon-ch3.md, storyboards/dragon-ch3.md, scripts/dragon-ch3-past-mistakes.md.
  - **The capital in three screens:**
    - M326 the palace (A): S01 Kusada; the war council door; the palace well (1,500); TB-dragon3-b at the palace window (dinner C).
    - M325 the streets (B): the three mansions; R141 Year-400 Armourer (T3); the gaijin trader.
    - M323 the south gate (C): it now also has Ushimo's house (M327) and Miyoshi's studio (M328).
    - Re-linked: the orchard (M322) opens onto the palace, and the gate's west road goes to Izumida.
  - **Maps:**
    | Map | What |
    |---|---|
    | M329-M331 the mansions | one dinner (G770: 1 Bayushi / 2 Doji / 3 Shiba). Accepting one insults the other two (their doors close). Each has one exclusive chest: W140 Shosuro Tanto / I191 Crane Ward Fan / A140 Isawa Robe |
    | M327 Ushimo's house | S03, behind the G772 lead (Ch2's ushimo_lead, or the palace guard's tip after the dinner). Help Tsuhime: History +10 and **Seppun Ushimo joins (P134)** |
    | M328 Miyoshi's studio | pay 3,000 for the mirrors (I189): History +10. Barter/Pilfer wait for Tamotsu/Sayo |
    | M333 the Izumida road | the musket-ball trail -> b_scout_camp (gid 100 / 104 alone) |
    | M334 Shiro Izumida 1 | b_izumida_musketeers (101 / 103 alone); take a musket: History -15 (W142) |
    | M335 Shiro Izumida 2 | the scorched coast map (I193; Discern the dates); the powder store (-5); the ridge -> the palace |
    | M332 the war council | S05 (save) and S07; reward W141 Shukujo |
    | M336 the parley ship | S06 b_boss_parley (gid 102) |
    | M855 / M856 | backdrops (snapped): snow and paddies; the ship's deck with powder barrels |
  - **History:**
    - `hist(delta)` moves G748 and shows the HUD.
    - Spectacles at noble doors (mansions, war council): take them off, or keep them on for History -2.
    - Bayushi: refuse +5 / agree -25. Sanro +5. Tsuhime +10. Mirrors +10. Glass beads -5. Musket -15. Powder -5.
    - At 0: "The World That Should Not Be" plays and Gendo is pulled back with History at 30 (G787). This replaces a game over, because the engine has no game-over command.
  - **Plugin:**
    - rt_untouchable (Akuro): hits on him do nothing. He only lowers the pistol on round 1, barks on rounds 2-3, then steps over the rail and leaves on round 4 (script S6).
    - The auto-battle AI ignores him.
    - rt_captain can now carry its own falling line: "The powder room explodes. When the smoke clears, Akuro is gone."
    - HISTORY_MAPS + M325-M336.
  - **Party design (my call; the production text leaves it open):**
    - Helping Tsuhime makes Ushimo a front-row companion for the rest of the Dragon path. If he isn't helped, Gendo is alone.
    - So the fixed fights have solo versions (gids 103/104), and M333-M335 have ALONE encounter tables (one or two foes; rt_ifnot G793).
  - **Engine and parser fixes (all chapters):**
    - ROOM_DIMS entries for every Dragon castle floor. Interior arrivals had been landing by luck.
    - `(internal)` lines now show as a thought in parentheses, plus any `(aloud)` speech. Before, say() stripped them.
    - full_first no longer expands a given name that is the family half of another name ("Gusai Iami" is not Akodo Gusai).
  - **Art:**
    - Akuro: boss art EP144 / banner EP536 from cand_dragon3/Togashi_Gozato.jpg, using a new gen_bossart mode "paperkey" (cream paper ground; holes filled from every edge).
    - Gaijin pikeman, musketeer and captain plus the deserter palace guard, in gen_human_enemies. gen_sprites2d has a new "musket" weapon.
    - New side cast: miyoshi, tsuhime, atsuki, tomeko, seikidera, katsutoshi, sanro, gaijintrader, iami.
  - **Balance (Lv 30-34):**
    | Fight | With Ushimo | Gendo alone |
    |---|---|---|
    | Parley boss | 4-5 rounds, real pressure | with a healer hireling: 11-12 rounds, won about half the time on auto with no items |
    | Fixed fights | 3-5 rounds | 5-10 rounds |
    | Encounters | 2-4 rounds | about 9 rounds (long) |
    Seppun Draw was cut to 0.65 dmgrate: it hit for over 1,000.
  - **Data:**
    - Enemies E436-E442.
    - Skills S489-S495.
    - Items I189-I191, I193; W140-W143; A140/A141; R141.
    - Groups 100-104. Flags G769-G797 (numeric G770).
    - Hirelings #42 Crane Ashigaru (yari), #43 Isawa Novice (heal).
  - **Not built:**
    - The kata "My Brother's Soul" (there is no kata system).
    - Portraits changing below 50% History.
    - Haruki/Sayo help for Tsuhime.
    - Path-action NPCs in the capital.
    - TB-dragon3-a.
    - The gunpowder barrels as usable battle items (-10).
- **User request (2026-10-30): the music should be "more medieval Japanese". They appreciate having sound.**
  The current BGM is the engine's stock Western set (resource/bgm, 23 tracks), and nearly every map uses MU006.
  Next: generate a Japanese soundtrack (koto, shakuhachi, shamisen, taiko; in/yo scales) with one mood per kind of place, then assign it per map. Memory: music-medieval-japanese.
- **The soundtrack v1 (2026-10-30, user: "music should be more medieval Japanese :) but i appreciate sound").**
  - **tools/gen_music.py** synthesizes everything in numpy. ffmpeg encodes it (libvorbis, 44.1 kHz stereo, the same format as the stock files).
    - Instruments: koto, shamisen and biwa (additive plucks with sawari buzz and oshi-de bends); shakuhachi and shinobue (breath, meri scoop, late vibrato); hichiriki (enbai slides); sho (aitake clusters); o-daiko, shime-daiko and kakko; kane and rin bells; waves and drips.
    - Scales: yo, in (miyako-bushi), ryo, hirajoshi.
    - Melodies come from scale-step phrases, repeated with variation.
    - **Loops are seamless.** Notes and the reverb (an FFT convolution with a decaying-noise impulse) are rendered circularly, so tails wrap round to the start.
  - **Tracks:**
    | Id | Key | Title |
    |---|---|---|
    | MU101 | town | Village Lanterns |
    | MU102 | road | The Long Road |
    | MU103 | cave | Beneath the Stone |
    | MU104 | battle | Steel Drawn |
    | MU105 | boss | The Fortunes Turn Away |
    | MU106 | court | Halls of the Gozoku |
    | MU107 | shrine | Incense and Bells |
    | MU108 | sea | Salt Wind |
    | MU109 | night | Moon Over the Paddies |
    | MU110 | past | Ink Between the Years |
    | MU111 | shadow | Where the Kami Do Not Go |
    - Cues (an intro, then a quiet loop): MU112 victory, MU113 inn, MU114 fall. The engine's own MU021 (victory), MU022 (inn) and MU017 (game over) entries in resource/bgm.json are re-pointed to them.
  - **Assignment:**
    - gen_maps `music_for()`: MUSIC_OVERRIDE, then MUSIC_RULES by map name (shadow / cave / town / shrine / court / sea / road). Carved maps outdoors count as roads. The year 400 gets past, or court for the palace, mansions and council.
    - Every map's bgmid is set in register(). Map encounter groups play MU104.
    - gen_data: M001 groups play MU105 when the name has "boss" or "duel", otherwise MU104. M000 (title) plays road; M001 (template) plays town.
  - **Checks done:** spectrograms (notes, drums and scoops present; flute breath noise was too loud and broadband, now cut); levels (RMS ~0.16, peaks under 0.95).
  - **Not checked:** I can't listen. The user should play it and say what to change: tempo, instruments, mood, loudness.
  - **To regenerate:** `python -E tools/gen_music.py [key ...]`. Preview WAVs go to _art/preview/music/. The rebuild doesn't run it; the OGG files persist.
- **Dragon Ch4 "The Battle of the White Stag" (2026-10-30): DONE. Every scene was run in-engine, S01-S06 plus the three fronts and the boss. The Dragon path (Ch1-4) is complete.**
  Sources read in full: production/dragon-ch4.md, storyboards/dragon-ch4.md, scripts/dragon-ch4-the-battle-of-the-white-stag.md.
  - **Getting in:**
    - The Ink Door (M320 frame), once Ch3 is done (G784): the warning "the door will close forever", then the war camp.
    - From the past: the war council's map table (M332).
    - After the chapter (G830) the door is "just paint".
  - **Maps:**
    | Map | What |
    |---|---|
    | M337 the war camp | S01 (the make-up artist; Yosai returns "Twenty-one!": P132 rejoins, G759 false). Ushimo (if he was with Gendo) rides off to lead the relief (G824). Fronts on talk events. Field kitchen inn; R142 Quartermaster (T4). Crane veteran Discern (G800): Gendo gives the calm order. Chests: Ginseng x3, A143 Seikidera's Hachimaki. Hirelings #44 Centipede Scout (yumi volley), #45 Crane Field Medic (heal) |
    | Land front | b_front_land (gid 105), rt_hold 6: the gaijin leave on round 6 and the relief arrives. Ushimo's line if Tsuhime was helped. Won: cannons every 6 rounds instead of 3 (G802) |
    | M339 the Mantis cabin | Discern Iami (the elegant win) or duel his champion (gid 106, rt_duel). Won: a broadside (G804, Kumpei starts 15% down) |
    | Lighthouse front | b_front_lighthouse (gid 107) with Isawa Sanro (P135) in the party. If he falls: History -30 (G808) and the front is lost. Won: the wards (G806, Void Guard on everyone) |
    | M340 the harbour tunnels | b_harbour_musketeers (108); the barrel temptation (History -5) opens the smuggler's cache (Storm Legion Token, Pearl x2); a save at the gangway (F-3) |
    | M341 the flagship | S04 b_boss_kumpei_flagship (109); I194 the vial if he is broken before round 8; spare (G814) or the guards |
    | M342 the private audience | S05: accept (History -50, G819) or refuse (G818, Honor G060 +5) |
    | M320 the cove | S06: home, and the door closes (G830) |
    | M344 Kitsuki Yasu's hall | the jester line, the persimmons, the prophecy ("Seven. There are eight of us."); A142 Pressed Cherry Blossom; Shukujo is taken back |
    | M343 Shiro Kitsuki | the revisit node: inn, R143 Kitsuki Outfitter (W144 Togashi Bo), the ferry to Tortoise, TB-dragon4-b on the bench. The Tortoise ferryman now also sails to the mainland |
    | M857-M860 | backdrops (snapped) |
  - **Lost fronts are not a game over:** front_battle() uses losefunc 1 (recover and continue), and rpgvar RESULT < 0 means the front is lost (History -10, no buff, Gendo's line "I filed this battle as a victory. I was wrong."). fronts_won is G807.
  - **Plugin:**
    - rt_hold: a HOLD n/6 counter.
    - rt_kumpei: front buffs at the opening; cannons (12% max HP to every traveler, every 3 or 6 rounds); the living-ink sigil copies one traveler buff a turn (K020/K022/K024/K040); the vial (Suki before round 8 -> G815; round 8 -> thrown, G816, Yosai "TWENTY-TWO!").
    - HISTORY_MAPS + M337, M339-M342.
  - **Art:**
    - Kumpei: boss art EP145 / banner EP537 from cand_dragon4/Kakita_Tadanobu.jpg (paperkey, plus a DROP_ALL polygon for the floor). gen_bossart's paperkey mode now honours DROP_ALL.
    - New side cast: yasu, makeup.
  - **Engine note:** a one-line cmd_script with `local lv = 1; if(...)...` failed to compile ("end of statement expected"). The proven pattern `local p = ..., n = ...; if( n && p.LV < n.LV) p.setLV( n.LV);` works. Ternaries are suspect too.
  - **Balance (Gendo + Yosai, Lv 42-44):**
    - Land front: 7 rounds (hold 6).
    - Lighthouse: 3 rounds; Sanro lives.
    - Duel: 4 rounds (with Daisho).
    - Tunnels: 3 rounds; encounters 3-5 rounds, 50-80% HP left.
    - Kumpei: 6-8 rounds with no buffs, 5 with all three; the vial is usually saved.
  - **Data:**
    - Enemies E443-E448.
    - Skills S496, S498, S499, S500, S501.
    - Items I194, A142, A143, W144; R142, R143.
    - Groups 105-109. Flags G798-G830 (numeric G807).
    - Players: P135 Sanro.
  - **Not built yet:**
    - The kata "Time Between Breaths".
    - The darker-1123 coda for the "saviour" route (it belongs to the finale).
    - The camp's other path actions.
    - TB-dragon4-a (Haruki).
    - The Mitsue make-up variant (it waits for the travelers to meet).
- **Scorpion Ch1 "Blood and Iron" (2026-10-31): DONE. Every scene and fight run in-engine, prologue to "complete" (not played as one continuous run). Plan as built below, then the results.**
  Sources read in full: production/scorpion-ch1.md, storyboards/scorpion-ch1.md, scripts/scorpion-ch1-blood-and-iron.md,
  research/blood-and-iron.md, and the whole adventure PDF (30 pp; the research note's skimmed middle is now read:
  addendum in the research note).
  - **Ids:** maps M345-M358, backdrops M861-M864; flags G831+; enemies E449+; skills S502+; items I195+, W145,
    A144; stores R144+; groups 110+; hirelings #46-#48. New element: **Crystal** (ELEMS index 13; plugin ELEM_NAMES).
  - **Maps:**
    | Map | What |
    |---|---|
    | M345 Kyuden Bayushi - the memorial garden | S01: start; Eavesdrop x3 marked courtiers (rumours_found G833 0-3); incense; Norie |
    | M346 Kyuden Bayushi - the willow teahouse | S02: Norie's orders and the tiered parcel; Many Faces tutorial -> the castle town |
    | M347 Kyuden Bayushi castle town | outfitter (R144), apothecary, inn (Yosai's first meeting), shrine to the Fortune of Secrets, mask-maker, street actor, Bayushi guard, beggar (Scorpion informant); the servants' gate south (the guard: "Evening, girl."); hirelings #46 |
    | M348 Traitor's Grove | S03: the posts (Mitsue counts 19), the chained traitor's purse, b_road_bandits (Steal tutorial); encounters |
    | M349 Shutai | border town: inn (innkeeper Eavesdrop: bloodless victims), Shosuro Noburo (the Shosuro shadow; the Shutai murders), Megu's sake house (the half-made maho pattern), priest, store, shrine |
    | M350 the River of Gold road | encounters; the bridge |
    | M351 Kudo | hub: Sparrow street (north), Fox street (south), the bridge; Kitsune Hall, the Mantis office (yellow quarantine banner), the Suzume hall, the docks (dock-hand, Kasuga Yodo the Tortoise), the Dreaming Carp, fishmonger, Inari shrine (Water: Kansen counter), old woman; street flare-ups; hirelings #47-#48 |
    | M352 the Kitsune Hall | S04b Many Faces: the "governor" eats raw fish (governor_fake) |
    | M353 the Mantis guest house | Yoritomo Rui (the acting magistrate; the map of flags) |
    | M354 the Dreaming Carp | inn; S08 at dawn |
    | M355 the river crossing (night) | S05: the sick vanish; Rui joins (front-row companion); b_kommei_brood (one command swap) |
    | M356-M357 the west marsh | S06: Taint tiles; the barge of bloodless dead (Meiji, the real governor); b_marsh_leeches; the Miya relics (Crystal Shard x4); shrine save |
    | M358 the heart clearing | S07 boss: the ritual counter; Suki drops the box; Steal it |
  - **Companions:** Mitsue alone (Yosai optional from the castle-town inn); Yoritomo Rui (P136, canon NPC from the
    adventure, Mantis yoriki, kama + Storm Heart: Air) joins at S05 for the night to the end (Yosai steps out).
  - **Plugin:** Many Faces = Steal or Copy (talent pick, like Rensei's): Copy turns the target's last-used skill on it;
    Iron Box (I195) held -> Mitsue starts each battle with 0 VP; rt_ritual (Hana): counter pops, 5/7 barks, 7+ the
    Oracle's grapple, 10+ Blood Tide; Suki stops it and drops the box (G8xx); rt_kommei_once (one swap);
    AI throws Crystal Shards at rt_crystal foes.
  - **Built as planned, with these changes:**
    - Kudo: Sparrow district west (by the river), Fox district east; buildings only on the far side of the street.
    - The Suzume "assassin" (Rika's eavesdrop): "There was no man. A cloud." (the source's yellow-green Kommei
      cloud) instead of the production's "he wanted sympathy".
    - The production's sick clerk is Yoritomo Rui (the adventure's acting magistrate); her briefing (G876) counts as a
      suspect (G878). S05 needs governor_fake (G849) + 2 suspects (G851) + the briefing.
    - Eavesdrop: one try per target; a failure is seen and costs Honor -1 (production tutorial text).
    - Hana: Res 7 (bosses.md said 8). The marsh barge can be burned (Honor +1).
  - **Plugin:**
    - Many Faces is a pick (Steal / Copy), like Rensei's iaijutsu. Copy (S505) uses the target's last skill
      (recorded in onPostCommand) on it, or on Mitsue's side for a heal or buff: Hana's own Choking Death (Air)
      breaks her shields.
    - Iron Box (I195) held: Mitsue starts every battle with 0 VP.
    - rt_kommei_once: one command swap in round 2. rt_ritual: counter pop, 5/7 barks, 7+ grapple (8%), 10+ Blood
      Tide (12%, G868); Suki stops it for good (G866); Steal then takes the box (G867).
    - AI: one Crystal Shard a round at an rt_crystal foe. Test hook -rtcopy (Copy / Steal the box).
    - New element **Crystal** (index 13; Field.sk ELEM_NAMES and elemName).
  - **Fixed along the way (older bugs):**
    - Gaki, Tsuchigumo (Phoenix Ch3) and Mieko's Shadow (Phoenix Ch4, also the dark Mieko field props) showed boss
      banners: their sprites sat on EP450-452, which gen_bossart overwrites. Moved to EP160-162.
    - Boss intro banners after Shelf Kami were drawn but never shown: added EP525-537 (O-Tamai ... Kumpei) and EP538
      Kansen-Hana to RokuganBattle BOSS_BANNER.
    - testbattle PARTY_NAMES: + Shosuro, Yoritomo.
  - **Art:** Kansen-Hana boss art EP146 / banner EP538 from cand_scorpion1/Kansen_(TCG).jpg (paint mode, PAINT_HINTS
    with a new tealkey option). The Kommei brood wears the Kommei art EP123 (no banner). Blood Leech EP163
    (gen_monsters). 18 side-cast entries (mitsue_maid ... h_kitsune).
  - **Balance:**
    - Bandits (Mitsue Lv 2): 5 rounds.
    - Kommei brood (Lv 5, + Rui): 5 rounds, Mitsue at 45-75%.
    - Leeches (Lv 6): 5 rounds.
    - Hana (Lv 8, + Rui): 10 rounds with the shards (Mitsue ~30%); 7 rounds without (Rui's Air breaks her).
    - Encounters: grove 1-4 rounds (56-91%), river road 2-4 (74-99%), marsh 2-4 (80-97%).
  - **Data:**
    - Enemies E449-E460. Skills S502-S512, S505.
    - Items I195-I199, I185-I186, W145-W146, A144. Stores R144-R148.
    - Groups 110-113. Flags G831-G878 (numeric G833 rumours, G851 suspects). Player P136 Rui.
    - Hirelings #46-#48.
  - **Not built yet:**
    - The recruit variant (Mitsue joining another traveler at the servants' gate).
    - Other travelers' path actions in Kudo and the castle town (Charm, Duel, Sumai, Pilfer, Barter, Bless,
      Discern); the Kudo Pass.
    - TB-scorpion1-a/b (need Tamotsu, Haruki).
    - The kata pick at Lv 5 (no kata system).
    - A Ch2 entry point (City of Masks appears north of Shiro no Soshi).
- **Scorpion Ch2 "City of Masks" (2026-10-31): DONE. Every scene and fight run in-engine (not as one continuous run). Plan as built below, then the results.**
  Sources read in full: production/scorpion-ch2.md, storyboards/scorpion-ch2.md, scripts/scorpion-ch2-city-of-masks.md,
  research/city-of-masks.md, and the adventure PDF again (28 pp; Appendix B: the masks are a sentient parasite).
  - **Ids:**
    - Maps M359-M367, backdrops M865-M868. Flags G879+.
    - Enemies E461-E471. Skills S513+. Items I400+ (bestiary drops fill I200-I28x).
    - Masks A145-A152. Stores R149-R151. Groups 114-117. Hirelings #49-#50. Player P137 Isawa Kasiko.
  - **Maps:**
    | Map | What |
    |---|---|
    | M359 the plains road | S01 rumour NPCs; from the Kyuden Bayushi castle town's north road (after Ch1); encounters |
    | M360 Hisatu Kensu | the too-hospitable Unicorn hot springs; Ide Xue (smiling magistrate); bath attendant Eavesdrop; the inn night = the mask dream; trader R149; hireling #49 (Xue's Shinjo yoriki) |
    | M361 the plain before the city | S02 the dying scout, Ikoma Yoshi: Giseiki's mask (A150, a key accessory); S08 at dawn after the boss |
    | M362 Kamen no Toshi - Hospitality | S03 snubbed at the gate; the sake-seller (wood, welcomes Iron); Sweet Cup -> M363; Crimson Blossom inn; Moto Zhang; Yogo Meyako; Kitsu Kenshai (the wrong body); the temple gatekeeper (stone, welcomes Silk) -> M365; district shrine ("Remove masks?", save); Doji Siko's ambush (b_siko) after the market killing |
    | M363 the Sweet Cup back room | S05 Osuko's hunters; Giseiki choice; crystal shop R150; hireling #50 (shadow hunter); Isawa Kasiko joins |
    | M364 Merchant District | mask vendors: Kaiu Naname (Iron), Ichiro Itami (Cedar), Togashi Sumi (Ink tattoo; the riddle), Bayushi Shiruko (Silk); Kasamashi (jade, barter); Hagane; Kakita Yuko (fire-lacquer, welcomes Ink); Miya Hatomu (clay, welcomes Cedar: the map); 3 Eavesdrop pairs (the history); the collapse in the market; shrine |
    | M365-M366 Temple District | stitched monks a/b (freed on Suki: Honor +1, max 3); save |
    | M367 the Monastery of the Silent Self | S07 b_boss_munashii (crystal full, else half; phase 2 copies buffs; Giseiki's counter-word); free / seal |
  - **Mask gate (plugin Field):** the city's maps (MASK_MAPS) drain 5% max MP from each masked member on each new
    district; the shrines remove masks (back to the bag) and restore MP. Talk gates check Mitsue's accessory.
  - **Built as planned, with these additions from the adventure:**
    - Ikoma Yoshi is the dying scout; Kitsu Kenshai is the scout whose soul is in a cultist's body.
    - Doji Siko, the fallen Emerald Magistrate, ambushes Mitsue (b_siko, gid 114) after the market collapse; the
      shadow hunters then lead her to the Sweet Cup.
    - Isawa Kasiko, the last of the magistrate team, is the companion from S05 (P137, Phoenix spells; counts as a
      shugenja for VP).
    - Togashi Sumi is the tattooist (ink mask) and the riddler; Bayushi Shiruko the silk seller. Agasha Kusuri can be
      eavesdropped (the poultice).
    - Kasamashi sells his real jade mask (2500 zeni; Taint immunity like the Jade Finger).
  - **Flow gates:** the collapse needs 2 masks (G883); Siko needs the collapse; S05 needs Siko; the Temple District
    needs the silk gatekeeper (G891) and Kasiko (G893). Ch2 starts from the castle town's west-gate north road after
    Ch1 (G861).
  - **Masks:** vendors offer "Put it on now" (cmd_equipop slot 4). Talk gates use ::Rokugan.wearsMask. Drain on each
    new district (RPGStage.launch hook). removeMasks(keepGiseiki) at shrines, before the boss (keeps Giseiki's) and at
    the end.
  - **Giseiki:** worn (G897): Void -1 until G909 (vpMax), barks in the boss fight, the counter-word = a free Suki in
    phase 2 (G914). Given (G896): the mask goes to Osuko. At the end his mask is removed from the bag.
  - **Art:**
    - Munashii boss art EP147 / banner EP539 from cand_scorpion2/Goju_Assassin.jpg (line, DROP_ALL the furniture).
    - Paddy Python EP164, Giant Hornet EP165.
    - 27 side-cast entries. The sprite kit gained mask_tone (a full mask's colour) and mask_plain (porcelain without
      the glowing eyes).
  - **Balance:**
    - Siko (Mitsue alone, Lv 22): 7 rounds, 25% left.
    - Monks (+ Kasiko, Lv 22-23): 3 rounds each (breaking frees them).
    - Munashii (Lv 25, + Kasiko, 3 shards): 9-13 rounds, sometimes Mitsue falls.
    - Encounters: plains 2-4 rounds (56-100%), temple 2-4 (60-98%).
  - **Data:**
    - Enemies E461-E471. Skills S513-S518, S521-S522.
    - Items I400-I402, A145-A151. Stores R149-R151.
    - Groups 114-117. Flags G879-G917 (numeric G883, G905). Player P137. Hirelings #49-#50.
  - **Not built yet:**
    - The Lion/Unicorn armies around the city.
    - Other travelers' path actions at Hisatu Kensu.
    - The mask dream lines of other travelers.
    - TB-scorpion2-a/b.
    - The Acting skill; the Rank 2 technique beyond narration.
- **Scorpion Ch3 = Unicorn Ch2 "Fortunes Lost" (2026-10-31): DONE from Mitsue's view (storyboard C-1). Every scene and the boss run in-engine (not as one continuous run).**
  Sources read in full: production/unicorn-ch2-scorpion-ch3.md, its storyboard and script, research/fortunes-lost.md, Unicorn Ch1's production (context), Rin's side stories, and the Fortune's Lost PDF Parts I-II (Shinobu orders General Soshi Furayaru's seppuku with Norie as witness; Gochu's fist-sized clapperless ceramic bell; Nihime's story; the hit squad's Quiescence of Air).
  - **Mitsue's view:**
    - Tamotsu is absent: Shinjo Tsune carries the Unicorn bench; the rice-cake balcony is Akodo Rin's.
    - Enemies use the 30-35 band (F-2).
    - Unicorn Ch1's events (the bombing, Naohida) are past news.
    - Tamotsu's view, the "both owners" merge and the flashback rule wait for the Unicorn path; the verdict flags are G934 (both) / G935 (soshi).
  - **Maps:**
    | Map | What |
    |---|---|
    | M368 the Ojatara road | from the plains road (M359 signpost, after Ch2); the Iuchi post: Many Faces -> the troupe grievance |
    | M369 Buried Leaves | inn, R152 Scorpion T3, R153 Unicorn T3, Shosuro Mayumi, hirelings #51 Mirumoto Ashigaru, #52 Refugee Herbalist; S02 Rin is followed |
    | M370 the tribunal hall | S01 the benches (Norie, Tsune, swing judge Doji Himeko); Rin joins (P138); S05 the verdict, the balcony, Wax Earplugs, the drained Seppun courier |
    | M371 the Soshi camp | the officers' fire (the well: Eavesdrop, or Many Faces for 300 zeni); the quartermaster's rolls (the padded armies); S01b the seppuku letter (I404, G925) after 3 grievances (G924) |
    | M372 Shioden | Soshi Ichihito (Katsu's funeral) |
    | M374 Yotomo bell hill | S02 Gochu and the bell (I403); feed his family (500 zeni, G928) or eavesdrop |
    | M375 Perfume Petal Blossom | the village, shrine save; M376 Nihime (tell her? G930); M377 the grave path (the sealed mine gate; the child's grave, Honor +1) |
    | M378 the mountain road at dusk | S04 b_boss_iuchi_hit_squad (gid 118) |
  - **Plugin:**
    - rt_bubble: every other round SP-costing skills fizzle ("no sound comes"); the round before, a warning; breaking or killing the amulet-bearer pops it (G942).
    - Rin's Cover = the Razor's Edge taunt. The Clouds Part = the Command effect.
  - **Balance:**
    - Hit squad (Lv 33, Mitsue + Rin): 5-7 rounds, tense.
    - Valley encounters: 2-3 rounds (72-100%).
  - **Data:**
    - Enemies E472-E478. Skills S523-S529.
    - Items I403-I405. Stores R152-R153.
    - Group 118. Flags G918-G943 (numeric G924). Player P138 Akodo Rin. Hirelings #51-#52.
    - Human enemies iuchi_shugenja / amulet_bearer (EP513-514). 12 side-cast entries.
  - **Not built yet:**
    - Tamotsu's view and the merge.
    - Bayushi Hideki's guest SS1 (offered here).
    - Other travelers' path actions.
    - TB-crossroads3.
    - Perfume Petal's fields still read as plain dark grass.
- **Scorpion Ch4 "The Eve" (2026-10-31): DONE. Every scene and fight run in-engine (not as one continuous run). The Scorpion path (Ch1-4) is complete.**
  Sources read in full: production/scorpion-ch4.md, storyboards/scorpion-ch4.md, scripts/scorpion-ch4-the-eve.md, bestiary rows (Dragon mountains, Tamori's Furnace), bosses.md b_furnace_elementals / b_ash_ghouls / b_boss_stolen_face.
  - **Entry:** a signpost in Buried Leaves (M369, examine, after Ch3 G936) -> the Dragon mountain town.
  - **The guide (S02):** Kitsuki Gendo if he is in the party (G963, script check of P102, for the merged game); else Togashi Yosai (joins if not already travelling, G965); else, while Yosai is lost in the ink (G759), Tamori Haku (P139, new: Heat-Ward K057 party Fire -50% 3 turns, Ember Palm). Every branch's lines from the production are in (S02, S03, S05, S08).
  - **Maps:**
    | Map | What |
    |---|---|
    | M379 Dragon mountain town | S01 the box talks (autorun on arrival), S02 at the mountain shrine; inn; R154 Togashi Outfitter (Dragon T4: W147 Mountain Tanto, Togashi Bo, Jade Tanto, A152 Heat-Ward, robes); R155 Incense-seller; Tamori apprentice (tells the heat rule, the ward, Water/Bo for fire spirits, Jade for ash); Kitsuki clerk Eavesdrop (the procession tip, G955/G956); chests 3000 zeni, A152; hirelings #53 Tamori Rain-caller (Water AoE), #54 Mirumoto Mountain Guide (Katana x2) |
    | M380 the mountain road | switchbacks (a step every 16 blocks), mountain encounters; the mountain inn door -> M381 |
    | M381 the mountain inn | S03 the dying Bayushi courier (Eavesdrop, cannot fail; courier_heard G946); his pack can't be taken (G958) |
    | M382 the Togashi road | S04 the procession (props; G925 adds the "distraction" line; G956 the clerk line) -> M383; S05 duty's knife at night (autorun on return) |
    | M383 Kyuden Togashi - the garden | S04 the garden (fated; Togashi's answer paraphrased in narration, never quoted; togashi_heard G947) |
    | M384 Tamori's Furnace - the lava tubes | S06; heat tiles; b_furnace_elementals (gid 119); the lava-step jump (70%, A153 Ward-Robe) |
    | M385 Tamori's Furnace - the ash-shrines | b_ash_ghouls (gid 120); the box screams; the last shrine (save); Ember Core x3 |
    | M386 the crater's mouth | S07 b_boss_stolen_face (gid 121); S08 the box into the fire (I195 removed: the VP curse ends), the Favors (I406), the fork, the blue eyes; Rank 3 (G962); Haku goes home; back to the town |
  - **The locked choice (S05):** a nested menu; each "greyed" option answers with Mitsue's reason (as a thought) and asks again without it; only "Keep walking." ends it.
  - **Heat tiles (plugin Field heatStep, gen_maps HEAT_TILES):** EMBER blocks in M384-M386; 35-50% per step, 3-4% max HP to every member without A152/A153, never below 1 HP. Test flag -rtheat100.
  - **Boss (plugin Hazard rt_stolenface):** the Bloodspeaker remnant (E486, L45, HPx12, Res 14, weak Jade/Katana/Air; Blood Lash = Taint chance; My Blood Is a Key = AoE maho, pays 4% HP). At 2/3 HP it steals the companion's face, at 1/3 Mitsue's: weaknesses become that traveler's weapon bits (Battle weakbits overridden; damage x1.5 / ÷1.5 in onAttack), next action mirrors their last skill (players' last skills recorded as state.plast). Mitsue's Steal takes the face back (50%, certain with G897 Giseiki; G964). Barks from the production for Gendo/Yosai/Haku. Iron Box curse still on (0 VP start).
  - **Art:** boss art EP148 / banner EP149 "We Wear What We Need" from cand_scorpion1/Kitsune_Impersonator_Tradition.jpg (paint; the light block on its right is her mask and sleeve). Monsters EP166 Snow Bear, EP167 Tengu Crow-Warrior, EP168 Fire Elemental, EP169 Ash Ghoul, EP170 Wolf-Spirit (tinted Grey Wolf). Side cast: haku, courier, shoju, togashi (scale 1.25), tamorimonk, kitsukiclerk, muledriver, tbeggar, incense, outfitter, pilgrimgirl, oldpilgrim, mirumotosentry, h_tamori, h_guide. The crater's Bloodspeaker field prop is Mitsue's own sprite (EP205).
  - **Fixed along the way:** "Abbot Munashii" was missing from RokuganBattle BOSS_BANNER (its EP539 banner never showed): added.
  - **Data:** Enemies E479-E488. Skills S530-S540. Items I406; A152-A154; W147. Stores R154-R155. Cond K057. Groups 119-121. Flags G944-G966. Player P139. Hirelings #53-#54. Maps M379-M386, backdrops M872-M874.
  - **Note:** the side cast now ends near EP695 (epid() runs EP540-EP699 before foe sprites at EP700+): about four entries of room left in that range.
  - **Balance (Mitsue + Yosai, Lv 40-44):**
    - Mountains (M380/M382, Lv 40): 2-3 rounds, 67-100% HP left.
    - Furnace (M384/M385, Lv 42): 4-5 rounds, 60-75%. Fire elementals were 13 rounds (nothing in this party hits Water/Bo; Fire resist 75): HP x0.5, Fire resist 50.
    - b_furnace_elementals 5 rounds, b_ash_ghouls 4 rounds.
    - Boss (Lv 44): two actions a round (ai actnum [2, 2]; one action was 10 rounds with Yosai at full HP). Verify in play.
  - **Tests run:** S01-S08, the eavesdrop, the locked choice through every refusal, the jump, the box, the signpost entry, both guide branches (Yosai, Haku); heat tiles (a -rtwalk onto the ring with -rtheat100); snapshots of all eight maps and the furnace/crater backdrops (crater ground darkened, garden ground made pale gravel).
  - **Not built yet:** other travelers' path actions in the town (Duel, Discern, Barter, Sumai shortcut and its cliff shrine, Bless, Charm, Pilfer); TB-scorpion4-a/b (need Tamotsu, Sayo); the Blackened Sight kata at Lv 51 (no kata system); the Rank 3 technique beyond narration; the Gendo branch is written but untested (needs the merged game).
- **User changes, 2026-10-31 (during Scorpion Ch4):**
  - **Arrowroot (Yosai, all paths): heals at most 50% of the target's max HP** ("i think arrowroot is too powerfull now, it should at most heal 50% of a chars total hp"). The base formula is unchanged, but Boost multiplied it to 4-5x a target's max HP. Capped in the plugin (RokuganHazard onAttack, after every multiplier, Boost included); the description says so.
  - **Battle music = light rock with biwa** ("for battle music how about something light rock with bawaas mixed in"). gen_music: a rock kit (kick, snare, hats, crash; taiko as the tom fills), bass and lightly driven power chords, the biwa on the lead riff with bends. v1 was 84% energy under 120 Hz (a boom) and clashed (the in scale's flat 2nd over power chords): rewritten in the min'yo scale (A C D E G, also rock's minor pentatonic) over Am-F-G; the mix now sits about 10/25/48/15/4% across the bands. The user liked it ("i kinda like that music") and asked for a faster tempo: battle 176 BPM (32 bars), boss 140 BPM full time (E min'yo, Em-C-D, hichiriki and kane on top).
  - **Music log:** the Field plugin prints "[RT] BGM <id> <file>" on every change. Field battles were confirmed to start MU104 rt_battle.ogg; the user's "not hearing it" was a game session started before the file changed (restart the game after gen_music).
  - The Tamori's Furnace caves played the road track ("Tamori" contains the road keyword "mori"): pinned to cave.
- **Unicorn Ch1 "Fault Lines" (2026-10-31): DONE. Every scene and fight run in-engine (not as one continuous run).**
  Sources read in full: production/unicorn-ch1.md, its storyboard and script, research/fortunes-lost.md, docs/rules (Tamotsu's battle skills, bosses.md row), and Fortune's Lost Part I again (the courts, the Ojatara wasteland, Jiochi, Hafuna, Motobu and the monk Hitoro at Denshi, the bombing at the Welcome Road, the pigeon note, Yotomo's boy Sabu, the cave with its overhang, Naohida in silk under cotton with a dai dao).
  - **Starter:** the prologue's 7th road (G967): Tamotsu (P106) starts in the Welcome Road inn. **Shinjo Ryuko** (P140, new: Tsune's niece; Guardian's Vow = the Cover taunt, Shinjo Sweep = Katana on all) is his guardian from S01 (memory tamotsu-shinjo-guardian). Akodo Rin (P138, the same record as Scorpion Ch3) joins after the bombing (S05). Yosai's first meeting is at this inn (YOSAI_MEET M388); he may travel beside Ryuko (the Tamotsu exception).
  - **Tamotsu's kit (support, no strong attacks):** Talent = a pick like Mitsue's: Barter Coin (the old money blow) or **Barter Coin: Bribe** (S541: 10 zeni x the target's level; a person for hire, enemy field rt_bribe, takes it and goes home; anyone else loses its next action counting). Words of Peace (Lv 1, ATK down all), Share the Stores (Lv 3, heal all), Song of the Ki-Rin (Lv 5, party Regen), **Gaijin Spyglass** (all weaknesses) from Hiroichi's telescope (G985: barter 2000 zeni early, or given at the end; plugin STORY_SKILLS P106).
  - **Maps (Ch1 is late autumn 1122, before the bombing: separate maps from Scorpion Ch3's later valley):**
    | Map | What |
    |---|---|
    | M387 Buried Leaves (autumn) | the Welcome Road inn door, Persimmon (EP172) at the stable, R156 Unicorn trader (T1: A155 Unicorn Riding Armour), the bitten Scorpion yojimbo, Crane clerk, Iuchi farmer (the salt lead); hirelings #55 Iuchi Water-Shugenja (Rolling River: Water AoE), #56 Moto Outrider (Yumi AoE) |
    | M388 the Welcome Road inn | S01 (Tsune, Norie, Ryuko joins, the tribunal purse 500 zeni), the case board, the strongbox (I408 case notes), S05 the bombing after 3 cases (Rin joins), S08 judge the living (name him? G983; the pebble I407; the telescope) |
    | M389 the refugee camps | S02: Barter the hoarded rice (100 zeni -> Rice Ball x10, G984); the grandmother; give it all (G970 camps_fed, Honor +1) or keep it; b_camp_thugs (gid 122, the Barter Coin tutorial); R157 rice merchant |
    | M390 the valley road (autumn) | the spine: Shiro Iuchi (N), Hafuna (S), Yotomo (N, after S05), Shiro no Soshi (SW), Motobu (W); signposts; encounters |
    | M391 Shiro Iuchi - the garden | case 1: Daiyu and the woodchuck (EP173), the carrot, Karasu's shadow-brands (Status opens it, F-1); Hiroichi's telescope |
    | M392 the Hafuna fields | case 2: Takanobu; Barter his supply ledger (200 zeni) |
    | M393 the Motobu crater | case 3: Hitoro (Etiquette: no duel for speaking) |
    | M394 Shiro no Soshi - the hall | optional: Bantaro, Shinobu (G976) |
    | M395 Miyahana's cottage | S04 after 2 cases |
    | M396 Yotomo | S06 Sabu ("Twenty. And the angry one.") |
    | M397 the pigeon cave | b_cave_guerrillas (gid 123); the stash (I409 Powder Bomb); save before the overhang (F-2); encounters |
    | M398 the vat chamber | S07 b_boss_naohida (gid 124) -> back to the inn |
  - **Plugin:**
    - Barter Coin pick ("coin"), Bribe (rt_bribe), surrender below 40% HP (rt_surrender, the guerrillas: "We're farmers!").
    - **Powder kegs** (rt_keg, EP174 enemies the AI never targets): any Fire hit (either side; Naohida's Powder Bomb too) or any blow on a keg sets one off: 20% max HP to everyone, Naohida 5%, never below 1 HP; Rin's "Water!" bark.
    - Naohida (rt_naohida) escapes below a fifth of his HP with everyone left (the victory); barks from the production.
    - Ryuko's Guardian's Vow joins the Cover/Razor's Edge taunt. Test hook -rtbribe (auto Tamotsu bribes the first foe for hire).
  - **Art:** Naohida boss art EP150 / banner EP151 "Judge the Living" from cand_unicorn1/Koji_(ronin).jpg (paint; the pink cast warmed with HUE_SHIFT + DESAT); his field sprite is a cast entry. Peasant Guerrilla EP515 (human enemies: 4 slots left, EP516-519). Monsters EP171 Pigeon Swarm (a tinted crow), EP172 Persimmon, EP173 woodchuck, EP174 powder keg. 14 side-cast entries (ryuko ... naohida).
  - **Sprite ids:** the side cast passed EP699 (EP700+ are the party-facing foe copies): gen_sidecast epid() now continues at EP1100+ for index 280 on (ryuko etc. keep their places; Moto Outrider/Naohida and the side-story icons are EP1100+).
  - **Balance (Tamotsu + Ryuko, + Rin in the cave):**
    - Valley road (Lv 4): 2-4 rounds, 57-86% HP left.
    - Cave (Lv 7, three of them): 2-3 rounds; the guerrillas surrender, easy by design.
    - b_cave_guerrillas 2-3 rounds.
    - Naohida (Lv 8): HPx10, ATK x1.6, 1-2 actions a round: 4-5 rounds, once Tamotsu fell.
  - **Data:** Enemies E489-E499 (the exp loop now runs to E999). Skills S541-S549, S551-S552. Items I407-I409, A155. Stores R156-R157. Groups 122-124 (BOSS_LAYOUT 124: five foes). Flags G967-G989 (numeric G975). Player P140. Hirelings #55-#56. Maps M387-M398, backdrops M875-M877.
  - **Not built yet:** the recruit variant (Tamotsu met at the inn by another traveler); other travelers' path actions in the town and the camps (Charm the Crane clerk, Discern/Eavesdrop the yojimbo, Sumai the farmer, Bless the orphan, Duel/Pilfer the ronin cook); Discern on Karasu (Gendo); Bless the monk (Haruki); TB-unicorn1-a/b (Natsuko, Gendo); the rubble-rescue as a battle (production's fit conversion: a cutscene).
- **Unicorn Ch2 "The Bell Without a Clapper" = Tamotsu's view of "Fortunes Lost" (2026-10-31): BUILT. Every new scene and the boss run in-engine (not as one continuous run).**
  Sources read in full: production/unicorn-ch2-scorpion-ch3.md, its storyboard (rule C-1) and script.
  - **How the views work:** the same maps M368-M378 as Scorpion Ch3; the scenes branch on G967 (Tamotsu's road). Mitsue is absent, so Shosuro Norie carries the Scorpion bench and stands in for Mitsue on the rice-cake balcony. The seppuku plays only as news (Mitsue's SEPPUKU scene now requires G967 off; I404/G925 are never set in Tamotsu's view). The merged game and the flashback with the locked verdict wait for join-up.
  - **Shared flags:** G920-G933 (grievances, G924 counter, G926 Rin followed, G927 Gochu, G928 gochu_family_fed, G929/G930 Nihime, G932 boss, G934 verdict both).
  - **New flags:** G990 S01 (Tamotsu), G991 seppuku news, G992 troupe props, G993 verdict iuchi, G994 Unicorn Ch2 complete, G995 Persimmon and the swing judge, G996 the water-carrier, G997 the ledgers.
  - **Entry:** after Ch1 (G982), talk to Tsune at the Welcome Road inn (M388): "Wait for winter" goes to M370. S01_UNI2 is the production's bench lines; Rin and Ryuko are already in the party. Ch1's ending now says Recommended level 22.
  - **Grievances (Tamotsu, gated on G990; grievance_once() guards the G924 counter):**
    | Grievance | Where | How |
    |---|---|---|
    | Jiochi well | M371 | Barter: a water-carrier (150 zeni) |
    | Shosuro troupe | M369 | Barter: a rag-peddler's costume trunk full of Iuchi arrows (200 zeni) |
    | Katsu's funeral | M368 | the Iuchi post sergeant (emissary Status) |
    | Katsu's funeral (also) | M372 | Ichihito, Tamotsu's version |
    | Padded armies | M371 | Barter: the quartermaster's ledgers (300 zeni) |
    Three grievances unlock NEWS_U2 in M369 (the news, then Rin is followed, G926).
  - **The swing judge:** Himeko (M370) takes Persimmon for an afternoon (G995; flavour, she gets bitten).
  - **Gochu:** with camps_fed (G970) he tells everything for free; otherwise Barter 300 zeni, or overhear. Both set G928.
  - **Nihime:** Tamotsu's lines from the production. If Naohida was named (G983), one extra exchange.
  - **Grave gate and boss:** the grave gate has Tamotsu's line. The boss is group 125 (in Mitsue's view, 118).
  - **Verdict:** both, or "Shield the Iuchi dead" (G993). Norie takes the rice cake; Wax Earplugs I405; the courier hook. **Rin stays** (she's in Unicorn Ch3).
  - **Data:**
    - Enemies E500-E504 (copies of E472-E476 at Lv 23-27).
    - E505 Iuchi Shugenja Lv 28, E506 Amulet-bearer Lv 29 (rt_bubble); AREA (1.1/1.05), (1.3/1.05).
    - Encounters on M368/M374/M377 split by UNI2/MIT3 (rt_if/rt_ifnot G967).
    - Hirelings #57 Mirumoto Ashigaru and #58 Refugee Herbalist (Lv 24, leader Tamotsu, M369, skills S553/S554).
  - **Plugin (Hazard bubble):** without Mitsue, Rin mouths "Left." to Tamotsu and he answers "...Did you say 'lunch'?" (production barks). RokuganBattle BOSS_BANNER gains Naohida EP151 (it was missing, so Unicorn Ch1's boss intro never showed).
  - **Balance:** boss at Lv 27 (Tamotsu + Ryuko + Rin): 5-7 rounds; in one run of four, Tamotsu and Rin fell. Tense, as in Mitsue's view. **Not yet run:** balance_encounters for the UNI2 tables (its PARTY dict keys M368/M374/M377 to Mitsue's party; it needs a Tamotsu entry or a flag option).
  - **Bug fixed (all chapters): the text cleaner (gen_maps _clean) wrote a raw  control character in place of "".** Every " ," or " ." left by a removed stage cue became an invisible character and the punctuation was lost (" ...Not" showed as "..Not"). It now keeps the punctuation, and an ellipsis keeps its space ("Here. ...Keep"). All maps were regenerated. Watch out: this shell turned "\1" inside a quoted heredoc into  again; use chr(92) or the Edit tool for backslashes.
  - **Not built yet:**
    - Encounter balance and snapshots for Tamotsu's view.
    - TB-crossroads3 (needs Mitsue).
    - Rin's side story 2.
    - Bless on the child's grave (Haruki).
    - Charm on the swing judge (Rensei).
    - The entry into Unicorn Ch3.
  - **Follow-up (same day): encounter balance done.** Tamotsu-view foes E500-E504 retuned (road 2.0/1.6, wolves 1.6/1.4, gaki 2.4/2.4, acolyte 2.0/2.2). Road (Lv 23), hill (Lv 24) and grave path (Lv 26): 2-4 rounds, 82-94% HP left. balance_encounters gained "M368:uni"-style keys with G967=1. The maps are Mitsue's (already snapped); no new backdrops.
- **Unicorn Ch3 "The Noblest Blood" (2026-10-31): DONE. Every scene and fight run in-engine (not as one continuous run).**
  Sources read in full: production/unicorn-ch3.md, its storyboard and script, research/fortunes-lost.md, bosses.md and bestiary rows, guests-19-23 (Karasu), and Fortune's Lost Part III (pages 33-45): the eight-pointed star, Karasu's warning (jade hurts Regret), the rule that wax blocks the sound completely, servants who pull your hands from your ears, Shahai's barricaded tower, Daiyu by the brook, Tsukaru and Tabezu, the dead before the mines, and "animals cannot be possessed".
  - **Entry:** a signpost in Buried Leaves (M369 at 94,14; G994) leads to the star field M399. Party: Tamotsu + Ryuko + Rin. **Iuchi Karasu = guest #12** (gen_maps GUESTS, flag G1020, plugin GUEST_SKILLS S559 "Iuchi Karasu: Jade Strike", 2 uses). A guest takes no party slot, so storyboard G-1 doesn't apply and Rin stays.
  - **Covered Ears (G999):** the castle gate (M399) puts the wax in; a safe map (M399, M403, M404) takes it out on arrival (an autorun while G999 is set).
    - NOTE lines: note() helper; the label reads "Ide Tamotsu (note)", the text is in capitals as the script has it.
    - **Plugin (RokuganHazard):**
      - Voice skills (rt_voice: S542 Words of Peace, S543 Song of the Ki-Rin, S527 The Clouds Part) fail while covered: "(nobody can hear it)". The AI skips them (RokuganAI usable/knownSkills).
      - The servants' Hum (S555 rt_hum) silences only travelers whose ears are open.
      - Pull the Wax (S556 rt_pullwax) uncovers one traveler for the rest of the battle.
      - Breaking a servant (rt_singing; onBroken) wakes it: it fades, non-lethal, Honor +1 for each of the first three (G1011). Tamotsu's bark: "GOOD MORNING. SORRY."
  - **Maps:**
    | Map | What |
    |---|---|
    | M399 the star field | S01: the burned star, the courier, Karasu joins (guest), the Covered Ears tutorial, save; gate -> the tower; east -> the woods (G1000); south -> the camp (G1002); west -> Buried Leaves |
    | M400-M402 the tower (castle floors, encounters) | 1F the notes ("DON'T STEP ON THE HUMMING ONES"), chest Jade Dust x4 (the counter in reach); 2F b_tower_servants (gid 126), the wind-shaft ledge (70%: Daikyu-pattern Yumi); 3F S02 Shahai's notes (G1000) |
    | M403 the Iuchi woods | S03 Daiyu: comfort, or the whole truth (G1003, Honor +1); Shahai's reunion; "animals can't be possessed"; woodchuck hoard (Carrot x3 I412, 800 zeni); forest save shrine |
    | M404 the Mirumoto war-camp | S04: Tsukaru and Tabezu, Barter narration; the terms: jade (G1005 off), or honour if Honor >= 3 (G1005); the wax demonstration; the Gendo lines (script check of P102, merged game); R158 Mirumoto Quartermaster (Dragon T3); field kitchen inn; Kitsuki scout (Barter 50: Kurosho at the window); camp follower (Barter 60: Calming Tea x3); drummer; chests Ginseng x3 and Fine Katana; hirelings #59 Togashi Bo-Monk (Bo), #60 Agasha Fire-Shugenja (Fire AoE); S07 the ending (Nihime's note I414 if nihime_told G930); "Next: Regret (Recommended level 41)", G1010 |
    | M405-M407 the jade mines | S05 the graves (Karasu); camps_fed G970: Gochu and the porters, every raw-jade node is yours (else the "porter" nodes go to the carts); b_mine_dead_a (127) and b_mine_dead_b (128); raw-jade nodes (Raw Jade I410 x2 each, G1014-G1019); the foreman's ledger (I413, Kurosho's hand); save shrine; S06 b_boss_mine_guardian (129); then the jade weapons (W149 Jade-tipped Yumi, W148 Jade-backed Katana x2) |
  - **Boss:**
    - The Mine Guardian (E513): L35, HPx7, Res 12, weak to Jade, Fire and Yari; atk 1.5, two actions a round. Skills: "Stay With Us" (a big hit with a bark) and "The Quiet Dark" (AoE, Terror chance).
    - Barks: Raw Jade thrown ("Ancestor - forgive the rudeness - catch!") and Karasu's call ("a very angry oni").
    - Art: boss art EP152 and banner EP153 "All Who Dig Here Stay", from cand_unicorn3/Undead_(TCG).jpg (new; downloaded with the wiki API).
    - gen_bossart gains **KEYOUT**: per-boss hue ranges to drop, optionally limited to a zone, with keep-boxes. It cut out the red moon and the cyan ghost-fire and kept the red eyes.
  - **Balance (Tamotsu + Ryuko + Rin):**
    - Tower encounters (Lv 31): 2-3 rounds.
    - b_tower_servants: 4-5 rounds. Servant Resolve is 2, not bosses.md's 3, because with 3 the servants always died before a break could land.
    - Mine encounters (Lv 32-33): 2-5 rounds.
    - b_mine_dead_a and b: 5 rounds.
    - Guardian (Lv 34): 6-10 rounds in auto-battle, which never throws Raw Jade or calls Karasu. Expect 5-7 rounds in play; verify.
    - The star field reuses Mitsue's Ojatara foes E472-E474 and is a little easy.
  - **Data:**
    - Enemies E507-E513: Singing Servant x2 (EP516, new human enemy), Risen Dead, Gaki, Cave Bats, fixed Risen Dead, Mine Guardian. Groups 126-129.
    - Skills S555-S563 (S559 guest, S560/S561 hirelings, S562/S563 jade weapon strikes).
    - Items I410 Raw Jade, I412 Carrot, I413 the Foreman's Ledger, I414 Nihime's Note. Gear W148, W149, A156 Guardian's Lantern (the guardian's steal: Fire resist 30%). Store R158.
    - Flags G998-G1021, numeric G1011 (the first four-digit flags).
    - Cast: shahai, tsukaru, tabezu, campfollower, drummer, h_bomonk, h_agasha. Maps M399-M407, backdrops M878-M880.
  - **Not built yet:**
    - Other travelers' camp path actions: Duel the duellist, Bless the monk, Charm the follower, Sumai the drummer, Pilfer the quartermaster.
    - The Tremor side gallery (Gendo).
    - Bless on the miners' tools (Haruki).
    - TB-unicorn3-a/b (Gendo, Natsuko).
    - Karasu's SS1 "Six Months" (b_ss_karasu_hunters).
    - Silent battles have no mimed spell icons; the gimmick is the Hum and the voice rule instead.
- **Unicorn Ch4 "Regret" (2026-10-31): DONE. Every scene and fight run in-engine (not as one continuous run). The Unicorn path (Ch1-4) is complete.**
  Sources read in full: production/unicorn-ch4.md, its storyboard and script, bosses.md (b_tunnel_legion, b_boss_kurosho_regret), bestiary "Shiro Iuchi wind tunnel", equipment.md (Regret's Silence, Persimmon's Saddle, Meishodo Ward), schools.md (Tamotsu's R3 When the Veil Moves, R5 Immovable Hand), and Fortune's Lost Part III's ending (the wind tunnel, the stair of the possessed, the storm room, Nihime's curse, Kurosho's spells).
  - **Entry:** at the Mirumoto camp (M404), after Ch3 (G1010), the drums ("March with them. Chapter 4"). The siege camp is M408.
  - **Party:** Tamotsu + Ryuko + Rin. **Naohida = guest #13** (S565 Powder Charge, 1 use, Fire AoE; G1036; plugin GUEST_SKILLS index 13). Karasu walks with them as a story companion (NOTE lines; F-1).
  - **Tamotsu's Rank 3, at Lv 41:** **When the Veil Moves** (S566, once a battle). The party is Veiled (K058, new) for 3 turns: the Wail and the Hum can't take them; guard.
  - **Covered Ears, revised for both Ch3 and Ch4 (production Ch4: "Uncover to use them - but the Wail can reach you"):**
    - A voice skill used with the wax in pulls the wax out first: the skill works, and the speaker stays uncovered for the battle.
    - Spare Wax (I415, consumable, sold at the siege camp) puts it back.
    - The Ch3 narration says so.
    - The AI still avoids voice skills while covered.
  - **Gale tiles (new field mechanic, plugin Field galeStep; gen_maps GALE_TILES, map.json rt_gale):**
    - The wind tunnel's pale SAND strips. A two-beat rhythm, 0.9 s gust then 0.9 s lull (skGetTime). A step onto a strip in a gust shoves the party back to the previous step.
    - Test flag -rtgale100. Verified: forced gusts hold you back; the natural rhythm lets you through with a shove or two.
  - **Maps:**
    | Map | What |
    |---|---|
    | M408 the siege camp | S01 Naohida under the white flag: if named (G983), Barter the truce (G1023; Hiroichi takes nothing), else the pebble lines; the jade knife; Nihime arrives if told (G930); save. R159 (Unicorn + Dragon T4, Spare Wax); field kitchen; pigeon-keeper (Barter 300: the Pigeon's Letter I417, so Nihime's curse works without her: storyboard); the grandmother (camps_fed: Persimmon's Saddle A157); Soshi envoy (Barter 100: "a treaty, not an heir"); Hiroichi's chest (the Spyglass if not owned, else 4000 zeni); hirelings #61 Iuchi Water-Shugenja (Water: the Doji), #62 Mirumoto Yari Sergeant (Yari: the Legion); the tunnel mouth puts the wax in |
    | M409-M410 the wind tunnel | S02 (honour, G1005: Tsukaru holds the door; the Legion start a shield down, plugin); gale strips; pigeons; wind-ledge 70% (A159 Unicorn Lamellar); b_tunnel_legion (gid 130, the chant = a Hum); Legion Kabuto A160; encounters (possessed Legion, Moto Akutsukai, Singing Servant IV) |
    | M411 the great stair | S03 kneeling servants; notes; Shahai: send her back, or keep her close (needs shahai_trusts G1000; G1028; Karasu's Tuning Fork I416); save |
    | M412 the storm room | S04 b_boss_kurosho_regret (gid 131), then S05: Kurosho's death (with Nihime: "Mine?" "Yours."; else alone); Daiyu's line by daiyu_state (shattered: Honor +1); settlement: heir (G1030) or treaty; the Jade Toll flag G1037 if mirumoto_terms jade |
    | M413 the valley road home | Persimmon bites everyone; "the fat emissary"/"Round, my lord!"; Tabezu and the Jade Toll (G1037: M404's clerk becomes R160, jade goods +25%); Shahai's rice cake; the fork if not given; chapter card; G1031 |
  - **Boss (plugin RokuganHazard):**
    - The Shuten Doji of Regret (E518): L45, HPx11, Res 18, weak to Jade, Water and Void; Every Apology (AoE maho, Taint chance), Tears of Regret.
    - Iuchi Kurosho (E519): HPx6, Res 10, weak to Air and Bo; Bo of Water, Fury of Osano-Wo.
    - **The Wail:** every third round. The round before, "the storm draws breath". Open ears that are not Veiled and not wearing Regret's Silence are possessed (Confuse) on a 50% roll.
    - Tamotsu pulls out one plug at the start.
    - **Nihime's curse** at half the Doji's HP (needs G930 or the letter I417): Kurosho's shields break for one breath, with the production barks.
    - **The reversed song:** with G1028 and the fork, the first Wail is turned back and the Doji loses a turn.
    - **Bribing the Doji, once:** "take mine instead - and get out." It loses a turn and two shields. Kurosho ignores coins.
    - When the Doji falls, Kurosho falls too ("the wind stops").
    - Drop: Regret's Silence (A158: immune to Silence and Confuse, plugin putCondition).
    - Layout: BOSS_LAYOUT[131] puts the Doji behind and Kurosho in front.
  - **Art:**
    - The Doji: EP154 / banner EP155 "Say It Again", from the wiki's pencil "Shuten Doji 2", line art with a grey-violet ramp.
    - Kurosho: EP156 / banner EP157 "For Want of a Son", from the painted "Iuchi Haruma" (PAINT_HINTS keep the scroll).
    - New sprites: Possessed Legionnaire (human enemy EP517), the Kurosho field sprite, pigeonkeeper, soshienvoy, h_yari.
  - **Balance (Tamotsu + Ryuko + Rin):**
    - Tunnel encounters (Lv 41-42): 2-4 rounds, 78-99% HP left. The Akutsukai copy was retuned to hp 0.9 / atk 1.5.
    - b_tunnel_legion (Lv 42): 5 rounds.
    - Boss (Lv 44), in auto-battle without Spare Wax, the Veil or the guest: 9-10 rounds, all wins, two of four close. At HPx14 it was 10-11 rounds and 2 losses in 3.
  - **Data:**
    - Enemies E514-E519. Groups 130-131.
    - Skills S564-S572. Condition K058.
    - Items I415-I417. Gear A157-A160. Stores R159 and R160.
    - Flags G1022-G1037. Hirelings #61-#62. Maps M408-M413, backdrops M881-M882.
  - **Not built yet:**
    - Other travelers' camp path actions: Bless the Iuchi shugenja for the Meishodo Ward, Duel the sergeant, Charm/Sumai/Pilfer the soldiers.
    - TB-unicorn4-a/b (Mitsue; Naohida).
    - The Immovable Hand of Peace (R5, finale).
    - The Wail possession is plain Confuse (allies attacked at random), not a scripted "attack a friend".
- **Ronin Ch1 "What's Eating the Eta" (2026-10-31): DONE. Every scene and fight run in-engine (not as one continuous run).**
  Sources read in full: production/ronin-ch1.md, its storyboard and script, research/honor-and-eta.md, the Honor and Eta PDF (all 9 pages), docs/rules/sayo-remedy.md, battle-skills (Sayo), schools (the ronin schools), bosses.md 8. RONIN, bestiary rows.
  - **Start:** the prologue's eighth road (all eight are open now; G1038; P107 Sayo; prop EP207).
  - **Party:** Sayo alone. **Hiro is guest #14** (S588 No-dachi Sweep, 2 uses, double damage on Tomie Cho; G1056; plugin GUEST_SKILLS index 14). Yosai can be met in the Cakon market (YOSAI_MEET M416).
  - **Remedy (her Talent; plugin "remedy" pick list):**
    - The list: Ume-baa's Poultice (S127, renamed, free) and seven recipes S573-S579. Each recipe carries rt_recipe = [base, catalyst] and spends one of each ingredient.
    - Missing ingredients grey a recipe out (the right label shows the count); if they run out mid-battle, it fizzles.
    - Ingredients I418-I423: Ginseng, Rhubarb, Hanabi Powder, Rice Wine, Moxa, Willow Bark (sell-only items). Sold by R161, the herb seller; also from chests and Pilfer.
    - The AI uses the healing recipes while the bag holds the ingredients. Verified: "spent I418 + I421".
  - **Sayo's skills by level:** Pilfer S580 (Lv 1, steal), Compliment S581 (Lv 1), Field Dressing S583 (Lv 3), Bitter Root S584 (Lv 6: Poison + DEF down). Pilfer and Compliment carry rt_noauto, so the AI leaves them alone (it used to spam Pilfer).
  - **Pilfer path action** (gen_maps pilfer()): a chance roll; caught = Honor -1.
    - Targets: the Sono servant (55%: the Sono Chit I425 + 120 zeni, sono_link G1042), the herb seller (Ginseng x2), the bargeman (40 zeni + the Sono-barge note).
  - **First ronin school** (S01 choice; numeric G1039):
    | School | Effect | Verified |
    |---|---|---|
    | Warrior | Wolf's Technique: x1.3 on whoever targeted her this round | in logs |
    | Duelist | Wind Technique: K059 Speed +25% for the battle | in logs |
    | Yojimbo | Way of Sacrifice: her Defend gives the weakest ally K060 DEF up | needs an ally; untested solo |
  - **Maps:**
    | Map | What |
    |---|---|
    | M414 the memory (the riverbank) | Ume-baa and young Sayo; the ginseng; "clean hands" |
    | M415 Cakon docks | S01 the jump; the school choice; b_dock_thugs (132; Remedy tutorial; Ginseng x2, Rice Wine x2); harbour inn; chandler R163; the bargeman (Pilfer); the ferryman; hireling #64 Mantis Ferry Archer (Yumi) |
    | M416 the market | S02 Kagemaro (300 zeni); musicians; the doorman; the Sono servant and the herb seller (Pilfer); R161, R162 (Crane T1); the House of Tranquillity storehouse (Ieko's Love Poem I426 + 150 zeni); hireling #63 Hanabi Seller (Fire AoE); **S08 clean hands** (the execution off-screen; Kagemaro's giri; the chit if sono_link; Hiro's scars; "Next: The Noble and the Ronin (Recommended level 20)"; G1055) |
    | M417 the alley and the river gate | S03a b_alley_ambush (133: Tetsuo + the disguised Lion Ogura Tokinari, both flee at half; the chit reading); S03b the beggar-monk and the dog (the riddle, G1044) |
    | M418 the eta village | S04: Fumi, Hiro joins (guest), the blood trail; Akari's cameo (the fire talks, G1046); Ume-baa's herb box (Moxa x3) |
    | M419 the canal bridge | S05 b_tengu_bridge (134; knock-off, Compliment, they flee at half; Tengu Feather A161 by the event) |
    | M420 the paddy edge | S06 b_bakemono (135: six goblins, BOSS_LAYOUT) and the loot choice (return: Honor +1 G1049 / keep: 200 zeni, Honor -1 G1050); the cedar and two red stones (with monk_riddle: the Jade-handled Knife W150); wayside Jizo save |
    | M421 Tomie Cho's hut | S07: the firebrand I428; b_boss_tomie_old (136) then b_boss_tomie_cho (137); the end lines; to the market |
  - **Plugin (RokuganHazard):**
    - rt_flee: foes leave at half HP, with their line.
    - The tengu log: a hit of a quarter of the target's max HP or more knocks either side into the canal (K061, 2 turns). Compliment on rt_tengu makes it lose a turn preening.
    - **Tomie Cho:**
      - The old woman (rt_tomie_old) takes x0.35 damage behind the walls; a Fire hit burns the hut (G1053) and ends that battle. Without fire she can be beaten through the wall.
      - Then the tiger (rt_tomie, the Tiger boss art): at half HP the tiger form (shields back to 9, ATK up, K059 Speed up).
      - Hiro's sweep does double damage to her in both forms.
      - Barks from the production.
  - **Art:**
    - The crow-tengu: EP158 / banner EP159 from the wiki's painted "Ajari" (red silk kimono, the PDF's look), used for both. The blue "Tengu" art couldn't be cut from its sky.
    - The tiger: EP182 / banner EP183 from "Tiger". KEYOUT drops the sky, the swirl and the green wall; PAINT_HINTS for both.
    - New human enemies: tomie_old EP518, tetsuo EP519. **The human-enemy range EP500-519 is now full.**
    - 17 new side-cast entries (umebaa ... h_ferryarcher).
  - **Balance (Sayo alone, Warrior; auto-battle, no guest, no hireling):**
    | Fight | Lv | Rounds | HP left |
    |---|---|---|---|
    | b_dock_thugs | 1 | 2 | 60% |
    | the ambush | 4 | 2 | 73% |
    | the tengu (HPx3) | 5 | 5-10 | - |
    | the goblins (HPx0.42) | 6 | 5-11 | - |
    | the hut | 8 | 7 | - |
    | the tiger (atk 0.88) | 8 | 6-8 | 49-100% |
    | road encounters (M419/M420, Lv 5-6) | 5-6 | 2-3 | 65-94% |
    - The road foes were raised to atk 1.4-1.6, and one crow group cut to two crows.
  - **Data:**
    - Enemies E520-E532. Groups 132-137. Skills S573-S593. Conditions K059-K061.
    - Items I418-I428. Gear A161, A162, W150. Stores R161-R163.
    - Flags G1038-G1062 (numeric G1039). Hirelings #63-#64. Maps M414-M421, backdrops M883-M887.
    - Fixed: hire_npc assumed every leader has a family name ("Coin first, Hiruma-sama"); for Sayo it now says "Coin first, Sayo. Ronin pay up front."
  - **Not built yet:**
    - The recruit variant (Sayo met by another traveler in the market).
    - The samurai bridge lines (merged game).
    - Other travelers' path actions in Cakon (Eavesdrop, Discern, Charm, Duel, Sumai, Bless).
    - TB-ronin1-a/b.
    - The kata pick at Lv 5 (no kata system).
    - Kagemaro's giri favour as a later door.
- **Ronin Ch2 "The Noble and the Ronin" (2026-11-01): DONE. Every scene and fight run in-engine (not as one continuous run).**
  Sources read in full: production/ronin-ch2.md, its storyboard and script, Entanglements & Tied Snakes (all of it, incl. the
  den: white sand, black-sand kanji, holes in the walls, the green light turning white), Adventure Ideas "The Noble and the
  Ronin", bosses.md, bestiary F row, kiho.md (Jinnai), sayo-remedy.md, schools.md (ronin ranks).
  - **Entry:** Cakon docks M415, a talk at the west edge after G1055 ("Chapter 2 ... Recommended level 20") -> M422.
  - **Party:** Sayo alone. **Jinnai = guest #15** (S596 Freezing the Lifeblood, Paralysis, 2 uses; G1079; plugin GUEST_SKILLS
    index 15). Chi Protection is automatic: once a battle, while Jinnai is the guest (G232=15), Sayo under 1/3 HP is healed 40%
    and cured of Poison/Paralysis. He slips away on night 2 (G232=0), rejoins in the boss scene, leaves at dawn (G232=0).
  - **Remedy:** recipes can take three ingredients now (plugin recipeCount/spend loop over rt_recipe). New: S594 Ginseng +
    Willow + Snow-Lotus (heal, DEF up, Regen K040; the barge's story brew), S595 Ginseng + Snow-Lotus (heal + Regen). Skill
    field rt_learn (a flag): the pick list hides a recipe until taught (G1066). Snow-Lotus I429, Wild Honey I436.
  - **Rank 2** (S09 pick, rpgvar G1092): her school's R2 or another school's R1. Plugin ronin(t) checks G1039 or G1092.
    4 Punish the Arrogant (next blow on whoever wounded her x1.25), 5 Taking the Measure (+15% per blow on the same foe, max 2),
    6 Will Not Flesh (once a round a single blow meant for an ally hits Sayo). All three verified in logs.
  - **Maps:**
    | Map | What |
    |---|---|
    | M422 the river road in winter | S01 Sadanobu, b_retainers_road (138; they flee at half), the writ (Pilfer: I432, writ_pilfered G1065, Honor -1, the crow); fox tracks + Fox shrine (a rice ball -> Fox Charm A144); ditch chest; encounters (wako, python, kappa, glory-hungry bushi; E539-E542) |
    | M423 the rice barge (night) | S02: Jinnai, the two-catalyst brew (Snow-Lotus x2, Willow), guest join |
    | M424 Floating Flowers | S03 the radish-nose poster, save; the inn = the nights (F-1): rest 1 = S04 the storm (b_storm_jetties 139, or 140 with one squad lost if the pedlar's lantern was pilfered G1083), spare (G1069, Honor +1) / drive (G1070); rest 2 = Jinnai's empty bed -> the den. Kanemori & Oyuki (Sayo-only route: Remedy her cough with Willow + Wild Honey G1080 -> Pilfer his unsent letter G1081 -> a cup of rice wine, he asks on the jetty G1082: Kanemori's Discount I435 + Herbal Salve x5). Madame Hagi (200 zeni: the midnight visitors), Tokubei + his office (the newer floor mats; chest), fisherman (Pilfer fish), boatman (the storm warning), shrine (rites), Oyuki's riverside hut. Shops R164 market T2, R165 Kanemori's goods: every line twice, full price / 90% by reqs on G1082 (reqfail 0 hides the other). Hirelings #65 Sparrow Ronin (Katana), #66 Wandering Air-Shugenja (Air, all). S09 dawn on the jetty: Snake Beads I430, Rank 2, card, G1078 |
    | M425 the snake den | S05 (G1093); Jinnai's back far ahead; the alcove (the bead-snake: Shadow Scale x2, Antidote x3); encounters (shadow-snakes, python, Order watcher) |
    | M426 the sand room | S06: crawl (crawl_results G1073 +1) or walk (HP -18%, Poison on Sayo); Yosai, if along, walks it upright and regenerates. White sand = the SNOW tile (SAND draws as cobbles) |
    | M427 the serpent's mouth | S07 the Voice; save |
    | M428 the way out | S08 b_boss_snake_enforcers (141) -> the Snake Ring I431, order_promise kept G1076 / refused G1077 -> M424 dawn |
  - **Boss (plugin):** shadow-snakes (rt_shadow) rise every 2nd round while an enforcer (rt_enforcer) stands ("Rise, children of
    the den!" - verified). First enforcer broken, or a blow that would kill one (surrenderDying chain): Jinnai steps in, every
    foe stands down (fade), G1075. Freezing the Lifeblood has its lines.
  - **Engine fix (affects Ronin Ch1 too):** RPGResource.getResourceType accepts only 5-character ids, so every sprite id past
    EP999 (the side cast EP1100+: Ume-baa, Kagemaro, Hiro... and all of Ch2's townsfolk) was an INVISIBLE ghost on maps and
    in battle (fade() also crashed on them). RokuganField.sk now replaces ::rpgres with RTResource, which also takes longer
    all-digit ids. Verified by screenshot (Floating Flowers' cast now draws). Ch1's earlier "verified" runs were logs only.
  - **Art:** side cast sadanobu ... h_windpriest (EP1129-1140); human enemies EP1300+ (ikoma_retainer, retainer_captain,
    snake_enforcer, order_watcher; gen_human_enemies epid extended); Shadow-Snake EP175 = a dark hsv copy of the Paddy Python.
  - **Balance (Sayo alone, Warrior, auto-battle, Jinnai as guest, a few ingredients):**
    | Fight | Lv | Rounds | Result |
    |---|---|---|---|
    | b_retainers_road | 20 | 3 | won, 62% HP |
    | b_storm_jetties (5) | 22 | 10 | won (with remedies) |
    | b_storm_jetties (4) | 22 | 6 | won, 50% |
    | b_boss_snake_enforcers | 23-25 | 5 | 4/4 won, 34-81% |
    Tuning: retainers atk x0.75 (captain 0.85), enforcers HPx3 atk 0.7, shadow-snakes atk 0.45, Shadow Bite poison 35%,
    Serpent's Cut 25%. The air-shugenja's wind raised to PDEF*0.6+40+LV*11 (it was too weak to matter).
  - **Data:** Enemies E533-E543. Groups 138-141. Skills S594-S601. Items I429-I436 (I433/I434 are sell-only trophies).
    Stores R164-R165. Flags G1063-G1093 (numeric G1073, G1092). Hirelings #65-#66. Maps M422-M428, backdrops M888-M890.
  - **Not built / not verified:**
    - The Remedy pick-list filter (rt_learn) is UI code; auto-battle doesn't open it, so it is untested by hand.
    - Other travelers' path actions in Floating Flowers (Discern, Eavesdrop, Charm, Duel, Sumai, Bless, Barter): Sayo has
      her own routes (Pilfer, Remedy, coin); the others wait for the merged game.
    - TB-ronin2-a/b. The kata pick (Striking as Void at Lv 25: no kata system). Kappa "Bow".
    - writ_pilfered (G1065) pays off in Ronin Ch3 (the Lion checkpoint).
  - **Later the same day (Ch2 follow-ups):**
    - Boss art for the den fight: the lead "Enforcer of the Order" (E544, same stats as an enforcer) wears the wiki's
      painted "Kolat Assassin" (EP176, banner EP177 "The Line Must Stay True"), cut along a hand-traced polygon
      (gen_bossart POLY: grey robe on a grey wall defeats GrabCut). Group 141 = E544 + E536 + two shadow-snakes;
      BOSS_LAYOUT[141]. Re-tested: 5 rounds, won.
    - M890 now uses rt_hd2d_battle: the cave preset turned every sprite in the den fight to a silhouette (memory: no
      fog on bosses).
- **Ronin Ch3 "The Village of the Wounded Lion" (2026-11-01): DONE. Every scene and fight run in-engine (not as one
  continuous run).**
  Sources read in full: production/ronin-ch3.md, its storyboard and script, Past Heroes (all 16 pages: the snow mounds
  = burnt huts, the rock shelter with the frozen yari and the Imperial Guard banner, the Crane shot with the Guard's
  arrows, the courtyard of frozen rebel guards, the pagoda, the kneeling Matsu "I have failed", the basin of
  bloodstones, Togashi's words to Kichi), bosses.md, bestiary F, kata.md (Endless Strike), equipment.md.
  - **Entry:** Floating Flowers M424, a talk at the west edge after G1078 -> M429.
  - **Party:** Sayo; **Matsu Hanae (P141)** joins at the trailhead (front-row companion; Matsu Fury S607, Lion's Charge
    S608) and leaves at the village gate after the descent. The other four grandchildren climb along as story NPCs.
    **Mirumoto Hikaru = guest #16** for the boss only (S602 Endless Strike, 2-4 hits, 2 uses; G1129; GUEST_SKILLS 16).
  - **Maps:**
    | Map | What |
    |---|---|
    | M429 the road north | S00 the Lion checkpoint: the writ (G1065) waves her through (G1095); else pay 300 zeni or walk through (b_lion_checkpoint 142) (G1096); the frozen shrine (save); chests |
    | M430 the village | S01 the five grandchildren, Old Mosuke at the snow mounds, save; inn, outfitter R166 (Lion T3, Bo, jade), Mosuke's wife R167 (Rice Cakes I439); Pilfer the outfitter's crate -> Climbing Spikes I437; the hero shrine (rites) and its storeroom (the tablets' dates don't match); hirelings #67 Goat-herd Archer (Yumi), #68 Jade-dust Pedlar (Jade, all); the trailhead (Hanae joins, G1098); S06/S07 at dusk: Mosuke (mosuke_knows G1114), the fire, the snake-ring watcher (order_promise G1076: bows / writes) |
    | M431 cedar slopes | rope point 1 (gate until tied), the rock shelter (frozen yari + Guard banner), the Crane grave -> b_snow_beasts (143), Hikaru first seen |
    | M432 ice ledges | rope point 2, the scorched gate -> b_frost_spirits (144), the frozen pack (Frost Shard x2), the spiked ledge (Climbing Spikes: Ginseng Tonic x2, Jade Dust x3) |
    | M433 cloud bridge | rope point 3, the Mirumoto armour facing down, the castle gate (save) |
    | M434 the courtyard | the frozen dead; replays 1 (the kidnapping) and 2 (Lion kills Crane) |
    | M435 the pagoda | replays 3 (the gate fuse), 4 (Mirumoto runs); the kneeling Matsu, "I have failed" (Hanae); the nursery (Silver Rattle I438); replay 5 at the basin door (needs 1-4) -> "The legend is a lie", save (G1109) |
    | M436 the basin hall | S04 b_boss_ghost_guard_basin (145) -> S05 Hikaru speaks (hikaru_spoke G1111), climbers_told (G1112) -> S06 the blizzard descent (everyone comes down; Hikaru stays; Kata Scroll I440; Hanae's bow) -> the village |
  - **Boss (plugin):** the basin (rt_basin) raises the fallen guards and the shade (rt_ghostguard) every 2nd round;
    cracks at half HP; broken or destroyed (surrenderDying chain) it ends the fight: everyone fades, bowing (G1110).
    Drop: Bloodstone Shard A163 (+1 VP at the start of every battle: plugin RokuganBattle state init).
    Art: the Shade of the Crab Lord EP178 / banner EP179 "The Prince Must Not Come Down" from the card art "Shiryo no
    Hida" (gen_bossart DARKKEY: green hues above a value threshold; the night sky dropped). The basin EP181 is drawn
    (gen_monsters bloodstone_basin, scale 3.2). Ghost-guard EP1304.
  - **Balance (auto-battle):**
    | Fight | Party | Lv | Rounds |
    |---|---|---|---|
    | b_lion_checkpoint | Sayo alone | 30 | 5 (won, 52-80% HP) |
    | b_snow_beasts | Sayo + Hanae | 31 | 3 |
    | b_frost_spirits | Sayo + Hanae | 32 | 3 |
    | b_boss_ghost_guard_basin | Sayo + Hanae + Hikaru | 34-35 | 5-9 (won; once Sayo fell and Hanae finished it) |
  - **Engine/tool fixes:** MapSpec.walls (extra no-entry cells) were never shifted by pad(); now they are (the cloud
    bridge and the ice ledge edges use them). D: drive writes fail intermittently (Errno 22, likely Defender scanning
    new PNGs): run generators through scratchpad retry_run.py-style save retries if it happens.
  - **Data:** Enemies E545-E554. Groups 142-145. Skills S602-S608. Items I437-I440. Gear A163. Stores R166-R167.
    Flags G1094-G1131. Player P141. Hirelings #67-#68. Maps M429-M436, backdrops M891-M893.
  - **Not built:** TB-ronin3-a/b; other travelers' path actions in the village (Eavesdrop, Sumai, Charm, Discern,
    Duel, Bless, Barter); Rank 3 at Lv 41 (her third technique: the pick belongs at the start of Ch4 or a level hook).

- **Python environment (2026-11-02):** the old system Python (C:\Program Files\Python311, with numpy/Pillow/OpenCV) is
  gone; only a bare user Python 3.11 and a new Python 3.15 remain. A project venv now holds the packages:
  `D:\RokuganTraveler\.venv` (Python 3.11.9; numpy 2.4.6, Pillow 13.0.0, opencv-python 5.0.0). Run every tool with
  `.venv\Scripts\python.exe -E tools\<script>.py` (regen.py passes its own interpreter on).
  gen_bossart.py now takes boss keys (`gen_bossart.py naga_champion`) to rebuild only those, so the new library
  versions don't silently redraw approved bosses.
- **Ronin Ch4 "The Oracle's Choice" (2026-11-02): DONE. Every scene and fight run in-engine (not as one continuous
  run). The Ronin path (Ch1-4) is complete.**
  Sources read in full: production/ronin-ch4.md, storyboards/ronin-ch4.md, scripts/ronin-ch4-the-oracles-choice.md,
  bosses.md (b_well_agents, b_race_assassins_1-5, b_boss_naga_champion), bestiary F "Oracle's volcano town" (Kolat
  Agent, Shosuro Renegade, Fire Elemental), sayo-remedy.md §4 (Anatomy -> Diagnosis), equipment.md (Ember Charm, Naga
  Pearl), schools.md (Sayo's Rank 3 at Lv 41).
  - **Entry:** the Wounded Lion village M430, a road-marker at the gate (4,19) after G1116 -> M437.
  - **Party:** Sayo alone. Hiro answers the Guest call (#14) from the eta quarter (S03) until he holds the alley (race
    battle 2). Hirelings #69 Crater-shrine Archer (Yumi), #70 Isawa Wind-Priest (Air AoE: a boss weakness). Yosai meets
    her in the town (M438).
  - **Sayo-only path actions:** the other travelers' actions in the production table (Eavesdrop, Discern, Bless,
    Barter) are Sayo's own here: the pilgrims are calmed with a ginseng root (Bless -> G1136: the crowd parts on the
    road and heals 30% HP), the old priest's back-gate key is bought for his roof, 800 zeni (Barter -> G1137), the
    scout and the second agent only talk. The cipher letter is the required Pilfer (70%, repeatable).
  - **Maps:**
    | Map | What |
    |---|---|
    | M437 the pilgrim road | S00 chapter card + **Rank 3 pick** (G1133, generated per G1039/G1092 combo: an R3 if she holds that school's R1+R2, else R2s/R1s she lacks); lava pools; wayside save shrine; lava tube (b_lava_tube 152 -> Ember Core x3, G1155); encounters |
    | M438 the shrine town | S01 Akari (save; she follows until S03); agent (Pilfer: Cipher Letter I441, G1135); snake scout (G1156); priests; pilgrims (Remedy, G1136); old priest (key I442, G1137); inn; R168 temple outfitter (T4 + jade, incl. Matsu War Yari), R169 herb stall; S05 the teahouse offer (fake choice; order_promise line); the agents' lodging chests (Shosuro Powder, Actor's Mask, Shosuro Tanto) |
    | M439 the eta quarter | S03 Ume-baa, Anatomy (G1138: Diagnosis in the Remedy list), Hiro's scars (G1139 Hiro SS2 unlocked), Rhubarb + Moxa x2, Hiro guest; the well lane (needs the letter) -> M440; Akari starts the race after S05: route choice (G1144 1 road / 2 cliff), G1145 -> M441 |
    | M440 the poisoned well (night) | S04 b_well_agents (146; they flee at 25%) -> the brew (spends Rhubarb + Moxa if she has them) G1141 -> the three faces G1142 -> save |
    | M441 the rooftops (night) | race 1 (147) on the roofs, race 2 (148) in the alley; Hiro stays (G232 0); no way back, no save |
    | M442 the switchback stair (night) | race 3 (149) or: climbers_told + road -> the grandchildren hold it; key + road -> the back gate skips it; cliff: 149, 150, 151 (key skips 151); the crater lantern (save, G1151); S07 b_boss_naga_champion (153) -> Honor +1 if talked down, Naga Pearl A165 -> M443 |
    | M443 the crater shrine (dawn) | S08 the ascension: Ember Charm A164; the mosuke_knows line; chapter card -> back to the town |
  - **Boss (plugin rt_naga):** half HP barks; broken (Suki) -> talked down (G1153), fades; a killing blow -> he yields
    and coils aside (no flag). Poison never takes on him (RPGEnemy.putCondition refuses K001: the engine ignores CDR on
    option-borne conditions). Art EP184 / banner EP185. The pearl is given by the event (escaped foes drop nothing).
  - **Plugin:** Rank 3 (ronin( t) reads G1133): Desperate Speed +1 blow x0.75, Strike Like Wind +1 blow x0.7 never
    misses, Hasten the Blade K062 after Defend. Diagnosis (S609, rt_diag) marks; next Remedy on them x1.5. Ember Charm:
    the accessory grants S615 Spark / S616 Rekindle via opt_getskill (works on equipment); one use a battle shared by
    rt_usekey (RokuganAI usesKey). rt_flee_pct now uses rt_fleebark. Test hooks -rtember, -rtdiag.
  - **Balance (auto-battle; Sayo with the Excellent Katana W134 - the Ch1 Ronin's Katana is far too weak for Lv 40+):**
    | Fight | Lv | Rounds | Sayo HP left |
    |---|---|---|---|
    | b_well_agents (+Hiro) | 42-43 | 4-5 | 30-90% |
    | b_race_assassins_1/2 (+Hiro) | 43 | 2 | 78-86% |
    | b_race_assassins_3 | 43 | 5 | 23-37% |
    | b_race_assassins_4/5 (cliff; tested with the weak W100 only) | 43 | 4-5 | 38-52% |
    | b_boss_naga_champion, katana (auto spams Bitter Root, useless vs him) | 45 | 25-29 | 51-60% |
    | b_boss_naga_champion, Matsu War Yari (weakness) | 45 | 13 | 53-69%, talked down |
    | road encounters | 41 | 2-6 | 49-91% |
    The champion's HP (AREA 1.4) is set so 16 weak hits break him just before his HP runs out.
  - **Data:** Enemies E555-E561. Groups 146-153. Skills S609-S616. Items I441-I442. Gear A164-A165. Cond K062. Stores
    R168-R169. Flags G1132-G1158 (numeric G1133, G1144). Hirelings #69-#70. Maps M437-M443, backdrops M894-M896. Cast:
    oracle, snakeelder, pilgrimagent, nashiko, h_shrinearcher, h_windisawa.
  - **Not built:** TB-ronin4-a/b; Hiro SS2 "The Tiger in the Blood" (only the unlock flag G1139); Rensei's "Next time"
    beat (no samurai in her party); Rank 4 at Lv 51.
  - **Python environment (same day):** see the entry above: tools run from `.venv`.
- **The finale "The Empress of Nothing" (2026-11-04): IN PROGRESS, built in slices.**
  Sources read in full: production/finale.md, storyboards/finale.md, scripts/finale-the-empress-of-nothing.md,
  flag-ledger.md, OCTOPATH-FIT.md.
  - **The join-up (new).** There is no merged game yet (each save walks one traveler's road; the M099 prologue picks
    it). F01 "Eight Roads" has all eight arrive on their own, so the finale does the join-up itself:
    `::Rokugan.fJoinAll()` (plugin RokuganField) brings every traveler up to the best traveler's level and gives anyone
    still on their Ch1 weapon a road-worn T4 kit (FKIT). Story companions leave (Yosai waits at the shrine).
    - **Two parties of four (production F02/F09).** The battle takes every member, so Party A is
      `::rpgstat.members` and Party B is a reserve bitmask in **G1160** over P100-P107. `fSwapAll`, `fTrade(a, b)`,
      `fSummary`, `fLabelA/B` (choice labels use `${...}` templates: replaceTemplate expands text0-7 and message
      text). Whoever steps in shares the party's level (OT2).
    - gen_maps `PARTY_MENU` (swap / trade one / leave) at the stockade gate; `REST_ALL` also heals Party B.
    - **The unlock:** production says all eight Ch4s. `finale_gate(ev, x, z, own_ch4_flag)` puts a road-marker on a
      path's last map that opens on that path's own Ch4 while `FINALE_ALL_EIGHT = False`; flip it when the merged
      game exists. CH4_DONE: G286, G434, G830, G573, G698, G953, G1031, G1154. Placed so far: M438 (Ronin).
  - **Slices:** A = Act 1 (the road, the shrine, F01-F03, seven waves); B = Act 2 (Shinomen, Stich'Kik, Mamoru, the
    glade); C = Act 3 (the debate, eight shields); D = Act 4 (three phases, boss art); E = F10 montage, F11, E01
    codas, E02, post-game.
  - **Slice A (built; see the next entry for test results):**
    - M444 the Plains of Thunder (F01 at the west end: the eight lines, the join-up, TB-finale "Eight Roads"; the
      burned village; the waystone save; the thunder-split rock -> Moonlit Yumi W153, G1171; encounters on M897).
    - M445 the Shrine of Osano-Wo (F01 at the gate: Jinnai, the abbot, Jinnai answers the Guest call #15; the pilgrim
      hall inn, closed during the waves; R170 Shrine Smith T5, R171 Pilgrim Hall Stores; the thunder shrine save; the
      jade cache I130 x5; hirelings #71 Thunder Monk (Air AoE), #72 Hida Jade Archer (Yumi + Jade); the stockade gate
      runs the seven waves, each followed by an automatic party swap; F03 the herald; save).
    - Waves (groups 154-163, backdrop M898): goblins; ogre + goblins (Natsuko); burning fanatics (Water); the ram
      (ogre captain, or "Ryozo" E571 if oni_named_ryozo G050: boss art EP186, G1174); the abbot (onikage); the breach
      (Akutsukai + zombies; Shizue); the many-legged horror E575 (boss art EP188, line art "Kumo 3"). Kage's flare
      (G281 or G217) brings the Hiruma a wave early: waves 5-6 use the one-foe-fewer groups (G1175). three_clan_truce
      (G570) + G1173 (defence in progress): weakness hits break 2 shields (RokuganBattle onAttack).
    - Data: E562-E575 (road E562-E566); S617-S623; W151-W156 (T5; W153 chest only); A166-A168; R170-R171; flags
      G1160-G1177; cast abbot, herald, thundermonk, shrinepeasant, h_thundermonk, h_jadearcher; art
      _sources/wiki_art/cand_finale1 (Kumo, Spider, Hermit candidates).
  - **Slice A tested in-engine (2026-11-04), 0 script errors:** F01 on the plain (the eight lines, fJoinAll: kits to
    the seven who hadn't walked their road, Party A = the arriving traveler + P100-P102, Yosai's farewell when he was
    travelling); F01 at the shrine gate (Jinnai guest, rest + save); the stockade gate's party menu (trade one: labels
    from templates, Lv catch-up); wave 4 with oni_named_ryozo + the flare (Ryozo lines, Kage, G1175, auto-swap);
    wave 7 -> F03 the herald -> save; the truce (Resolve 3 -> 1 per weakness hit). The -rtfast log now expands
    `${...}` templates, as the player sees them.
    | Fight (Lv 55, Party A in the arrival kits, auto) | Rounds | HP left |
    |---|---|---|
    | wave 1 goblins / 2 ogre + goblins / 3 fanatics | 4 / 4 / 4 | weakest 18-46%, others 75-100% |
    | wave 4 ogre captain / "Ryozo" | 5 / 6 | Ryozo: Gendo 4%, Rensei 44% |
    | wave 5 onikage / 6 the breach | 4 / 5 | Rensei 11% / 37% |
    | wave 7 the many-legged horror (Taint lowers max HP) | 10 | 61-100% |
    | road encounters (Lv 51) | 2-5 | lowest 47-83%, total 86-95% |
    Each party fights 3-4 waves with no rest (items only), so the waves are tuned as a gauntlet, not one by one.
    Note: Gendo's Interrogate makes the target's next skill fizzle (the "Battering Ram 1" hits).
  - **Not built in Slice A:** the escort mechanic of wave 5 (the abbot is narration; the battle is the onikage); Kage
    as a guest; reserve healing at the inn (Party B heals at save shrines and REST_ALL only); road-markers on the
    other seven paths' end maps are placed from heights only, not yet snapped (FINALE_GATES).
  - **Next: Slice B, Act 2 "Shinomen Mori"** (shinomen_edge, shinomen_1-4, kumo_fire, corrupted_glade approach;
    Stich'Kik, Squeak if nezumi_friends G051; Naga marks if naga_talked_down G1153; Mamoru's courtesy test; the Duty
    plaque; the point-of-no-return save). Free backdrop ids left: M806-M809, M819, M899. Free art EP190-EP199.
  - **Slice B, Act 2 "Shinomen Mori" (built and tested 2026-11-04, 0 script errors):**
    - The stockade gate (after F03) now offers "Go to the Shinomen Mori" -> M446.
    - M446 the edge (F04 Stich'Kik: Squeak if nezumi_friends G051; both choices free him; the dry-cave fallback (F-3);
      a waystone save). M447 the deer track (F05 the Naga marks, Sayo's extra line if naga_talked_down G1153, a Naga
      watcher). M448 the carved mock-seppuku (eight lines). M449 b_shinomen_a (group 164: Oni Spawn + 2 Kumo Brood,
      foes standing on the path) and the root-wall (Tremor) -> Naga shrine: Naga Pearl A165 x2, + Spawn Pearl I444 if
      G1153. M450 the Lava Trees: b_shinomen_b (165: 2 dryads + 2 poppies), the mossy-shrine save. M451 Mamoru's
      fire (F06: polite -> "Two Voices" hint, mamoru_hint G1185; rude -> b_kumo_spiders 166, G1186). M452 the glade
      (F07: the "Duty" Plaque I443, Stich'Kik turns back; the last save with the point-of-no-return prompt (F-2); the
      way on is a placeholder for Act 3).
    - Stich'Kik follows the party M446-M452 (rt_follow) until the glade.
    - finale_shrine(): save points in the finale rest both parties and offer the party menu (F01's promise).
    - Encounters M447-M450 on backdrop M899: Kumo Brood E576, Naga Scout E577 (yields when broken: new plugin hook
      rt_yield_broken in RokuganHazard, via the surrender path; killing one sets G1188), Lava Tree Dryad E578,
      Toothed Poppy E580, Oni Spawn E566, Wolf-Spirit E582. Fixed: E579 Oni Spawn, E581 Kumo.
    - Art: EP107 Naga Scout, EP108 Lava Tree Dryad, EP109 Kumo Brood, EP208 Oni Spawn (gen_monsters); EP357
      Stich'Kik (gen_nezumi, one-handed); cast "mamoru" (gen_sidecast). Both Oni Spawns (E566 road, E579) now use
      EP208: they had inherited the Kommei boss art (user rule: boss art for bosses only).
    - Data: S624 Cocoon, S625 Ember Rain; A169 Kumo Silk (Evasion +12; Kumo drop 8%/25%); A165 drop from Naga
      Scouts 15%; I443 Duty Plaque; I444 Spawn Pearl; flags G1178-G1188; groups 164-166.
    - Balance (Lv 56-57, Party A in the arrival kits, auto):
      | Fight | Rounds | HP left |
      |---|---|---|
      | b_shinomen_a (oni + 2 kumo) | 5 | Rensei 7%, others 64-94% |
      | b_shinomen_b (2 dryads + 2 poppies) | 5 | weakest 50% |
      | b_kumo_spiders | 4 | weakest 74% |
      | Shinomen encounters | 2-5 | lowest 43-76%, total 80-91% |
    - Note: map geometry needs `regen.py --maps` (without it the new .bw files are missing and battles crash at
      launch: "loadData does not exist in null").
    - Not built: the "Two Voices" hint does nothing yet (Slice C/D should read G1185); Squeak and Stich'Kik's
      homecoming is narration only (the codas, Slice E, can show it).
  - **Slice C, Act 3 "The Debate" (built and tested 2026-11-04, 0 script errors):**
    - The glade's way on (M452, after the plaque): "Go on. (There is no return.)" -> M453 the heart of the glade
      (no exit). F08 plays on arrival: Doji Nashiko (new cast "empress": white and crimson court robes) on the
      leathery mat.
    - The debate UI is the Lion Ch2 / Phoenix Ch2 one: for each traveler, her doubt (their clan's weakest virtue), the
      stumble, her attack on their strongest, then a choice: the strong answer from their story or a weak stock one
      (her retort). Each strong answer breaks one of her eight shields: **numeric G1189 (0-8), for Slice D.**
      Sayo's last word is the eighth.
    - Story lines inside the strong answers: play_known_scenes G421 >= 1 (Rensei: "I've read your play" / "Act
      three. Scene two." -> "WHAT PLAY?"), glory_refused G818, report_truth G569, whole G696, courier_heard G946
      (before the choice), box_destroyed G953, settlement heir G1030.
    - Then "The Empress rises": a save offer; G1190. Act 4 is a placeholder line.
    - Tested: all strong + every flag (8 of 8, every extra line), all weak (0 of 8).
    - The strong answer is the second option for Rensei, Haruki and Tamotsu (rchoices), the first for the rest.
  - **Slice D, Act 4 "The Empress of Nothing" (built and tested 2026-11-04, 0 script errors):**
    - F09 autoruns in M453 after the debate (G1190; scene flag G1195, so a reload of the debate's save starts it
      again). Party A fights phase 1, fSwapAll, Party B phase 2, then "choose your best four" (BEST_FOUR: up to six
      trades, "Fighting / Waiting" labels from the new plugin fFight()), phase 3, "she flees" -> placeholder for F10.
      No healing between phases (the save before F09 is the retry point).
    - Phase 1 b_boss_final_nashiko_p1 (gid 167, backdrop M806 the glade): E583 Doji Nashiko (EP190, Res 20) + two
      Seduced Champions E584 (rt_bloodshout). Plugin rt_bride: she vanishes every third round for one round (hits
      do nothing; jade or crystal reveals her); nashiko_unmasked G279 = not on round 1; same_woman_proven G361 = -4
      shields; Blood Shouting moves her damage onto a standing champion (her shields still crack) unless the party
      has "Against the Bloodspeakers" I177; champions are freed (broken or beaten down), never killed. A lethal blow
      makes her rise out of reach.
    - Phase 2 (gid 168, backdrop M807 the starfield): E585 Body of Damned Time (EP192, Res 24, two actions). Plugin
      rt_aging: from round 2 everyone ages a year a round (-6% dealt, +6% taken per year); Whole G696: Haruki's
      Water heals take two years off.
    - Phase 3 (gid 169, M806): E586 The Empress of Nothing (EP194, two actions). Plugin rt_trueform: Resolve 28 -
      G1189, -2 more for "WHAT PLAY?" (G421; -1 with G429). Exploits, automatic, once each: round 2 "Empress" Bait
      (G427 + Rensei: Suki; with G429 only half her shields), round 3 Two Voices (G1185), round 4 Sayo's smooth stone
      (colour-blind), round 5 the Immovable Hand (Tamotsu Lv 61+ = Rank 5); a critical hit = a Disfiguring Strike
      (she loses her next action, once a round). Obsidian: rt_obsidian_weak (the existing Lion Ch4 rules). At 10% she
      flees (rt_flee_pct); a lethal blow leaves her at 1 HP.
    - Simplification: the production's exploit "commands" are automatic barks on fixed rounds, not menu commands.
    - Art: gen_bossart nashiko_bride EP190/banner EP191 and nashiko_time EP192/EP193 (line art "White Woman", two
      ramps), nashiko_true EP194/EP195 (painted "Doji Nashiko", a hand-traced POLY plus DROP_ALL curtain holes).
      BOSS_BANNER now also has the Naga's Champion, "Ryozo" and the Many-Legged Horror (drawn but missing before).
    - Data: E583-E586, S626-S632, groups 167-169, flags G1192-G1196.
    - Balance (Lv 58, arrival kits, auto, no items):
      | Fight | Rounds | HP left |
      |---|---|---|
      | phase 1 (Party A: no healer) | 9 | Gendo down, others 37-88% |
      | phase 2 (Party B) | 7-8 | 60-100% |
      | phase 3, debate 0/8, no exploits | 9 | Haruki 29%, Shizue 27%, others 77-100% |
      | phase 3, debate 8/8 + exploits | 10 | Rensei and Sayo down, Haruki 13% |
      (Variance is large; earlier tunings lost phase 1 (hidden 2 rounds in 3) and phase 3 (HPx2.0).)
    - Bug to remember: `battle()` takes the encounter map M001, not the backdrop (the group's mapid is the
      backdrop); with a backdrop id the fight silently doesn't start.
  - **Slice E (2026-11-05): F10 Flight, F11 Death, E01 Eight Codas, E02 Final Image, post-game. DONE, run in-engine.**
    Sources read in full: production/finale.md (F10-post-game), scripts/finale-the-empress-of-nothing.md (Flight to the
    end), storyboards/finale.md (epilogue maps, F-4 post-game rule).
    - **F10/F11** (gen_maps F10_FLIGHT, F11_DEATH; appended to F09_FINAL in place): the montage, one shot per flag:
      Kage G286 (Crab Ch4 done), Squeak G051, Gonta G015, the old guard G248, Sanae palanquin G429 / with Masanori,
      her line G433 Empire / the House, Imuro G311, the Scorpion merchant G316, the Mirumoto army G1004, Yosai G818,
      Momo G715, Toturi G499, Atsuko G505==1, Shogen G532, Mieko G696, Keiki's monks G625, Hana G859, Osuko's souls
      G907, Naohida G1030, Karasu G998, the Ojatara refugees G970, Hiro G1049, the Naga G1153, Akari G1154 (Ronin Ch4
      done). Skipped: the Phoenix Inquisitors and Benjiro's father (their side stories aren't built). Then Gendo's
      footnote, the mask, "Starving.", G1197, save.
    - **Codas** (CODA, CODA_GO, CODA_SPOTS, with_coda wraps the existing builders in MAPS, so no builder changed):
      a one-time autorun scene on each map, after G1197 and the previous coda's flag; props show only while that
      coda is current. Plugin `fLead(pid)` (RokuganField): that traveler leads alone, the rest wait in G1160.
      | Flag | Traveler | Map | Flags read |
      |---|---|---|---|
      | G1198 | Natsuko + Kage (+ Squeak, Stich'Kik) | M140 Hida road (27,15) | G285, G051 |
      | G1199 | Rensei; Masanori in the dojo door | M200 (31,16) | G431 |
      | G1200 | Gendo | M454 Gendo's office (new interior 18x7) | G819, G949, G814 |
      | G1201 | Shizue + Hiruto | M242 (30,12) | G569 |
      | G1202 | Haruki + Mieko | M281 inner garden (17,10) | G697==1 |
      | G1203 | Tamotsu; a daimyo by Persimmon | M413 (17,14) | G1030 |
      | G1204 | Sayo at the long table with the seven | M455 road inn (new interior 22x7) | G1142, G1114 |
      | G1205 | Mitsue, alone | M382 the Togashi road (30,15) | G947, G859 |
      The glade's exit scene (G1208, after G1197) starts the chain, so a reload of F11's save still goes on.
    - **E02** M456 "Otosan Uchi - the river at night (1123)" (new map, night RSET, music night): lanterns on the
      river, Bayushi Shoju (the masked figure in red) on a watchtower roof, the drum, the two title cards, THE END.
      Then fLead P100 + fJoinAll (the eight back, Party A/B), G1207 cleared, to the shrine M445.
    - **Post-game** (M445 scene G1209, after G1207 + G1206): resets G1190/G1191/G1195 (the debate and battle replay
      from the Shinomen) and offers the clear save. F08_OPEN now resets G1192-G1209 first, so a replay plays F09-E02
      again with other flags. The Shadowlands/Hiruma Castle Lv 61-80 regions aren't built (a SYSTEM line says so).
    - interior() gained layout entries with a 5th value y (things on a tatami: 2) and npc kind "prop" (arg = d).
      For props, d=2 faced the camera inside the inn and d=0 faced away.
    - **Balance:** phase 1 lost once in a full run (Party A has no healer). E583 attack 0.85 -> 0.75; then 3/3 won
      (9, 14 and 9 rounds; the 14-round run ended with only Shizue standing).
    - **Tests:** runevent M453 #3 (F09 -> F11, all montage flags, 0 errors); runevent M453 #5 (the glade exit ->
      eight codas -> E02 -> the shrine save, 0 errors). Snaps of every coda spot (rooms enlarged after the user's
      note: rooms can be bigger, not to scale).
  - **Finale leftovers, done (2026-11-05):**
    - **Wave 5 escort** (plugin RokuganHazard ::Rokugan.esc, after the finale block): while G1210 is set (WAVE[5]
      sets it around the battle), each raider's action has a 40% chance to go for the abbot instead (spent; he loses
      12-16 of 100, pop "goes for the abbot! (abbot n/100)"). Jinnai's Freezing the Lifeblood spends the first
      raider's first action. At 0: "THE ABBOT FALLS", G1211 -> he's carried inside, no gift; saved -> Ginseng Tonic
      x3 (I131). Tested (Lv 55): Party A 4 rounds, abbot 6-22 at 45%/13-17, so eased; Party B 4 rounds, abbot 33-72.
      Note: this Squirrel has no float.tointeger(): use int(x).
    - **Kage as a guest**: guest #17 (GUESTS, plugin GUEST_SKILLS "S633"), flag G1212, joins in wave 4 when the flare
      brought him (replaces the current guest, Jinnai). S633 "Hiruma Kage: Father's Tanto" (Tanto + Jade, one enemy,
      2.2-2.4, 2 uses). Tested with -rtguest on wave 7: ~950 a hit, uses count down, jade breaks shields.
    - **Inns rest Party B**: gen_data appends one cmd_script ("RT reserve rest", added once) to the shared inn macro
      X014: heals fReserve() (empty outside the finale). Ran clean via the Hoshi-no-Ichi innkeeper (runevent can't
      start a hotel-role event: "page" missing).
    - **FINALE_GATES snaps** (_art/preview/finale_gates.png): all eight on walkable ground. Bug fixed: the two indoor
      letters (M229 Crane, M344 Dragon) were placed in room coordinates after the room was embedded; make() now adds
      ROOM_OFS. The Crane letter runs.
    - **SS-TEAM "The Inquisitors' Last Hunt"** (sidestories/guests-07-12.md, read in full): M101 garrison yard
      (40,25), Michio with a "?" badge (SS_ICON += michio, EP1170) and Takeo/Mai/Fujio/Sakura as props, after Crab Ch4
      (G286) with the four Kyuden Hida SS1s done (G233-G236). Michio (P124) and Goro (P123) join at Lv 46 for
      b_ss_team_nest (gid 170, cave backdrop M813: E587 Nest Goblin x2, E588 Nest Onikage, E589 Nest Oni Spawn,
      relevels at Lv 46-47). Win: G1213 inquisitors_hunt_done, Jade Pouch x3. Tested: 5 rounds, 39-100% HP; the
      scene runs, 0 errors.
    - **Benjiro SS2 "The Moto Curse"** (guests-19-23.md #22, read in full). Moved: the source says beyond the Wall
      after Crab Ch3, but Benjiro is a Lion Ch2 guest (G507), so he waits on the Plains of Thunder road (M444 68,16,
      badge EP1171) after the join-up (G1162). He answers the Guest call (G232=10) for b_ss_benjiro_father (gid 171,
      backdrop M897): E590 Moto Akutsukai, his father (Lv 55, HPx 20, Res 14, weak Jade/Fire/Yari, two actions,
      the existing Moto Akutsukai mini-boss art EP122 + banner). Win: G1214 benjiro_father_home; the plugin's
      guestSkill gives guest 10 S634 (Death Trance, 3 uses) from then on. Tested: 5-6 rounds, 40-80% HP left (HP
      24k; the four hit all three weaknesses, so he breaks fast); 3 uses confirmed; the scene runs, 0 errors.
    - Both side stories now have their flight shots (F10): "Moto Benjiro, face unpainted, at the head of the Crab",
      "Isawa Michio's Inquisitors - all six of them - blocking a path".
    - **Phase 3 exploits are commands now** (production F09 "commands appear when available"): skills S635 "Empress"
      Bait (Rensei, G427), S636 Two Voices (anyone, G1185, a second traveler standing), S637 Smooth Stone Decoy
      (Sayo), S638 The Immovable Hand of Peace (Tamotsu Lv 61+): once a battle each (rt_uses 1, shared), listed
      under Call only against the true form (plugin RokuganHazard exploitsFor -> RokuganBattle callables). The
      effect runs in onPreCommand (rt_exploit); the old fixed-round barks are gone (trueRound only sets Resolve).
      The Disfiguring Strike stays automatic (a crit). The auto battle uses them as soon as they're there. F09's
      phase 3 line now says "look under Call". Tested Lv 61 (Rensei, Sayo, Tamotsu, Gendo; 8 shields, G427,
      G1185): all four fire with their barks, Bait -> SUKI. Several travelers queuing the same exploit in one round:
      one counts, the rest become attacks ("NO USES LEFT"), as with guests.
    - **Still not built:** the post-game regions (plan below). (CH4_DONE["P105"] = G953 is box_destroyed;
      it works as "Scorpion Ch4 done" because S08 always throws the box into the fire.)
- **NEXT: the post-game (plan, 2026-11-05; nothing built yet).** Session stopped at the user's 90% meter; the user
  resumes 2026-11-05 11:20 CST. Resume step: read the "Not yet read" sources below in full, then build P1.
  What the docs fix (read):
  - finale.md "Post-game unlocks": Rank 5 content (Lv 61+); the Orochi superboss (Crane coast; Crane Ch3 sighting);
    the Hiruma Castle side story (the canon Hare sword); Mirumoto Hikaru's Endless Strike for Gendo (kata.md: a
    "taste" of Mirumoto 5, from Hikaru's Kata Scroll, equipment.md); Purity of Shinsei for Haruki (kiho.md: Fire 5
    after Lv 61; field light in dark dungeons, battle vs Tainted/Gaki).
  - storyboards/finale.md F-4: the clear save at the shrine (built); the Shadowlands reopen through the Wall gate
    (Crab Ch3's skill-locked chests reachable); the Shinomen stays open.
  - bestiary.md row "Post-game: Shadowlands deep / Hiruma Castle" Lv 61-80: all IV/V archetypes with a "Fallen"
    palette (+30% stats), uncommon Troll Elder, rare Orochi-spawn (V). DESIGN.md: Rank 5 = 61+ (cap 99).
  - 01-world-and-timeline.md: 1123, the Hare sword is found in Shiro Hiruma (Crab tie); crab-ch3 script: the Map of
    the Road Home key item points to Hiruma Castle.
  Not yet read (read in full first, rule depth-over-speed): kata.md Gendo section, kiho.md Purity of Shinsei,
  equipment.md T5 + post-game rows, crane-ch3 production (the Orochi sighting), any Hiruma Castle / Hare canon in
  research/ (grep "Hare", "Shiro Hiruma").
  Proposed slices:
  - **P1 the gate back:** after G1207, the Wall gate (M101) opens to a deep Shadowlands road (new maps, Lv 61-68,
    "Fallen" palette relevels of the IV/V foes, Troll Elder uncommon); Crab Ch3's locked chests become reachable.
  - **P2 Hiruma Castle** (Lv 68-75): the Map of the Road Home leads there; dungeon floors; the Hare sword as the
    reward; a boss (needs wiki art).
  - **P3 the Orochi** (Crane coast, superboss Lv 80; wiki art; Water-weak to Air/Yari per the Orochi-spawn row).
  - **P4 the teachers:** Hikaru teaches Gendo Endless Strike; Haruki's Purity of Shinsei at Lv 61 (Fire 5).
  Free ids to check before starting: maps from M457, backdrops M808-M809/M819, art EP196-EP199/EP209+, flags from
  G1215, skills from S639, enemies from E591, groups from 172.
- **Post-game P1 "the gate back" (2026-11-05): BUILT, tested.**
  - Changed from the plan: NOT Crab Ch3's maps. Reopening M101/M170-M177 would replay Natsuko's Ch3 scenes in any
    save that didn't walk the Crab path (their flags are unset), and Crab Ch3's "skill-locked" root (M172) has no
    lock in the code. So the post-game road is its own maps:
    | Map | What |
    |---|---|
    | M445 shrine | a Crab rider at the east gate (92,15) after the clear (G1207): "Ride south to the Wall" -> M457 |
    | M457 Kaiu Wall - the Shinomen gate | the hub: the T5 smith (R170 stock), a waystone, two NPCs; the open gate (55,28) -> M458; west edge -> back to M445 |
    | M458 the Fallen road | Lv 61; Taint tiles TARSTAIN; Jade Pouch x2, Ginseng Tonic x3 |
    | M459 the bone fields | Lv 63; EMBER; 3,000 zeni, Kansen Mist x2; a bone-field marker |
    | M460 the Hiruma road | Lv 65; POPPYF; waystone (96,12); the east end: Hiruma Castle on a hill, "on Father's map" (P2 placeholder) |
    Edges are touch talks with go() (no landing on a trigger). gen_maps `deep_road()` builds the three.
  - Foes (gen_data, bestiary F post-game row): the Fallen relevels E591 Goblin 62, E592 Ogre 64, E593 Onikage 63,
    E594 Akutsukai 65, E595 Kansen 63, E596 Oni Spawn 66 (EP208), E597 Bloodspeaker 64, AREA (1.7, avg, 1.4)
    (Oni Spawn atk 2.0, 1-2 actions); E598 Troll Elder (EP113, Lv 66, HPx 6, atkx 1.9, 2 actions, uncommon); E599
    Orochi-spawn (EP441 the sea-serpent sprite, Lv 67, HPx 5, atkx 1.9, 2 actions, rare). Backdrop M817.
    Also fixed: E589 Nest Oni Spawn showed the Kommei boss art (EP123): now EP208.
  - Balance (balance_encounters, Party A in the arrival kits, Lv 61/63/65): every group 1-6 rounds, all "ok" but
    Kansen pairs (1-2 rounds, easy); the troll and orochi still gentle (lowest 53-96%). First pass was far too easy
    (0.85 HP / 1.15 atk).
  - Snaps: _art/preview/postgame_p1.png. The shrine marker -> M457 runs, 0 errors.
  - (M459 recoloured 2026-11-05: user said the all-ash bone fields looked like snow; now SL_GROUND + ash drifts.)
  - **P2 was planned here** (Lv 68-75). Read first, in full: research/ grep "Hare", "Shiro Hiruma"; crab-ch1
    production line 384 (the Map of the Road Home); crab-ch3 script line 82; 01-world-and-timeline.md 1123; bosses.md
    for a castle boss; wiki art candidates for the boss. Free ids: maps M461+, backdrops M808-M809/M819, flags G1215+,
    skills S639+, enemies E600+, groups 172+, art EP196-EP199/EP209+.
- **Post-game P2 "Shiro Hiruma" (2026-11-05): BUILT, tested.**
  Sources read: 00-synthesis.md (the Hare sword in Shiro Hiruma), 01-world-and-timeline.md 1123, 02-travelers.md
  (Natsuko's father's map), crab-ch1 TB "The Map", mirror-mirror.md (Hiruma lost the castle 15 generations ago),
  bosses.md (no post-game boss there), the CCG card Oni no Okura (flavour: Akuma's daughter, the Jade Champion's name).
  - M460 east end: Shiro Hiruma sighted (G1215) -> M461 the outer bailey (BAILEY: the map, "It leads here", G1216; Lv
    69 encounters; 5,000 zeni, Jade Pouch x3) -> M462 the keep (the Hiruma tablets set up, G1219; waystone; Lv 72) ->
    M463 the lord's hall: OKURA scene G1217, b_boss_okura gid 172 on M808 (new backdrop), win -> W157 The Hare Sword
    (katana ATK 176, Crit +15, no price) and the last line of the map; G1218. Loss: talk to the throne to retry.
  - Boss: E606 Oni no Okura (Lv 75, HPx 16, Res 22, weak Jade/Crystal/Tetsubo/Fire, two actions; S639 Akuma's Rage
    all+Fear, S640 The Stolen Name heavy, S641 The Castle Remembers all+Taint). Art: gen_bossart "okura" EP196 /
    banner EP197 "Akuma's Daughter" from cand/Oni_no_Okura-card.jpg (crop 165,95-375,310, hand POLY); BOSS_BANNER
    entry. Tested Lv 75 (four, arrival kits): won in 9-11 rounds, two travelers ~25%.
  - Foes: E600 Restless Hiruma 69, E601 Fallen Ogre 70, E602 Fallen Akutsukai 71, E603 Fallen Bloodspeaker 72, E604
    Fallen Oni Spawn 72 (EP208), E605 Troll Elder 72. Balance (Lv 69/72): all ok, lowest 6-88%, total 68-96%.
  - Scenes run in-engine, 0 errors (bailey; the boss scene through the Hare Sword). Snaps _art/preview/postgame_p2.png,
    battle_backdrops.png (gid 172).
  - **Next: P3 the Orochi** (Crane coast superboss, Lv 80) and **P4 the teachers** (Hikaru's Endless Strike for
    Gendo, Purity of Shinsei for Haruki). Read first: crane-ch3 production (the Orochi sighting) and its maps; kata.md
    Gendo; kiho.md Purity of Shinsei; equipment.md Hikaru's Kata Scroll. Free ids: maps M464+, backdrops M809/M819,
    flags G1220+, skills S642+, enemies E607+, groups 173+, art EP198-EP199/EP209+.
- **Post-game P3 "the Orochi" + high-level healer spells (2026-11-05): BUILT, tested.**
  Sources read: crane-ch3 production S05 / storyboard / script (the sighting), research/the-edge-of-treachery.md ("a
  hidden superboss"), the L5R wiki "Orochi" (via the fandom API: sea serpents of Sakkaku, green scales, golden eyes,
  intelligent, humourless; they keep the ships they sink and the souls aboard; guardians of the ningyo). Art
  candidates downloaded to _sources/wiki_art/cand_postgame (Orochi, Orochi-card, Orochi_2-4).
  - Canon fix: E599 Orochi-spawn's desc no longer says "eight-headed" (that's the Japanese Orochi, not L5R's).
  - M445: a Crane ship's master + the sailor (88,13), after G1207 -> M464 "The Orochi's water" (a deck in the storm;
    OROCHI scene G1220; a calm-water talk to retry; sail home). b_superboss_orochi gid 173 on M809 (new backdrop: the
    deck on the party's side, open water on its side). E607 The Orochi: Lv 80, HPx 30, Res 30, weak Air/Yari/Tetsubo,
    Water resist 50, two actions, S642 Tidal Lash (Water all), S643 Coil (heavy), S644 The Drowned Crews (all+Fear),
    atkx 1.3; rt_surrender 10 (it yields; its own kill flag G1222, not Crane Ch1's G336). Win: A139 Orochi Scale +
    20,000 zeni, G1221. Art EP198 / banner EP199 "Keeper of the Drowned Ships" (gen_bossart "orochi", line art
    Orochi_4.jpg, green ramp).
  - **User: the Orochi may require Lv 95+** ("Recommended level 95+"). Tested Lv 95 (Natsuko, Haruki, Gendo,
    Shizue; arrival kits; auto): 3/3 won, 9-11 rounds (Haruki 5% once). At Lv 80 with the same: 0/3 even at atkx 1.1.
  - **User: high-level healer spells** (haruki-spells.md new "Rank 5" tables at the END of section 3, so no spell id
    shifted; curve rows Lv 70 / 75): S392 Mass Path to Inner Peace (Water 5, all allies, no VP needed), S393 Rain of
    Regrowth (Water 6, all allies, Regen), S394 Return the Soul (Water 6, revive one ally at 50%: built on the engine's
    Raise S043), S395 Stillness of the Void (Void 4, 2 VP, all allies immune to Terror 4 turns + cures it). Haruki
    learns them at 70 / 75 (lvoption).
  - **Bugs fixed:**
    - Courage of the Seven Thunders did nothing ("immune" matched no condition): now puts K058 "Courage" (new cond,
      4 turns; the plugin's Terror check honours it) and cures Terror.
    - Regen (K040, bit 40) as a putconds bitmask decoded wrongly: the user saw Rain of Regrowth "spam status effects on
      the party till it crashed"; the old single Regrow the Wound had the same bitmask. spell_skills now puts any
      condition above bit 30 by id (opt_putcond). K040 MAXLV 1 (no stacking).
  - Auto battle (RokuganAI): revive a fallen ally first (a heal that cures Down); a party heal when two or more are
    under half (an instant one before Rain of Regrowth); Stillness of the Void when someone is Terrified and nobody is
    warded; the revive is never used as a plain heal.
  - Snaps: battle_backdrops.png (gid 173), snap_M464.png. Shrine -> M464 -> scene runs, 0 errors.
  - **Next: P4 the teachers** (Hikaru's Endless Strike for Gendo: kata.md says "a taste" of Mirumoto 5, from Hikaru's
    Kata Scroll (equipment.md, Ronin Ch3); Purity of Shinsei for Haruki at Fire 5 (kiho.md, Lv 61+)). Free ids: flags
    G1223+, skills S645+ (S392-S395 are the new spells), maps M465+.
- **How the user plays (2026-11-05).** The user has no saves; they've been waiting for an alpha-complete game. Made:
  `Play Rokugan Traveler.bat` (project root: `rpgcobo.exe -testplay`, no test flags -> the real title screen: New
  Game -> the M099 prologue picks the traveler), a desktop shortcut "Rokugan Traveler", and `HOW TO PLAY.txt`
  (roads, finale, post-game, controls, saving, alpha limits). Verified: the launcher starts the game; title screen
  captured (_art/preview/title.png). Not done: a packaged export (RPG-Cobo exports Windows/Web builds from the
  editor's UI only).
- **Choice menus clipped (user screenshot, 2026-11-05).** The stock dialog_choices box showed ~34 characters; 133 of the
  536 choice labels in the game were longer (up to 109). Fix: gen_maps `choices()` now passes `pos` {left, right,
  y: 380} so RPGMain.showView stretches the box (stretchSize) to the longest label: width = 11 px/char + 70, clamped
  420-1200 (screen 1280; `${...}` templates counted as 24 chars). The prologue labels are now "Name (Clan)" with the
  one-line descriptions in two narration boxes before the choice. All maps rebuilt; checked the prologue and the
  debate's first choice (snap_M099, snap_M453, choices_check.png).
- **Name-collision bug (user stuck on the Wall, 2026-11-05).** gen_maps builders read module names when the map is
  BUILT, after the whole module has loaded, so a later chapter's `S01 = ...` (Crab Ch2, Kisada's court) replaced
  Crab Ch1's opening on the watchtower (the user saw the court dialogue on the Wall, then couldn't move). An AST scan
  found 10 such late-binding collisions; renamed the earlier definitions and their uses: S01_CRAB1, S05_IN_CRAB2,
  S06_IN_CRAB2, FLARE_CRAB3 (Crab Ch4's flare scene), S04_IN_CRANE1, DAWN_CRANE1, S08_AFTER_CRANE1, HOME_LION3,
  GATE_UNI3. Duplicate function names (barracks, battle_cove, ...) are all registered right after their own def:
  fine. All maps rebuilt. **Rule: new scene constants need a chapter suffix** (or re-run the AST check: a
  module-level name assigned twice and read inside a function).
- **Japanese leftovers + stuck-in-room pass (user, 2026-11-05).**
  - Japanese: 217 template records still had Japanese; only 16 are used. gen_data `english_leftovers()` (runs last)
    translates type.json's menu labels (eqslot Weapon/Shield/Head/Body/Accessory, eqtype, dmgform, resistg, tribe,
    jobslot ...) and the used descriptions (A141, I000/I001/I004/I010/I011/I016, J000, J105, K005, S003, S190 name),
    and drops the template Wooden Shield (A000) from every traveler's starting kit. **Gotcha:** gen_data `load()`
    returns the untouched TEMPLATE file; a late pass must read the generated file (english_leftovers has its own
    load). A first try saved templates over player/item/skill/... (regenerated, fixed).
  - Stuck room: M111 the garrison barracks had the hearth in the doorway (user trapped). Rebuilt 22x8, hearth at the
    back. Guards: interior() nudges any furniture out of the door lane; castle_floor() keeps the down/up stair cells
    and the step in front clear (candles stood on the down-stair in M290, M308, M316, M381, M388; a barrel on M145's
    up-stair). M455 inn-table prop moved off the door.
  - New tool `tools/walkcheck.py`: rebuilds each map in memory (no engine) and flood-fills the standable cells from
    the portals, touch triggers and every go() arrival; reports exits/NPCs/chests/triggers out of reach (2-cell reach
    for hit boxes; hearth 4x3 footprint). First full run: 20 maps flagged -> fixed: M147 women's shrine (a pit between
    the stair top and the shrine: landing raised), M151 two NPCs inside the dojo / tea house, M202 the tax-ledger
    examine spot inside the headman's house (Crane Ch1 key item; moved to the wall), M390 and M396 chests inside the
    stone, M290 hospital (candle on the stair). Left: M215 Miyako on the ridge (scenery, on purpose).
  - walkcheck re-run after the fixes: 2 maps left, both expected: M215 (Miyako, scenery on the ridge) and M147 (a
    false positive: the torii's crossbeam over the shrine stairs reads as the floor; the checker takes each column's
    HIGHEST standing surface, so walk-under beams/arches show as walls).
- **Desks too big (user screenshot, M110 Tomoe's office).** The counter/desk model is wider than its 2 cells and
  swallowed the arriving player; Tomoe stood behind a candle. M110 rebuilt 16x8 (desk back at (8,5), Tomoe behind it
  at (9,7), arrival (8,2); Crab S01's dawn mapmove updated to the new embed offset 7,10). A scan of every interior for
  people on or just in front of big furniture: shopkeepers beside counters (fine, as designed), Gendo's office (desk
  behind him, intended), and M165 the Kyuden Hida tea house (host inside the table): rebuilt 17x8, host on a mat in
  front of the tables. Not snapped in-engine (the user was playing).
- **Block-built furniture (user: "rebuild it all", "make what makes sense visually", 2026-11-05).** The engine's
  library furniture (FreeBlock fbtype 4 / the hearth fbtype 2 param 7) is placed by native code with position and
  rotation only (RokuganMapGen placeFreeBlock: no scale) and was oversized next to the cast. gen_maps FURNITURE +
  furnish(): table / lowchest / bench knee-high 2x1, counter 2x1 waist-high with a dark top, highchest 1x1 tall,
  shelf 2x1 1.5 m, box / box2, ricebag (straw), and the hearth as an irori (a 2x2 stone square in the floor with a
  small flame). Used by interior() and castle_floor() for every room; small library pieces (barrel, pot, candle,
  sword/shield racks, books, dishes, bucket, jewel) stay. Every piece adds invisible-wall cells (m.walls); embed()
  now shifts m.walls with the room (it didn't). walkcheck honours m.walls.
  - walkcheck after the furniture rebuild: still only the 2 expected flags (M147 torii beam, M215 Miyako).
- **Our own props instead of library stand-ins (user: "candle holders with candles on the river, instead of paper
  lanterns... make them yourself", 2026-11-05).** gen_props: EP358 "Floating lantern" (toro nagashi: a glowing paper
  box in a dark frame with an ink stroke, on a little float, a broken orange reflection; 4 frames, bob + glow) and
  EP359 "Star" (a four-pointed twinkle, 4 frames). M456 the capital's river: 26 EP358 props (were 46 candle stands).
  M321 Outside time (Dragon Ch2 ink limbo): EP359 stars at varied heights (were candle stands). M807 the finale's
  battle starfield (no events on battle maps): 90 pale PLASTER specks (were candle stands). Remaining LAMP_CANDLE
  uses are real candles (caves, shrines, studies). Not yet seen in-engine (the user was playing).
- **Our own decorations (user: "you just really need to go make the furniture and decorations", 2026-11-05).**
  gen_props DECOR (EP210-EP220, pixel art at the cast's scale, preview _art/preview/decor.png / decor_zoom.png):
  EP210 katana rack (kake, katana + wakizashi), EP211 armour stand (yoroi: kabuto, laced do, sode), EP212 sake
  barrel (straw-wrapped taru, label), EP213 storage jar (tsubo), EP214 bucket (oke), EP215 writing set (scroll,
  inkstone, brush), EP216 bound books, EP217 meal tray (zen: rice, miso, chopsticks), EP218 sake flask (tokkuri +
  cup), EP219 lacquer box (maki-e, red cord), EP220 andon (paper floor lamp, 4 frames, + a warm light event).
  gen_maps: DECOR_EP + place_decor() (props appended AFTER a room's own events: castle floors have fixed ids like
  #3#); interior() and castle_floor() send these kinds there (candles became andon). library_to_ours() in make()
  converts any library piece left on a field map (outdoor pots, buckets, barrels, the driftwood armour stand, jade
  carts...) into block furniture or our props; battle maps get a small wooden block (no events there). Now no
  fbtype-4 library furniture is placed anywhere except jade glints in battle backdrops. walkcheck: still clean
  (M456's river lanterns are flagged, as expected). Not yet seen in-engine.
- **Moving between maps + followers (user, 2026-11-05).**
  - "Cannot freely move from screen to screen" (the garrison's only east exit was one unmarked cell behind trees):
    gen_maps mark_exits() in make() for every field map: each edge exit (portal, or a touch trigger that map-moves)
    gets a trigger ~10 blocks wide along its edge (mdl r half-extent 2.5 m) and a stone lantern on each side of the
    opening. walkcheck still clean.
  - "Followers should start following you on screen as soon as you recruit em": plugin RokuganField partyFollow()
    (updateStageBody hook): every party member after the leader is a plugin-made sprite (::conf.player[id].mdlid)
    walking the leader's trail 1.1 m apart; rebuilt when the party signature changes or a map loads; no body.
    UNTESTED in-engine at the time of writing (the user was playing): run any -map test and look for "[RT] party
    followers" and exceptions.
  - "Cart as well": M101's cart + driver are parked until S02 (G011) and then follow (ESCORT), as on the Coast Road.
  - The user saw "exit left -> far right of the 2nd screen" on the escort: the links are geographically consistent
    (M102 west -> M101's east exit, M101 east -> M102 west); asked the user which exit they meant.
- **Edge exits, final design + tested (2026-11-05, supersedes the mark_exits notes above).**
  - Engine facts (src/rpg/RPGObjects.sk getPortalPos, RPG3DObject RPG3DGhost): a portal's trigger box is
    mdl.r = [x, y, z, half-x, half-y, half-z] in metres, in the event's LOCAL frame, which turns with its d. The
    trigger is touch-based (any walking direction). Arriving at a portal puts you 1 m from it along d.
  - Old bug (everywhere outdoors): edge portals had d pointing OFF the map (west edge d=1, east d=3), so arrivals
    landed at the edge and walking in crossed the exit again (the user's "wrong side" / bounce on the cart escort).
  - mark_exits() now, for every edge exit on a field map: d points inward (w->3, e->1, f->2, b->0), r[3]=2.5 (5 m
    wide along the edge, whatever d is), r[5]=0.5 (1 m deep: the arrival is 0.5 m clear), stone lanterns 6 blocks
    either side (outside the opening). Tested in-engine: garrison -> Coast Road (arrive inside, no bounce) -> walk the
    whole road -> Hoshi-no-Ichi; walking back west from the arrival spot does not bounce.
  - Note: maps are padded (PAD_X 26) AFTER mark_exits, so a "map edge" exit is the builder's edge, with 26 blocks of
    open padding beyond it (the user saw that as a blank edge: worth a visual edge treatment some day).
- **Party followers tested (2026-11-05):** garrison with Goro + Michio: they trail Natsuko in a line (snap pf2.png),
  no exceptions. Bug fixed on the way: this Squirrel has no array.remove() (trail trims use slice()); the old
  RTFollowAction trail had the same call at 80 points (would have thrown on a long cart escort).
- walkcheck after everything: 3 known flags only (M147 torii false positive, M215 Miyako scenery, M456 river lanterns).

## START HERE after Saturday (written 2026-11-05)
The user is PLAYING the alpha now (desktop shortcut / "Play Rokugan Traveler.bat"; HOW TO PLAY.txt). Work comes from
their screenshots and bug reports. Rules learned this week (also in memory):
- Ask before any engine test while they might be playing (the test tools taskkill rpgcobo.exe).
- Rooms can be bigger; build furniture/decor ourselves (no engine library pieces); make what makes sense visually.
- New scene constants need a chapter suffix (late-binding name collisions: an AST check is in the notes above).
- gen_data load() returns the TEMPLATE; late passes must read the generated file.
Open items, roughly in priority order:
1. Verify by eye (screenshots): the new block furniture + DECOR props in a sample of rooms (armoury M112, Tomoe's
   office M110, an inn, a shop, the Kyuden Hida tea house M165), the river lanterns (M456), the exit lanterns. Tune
   sizes/colours of the DECOR sprites if they look off in 3D.
2. The user's "exit left -> far right" report: probably the bounce bug (fixed). Confirm with them.
3. A visual treatment for map edges (the padding beyond an exit looks like a blank wall of ground).
4. Crab Ch2: a fade-in image of Kisada's court when it really plays (the user suggested it for the opening).
5. Post-game P4 (the teachers): Hikaru's Endless Strike for Gendo, Purity of Shinsei for Haruki (see "NEXT").
6. Maybe: our own voxel furniture models (nicer than block furniture), a packaged Windows export (editor UI only).
- **Whole-edge transitions, barricades, encounter rate (user, 2026-11-07).**
  - User rule (memory map-edges-transition): the whole last edge of a map that connects to another map is the
    transition, both ways; closed roads = barrels/crates + a samurai ("The road's closed for now"); when the road
    opens the map reloads without them; and "don't try to be too clever: lots of JRPGs to draw on".
  - gen_maps mark_exits() (pre-pad): finds edge exits (portal / touch trigger with a map move, within 2 cells of the
    builder edge), points portal d inward, and for an exit closed by a one-flag condition (portal reqs0, or the
    map-moving page's reqs) builds a barricade two cells in (EP212 barrels + EP221 crate stacks, memo "barricade") and
    a townguard samurai, shown with the inverted condition. Exits at the same spot (alternatives by flag, e.g. Hida
    road east: winter town / summer town) are one doorway: same stretch, no barricade.
  - edge_triggers() (post-pad, make()): each exit's trigger moves to the real (padded) edge and spans its stretch (the
    whole edge, or to the midpoint with the next doorway on that edge), 6 m tall; a portal's own event stays as the
    landing spot (role custom, no trigger; other maps arrive at it by event id) and a copy at the edge does the moving.
  - Plugin RokuganField barricadeCheck(): records the flags behind the map's barricades on load; if one changes while
    the player is there, reloads the map in place (RPGMain.moveMap remap) once any scene has finished.
  - 56 maps got barricades (listed with the flags in the session; examples M101 Hida road until G054, M200 the
    academy gate until G301). walkcheck skips memo "barricade" props.
  - Reciprocity check: 23 edge exits, 11 one-way, all doors/gates/rides on the other side (cave mouths, the Wall gate,
    the Shinomen gate, signposts) except M460 -> M461, fixed (its trigger moved onto the edge).
  - Random encounters: the template's encntrate 1.0 = one fight per ~100 m (the user walked the whole Coast Road
    escort without one). gen_maps ENC_RATE = 4.0 for every encounter map (~ a fight per 25 m). Wild maps without an
    encounter table are story/scene maps; the storyboards give no encounters there.
  - NOT yet tested in-engine: the edge triggers, the landing spots, a barricade + reload, the new rate.
- **The shifting waste: a Shadowlands lost-woods maze (user, 2026-11-07: "shadowlands by lore seems to move around").**
  Post-game deep road only (Crab Ch3's Shadowlands carry story scenes; asked nothing there). gen_maps MAZE / MAZE_SEQ /
  maze_move() / shifting_waste(): M458 the Fallen road is the start (west -> the Wall gate M457; a Hiruma waymarker at
  (14,13) carries the chant "East. West. North. South. West, west, east. Never twice south."), east -> six 72x48 maze
  maps open on all four edges (MAZE = M459 (was the bone fields), M465-M469; random ash, Taint patches, rocks, a
  stone landmark per map; deep-Shadowlands encounters; Taint tiles). Right edge -> next map; wrong edge -> one map
  back ("The ground shifts underfoot... This place again."); south twice in a row (flag G1223) -> back to M458
  ("The Shadowlands fold like paper."). The 7th right move (east) -> M460 the Hiruma road; M460's west edge leads
  back to M458 (out is easy). Transition table checked offline; NOT yet walked in-engine.

- **Battle jukebox + test-battle music fix (2026-11-07).** New `tools/battlejukebox.py [gid ...] [--secs 90]`: waits
  for the game to close, then plays one battle per battle theme at normal speed (sound, -rtauto), up to 90 s each;
  closing a window skips. Found on the way: `-battle` test launches were silent ("[RT] BGM null"): testplay.sk never
  set sstat.statmap.bgmid (moveMap does in play). Fixed there (group bgmid, else the map's). In-game battles were
  never affected.
  - `-rttank` test flag (RokuganField, wraps Rokugan.onAttack): before every hit on a party member HP goes back to
    MAXHP and the hit is capped at MAXHP-1, so nobody falls. (Setting HP above MAXHP is clamped on the next hit;
    assigning MAXHP broke the refill.) battlejukebox always passes it; `--secs 0` = play until the window is closed.
- **Orochi theme MU122 re-voiced (user, 2026-11-07: "the two layers of music do not match well").** The "heads"
  figure was in semitones over each chord root, so over C / B / F# / G it played Eb, Ab, D, C# against the E
  hirajoshi lead; the guitar/bass power chords and the section-B choir/strings put C# / D fifths on F# and G. Now the
  heads move by scale steps (over E unchanged), F# and G take a 4th instead of a 5th (power(), bass_bar fifth=),
  and the riff is 0.7x (it was 37% of the mix over a 15% lead; now 23 / 19). A note census confirmed every
  pitched note is in E F# G B C.
- **IN PROGRESS: key-fit pass on every track except the Orochi (user, 2026-11-07: Orochi fix "perfect", "do what you
  can to all the other tracks like this, same method"; "the orochi was perfect... i wanted the other ones fixed").**
  - Method: no layer may play a note outside the track's key against an in-key note a semitone away. (Plain
    semitone rubs between in-key notes are the scale's colour: hirajoshi / in have them; the Orochi still scores
    ~180 s of those and is "perfect", so do NOT chase the total.)
  - New `tools/music_census.py [key ...] [--all]`: renders tracks, lists out-of-key notes per stem, stem shares,
    and FOREIGN clash seconds (semitone pairs across stems with an out-of-key note; --all = every semitone pair).
    Before-fix full report: _art/preview/music_census.txt. After-fix run was started -> _art/preview/music_census2.txt
    (check it finished; rerun if empty).
  - gen_music.py changes (NOT yet rendered to .ogg; nothing in-game changed yet):
    - Track.sc / Track.root (None = old behaviour). Every t_/c_ track sets `tr.sc, tr.root = sc, root` EXCEPT
      t_orochi (left exactly as the user approved). final3 switches to RYO 62 for the travelers' sections
      (32-47, odd j in 48-55, 72-79) and back to IN 62 after.
    - Helpers: in_key / snap (nearest key note, step down first) / fifth (5th if in key else 4th) / key_step (riff
      semitone shapes -> scale steps over the chord root, then snap). riff(), arp(), chord_pad(), bass_bar() (all
      notes snapped; waltz/shuffle fifth via fifth()), gtr_bar() (root snapped; default power chord uses fifth()).
      Okura's direct choir hits use fifth().
    - Out-of-key chord roots replaced: battle F -> C (A A C G / C G Em A...), boss C -> G (E E G D...), mini-boss
      Bb -> G (D D G C...). Travelers / ending / victory keep G and A in TRAV_HR: snapping turns G B D into Bm/F#
      and A C# E into Asus4 (judge by ear; alternative is G -> E in TRAV_HR).
    - Bells retuned into key: boss kane 560 Hz (C#) -> D5 (KANE), shadow 310 Hz (Eb) -> E4, fall 240 Hz -> Bb3.
  - NEXT: read music_census2.txt; remaining suspects from the first census: shadow (pad Bb, biwa Bb/Eb), past (pad
    Ab), court (pad G, now snapped), night/intrigue arp (in-key semitones only?), duel. Then
    `python -E tools/gen_music.py <keys> --clips` for every changed track (NOT orochi), then play them with
    `tools/battlejukebox.py ... --secs 0` (battle themes; -rttank keeps the party alive) for the user. Field themes
    (town/road/court/...) need another way to listen (_art/preview/agents/music clips or a -map test).
- **Also this session:** testplay.sk `-battle` now sets the group's bgmid (test battles were silent); `-rttank`
  flag; tools/battlejukebox.py (see above). Orochi MU122 fix rendered and approved.
- **Key-fit pass DONE + rendered (2026-11-07).** After the fixes the census (_art/preview/music_census2.txt, then the
  direct sho / bass_koto / victory-chord fixes) shows 0 s FOREIGN clash on most tracks. Left on purpose: pitch-bend
  starts (battle/boss/final3 riffs bend up from a step below), final3's D ryo sections (the census measures it in
  one key), and the Shadowlands' Bb-over-A horror cluster ("Where the Kami Do Not Go", by design: ask the user
  if it should be calmer). New helper keyed(tr, ms); bass_koto(r +- n) calls are snapped. All tracks except the
  Orochi re-rendered (`gen_music.py <all keys but orochi> --clips`; log _art/preview/music_render.txt).
  NOT yet heard by the user: offer battlejukebox for the battle themes, clips in _art/preview/agents/music for the rest.
- **Sprites: the v4 set is now everywhere (user: "make sure the new sprites are implemented, and dump the old ones").**
  - Re-ran gen_human_enemies, gen_nezumi, gen_portraits (the sprite agent had left those on the old layout):
    64 registry entries moved to v4 (14x11).
  - Tinted copies are made by gen_monsters from their source entry: EP115 Drunken Samurai II still had the old 8x8
    animap over the new sheet; refreshed from EP408. ORDER: after gen_human_enemies, rerun the gen_monsters copy
    loop (or the whole gen_monsters) so EP114/115/118/170/171/175 match their sources.
  - Dumped: 3 orphan files (banner_iron_crane, banner_tengu_blue, boss_iron_crane .png, not in enemy_pic.json or
    any code) moved to the session scratchpad. Kept: the engine stock sprites EP000-EP059 (only template enemies
    on the unreachable template map M005 use them; gen_monsters derives the Goblin Warmonger from the stock
    goblin) and 347 registry entries that no data names (mostly side-cast ids that may be built at runtime).
- **Gonta rework (user: the Crab ronin camp "definitely needs the sprite re work, boss especially").** New build
  "sumai" in gen_sprites2d (side + front/back views): bare skin torso with a forward belly, thick bare arms and pillar
  legs, bare feet, draw_mawashi() (band under the belly, knot at the back, sagari cords at the front), +3 width,
  thicker neck, strong nose. Gonta: build sumai, chonmage (the mane hid his face), mawashi lower=(54,58,92),
  scale 1.45. gen_sidecast has `--only key1,key2` (partial runs skip the full preview sheet). Snapped in-engine:
  snapbattles 6 (the sumai bout, M812) and 4 (human mobs) look right. The two Hidden Ones (hidden1/2) were left as
  they are (generic ronin, already v4); ask the user if the camp's other sprites should change too.
- **Gonta v2 after the user's reference (a chibi sumo walk sheet: full black hair in a tall top-knot bun with a red
  tie, bare round body, dark mawashi; "can he be more like" this).** New hairstyle "sumotop" (side + front/back:
  full hair, bun on the crown, red cord from T["band"]); Gonta now sumotop, bangs short, band (196,44,40),
  stubble instead of a beard. Mawashi deeper (hy-1..hy+3) with a front/back panel between the legs; front-view
  legs thicker (4.4/3.8, 3.6/3.0). Written with `gen_sidecast.py --only gonta`, portraits rebuilt, snapbattles 6 ok.

## 2026-11-07: Dialog busts (painted portraits behind the dialog box, made with the user's ComfyUI)
- **What it does.** When a character with a bust speaks (cmd_showmsg key message_talk), a painted anime bust stands
  bottom-left behind the dialog box (like the user's reference, _art/reference/dialog_bust_reference.png). The chin is
  placed at y=380 (above the name tab) from per-image face data, the bottom runs off the screen edge. Same speaker on
  the next line: the image swaps (emotion) without a fade; another speaker / narration / end of the talk: it fades out
  (it lives in the "message" layer and goes when no message_talk box has been up for ~0.2 s). Map changes clear it.
- **Files.** plugin/rokugan/RokuganBust.sk (the plugin; loaded last in plugin.sk), RokuganBustData.sk (GENERATED by
  gen_busts.py: name -> key, emotions, looks, face positions, map looks), resource/bust/<key>/<emotion>.png and
  <look>_<emotion>.png (+ faces.json). No engine src change.
- **Emotion tag convention (for gen_maps.py and the other generators).** Start the line's text with a tag:
  `[angry] Get away from the cart!`. Emotions: neutral happy angry sad surprised worried determined hurt. A look can
  ride along: `[bath happy] ...`, `[travel]`, `[court]`, `[night]`, `[base]`. The tag is stripped before display (also
  for speakers without a bust). Alternatives: fields on the message command `"emo": "angry"`, `"bustvar": "bath"`; a
  scene-wide look from a cmd_script `::Rokugan.bustScene("bath")` (cleared on map change); whole maps in gen_busts.py
  MAP_SCENES (Winter Court floors M142-M146 and M229 -> court). Untagged lines are guessed from keywords and
  punctuation (::Rokugan.bustGuess: "ugh/argh" hurt, "?!" surprised, "damn/how dare" angry, "sorry/forgive" sad,
  "careful/afraid" worried, "thank/ha!" happy, "I will/we must" or a final "!" determined, a final "..." worried).
  Names: exact speaker label, else the label before " (" ("Shosuro Mitsue (thinking)" -> Mitsue).
- **Who gets what (user).** The 8 travelers: 8 emotions x 5 looks (base + travel, court, bath, night). Everyone else:
  ONE neutral bust (shown for any emotion). NPC order: by dialog line count, Crab path first.
- **Regenerate.** `python -E tools/gen_busts.py base <key> --seeds 1,2,3` (candidates + sheet in
  _art/preview/agents/busts/), pick one: copy it to _art/busts/<key>/approved_base.png and set seed/face/neck_y/crown_y in
  CHARS; then `all <key>` (travelers: emotions + looks + export) or `npc <key>` (one neutral). `data` rewrites only
  RokuganBustData.sk. ComfyUI must be running (127.0.0.1:8188; checkpoint waiIllustriousSDXL_v170; API workflows in
  tools/comfy/). Nothing was installed in ComfyUI.
- **Test.** `python -E tools/testbust.py ["Name|[tag] text" ...]`: -rtbustdemo shows one line with its bust on M101 and
  -rtshot saves it (_art/preview/agents/busts/ingame_*.png). It waits while rpgcobo.exe is running. -rtfast logs
  `[RT] BUST natsuko/angry.png` per line (runevent.py shows which bust each line picks). -rtnobust turns busts off.
- Work log: _art/preview/agents/busts/WORKLOG.md.
- **Sprite style pass toward the user's reference roster (sprite agent 2, 2026-11-07).** Log, previews, backups:
  `_art/preview/agents/sprites2/` (WORKLOG.md; backup/ has every replaced generator, sheet, portrait, json).
  - Adult proportions: gen_sprites2d `stature()` (STATURE 1.26 / BREADTH 1.08, per-build BUILD_STAT), longer limbs
    and weapons (WEAPON_SCALE 1.12), HEAD_SCALE 0.75 -> 0.64; registry scale x HUMAN_SCALE 0.92 so in-engine height
    stays the same (CAST_SCALE untouched).
  - Gonta: sculpted bare-skin shading (`sculpt()`), mass, white mawashi + sagari at the front under the belly,
    near arm outlined with a contact shadow, no arm cords (user: they read as cuts), face shown; scale 1.6.
  - Katana / nodachi / bokken / naginata edge fix (user: "held upside down"): forge_blade normal flipped, edge toward
    the opponent / down, curve back toward the spine.
  - Sashimono back banners (`sashimono=`) on 9 human-enemy soldier types + 7 side-cast guards; brighter spell release
    (core, halo, sparks, caster rim light); harder hurt recoil; portraits re-rendered from specs (no banner).
  - Regenerated: gen_sprites2d (all looks), gen_sidecast, gen_human_enemies, gen_monsters copy loop, gen_portraits.
    Registry: same 1330 ids; only `scale` changed on human entries.
  - Left: field maps not snapped (guards with banners, Gonta's camp); KO still kneels (reference lies flat).
  - Ask the user: Gonta's white mawashi OK? banners for archers / officers / ronin too? heads 0.64 small enough?

## START HERE tonight (after 6pm CST, written 2026-11-07 at the 90% stop)
Two agents were working; both were told to wrap up and log in their WORKLOG.md + NOTES.
1. **Dialog busts (ComfyUI, http://127.0.0.1:8188, the user's anime checkpoint).** Agent log + previews:
   _art/preview/agents/busts/ (WORKLOG.md, QUEUE.md + JSON manifest of everything queued). A huge ComfyUI queue was
   submitted for review later: unreviewed images are NOT wired into the game. Collect with the agent's collect
   script (see its NOTES entry), review contact sheets with the user.
   User decisions so far: Hiruma Natsuko base = **cand_28** (darker skin for sure); every emotion/scene builds on it;
   bath variant = less clothing, tasteful (they then said it made too many bath ones: keep 1-2). Busts must sit
   higher (face fully above the dialog box). Only the 8 travelers get emotion/scene sets; every non-playable
   speaker (companions, shopkeepers...) gets ONE bust. Redos asked for: the Natsuko yukata bust with the "big bald
   spot" forehead; Gendo's travel bust (a literal drinking straw in the "straw hat": never use the bare word
   "straw" in prompts); Squeak = a young Master Splinter-style rat, not a cartoon mouse.
2. **Sprite style pass (agent log _art/preview/agents/sprites2/WORKLOG.md).** Done: taller proportions (heads 0.64,
   HUMAN_SCALE 0.92), sculpt() skin shading, sashimono banners (9 enemy types + 7 guards), spell glow, harder
   hurt; all generators rerun, registry ids unchanged. User said Gonta still looked wrong ("arm split in half
   bleeding and attached to his belly"): sent back (remove red arm cords, separate/outline the near arm from the
   belly, sagari at the FRONT under the belly). Also a real bug: **every katana was drawn edge-toward-the-wielder**
   (forge_blade normal sign) -> fix sent (normal (dy, -dx)) + full regen. CHECK BOTH YOURSELF at 6x zoom before
   telling the user they're done. Open questions for the user: Gonta's mawashi white (reference) vs dark blue;
   banners for archers/officers/ronin too?; a lying-down KO (sheet layout change); head scale 0.64 vs 0.68.
3. **Music:** every track except the Orochi key-fitted and rendered (see "Key-fit pass DONE"); the user hasn't
   listened to the new versions yet: offer `tools/battlejukebox.py --secs 0` (battle themes, -rttank).
4. Older open items: the "START HERE after Saturday" list above (edge triggers / barricades / encounter rate /
   shifting-waste maze still untested in-engine).
- **Wrap-up 2026-11-07 (user at 90%): big ComfyUI queue for review after 6pm CST.** `tools/queue_busts.py` submitted
  1150 jobs (manifest _art/preview/agents/busts/QUEUE.md + queue.json): Gendo/Shizue travel+bath redos (the "straw hat"
  became a drinking straw / cup; prompts fixed: "sugegasa ... kasa hat", negatives drinking straw/cup/plastic) and
  ONE neutral bust per non-playable speaker (2-3 candidates; Crab path first, then by dialog line count; prompts from
  gen_sidecast's CAST text, else the family name's clan colours and role words). After the queue:
  `python -E tools/collect_busts.py` (downloads into _art/busts/<key>/review/, contact sheets review_npc_NNN.png and
  review_variants.png). Nothing from the queue is in the game until picked.
  **In the game now:** Natsuko (8 emotions x 5 looks, user-approved base cand_28), Rensei, Gendo, Shizue full sets
  (bases picked by me; Gendo + Shizue travel/bath are the bad ones until the redos are picked), Haruki / Mitsue /
  Tamotsu / Sayo when their background run finishes, and 9 NPC busts (gonta yosai ryozo takakana goro sachiko kage
  satomi michio, picked by me). **Open:** user review of all of those; Squeak (Splinter-style candidates
  squeak_candidates_splinter.png); fujio tomoe kiyo sakura ryoichi mai takeo candidates are in *_candidates.png
  (pick -> NPC_PICK -> `gen_busts.py npc <key>`); Rensei's skin came out grey-pale (grey background); white hair-gap
  slivers by the ears on some busts; the in-game look of NPC busts (placement uses a default chin height without a
  face box) is unverified.
- **Sprites round 3 (2026-11-07 evening; user: stay procedural, "scrap the sumo... big muscular").** Gonta is now
  build "strongman" (gen_sprites2d strong_*; `mass` 1.12; "sumai" kept but unused): muscular, V torso, white
  mawashi + sagari apron, ready stance, no red on the body. Front/back sashimono now beside the head on a pole (they
  read as tall black hats in the field); dark flag colours lifted. KO now lies flat (`lying()`, LYING_KO; same v4
  layout and animap ids). All sheets + portraits regenerated; field snaps M104 / M151 and battle gids 6 / 33 checked.
  Ask the user: lying KO OK? banners for archers / officers / ronin? head scale 0.64? Log: _art/preview/agents/sprites2/WORKLOG.md.
- **2026-11-08 busts, continued.** In the game: the 8 travelers' full sets (Rensei rebased with natural skin; travel /
  bath looks redone for Gendo, Shizue, Haruki, Tamotsu, Rensei; the word "kasa" summoned a one-eyed umbrella yokai on
  hats, dropped) and 76 NPC single busts (picks: gen_busts.py NPC_PICK + _art/busts/npc_picks.json; chin heights
  CHIN_FIX). Keying: hair-gap slivers cut, tolerance 12 (26 ate pale faces). **Bug fixed:** a quoted speaker label
  ('"Ryozo"') broke RokuganBustData.sk and the whole rokugan plugin with it; names are json-escaped now. After any
  `gen_busts.py data`, run one engine test (testbust.py) to be sure the plugin still compiles.
  **Still running:** ~900 redo jobs in ComfyUI (better NPC prompts: no clan animal words, kimono, cast-looks.md).
  Then: `collect_busts.py`, pick into npc_picks.json ({key: {names, file: "review/cand_s<seed>.png"}}), set a chin in
  CHIN_FIX, `gen_busts.py npc <key>`, `bust_review_sheet.py` (REVIEW_in_game*.png = everything wired in).
- **2026-11-08 busts, round 2.** 98 busts in the game (8 travelers + 90 NPCs). User-review redos done (Kisada keeps
  the helmet with heavy o-yoroi now, Jinnai, Nezumi Warrior, Kuni Taira, Shizue travel, Tamotsu bath, Maid, Ryoichi).
  A redo queue of 932 jobs is running in ComfyUI with fixed prompts (the first redo leaked clothes colours into hair).
  Workflow after it finishes: `collect_busts.py` -> `pick_sheet.py` (look at pick_NN.png) -> `pick_sheet.py --apply
  "0:2,1:x,..."` -> chin in gen_busts.CHIN_FIX -> `gen_busts.py npcpicks` -> `testbust.py` (plugin compiles?) ->
  `bust_review_sheet.py`.
- **Sprites round 4 (2026-11-07 night).** Gonta: heavier strongman (mass 1.28, wide 3) with `smooth_limb()` (each
  limb one tapered shape with muscle bellies + highlight, elbow/knee crease; no stacked segments), bigger chest with a
  pec shelf, traps, deeper back. KO fixed for every build (`lying()` lays a straight pose: legs on the ground,
  arms along the sides, weapon beside; checked ko3.png). Full regen; 1330 ids, 0 animaps changed; gid 6 snapped.
  Still open for the user: banners for archers / officers / ronin; head scale 0.64; lying KO vs kneel.

## Session wrap (2026-11-08, evening) - START HERE next time
- **Dialog busts (ComfyUI):** 98 in the game (8 travelers x 8 emotions x 5 looks; 90 NPCs, one each). Plugin
  plugin/rokugan/RokuganBust.sk + generated RokuganBustData.sk (names escaped: a quote in "Ryozo" once broke the
  whole rokugan plugin). Tags: `[angry]`, `[bath happy]`, msg fields emo/bustvar, ::Rokugan.bustScene("bath").
  User decisions: Natsuko = cand_28, darker skin; Hida Kisada KEEPS his full face helmet (canon) + heavy laced
  armour; travelers get sets, everyone else one bust; Squeak/nezumi = young Master Splinter style, never cartoon.
  Prompt lessons: never the bare word "straw" (drinking straws) nor "kasa" (umbrella-monster hats); clan names
  grow horns/lion manes; clothes colours leak into hair; say Japanese clothing explicitly (negatives: western,
  suit, jacket). ~932 jobs still queued in ComfyUI: run tools/collect_busts.py, tools/pick_sheet.py, pick into
  _art/busts/npc_picks.json, set chins, export (steps in the busts WORKLOG). Open: Kuni Taira white flecks on the
  hair edge; Toturi's hair colour (agent claims canon = dyed gold, unverified: ask the user); 7 speakers requeued
  (Moto Benjiro, Gochu, Kakita Yumi, Mibu Kagemaro, Akari, Doji Hayato, Yoritomo Rui). Review sheets:
  _art/preview/agents/busts/REVIEW_in_game*.png.
- **Sprites:** stay procedural (user agreed; ComfyUI pixel models judged wrong for 154-frame sheets). Done today:
  taller proportions, sashimono banners (field view: beside the head on a pole), katana edge fix, Gonta rebuilt
  as build "strongman" (old "sumai" unused). In progress when wrapped (see the sprite agent's NOTES entry):
  Gonta muscle pass (smooth tapered limbs, bigger shoulders/chest, from the heavier option) and the lying-down KO
  (legs-up/flipped for Gonta + musketeer, Natsuko's armour jumbled: fix per build or fall back to the kneel).
  Open questions for the user: banners for archers/officers/ronin? heads 0.64 vs 0.68?
- **Music:** all tracks except the Orochi key-fitted + rendered; the user has not listened to the new versions.
- **Sprite agent 2 stopped here (2026-11-07, end of session).** Nothing in flight; all sheets/portraits in the game are
  the final 4th-pass output (Gonta strongman v4 + flat KO). Left for the user to decide: lying KO vs kneel
  (LYING_KO switch), banners for archers / officers / ronin, head scale 0.64. Log: _art/preview/agents/sprites2/WORKLOG.md.
- (wrap addendum) The sprite agent finished both items before the wrap: Gonta v4 (smooth tapered single-outline
  limbs, bigger chest/traps; _art/preview/agents/sprites2/gonta_v4_final.png) and the lying KO for every build
  (ko3.png, no kneel fallback needed). Lead's check: KO lies flat for all builds, good. Gonta reads cleaner but
  still more round/soft than "big muscular": ask the user if it's good enough or wants more definition.

## 2026-11-08: AI sprite sheets + bust candidates, automatic runner (no Claude needed)
- **Start (also after a reboot, ComfyUI up first; nothing auto-starts it):** double-click `tools\start_pixeldrive.bat`. Safe
  to rerun: a second copy exits, valid finished frames are skipped, jobs lost in a ComfyUI restart are resubmitted.
- **Stop:** `powershell "Get-CimInstance Win32_Process | ? CommandLine -like '*gen_pixeldrive*' | % { Stop-Process -Id $_.ProcessId -Force }"`.
- **Check:** `_art/preview/agents/pixelai/PROGRESS.md` (every 20 min, with time left), `progress/` sheets + GIFs, `drive_base.log`,
  `ERRORS.txt`, `DONE.txt`.
- **Order:** 410 base v4 sheets (8 travelers, Gonta, side cast, human enemies), 334 weapon/hat look sheets, then bust candidates
  (`queue_busts.py --redo` + `collect_busts.py`). Rough time at 18-27 s per frame: travelers ~9 h, all bases ~13 days, looks ~16
  days more, busts ~3 h. Style: s11 (waiIllustrious + pixel-art-xl + ControlNet union promax, guided by our rig);
  strict palettes in `tools/pixelai_specs/`.
- **When done:** nothing is in the game yet. Review `sheets/<key>.png`; busts via `tools/pick_sheet.py`, then the NOTES steps above.
- **Upright fix:** guides in `pixelai/guides/` (RT_UPRIGHT=1 in gen_sprites2d, default off; game sheets unchanged). Recommended for
  the procedural game sheets too if any stay in use (48 standing frames per sheet; grips checked on all builds): run the sprite
  generators with RT_UPRIGHT=1, after approval.


## AI sprite runner: stand-only NPCs (2026-11-08)
User: NPCs that aren't recruitable only need to stand. tools/pixelai_standonly.json lists 258 side_ sheets limited to stand/stand_f/stand_b (5 rt_follow NPCs also get walk/walk_f/walk_b); gen_pixeldrive.worklist applies it. Fighters (enemy.json/player.json/skill.json/RokuganBattle refs, incl. hirelings and companions) stay full. When installing AI sheets, these NPCs need their other animations pointed at stand; NPCs moved by cmd_move in cutscenes have no walk frames.


## AI sprite runner: white hair holes fixed (2026-11-08)
key_out removed white hair along with the white AI background (Rensei: 11% of body pixels were holes; Natsuko and Gendo under 1%). Pal.quantize in gen_pixeldrive.py now fills anything inside the rig's solid body from the rig colour. Rensei restarted from zero; his old frames are in _art/preview/agents/pixelai/replaced/rensei_hair_holes.


## Battle screen redesign (2026-11-08)
Three boxes along the bottom: enemies (name, two lines for long names; shields; weakness slots, black dot = unknown, symbol = found), commands, party (name, VP gems, HP/MP/TP bars; TP kept for its coming use). Skill list: one wide box and a popover with the full name, description and cost (on by default; C toggles). Code: plugin/rokugan/RokuganBattleUI.sk (loaded after RokuganBattle). Art: tools/gen_battleui_art.py, then tools/patch_ui.py (bctl_n/bctl_g clips, parts/listitem9.ui is the battle copy of listitem3). Test: tools/snapui.py <gid> <out.png> [wait_ms] [flags]; flags -rtuicmd N (auto-pick a command), -rtuiback, -rtuireveal, -rtuidump. Compile errors in that plugin stop every plugin loaded after it.


## MP/TP split and Void caps (2026-11-08)
User's rules: MP = spells and kiho; TP = school techniques and kata. MP shugenja (full) > monk > other > samurai 0; TP samurai > other > monk > shugenja 0. Max Void shugenja 6, monk 5, other 3, samurai 2. Commands renamed: Skill -> Spell (key "spell"), Talent -> School (talent first, then TP techniques). tools/apply_resources.py does the data (class table, skill sort, curves as shares of each character's old MP curve) and runs at the end of gen_data; it warns about unsorted paid skills or someone owning a skill they cannot pay for. vpMax in RokuganBattle.sk reads rt_class; armor/weapon/condition field rt_maxvoid raises the cap (mechanism only; nothing uses it yet). TP is a pool, filled once per character on first battle and with every full heal (engine edits in RPGObjects, BattleRunnerBase, RPGEvent, RPGMain). Test note: the engine takes 13 command-line arguments at most; pack flags with -rt "lead P104;uicmd 2".


## AI sprites in the game for demos (2026-11-08)
User asked for the finished AI sheets in the game. tools/install_aisheets.py copies finished sheets over the game's (originals in _art/preview/agents/pixelai/game_sheets_orig; --restore puts them back; --started includes unfinished sheets; rerun gen_portraits.py after for the turn bar). Installed so far: Natsuko, Gendo (base look only; other weapon/hat combinations are separate sheets and stay procedural until done). The runner reads its own guides/, so it is not affected unless gen_upright_guides is run with --force after an install. Busts: 98 approved are in the game; about 430 speakers have unpicked candidates in _art/busts/*/review, not wired in.


## Stand-in busts (2026-11-08)
User: speakers with no bust use a generic finished NPC until their own is done. tools/gen_bust_generics.py writes plugin/rokugan/RokuganBustGeneric.sk (men npc_servant, women npc_village_herbalist, soldiers npc_gate_guard, the Mieko and child names use their real busts; monsters, spirits, notes get none). A real bust wins automatically. Rerun the tool after adding speakers.


## Text boxes and WASD (2026-11-08)
Dialog, big message and choice boxes use the battle look: atlas clips msgwin, mfram, msgplate1 (tools/gen_battleui_art.py) swapped in by same-length patches in tools/patch_ui.py (message_talk, message_talk_pic, message_big, parts/choiceitem, parts/dialogback, dialog_confirm). SKMultiImageView.updateColor is wrapped in RokuganBattleUI.sk so any bctl_ button keeps its colour. WASD: PlayerMoveAction (walking) and GPUI.setButtonKeyMap (menus). Not yet pressed by hand. Test choice menus with testbust.py "?choice|one|two".

Dialog box follow-up: smaller and rounded, drawn at real size (msgbox, msgbox_tall, namepill; RokuganBattleUI fitMsg). 3 lines fit; a longer line gets the tall box (estimate in msgLines). Any compile error in a plugin stops every later plugin: check after edits, and write newlines in .sk strings with care.


## End of the sprite queue (user, 2026-11-08)
After the AI run finishes: fix the remaining body tilt and the walk cycle on the AI sheets; Natsuko "looks like she is high stepping everywhere" (knees too high in walk). Check the guide poses for walk, then redraw the affected walk frames for every sheet. tools/pixelai_priority.json lists sheets drawn first (Sachiko and Ryoichi, for demos).


## Git branch and boss art redo (user, 2026-11-08)
Queue, in order: (1) Sachiko, Ryoichi, Yosai finish; (2) make the local git branch (version 1: everything of ours, playable, Apache-2.0 for our code and original assets, engine LICENSE/NOTICE kept and edited engine files marked; a notice that the L5R setting is not covered and this is a non-commercial fan project; left out: boss_*/banner_* sprites made from wiki and card art with placeholders in their place, _sources, the Adventures PDFs, OctopathTraveler, _art/reference, .venv, logs, saves; check the AI model terms and the engine's stock asset terms first). END of the sprite queue: fix tilt and high-step walk, and redo all 46 boss sprites and 46 banners with the AI pipeline, new designs inspired by the current ones. Work from written descriptions and our own pose guides; never feed the wiki-derived art in as an input image, or the result stays derived from it.


## Prologue introductions (2026-11-08)
M099: one text box per traveler, each outlined while introduced (spot() in gen_maps, ::Rokugan.spotlight in RokuganField). Always rebuild maps with tools/regen.py --maps: gen_maps alone drops the weather, camera and render settings that gen_render adds. It was run alone once today, and every map except M099's events was restored from the copy taken just before; the mapdata .bw files were rebuilt by that run.

Bust hold: bust_hold(key, emo) in gen_maps calls ::Rokugan.bustHold; explicit [tags] still win over a hold, and a hold beats the keyword guess. Used for Natsuko hurt from "You're bleeding." to Dawn (Crab S01); S02 office lines are tagged in docs/story/production/crab-ch1.md. A hold is not saved with the game.


## Traveler expressions, read by hand (2026-11-08)
All 1012 unique lines by the eight travelers have an emotion in tools/bust_emotions.json (speaker TAB text -> emotion), read in story order and checked against the acting notes in docs/story/production. tools/apply_bust_emotions.py sets the "emo" field at the end of tools/regen.py and reports any traveler line it can't match (new or reworded lines fall back to the keyword guess). Order: [tag] in text, then bustHold, then emo, then guess. "sad" reads as crying, so it is reserved for real grief.


## Small balance (2026-11-08)
Coin carriers (apply_resources COIN: bandits, ronin, gaki, thugs, ruffians, pirates, corsairs, wako, swords-for-hire) pay 1.5x zeni; everyone else keeps 10 + 4 per level. ENC_RATE 5.0 (a fight per ~20 m). Jump is Space on the field (PlayerMoveAction, RPGMain hint), X still works; not engine-tested when written because the game was open.


## Caves redone, MP/TP items (user, 2026-11-08)
tools/cave_sprawl.py runs in gen_maps.make() on cave_map() maps whose name reads as a cave (21 maps). Maps grow east (or south) where they have no exit, then get a cluster of new rooms with looping tunnels. Where a direct room-to-room tunnel has no event in it, that tunnel is walled off and the main route runs through the new galleries (8 maps; user: main routes can sit at the end of long corridors). The rest get side branches. The cluster only ever joins those two rooms or one spot, so scenes, bosses and sealed walls can't be bypassed. New galleries hold chests, and a rest-and-save shrine if the map had none. M170 and M157 had no room to grow and are unchanged. walkcheck: all caves pass (M147, M215, M456 list crowd villagers, not caves). Restoratives in apply_resources RESTORATIVES: I445 Sakaki Incense, I446 Temple Incense (MP), I447 Bitter Green Tea, I448 Warrior's Sake (TP); in 43 shops. M131's pool shrank so its bank is wide. Space Jump hint confirmed in engine.


## Licensed copy (2026-11-08)
D:/RokuganTraveler-licensed, its own git repository on branch licensed-demo (2 commits, local only, not pushed). Git refuses D:/RokuganTraveler in place: the folder is owned by an older Windows account (dubious ownership), and the only fix is a safe.directory setting that is the user's call. So this is a filtered copy: no wiki or card art, source PDFs, research, _art or logs; 92 boss and banner sprites plus their portraits are placeholders. LICENSE Apache-2.0, NOTICE.md lists what isn't covered. Rerun the copy when the demo should be refreshed. Stock assets: Apache-2.0. Pixel-Art-XL: CreativeML OpenRAIL-M. WAI-Illustrious on Civitai: no credit needed; commercial flags Image and RentCivit.

## 2026-11-09: Whole-game dialogue pass (user: "make sure it makes sense, NPC speeches don't overlap, busts match")
- **Read all of it.** 8,208 lines on 431 maps, every branch. Reading copies in `_art/preview/agents/dialog/`:
  `read3.txt` (sorted by map, pages / IF / CHOICE / flags shown, traveler expression in `<...>`, repeats collapsed),
  `dups.txt` (lines shared between events), `FINDINGS.md` (the working list). Rebuild them with the scratch scripts'
  logic if needed: walk map.json `event -> page -> cmdblock`, `cmd_if.cmdblocks[0/1]`, `cmd_choices.text0..N`.
- **The Seppun aunt asked twice (the user's example).** `S03B` (the noodle-stall scene) ran on through the script's
  `### S03b` block, which is the optional tea-house talk. Fixed in gen_maps.py (`stop_at="### S03b"`): she now speaks
  only in the tea house (first "You're Crab? ... Never mind.", second talk the request, sets G017). The cave lines that
  name her nephew still need G017, as the storyboard intends.
- **tools/apply_dialog_fixes.py (new, last step of tools/regen.py).** One table of fixes applied to map.json after
  apply_bust_emotions: text swaps, speaker renames, deleted/inserted lines, one new NPC page, a few patterns. It prints
  a count and lists any entry that no longer matches as STALE. `--check` reports without writing. Why a post-pass: the
  lines live in gen_maps.py AND docs/story/production/*.md; one table is easier to audit than fifty scattered edits.
  What it fixes:
  - Leaked directions: "rat-way shortcut through donjon_1) [END]" in Natsuko's mouth (M148), "off-screen", "The camera
    stays behind / slides", "Quick cuts:", "Training montage.", "The scene shimmers", "Not this chapter", `A beat.` ->
    `A pause.` (11), "Ship'S Master", and the clear-save note that said the post-game "isn't built yet" (it is).
  - Lines that fit no moment: Sachiko's "when the court's done with you" and Ryoichi's "Back from the Shadowlands" both
    showed in Ch1; Mutsuye stayed cheerful after the murder (new page when G210); Nishi's "eleven weeks" vs "a week";
    Ijako's same sentence twice running (tower, then hall); "guard. I challenge you"; the palace guard's doubled
    opening; Gendo's "second time someone's said that"; Crane Ch1's ending text for the blade-in-the-cell choice and
    its summary; Crane Ch1 said Seigen and Kiku "go their own ways" though both stay as guests.
  - Missing set-up lines added (narration): Kage and the map case (M101), the gift exchange (M210), the oni's parting
    shout before Benjiro answers it (M260), the dying healer (M290), Akuro's prophecy (M344), Akari (M418), Imuro's
    rice (M205), Kitsune Hana introduced before she speaks (M352).
  - Names: Nezumi Shaman / Warrior, Bandit Chief, Seduced Sentry, Mantis captain; **the fever-road child was also
    called "Kitsune Hana"** (the Fox lady of Scorpion Ch1: same bust) -> "Little Hana"; Norie's letter lines.
  - Terms: every "SP" -> "MP"; year-400 hirelings no longer say "Kitsuki-sama"; Charm-fail lines named the hireling's
    home ("castle town's lamps has had enough"); the Eavesdrop-fail line called Mitsue a tea-pouring servant in every
    town (kept only at the memorial, M345).
- **Busts.** "sad" is crying (user): 28 expressions changed in tools/bust_emotions.json. Sad is left on 13 lines only:
  Natsuko on the ridge when the road is real (3) and drawing the last line of the map; Rensei's "...Father."; Haruki
  when Hoju dies (2), reading the note (2), "It's where I broke her.", the dream (2), "twelve years to give it back".
  Also: "No." to Miyako and "We'll take it in jade." -> determined; Rensei's "You don't know our way." -> neutral.
  NPCs have one bust each, so there is nothing to choose for them.
- **Looked at, left alone.** Yosai's "Company!" block appears twice where two companions join: W is recomputed before
  each, so it only plays once. **Commands after a map move never run** (engine-checked with runevent.py: the objectives on M316, M335 and M346
  were silently lost). apply_dialog_fixes.py now moves the map move to the end of its block; re-run, all three show.
  Also engine-checked: Satomi's three tea-house pages, Mutsuye's new page, the M148 line. The Crab/Scorpion/Unicorn shared tribunal scenes read
  correctly for both leads.
- **2026-11-09, later: engine sweep + two more fixes.** 32 changed scenes run with runevent.py, 0 errors. Found and
  fixed: the fix pass was not repeat-safe ("Seppun Seppun Seppun Ushimo?" after three runs; `sub` now skips text
  that already holds the replacement, inserts skip when already present). M148 "Just like the Crab said" assumed the
  veteran's tip: now "Somebody came down here with a rasp."
- **Skill popover overflow fixed (RokuganBattleUI.sk `UI.tickPop`).** A description over one line wrapped onto the
  cost line and was cut after two (131 skills are that long; Earth Becomes Sky is 220 characters). The popover now
  grows to 2 or 3 lines with the cost on its own line. The label holds a RichText: its length is `getText().intext`.
  The panel group `g` clips its children, so `g` grows upward and its other children (infog, window, frame, lists,
  grayg) shift down by the same amount. Checked with snapui.py (`-rt "lead P104;uicmd 2"`, gid 77): uicmd index 2 is
  Spell. The skill-list scrollbar is tan now, not teal: nothing to fix.

## 2026-11-09: Sprite runner order changed (user: move the busts up)
tools/gen_pixeldrive.py `run()` now draws travelers + NPCs + enemies, then the bust candidates, then the 334 outfit
variants (70% of all frames). Restarted with tools/start_pixeldrive.ps1; finished work is skipped.
`queue_busts.py --dry` used to overwrite queue.json: fixed (it no longer saves on a dry run). The 934-job list lost that
way was rebuilt from the 1,229 candidates in _art/busts/*/review (names only where the speaker is still unpicked).
Still to draw at the bust stage: 924 candidates. Six finished travelers + Gonta are NOT installed yet (user decides).

## 2026-11-10: Sumai matches, monk fists (user)
- Sumai menus are Talk / Sumai match / Quick throw (n%) / Leave (Wall Crabs and hirelings likewise). `sumai_match()` (gen_maps) = M001 group 900, enemy E121. `::Rokugan.sumaiMatch` (RokuganField) takes the party down to Natsuko, swaps W106 in, gives E121 the NPC's name and sprite and scales it to her: 3 to 8 throws, fewer at higher quick-throw odds. `sumaiEnd` restores party, weapon, HP/MP/TP. Same rewards and penalties as the roll. Gonta's story bout is unchanged. Hirelings can't be called during a match.
- Monks (rt_class monk) with W106 or an empty hand: `getBaseScoreMap` wrapper in RokuganLook adds LV*LV*0.0447 PATK. Passes Thunder Monk's Bo around Lv 55-60. Engine: Yosai Lv 90 PATK 586 fists vs 356 Thunder Bo.
- New Unarmed-type claws: W159 Iron Nekode 64 (R143, R154, R158), W160 Thunder Claws 140 (R170), skill S690 Claw Strike. Drawn as the "none" look, so no new sprites.

## 2026-11-10: GitHub refresh
`python -E tools/sync_licensed.py [--dry]` updates D:/RokuganTraveler-licensed from this folder (boss and banner placeholders kept, engine license marks kept, `.gitattributes` keeps every file byte-exact). Then commit there and `git push origin licensed-demo:main` (akodoreign/Traveler). Test a fresh clone first: title, a boss with tools/snapui.py, a cave with tools/snapmaps.py (make `_art/preview/agents/ui` in the clone).

## 2026-11-10: Caves force the route through the new space (user: "force the travelers through a good part of each level")
tools/cave_sprawl.py reworked. `necks()` finds every narrow spot that is the only way between two parts of a cave with no event on it (round plug or thin wall). `sprawl()` runs up to 3 passes: wall off a neck, build galleries joining its two sides, so the only way on is through them. Swapping a bridge for a longer bridge keeps story order. `event_groups` rolls a pass back if anything gets cut off. Maps now grow both east and south when free. Sprawling caves: wall rims 5+ (too high to jump), final pass raises anything climbable.
Result: required walk across 21 caves 1120 -> 2288 steps; 20 of 21 forced by the check (M320 forced only past its last scene; M130's far goal unchanged in length). Sheet: `_art/preview/caves_forced.png`. walkcheck: only the 3 known flags (M147, M215, M456).

## 2026-11-10: Sacred blades vs clan-made weapons; fewer outfit sheets (user)
- Rule book (Core 3e clan Sacred Weapons, Book of Void): the Kaiu Blade and Kakita Blade are specific katana, separate from
  other Kaiu- or Kakita-made weapons. `CLAN_ONLY` is now W130 Heaven's Glory + W131 Kakita Blade (renamed from Kakita
  Masterwork), Crane; W158 Kaiu Blade (new, 126 attack, sold at R114 Kyuden Hida Arms, shares the katana sheet), Crab.
  Kaiu Tetsubo/War Spear etc. and W133 Kakita Wakizashi are open to anyone; W133 is back at R152. This overrides the
  W133 restriction in the 11-09 entry below.
- `LOOK_NOT_DRAWN` (gen_sprites2d): no kasa or hachimaki outfit sheets. A170 Straw Kasa shows the jingasa sheet, A172
  Hachimaki has no rt_look so it shows the traveler's own head. Outfit sheets 340 -> 224. Remove from the set to restore.
- `look_combos`: hats are only drawn with the traveler's own weapon type. Another weapon + a hat shows that weapon and the
  traveler's own head (plugin `lookFor` falls back to "weapon|"). Outfit sheets 224 -> 74. RokuganLookData.sk rewritten with
  `s2.write_look_table` only: running gen_sprites2d.py plain would overwrite installed AI sheets.

## 2026-11-09: Equipment rules and the Kakita blade (user)
- Sprites were already shared by weapon TYPE (`EQTYPE_LOOK`: every plain katana is the "katana" sheet). Nothing to merge.
- tools/apply_resources.py: monks can't equip Tanto/Katana/Yari/Axe; shugenja can't equip Heavy Armour/Heavy Shield
  (`NO_EQTYPES`, cleared from player `eqtypebits`). `CLAN_ONLY`: Heaven's Glory (W130), Kakita Masterwork (W131), Kakita
  Wakizashi (W133) are Crane only (`rt_only_clan`, checked in plugin RokuganLook.sk; the engine's eqflag can't do it,
  getEquipFlagBits always returns 0). Description says so. Removed from the two non-Crane shops (R142, R152).
- W130 and W131 use a unique weapon look "kakita" (white silk grip, gold guard, bright steel): Rensei only, EP2512-2517.
  `gen_sprites2d.py rensei --weapon kakita` draws just those sheets and leaves installed AI sheets alone. Plain
  `gen_sprites2d.py` would OVERWRITE them: reinstall with install_aisheets.py afterwards.
- Runner: the six Kakita sheets are drawn with the base sheets (before the busts). Installed today: Rensei, Shizue,
  Haruki, Mitsue, Tamotsu, Sayo, Gonta. Engine-checked: equip slots for Rensei, Natsuko, Haruki, Yosai, Hayato.

## 2026-11-10: Playthrough testing (user: "simulate each path ... approach it like a player")
User reports: Hiruma path no route to Hida castle; Crane path black screen after a screen change; Lion stairs don't
work; Lion "wait at night" goes black; you can jump/fall off the Wall and get trapped.
- **Test player** (plugin `RokuganBot.sk`, only with `-rtbot`; `tools/playbot.py NAME MAP X Z "steps" --vars ...`):
  holds virtual keys through the field controller (no Windows keys, no focus), `goto MAP X Z` walks there (jumps when
  blocked, detours), `tap z` talks, `shot NAME` screenshots, map changes logged. Steps are packed into the -rt arg.
  Output `_art/preview/bot/NAME/`. Coordinates are gen_maps block coordinates of the map named in the step.
- **Hida road**: the exit existed (M101 west edge) but nothing showed it (forest in the padding, a tree in the way).
  New `pave_exit()` (edge_triggers): every edge exit gets a 4-wide road out to the map edge, trees cleared, and inward
  until it meets a road. Edge trigger stays one square deep (user).
- **Direction rule** (user: "going left you should keep going left ... or east"): Hida road flipped (garrison west ->
  road's east end; road's west end -> Kyuden Hida's east side; M151 summer exit too). New `tools/edgecheck.py` checks
  every edge exit lands on the opposite edge of the next map: 47 wrong -> fixed with `MOVE_EXIT` (exit moved to the
  right edge, step-backs flipped) and `ARRIVE_AT` (portal lands at a walkable spot beside the right doorway). 8 left on
  purpose: mid-map gates/doors and one-way story moves (M220, M286, M340, M372, M377, M391, M396, M408).
- **Black screen**: DARK (cmd_screenfxon black) is only cleared by a map change; Crane M201 "Four days of road" (touch
  scene) and Lion M242 Ukita "Wait for night" went dark and stayed dark. `fix_dark()` (make()): any command list that
  goes dark and never moves map fades back in at its end.
- **Lion stairs**: castle_floor() drew the back-right stair on every floor, even with no floor above (Hiruto's chapel,
  barracks, guest wing, hall...). Now only when `up` is set.
- **Wall**: M100 far parapet had gaps and a 1-block lip; jumping off landed in the Shadowlands with no way back.
  Invisible walls along z 20-22 across the whole padded width.
- `tools/storycheck.py [--path N]`: symbolic play of the built map.json from New Game (value sets per variable):
  maps never reached, event pages whose conditions can never hold.
- **Stairs, the real cause** (engine-tested): the engine never steps up while walking, so every 0.5 m stair needed a
  jump ("you can kinda jump up them"). Plugin RokuganField: walking into a ledge 1 block high with room above lifts the
  player onto it (`::Rokugan.STEPUP` 0.55). The Wall stairs are now walked without a single jump.
- **Wall stairs (M101)** started 3 blocks above the yard (a jump clears 2): fell off the Wall = trapped. Two lower steps.
- **Edge triggers made from walk-on talks kept d 2**: on west/east edges their 15 m strip lay ACROSS the road at one row
  (fired early or never; e.g. M140 -> M151). edge_triggers() now sets d by side for every trigger.
- pave_exit clears trees 3 cells either side (canopies overhung the new roads).
- MOVE_EXIT M314/M351 put exits in the sea/river: moved the partner exits instead (M304 -> east, M350 -> west).
- `tools/exittour.py [MAP ...]`: end-state world (every true/false flag true), pathfinds (walkcheck grid, the map's
  largest walkable area) to every exit, walks in, checks it arrives where it should and the screen isn't black.
  Report `_art/preview/bot/tour_report.txt`. Bot `warp` on the same map sets the position (moveMap ignored it).
- `-rtvar @file` reads the list from a file (long lists): a JSON list, read with `decodeJSON(FileRef(f).load())`.
- Engine script gotchas met here: no `'c'` char literals in comparisons that compile, no `str.find` (use `slice`),
  no `x.tostring()` on numbers (use `"%d" % [x]`), `typeof(x) == SS_STRING` is a function, `FileRef.load()` gives a
  ByteBuffer (no asText): use JSON. A compile error in RokuganBot.sk silently voided the first whole-game tour.
- **Long edge triggers had dead ends** (engine-tested on M103's north edge: an 81 m strip fired from x 47-117 only;
  M104's south edge failed at x 44). Cause (RPGEvent.spawnDistantCheck): spawndist 1, the default, spawns an event
  only while its CENTRE is on screen (+3 m), so the far end of a long strip had no event at all. Edge triggers now get
  spawndist 5 (always there), and make() gives it to any event whose box is 4 m+ across. Trigger 5 ("walk in") needs
  the player's centre box (+-0.38 m) wholly inside the event box; no ray test (that's trigger 1/2 talk).
- **M140 -> M151** (summer Kyuden Hida, after Crab Ch4): the walk-on talk at the west edge never fired; now a second
  portal shown with G286 (the winter portal hides with it).
- exittour: the "main area" was the largest walkable area, often a cliff top (cliff tops count as floor; seeds within
  3 cells of an edge strip's middle landed on them); now the area under the exits' whole trigger boxes, seeds only at
  an event's height, edge strips don't seed. The 45 "no route" exits were all that.
- **Empty message boxes**: `Events.prop()` made every bottle/candle/dish a villager with msg "" (1,197 of them); the
  villager role always talks, so Z beside one opened an empty box (found by the story player in the M120 inn). A
  prop with nothing to say is now a custom event with no trigger (same model, still solid).
- **Crab Ch4 was unwinnable**: M153 (Kyuden Hida cellars) - the servants' stair portal (x 66) sat 2 cells past the
  end of the cellar's tunnel (it stopped at x 60), inside the rock: no way up to the dark castle. Tunnel runs to 68
  now (engine-checked: walks through to M154). walkcheck never saw it (it seeds at the portal itself).
- Story player found, all fixed in the planner (not game bugs): talk range ~1 m (closes in with `talkto`), examine
  exits (cave mouth M105 -> M130), guard choice exits ("Go back up?" -> M152), road-following at edge strips, routes
  keep 1 cell from trees, shops pick Leave, villager lines skipped under -rtfast (showUI message_talk).
- Story player results so far: Crab Ch1-3 complete start to finish (~40 min of play, Hida road walked both ways);
  Ch4 blocked at the cellar stair (fixed above).
- **Bad animation frames** (user: "like the togashi's head"): the AI sheets' 8-frame idle turns the head (frames 0-1
  and 6-7 show the side/back of the head, 2-5 the face): Yosai, Mitsue, Sachiko, Gendo, Tamotsu ... Every side-cast
  and cast sprite with an 8-frame stand now plays 3,2,2,3,4,5,5,4 (706 sprites); Yosai's walk 8/15 and run 16 too.
  `tools/frame_fixes.json` {EP: {bad: good}}, `tools/badframes.py --apply` (sheets as drawn kept in _art/frame_orig;
  a sheet the sprite runner redraws becomes the new original). `tools/animsheet.py EPxxx` = one row per animation.
  RE-RUN `badframes.py --apply` AFTER INSTALLING NEW SHEETS.
- Story player: a battle burst (3 frames, 0.35 s apart) per battle, `story_N_battle_NNN_F.png`, enemy names logged
  ("[RT] BOT battle shot") - for backwards sprites (user: enemies facing left / cast facing right) and bad frames.
- **Bad busts list** (user: "keep track of bad bust art, so it can be re-queued"): `tools/bad_busts.json` (speaker,
  file, why, found). `tools/bustsheet.py story_N` = sheets of every bust a playthrough showed (review them each run).
  `queue_busts.py --bad` queues 3 new candidates per listed speaker, even ones already in the game (not sent yet:
  ComfyUI is busy with the sprite runner). So far: Hiruma Ryoichi (full-body child, wrong framing), Wall veteran
  (too young for "forty years on the Wall"). Hida Tomoe as an old man is fine ("a grizzled commander").
- 2026-11-11: 147 finished AI sheets installed (install_aisheets.py) + portraits + frame fixes, pushed (ec2311f).
- Shop/inn doors: the portal sits 2 tiles out from the wall; walking along the footing past it never enters. Players
  walk up from the street, so the story player lines up 2 cells back and pushes in.
- `tools/storyplay.py PATH`: plays a path from New Game (M099, prologue choice = PATH). Bot serve mode: a JSON command
  file `{n, steps, flags, quit}`; after each batch the bot prints its map/position and the set story flags. The planner
  picks the nearest story event whose page would change a flag (Objective/arrival scenes first), routes map to map
  through open exits (whole trigger boxes), walks, talks, screenshots each leg (`story_N_LLL.png`). Exits that fail
  twice are reported as "BUG?" and routed around. Output `_art/preview/bot/story_N/play.txt`.

## 2026-11-11: Agent team (user: "spin up an agent ... watch animations ... testing all the paths ... pushes fixes every 5 hours ... monitors bust work")
- TESTER: plays every path with tools/storyplay.py, adds save/resume checkpoints (_art/preview/bot/checkpoints/path_N.json,
  COVERAGE.md), fixes game bugs it finds, notes under "Agent team - tester". Only agent allowed to run rpgcobo.exe.
- ANIMATION: reviews the tester's battle bursts (battlesheet.py) and every fighter's sheet (animsheet.py) for backwards
  sprites and bad frames; owns frame_fixes.json / badframes.py / install_aisheets.py runs.
- BUSTS: finishes the BiRefNet bust re-export (gen_busts.fg_mask, model in ComfyUI models/background_removal), scans
  holes (busthole.py), reviews busts each run shows (bustsheet.py), keeps tools/bad_busts.json.
- PUSH: every 5 h (session cron, expires after 7 days or when the session closes): sync_licensed.py + commit + push.
- Status files: _art/preview/agents/team/{tester,animation,busts,push}.md. To restart after a session ends: spawn the same
  roles again from this section; the tester resumes from its checkpoints.

## 2026-11-11: Agent team - animation
- 06:00 story_0 bursts 1-18 + rerun 1-8 reviewed; facing sheet of all 250 fighter EPs. Fixes: Togashi Yosai EP309 walk 12,
  run 21, atk 35 (off-model/turned heads); Gonta EP342 run 21; badframes.py now merges fixes per shared sheet (EP309/709,
  EP342/742 were undoing each other); boss Kumpei EP145 + Okura EP196 flipx True (+ gen_bossart FLIP); Sumai opponents
  faced away (party-side sprite on the enemy side) -> RokuganField.sk sumaiMatch swaps in the EP700+ foe twin
  (::Rokugan.sumaiFoe). Details + open items: _art/preview/agents/team/animation.md.

## 2026-11-11: Agent team - tester
- **Checkpoints** (storyplay.py): `--resume [--ckpt FILE]` starts at the saved map/spot with every story flag
  (defaults since cleared get `=0`), party (`-rtlead`/`-rtparty`, `-rtlv`), money and bag (`-rtitem`), tried pages and
  broken exits. Saved to `_art/preview/bot/checkpoints/path_N.json` every 40 legs, at each "- complete" card
  (`path_N_chK_doneD.json` kept) and at the end of a run. `--save-from-log LEG|last` rebuilds one from a run's
  log.txt + play.txt. RokuganBot prints `[RT] BOT kit N party=.. money=.. items=..` each leg; a resumed run numbers
  its battle bursts on (cmd `battle0`), logs to `log_resume.txt` (appended to log.txt at the end), appends play.txt.
  Not restored: equipment, the plugin's menu-answer rotation. Coverage per path: `checkpoints/COVERAGE.md`.
- **M103 -> M102 "BUG?" was the planner** (both Crab runs stopped there): its route cut through the west padding
  forest and wedged between canopies (engine trees collide wider than reach_map's 1-cell margin). Routes now prefer
  road squares (Dijkstra, road 1 / ground 3) and keep 2 cells from trunks when they can.
- **Crab Ch1-4 complete** in one resumed playthrough (checkpoints path_0_ch1..ch4_done*.json, ~260 legs). The Ch4 dark
  castle stalk (maid / guard / Akiko / Nashiko) is solved by the menu-answer rotation. After Ch4 the Crab save walks
  straight into the finale (M444 eight roads, fJoinAll -> M445 seven waves).
- Engine passes at most 13 command-line args: resume packs lv/party/item/money/fast/auto into `-rt`.
- Planner: door cells (portal boxes <= 9 cells) are never walked across on the way elsewhere (M141: the route east
  crossed the M160 inn door - in, out, in, forever); a "go" leg that lands on a third map without any flag change is
  reported (`??`) and after 3 routed around; hireling / Yosai offers (moneyop "hire", `W = n <= 1`) get one try at
  the lowest priority (they ate 6 legs each).
- **Finale wave 7 lost** (Many-Legged Horror, 30,571 HP) with Party A at 2 of 4 standing: the bot chained waves 1-7
  with no healing (the inn closes during the waves). Bot now rests at a save shrine on the map whenever a member is
  down or under 3/4 HP (`BOT kit ... hurt=N`), at anything offering "Rest and save." (shrines, the wave gate, the glade's last save); RokuganField's auto-answer always takes "Rest and save." (0).
- **GAME FIX - resting never raised the fallen**: REST (every save shrine, the wave gate, the glade's last save) was
  two cmd_hpmp, and the engine's changeHPMP skips dead characters: "(Rested. HP and MP restored.)" left a KO'd
  traveler at 0 HP. The finale has no inn from Osano-Wo to the Empress (8 maps, 4 with encounters), so a downed
  Party A member stayed down to the end; the bot wiped twice in the Shinomen Mori. REST now starts with the inn
  macro's cmd_condop (remove K000, ignoredead) (gen_maps.py REST); REST_ALL and the inn's "RT reserve rest"
  (gen_data.py, macro.json X014) also `removeCondition("K000")` on Party B. Lead: veto if save shrines should not
  revive (Octopath's don't; but the text promises it and there is no inn on the finale road).
- Bot `kit` also prints equipment (`equip=P100+0+W127,...`, Party A + B) and resume restores it (`-rt equip`); a
  resume with no equipment fought the finale in starting gear. Party wipe is reported as such ("PARTY WIPED").
- Battle burst numbers: a resumed run's offset was added again on every battle (cmd sent it each leg) - shots
  2341.. 3220 in story_0; now once per run.
- **Crab path played to THE END** (finale Act 1 seven waves won on auto with rests; Shinomen Mori; Act 4 Empress;
  epilogue codas for all eight; THE END; then back at Osano-Wo for the post-game). The Empress (13,134 HP, 20
  shields, vanishes - "crystal or jade finds her") beat the auto-battler twice; seen through with `--tank`
  (storyplay: -rttank, nobody falls). Not a game bug as far as the logs show; a player uses crystal/jade there.
- Bot talkto retries from the other sides when nothing answered (M445's gate ignored Z from one spot after the
  regen: six "talks", no message); RokuganField counts shown messages (`::Rokugan.msgn`) so a talk that ran and
  finished is not repeated.
- **Crane (path 1)**: Ch1 "Heaven's Glory" complete (checkpoint path_1_ch1_done1.json). Found and fixed:
  - **GAME FIX M210 castle gate**: the portal to the lantern garden (M211) sits on top of the 12-high castle wall
    (y 13), out of reach; only the guard's first-visit menu ever moved you in. After G346 the guard said "Up you go"
    and nothing happened - no way back to Lady Sanae's rooms (Ch2 report). The guard now moves you in (gen_maps.py
    garden_port). A scan of every small portal against the walkable area (scratch highportal check) found no other.
  - **GAME FIX M212 tide gates looped for ever**: after "Wait for low tide" the bridgehead's page flipped to its
    G376 page while the player still stood on it, which cleared G376, which flipped it back: wait, dry, under water,
    wait... (the engine re-fires a walk-on event when its page changes under you). The bridgehead's low-tide page is
    now empty; two new walk-ons on the shores past each bridgehead (tide_ashore) end the crossing.
  - The reported Crane "black screen after a screen change" did NOT reproduce: the black leg-19 shot was taken
    mid-cutscene (DARK before the move to M201); the next shot on M201 is normal. Leg shots are now taken after the
    scene ends (bot serve `shot`), so a black leg shot means a black screen the player is left with. A DARK + move
    test (bot step `darkmove MAP BX BZ [MS]`, also after a battle) never stayed dark.
  - Bot: menus met while passing through ("go"/"rest" legs) always take answer 0 (`pin 0`); the rotation (puzzles)
    only runs at the story target. The tide gate's rotation had answered "Not now." on the way across.
  - Ch2 "The Iron Cranes" and Ch3 "The White Squid" complete (path_1_ch2_done2 / ch3_done3). Sea chart: the
    planner now reads menus of places (`menu_moves`: each answer that moves map is its own exit) and the bot answers
    with step `answer N` (sets -rtchoice's queue for the next menu).
  - **GAME FIX M221 chart table** was 1 block high: walking up to it, the step-up lifted Rensei onto the chart and Z
    talked to Seigen instead. Now 2 high. (Talk targets also prefer squares on the event's own floor.)
  - **GAME FIX side doors in caves (14 maps)**: a one-square portal against a rock face to its east/west can't be
    walked wholly into (the body stops half a square short): M226<->M225/M227 never fired (Crane Ch3 shrine);
    same for M270, M284, M298, M299, M310, M311, M312, M318, M320, M334, M433 (paths 2-7). make() ->
    `portals_off_side_walls()` moves such a portal one square out. (North-wall doors with door openings are fine.)
  - **GAME FIX edge strips over rock**: edge_triggers() based a strip's box at the ground height at its MIDDLE;
    M226's east strip sat on 10-high rock and the paved way out at 3 ran under it. Strips now start at the lowest
    ground along their stretch. Full regen 12:00.
  - **GAME FIX M225 cliff path**: the exit to the White Squid shrine sat at the cliff's foot behind the climb; a
    ledge at the top of the path now holds it ("up the cliff path").
  - Bot: door pushes go toward the door's wall (door_push, up to 2 squares; the portal's d is the facing coming out,
    M227's west door is entered going left) and hold 1.6 s (0.9 s stopped short). Guest-call offers ("will answer
    the Guest call") join hirelings as one-try side business. Never regen while a run plays: gen_maps' RTMAPGEN
    kills the engine.
- **Lion (path 2)**: Ch1 "The Blood of Family" complete (path_2_ch1_done1.json).
  - **GAME FIX two exits on one edge**: MOVE_EXIT moved an exit onto an edge that already had one; both strips covered
    the whole edge and the first won: M254's east edge always went to M241 (never Shiro Akodo, M255 - Lion Ch2
    blocked), same for M326 (M325/M322), M333 (M323/M334), M350 (M349/M351). Those four MOVE_EXIT entries are
    removed (exits back where they were drawn). Scratch check: no other ungated overlapping strips (M140/M272's
    overlaps are flag-gated alternatives).
  - Bot: door push follows the door box's orientation (a box lying along x is walked into along z).
  - **GAME FIX M256 south-facing castle doors**: the Hall of Akodo (M262) and South Dojo (M260) doors sit on their
    buildings' south walls but had d 0 like the others, so coming back out set you down INSIDE the building and the
    fall-rescue lifted you onto the roof (Lion Ch2, after "The Crane spy! Arrest her!": stuck on the roof). d 2 now.
  - **GAME FIX arrivals into rock** (engine: RPGStageState.getPortalPos sets you 1 m in FRONT of the portal you
    arrive at, heading (d+2)*90: d 0 -> -z, 1 -> -x, 2 -> +z, 3 -> +x). Cave side doors on west walls were d 1:
    arriving faced the rock (M261 from the South Dojo: rescued onto a ledge, stuck; same M226, M227 and the other
    cave maps). make() -> `arrivals_face_open_ground()` turns any small portal/landing whose arrival square is rock
    and whose back is open ground. Full regen 12:50. Scratch scan left: M101 #1# (Wall stair, played fine) and
    M142 #5# (castle stair).
  - **GAME FIX M256 Moto Benjiro** stood inside the stables' solid block (24, 6): unreachable, so Lion Ch2's
    "Objective: Moto Benjiro, in the stables" (S08, G507) could never be done. Now at the stables' door (24, 10).
    Scratch scan of people standing inside blocks (floor 2+ above their feet), hireling homes excluded, found 18
    more, flavour villagers mostly (open, cosmetic): M103 #7#, M132 #88/89#, M143 #12#, M200 #16#, M206 #14#,
    M229 #13#, M241 #101# (closed-road guard), M256 #12/#13#, M282 #7# (Matsu Hisae) and #92#, M285 #108/#109#,
    M406 #89#, M411 #6-8#.
  - Bot: door pushes are a goto 2 squares past the door (keys are camera-relative; an interior camera turned M260's
    "down" into a push at the wall).
  - **GAME FIX M256 karo's office door** (Lion Ch3) sat inside the Central Dojo's eaves (12, 30) d 0: no way in,
    arriving set you inside the building. Now (12, 32) d 2.
  - Lion Ch2 "Shadow of a Doubt", Ch3 "The Deadly Message", Ch4 "Sorrow's Path" complete; finale Act 1 won
    (path_2_ch*_done*.json). Bot: an arrival scene whose flag was set while you stood on the map (M267 Ijako) is
    triggered by stepping out and back in.
  - **PLUGIN FIX RokuganField party followers**: an empty trail (`f.trail.last()` undefined) threw "index hypot
    does not exist in undefined" every frame - 40,000 exceptions in one Lion run. Guarded (~line 1101).
  - "Wait for night" (M242) and the M268 DARK scenes end lit: the one dark leg shot was the 0.9 s fade-in; leg shots
    now wait 1.3 s after a scene. A transient "image data error: size 0" loop in M265 (a sheet being rewritten
    while the run loaded it) did not recur.
- **Phoenix (path 3)**: Ch1 "The Silent Kami", Ch2 "The Silent Court", Ch3 "The Darkfever" complete
  (path_3_ch*_done*.json). New plugins load clean (ranks: 7 schools, jobs, HUD: 179 objectives; reported to lead).
  HUD: objective #0 showed a Crab line on other saves, boxes overlapped the key hints (lead fixed both).
  - **GAME FIX front-edge strips never fired** (every map, side "f"): the strip sat at z 1 with a 1 m deep box;
    the map border stops the player at ~1.2 squares and a portal needs the body wholly inside. Kyuden Isawa
    (M288)'s whole north side - to M285 and M297 - was dead (Phoenix Ch4 blocked). edge_triggers puts front strips
    at z 2 (back strips were already a square in). Engine-tested M288 -> M297. Full regen 17:00.
  - Bot: autorun scenes far from the arrival point are walked to (an autorun only exists while its spot is on
    screen: M282's Ch2 card at x 76, the landing at 29).
  - Ladder reachability (for the lead's tools/ladders.py; scratch ladderreach.py over my chapter checkpoints): all
    reachable except Crab G255 (M171-M176, beyond the Wall) and G286 (M152) - the lead moved those ladders.
  - Phoenix Ch4 "Howl" complete. **PLUGIN FIX RokuganField floorAt**: after the finale's party swap the leader's new
    model wasn't in the scene yet; the followers' groundTest threw "b3world in null" (RPG3DObject.sk:660) through
    RokuganLook's stage update and the field froze. Guarded (`if( !rp3d["scn"]) return null;`).
- **Dragon (path 4)**: Ch1 "Under the Skin", Ch2 "The Painting", Ch3 "Past Mistakes", Ch4 "The Battle of the White
  Stag" complete, finale Act 1 won (path_4_ch*_done*.json). No game bugs. Bot: a walk-on that fades to black and then
  moves map (M329's mansion door) counts as an exit. Floor-arrow shots for the lead (M142, M160): double chevrons
  read well.
- **GAME FIX autorun scenes (Events.scene, every map)**: the engine runs a trigger-6 event once per spawn, the first
  time its page is live (RPGEvent spawnandran), even when its own cmd_if says "not yet". A scene whose "after" flags
  were set while you stood on the map never played until you left and came back - Scorpion Ch1's memorial garden
  (M345) has no way out: soft-lock after the three conversations. Non-touch scenes now have an empty trigger-0 page
  and the scene page carries the guard as page reqs, so it runs the moment it goes live. Sampled after a full regen:
  Crane dawn, Lion S01, finale F01 all play once.
- **Scorpion (path 5)**: Ch1 "Blood and Iron", Ch2 "City of Masks", Ch3 "Fortunes Lost", Ch4 "The Eve" complete.
  - **GAME FIX cave maps with moved exits** (M384, M397, M405 "w" in MOVE_EXIT): the exit sat on solid rock past the
    cave's west wall - you arrived on the rock top, dropped into the cave, and could never climb back out. Removed.
  - Bot: talk gates that check a worn mask (`wearsMask( "P105", "A148")`) get `equip P105 4 A148` first (Mitsue wears
    the Silk Mask for the temple gatekeeper, as a player would in the menu); would_change follows both branches of an
    if on a non-story value (W from a script, money, items).
  - Fixed my own RokuganBot compile error (a literal newline in a printf) before it cost more than one start.
  - Open: M384's save shrine (#85#) can't be reached from the lava tubes; the Tamori heat tiles keep the party
    under 3/4 HP, so the bot keeps trying to rest there.
- **Unicorn (path 6)**: Ch1 "Fault Lines" complete; Ch2 "The Bell Without a Clapper" runs through Scorpion's lands.
  - **GAME FIX M347 trap**: Shosuro's town (M347) is reachable from the north road (M359) by anyone, but its own
    west gate only opened after Scorpion Ch1 (G861): a Unicorn save that wandered in (M359 -> M347 -> M348 ...
    M354) could never get back out. The gate now also opens after Unicorn Ch1 (G982).
  - Bot: any page with a money op (hirelings, a traitor's purse in the Traitor's Grove M348 that wedged the bot in
    the trees) is one-try side business.
  - Ch2 "The Bell Without a Clapper", Ch3 "The Noblest Blood", Ch4 "Regret" complete. Bot: a flag that keeps
    getting set again (the wax earplugs G999: in at the wind tunnel, out on arrival elsewhere) is a switch, not story,
    after its third flip. Ladder G1010: M400/M401 (the tower) unreachable once Ch3 ends - reported to the lead.
- **Ronin (path 7)**: Ch1 "What's Eating the Eta", Ch2 "The Noble and the Ronin" complete.
  - **GAME FIX M433 arrival in the clouds**: ARRIVE_AT put the way in from M432 at (7, 20) - the cloud sea under
    the bridge (the bridge is z 12-17, invisible walls keep you ON it, nothing gets you back UP): Ronin Ch3 stuck.
    Now (7, 15). The other ARRIVE_AT spots checked: all on their maps' floors.
  - Bot: walk-ons that pushed us back (a rope point: "Too steep to climb untied") get fresh tries whenever the
    story moves.
  - Ch3 "The Village of the Wounded Lion" and Ch4 "The Oracle's Choice" complete (completion flag G1154, set in
    S08_RON4 just before the "- complete" line). **All eight paths are now played through Ch4.**
- 2026-11-12 follow-ups: people standing inside blocks are moved to the nearest open square at their height in make()
  (`people_off_blocks`, hireling homes excluded; rescan: 0 left). M384's save shrine is reachable on the current build.
  Dragon Ch4 completion flag G823. **PLUGIN FIX RokuganVoidCrit.sk**: `RTCutIn` was declared in the file's scope but
  used from ::Rokugan.cutIn - every Void crit threw "index RTCutIn does not exist" (could end the battle); exported as
  ::RTCutIn. Sparring (M001 g199) on the 18:10 build: clean, cut-ins for every school seen. playbot.py gets
  `lead=`/`extra=` and its runs now burst their battles too (RokuganBot botname "pb").
- **GAME FIX companion joins (87 join sites)**: gen_maps join()'s one-line cmd_script (level up + full HP/MP/TP) did
  not compile ("end of statement expected") - the scene stopped right there with "handleerror does not exist"
  (Squeak in the Kaiu tunnels M170, every companion join). Now a plugin call: `::Rokugan.joinReady( pid, lv)`
  (RokuganField.sk) logs "[RT] join Squeak LV30 HP559/559 TP109". Full regen.
- Checked in engine: M151 finale road-marker + chevron + once-only objective (G1230 set); M152 trap stones fire once
  each, hatch visible; M170 exit chevron visible; Void-crit cut-in shot (`-rt shotcut` makes RokuganVoidCrit save
  tmp/rt_shot/cutin_N.raw): _art/preview/bot/cutin_1.png. Note: Natsuko (yari) used "Shell of Stone - Katana".
- 06:30 all ~67 remaining side-cast/hireling sheets reviewed (walk/run/attack): frame fixes for EP389, EP392, EP588, EP673,
  EP1107, EP1112, EP1127, EP1128, EP1140, EP1149 (heads turned away, hats/weapons popping, Hida Veteran morphing).
  Redraws (user "yeah redraw them"): Hida Sachiko - new gen_sprites2d flag club_back (tetsubo behind her head; rig and
  guide redone, procedural sheet in the game meanwhile); Moto Outrider - cleaner spec, procedural sheet in the game
  meanwhile. Both drawing via tools/pixelai_redo.py (detached, log pixelai/redo.log); old frames in pixelai/replaced/.
- 06:15 enemy sheets reviewed (walk/attack: humans, monsters, foe twins) - all fine. Hida Veteran redraw queued after
  Sachiko/Moto (spec said "sage green hair"; now grey-haired balding old man). Redraw progress: pixelai/redo.log.
- 06:40 Sachiko redraw restarted twice: the AI drew her facing left (backwards) from frame 0. Rig idle now plants the club
  behind her and lowers her near hand (gen_sprites2d club_back), spec says "facing right", and tools/pixelai_pick.py
  hand-picks a right-facing candidate. Try 3 is facing right. Queue: Sachiko, Moto Outrider, Hida Veteran (~15 h each
  at the shared ComfyUI pace).
- 06:45 club_back on Hiruma Kage (ch3), Kaiu Engineer, Hida Veteran too: plain sheets + guides redone; Engineer's AI sheet
  (club over face) set aside and queued for redraw after Sachiko, Moto, Veteran.

## 2026-11-11: Agent team - busts
- (bust monitor) Finished the BiRefNet re-export: all 99 bust keys (411 files) re-keyed with the final code. gen_busts.py:
  BiRefNet runs once per variant (key_out fixed_alpha= for the other emotions; was a ComfyUI job per emotion), masks
  cached in _art/busts/_masks. New cut_enclosed_bg() after the mask: (1) background BiRefNet kept above the shoulders
  (npc_akodo_rin's white patch) - flat background colour reached by the colour key's border flood; (2) enclosed gaps
  between hair strands and the neck (Natsuko's ponytail, Rensei, Shizue bath) - only with a face box, ringed by dark
  hair/lineart (a towel or hat top is ringed by light cloth; a flat-white-only rule cut Gendo's bath towel and travel
  hat top - don't); (3) vignette busts whose art fades out above the frame bottom (Doji Sanae, Maho Puppet, Naohida,
  Runner, Gonbei, Yogo scribe...) - bottom-touching exact background colour (median 0-1; white cloth is 3-5);
  (4) a 4 px band of flood-reached white along the silhouette (fringe).
- Scans (before = _art/bust_backup_20261111 -> now): enclosed holes 834k px -> 550k px, and every remaining one checked on
  sheets is a correct cut (background between hair and shoulders), none in faces/bodies; edge white fringe 51k -> 38k px
  (the rest is white lineart in the art). busthole.py's "bite" count flags every bust (open background between hair and
  arm) - not a useful number. New tools/bustfringe.py [key...] [--sheet]: _art/preview/bustcheck_<key>.png (every file on
  magenta, cyan = opaque pure white).
- Bad bust art (tools/bad_busts.json, user "yeah redraw them"): redrawn and exported - Hiruma Ryoichi (cand_s39551,
  waist-up teen scout in lamellar), Wall veteran (round 2 cand_s85203, old tipsy drinker, sake cup; round 1 was a
  close-up), Hida Kisada (cand_s73518, face and beard under the kabuto; the old faceless mempo pick armour_s303 was
  user-OK'd 2026-11-08 - revert in _art/busts/npc_picks.json if wanted), Fishwife (new key npc_fishwife, cand_s83508; she
  borrowed the herbalist girl via RokuganBustGeneric.sk - bustnames wins now). Chins in CHIN_FIX. queue_busts.py --bad:
  real prompts for picked NPCs, bad_busts "look" (weighted, first) and "seed_add", --bad --only X, "fixed" skipped.
  NOTE: a new pick needs `gen_busts.py npc <key>` - stage_export alone re-keys the OLD _art/busts/<key>/neutral.png.
- Open: sayo base/night keep green plant leaves from the source art at the edges; Mitsue's bath variant shows a red
  high-necked top instead of bare shoulders (art); several Lion women share one face (Akodo Rin, Matsu Hanae, Matsu
  Kiku) and Shiba Ashimita/Noboru look alike; Fishwife reads 20s-30s, not 40s. Status: _art/preview/agents/team/busts.md.
- (busts, follow-up per lead) Sayo base/night: the green plant leaves at the frame sides are keyed out - new
  CHARS option cut_edge_hue=(24, 90) -> gen_busts.cut_edge_hue() cuts regions of that hue in the outer 8% of the width
  (her green obi is central) with their lineart, and loose bits (a few tiny stem specks remain against her hair).
  Mitsue bath redone: the base's red half-mask had grown into a red high-necked top; new var_bath.png (review/
  var_bath_v61.png, pale skin to match her face, bare shoulders + towel; old one review/var_bath_old_redtop.png);
  settings kept in her CHARS entry (vseed/vtags/vneg bath). Look-alikes redrawn via bad_busts.json + queue_busts --bad:
  Matsu Hanae (cand_s65236: proud, black bob, gold headband, climbing rope, gold-black armour), Matsu Kiku
  (cand_s56507: shy, braid, cream kimono, lion shoulder guard, paintbrush in the obi), Shiba Noboru (cand_s25863:
  young humble yojimbo, topknot, yari) - all exported, checked on magenta, chins set. Hida Kisada keeps the face version.
  Tried and dropped: the dark-ring "enclosed gap" rule for NPCs (no face box) - it also hits white kimono collars
  ringed by dark cloth (Crab guard, Kaiu sapper, Shosuro Norie). Open: a small white patch of background between Matsu
  Hanae's rope and staff; Fishwife reads 20s-30s; story_1..7 bust sheets when the tester's runs land (only story_0 so far).
- (busts, 2026-11-12) gen_busts.py writes into resource\ atomically (save_png -> tools/atomic_io; faces.json and
  RokuganBustData.sk via save_text). Blocked items done: Kakita sensei, Bandit, Sariko (own keys), Village Herbalist
  (countrywoman). Review of story_0..7: no keying faults in any shown bust; the problem is 265 speakers showing a
  RokuganBustGeneric stand-in. The 11-08 redo queue's ~900 candidates were never collected - copied from ComfyUI
  output/rt_bust_queue into _art/busts/<key>/review/. Own busts picked + exported, most lines first: batch 1 (28:
  Doji Nashiko (+"Nashiko"), Mamoru, Abbot of Osano-Wo, Herald, Innkeeper, Oyuki, ...), batch 2 (28: Akodo Hojiki,
  Akodo Nishi, Kakita Kumpei, Dock-hand, Kitsu Kenshai, Kaiu Naname, Ide Xue, Abbot Munashii, ...); "Young Sayo" uses
  Sayo's bust. Rejected candidates requeued with a look in bad_busts.json: Akari, Gochu, Moto Benjiro (white skull face
  PAINT per cast-looks, no mask), Ume-baa (old), Tomie Cho (old woman), Doji Hayato / Mibu Kagemaro (natural hair),
  Kitsuki Oharu (was a Doji Sanae look-alike), O-Tamai (woman), Mirumoto Hikaru (tattoos). queue_busts.py --bad now
  also queues bad_busts speakers the map scan misses. ComfyUI restarted itself at 13:37; an export running then fell
  back to the colour key - redone. Picking workflow: scratchpad pick sheets, npc_picks.json, CHIN_FIX by eye,
  gen_busts.py npc <key>. ~200 low-line speakers still on stand-ins.
- (busts, 2026-11-12/14) Batches 4-6 of stand-in speakers -> own busts (27 + 31 + 30; Kakita Yumi, Suzume
  grandmother, Doji Aoi redraws picked). Rejected + requeued with a look: Old nun, Kitsune grandmother. Batch helpers
  now live in tools/bustbatch/ (work files in _art/preview/agents/busts/batch/: standins.txt = stand-in speakers by
  line count, skipped.json, picksel<tag>.json, pick<tag>_NN.png, done<tag>.png):
  `mksheet.py N tag [key:Name ...]` -> pick sheets of the next N stand-ins with candidates; `apply.py tag "i:c,i:x,..."
  note` -> npc_picks.json (x = skip); `bash export.sh tag` -> gen_busts npc per key, "FAIL" if the BiRefNet mask was
  unavailable (colour-key fallback), magenta sheet done<tag>.png with chin lines (yellow box = no chin);
  `chin.py key=0.45 ...` -> CHIN_FIX, then `gen_busts.py export <key>`.
- (busts, 2026-11-14) Batches 7-10 done: every person-speaker on the maps now has an own bust (~420 keys). Batch 7
  (28), 8 (34, last playthrough stand-ins), 9 (30) and 10 (~37) from a list rebuilt from the map scan
  (queue_busts.speaker_counts) - monsters/spirits/kami/goblins/naga left out (they shouldn't get a human bust).
  queue_busts.py --bad builds redraw prompts from the bad_busts "look" only, without the speaker label (labels
  misled the model: "Bloodspeaker" -> loudspeakers, "Old nun" -> western habit, "Otomo Shinken" -> a woman) and adds
  negatives (red cross, crab, animal on shoulder, child...). Redraws picked: Old nun, Kitsune grandmother,
  Bloodspeaker, Refugee Herbalist, Auntie Fumi, Otomo Shinken, Akodo Kagehisa, Kakita Miyoshi, Shinjo Miyahana. New
  side-quest givers got own busts: Hida yojimbo, Daidoji courtier, A bo-staff monk (Lion sergeant had one).
  Mieko (dark)/Dark Mieko/Gentle Mieko/Mieko (???) alias to Isawa Mieko; Shadow Hunter to Shadow hunter.
  Redos done (lead): Hida yojimbo without the crab, bo-staff monk older (40s sohei), Refugee Herbalist without the
  red-cross mark, Crane Field Medic (no crosses). Non-human speakers (kami, spirits, demon, goblin, naga, monsters)
  stay on stand-ins on purpose.

## 2026-11-11: Agent team - pushes
- 2026-11-11 ~08:45 push 9c5658a (licensed-demo -> main, 476 files): Rest revives the fallen, Sumai foes face the player,
  Kumpei/Okura boss flipx, bad-frame fixes + club_back sheets, full bust re-export + redrawn NPC busts, test-bot tools.
  Checks: 15 changed tools/*.py compile; story_1 log (after the 07:50 plugin edit) has no compile error; no backups in resource.
- 2026-11-11 16:11 push efdf608 (licensed-demo -> main, 37 files): Crane/Lion path blocker fixes (M210 gate, M212 tide
  loop, M221 table, cave side doors x14, edge strips, M225 cliff, two-exit edges M254/M326/M333/M350, M256 doors +
  Benjiro, arrivals face open ground), side-cast frame fixes, test-bot updates. Checks: 2 changed tools compile;
  story_2 log (after the 11:41 plugin edit) has no compile error; no backups in resource; 0 new boss files.
- 2026-11-11 21:15 push 0b6a2d1 (licensed-demo -> main, 92 files, previous 65456af): floor chevron arrows at interior
  exits (86 interior maps rebuilt), stacked Crab ladders M140/M148/M149, HUD fixes (G1227 1-based, boxes up),
  anim_harmonize.py + install_aisheets/storyplay. Checks: 4 changed tools compile; arrows/arrows2 logs (21:11, after
  the 17:12 plugin edit) load all plugins, no compile error; no backups in resource; 0 new boss files.
- 2026-11-12 03:15 push 1ad7ee2 (licensed-demo -> main, 67 files, previous 0b6a2d1): Events.scene autorun fix (Scorpion
  Ch1 M345 soft-lock), M363 hireling spots, cave exits on rock removed (M384/M397/M405), RokuganField follower/floorAt
  guards, tools/atomic_io.py atomic sheet writes, anim_harmonize updates + 48 harmonized/AI sheets, bot updates.
  Checks: 7 changed tools compile; story_6 log (23:23, after the 22:43 plugin edit) no compile error; no backups in
  resource; 0 new boss files. Harmonize run still going (last install 02:24) - rest goes in the next push.
- 2026-11-13 11:01 push agent: NO release. Version 4 (3c2788b, 11:00, release.py) was already out; dry sync showed only
  NOTES.md changed (lead's release.py notes). Checks: no tools/*.py changed since; no backups in resource; 0 new boss
  files. Newest bot log (story_3, 11-12 08:34) predates the 11-13 plugin edits (RokuganUpdate/Field/Objectives) - no
  engine run has verified them yet.

## 2026-11-11 (evening): Progression v2 - ranks, jobs, kata/kiho, Void, Support (user's design pass)
Spec: `docs/rules/progression-v2.md` (the user's decisions, quoted). Built (lead):
- **Boost -> Void** (1/2/3 VP = damage AND hit x2/x3/x5, no extra hits; RokuganBattle.sk VOID_MUL) and **Call ->
  Support** (battle command names, UI strings, tutorial lines in gen_maps/gen_data).
- **School ranks at Lv 15/30/45/60** (R1 at start): passive skills S700-S727 ("Insight Rank N: <technique>", shown on
  the level-up panel) via the players' lvoption (gen_data RANK_SKILLS / rank_options); effects in the new plugin
  **RokuganRanks.sk** (`::Rokugan.insight(pc)`, `ranked(pc, who, n)`). Sayo keeps her story rank picks. Tamotsu's
  Immovable Hand now needs Rank 5 (was Lv 61). Rank narrations removed (Rensei G369 line, Mitsue's "Insight Rank 2").
- **Dojos teach kata** (user: "instead of school rank ... that way its still a reward"): Goro's Hida dojo M164 ->
  Striking as Earth (G1224) + "back to the Wall gate" pointer (also the Ch2 end objective); the Kakita academy dojo
  M200 -> Kakita's First Stance (G1225).
- **Kata / kiho / tattoos** (tools/kata_data.py, S740-S794, stance conds K070-K124): School commands = the user's
  own weapon attack x mult + a stance for N turns (or the battle); one stance at a time (useKata in RokuganRanks.sk).
  Bushi kata (kata.md lists), Haruki kiho (6), Togashi Yosai kiho (8) + tattoos Tiger/Raven/Centipede/Phoenix at Lv
  15/30/45/60 (user named Tiger, Raven; Centipede and Phoenix are my picks).
- **Jobs** (tools/jobs_data.py, plugin **RokuganJobs.sk**): slot "Job" = Traveler (+0..50% EXP and money, JLv 1-10)
  or the own job J010-J017 (Scout, Duelist, Magistrate, Tactician, Scholar, Shinobi, Merchant, Herbalist); traits at
  job Lv 2/5/8 (J110-J132, + J103 Light Fingers) go in slot "Trait". Enemy jxp = 2. Flee macro X004 honours
  Wave-woman (G1226). Haggle scales store prices while the shop UI is open (check it really blocks).
- Verified by the tester (16:37 restart): both plugins load, no compile error; victory bonus + job grant logged.
- **Field HUD** (user: "a couple boxes in the lower right ... Story: *where to go next* ... Recommended level of
  area"): plugin RokuganHUD.sk; gen_maps `objective_pass` puts `G1227 = n` after every "Objective:" / "Next:"
  narration (list -> generated RokuganObjectives.sk, 179 lines) and `G1228 = N` after a chapter card's "(Recommended
  level N)". Level box = the current map's foe level range (respecting rt_if/rt_ifnot), else the chapter level.
  `-rthud0` hides it. Old saves show no Story box until the next objective line plays. NOT yet seen in engine.
- **Crab Egg Caves levelling** (user: after the nezumi part, caves 8-9 / 10-12 / 13-15 so the Hida road (Lv 18+)
  is reachable): E608-E618 (gen_data, foe_stats), M130-M132 groups gated `rt_if G049`, the old ones `rt_ifnot G049`.
- **tools/level_gaps.py**: per path (tester play logs) the foe levels each chapter offers vs the next chapter's
  recommended level. Every path's Ch1 tops out ~Lv 6-9 while Ch2 recommends 18-20; Crane/Phoenix Ch2 -> Ch3 gap 6-8.
  Same "post-chapter ladder" fix wanted on the other paths.
- **Levelling ladders, every path** (user: "anywhere that there is a spread of levels ... re use dungeons for various
  leveling and sub plot missions"): tools/ladders.py (path, chapter-done flag, [(map, lo, hi)]) for Ch1->2, Ch2->3,
  Ch3->4 and Ch4->finale; gen_maps apply_ladders() adds re-levelled copies of each map's groups (rt_if done flag, or
  rt_if2 when the group already has a path rt_if - new plugin field in RokuganField/RokuganHUD) and turns the old
  groups off (rt_ifnot); clones E619-E947 (`_ladder_foes.json`, stats scaled from the base foe by foe_stats, exp ~
  lv^2). 83 maps, 329 foes. Not covered: Dragon Ch4 and Ronin Ch4 (no completion flag found), Unicorn Ch2 (shares
  the Ojatara maps with Scorpion Ch3). Reachability of each map after its chapter is NOT checked yet (tester).
  HUD fixes after the tester's shot: G1227 is 1-based (0 = none: old saves showed a Crab line), boxes 62 px up off the
  key-hint bar. Crab G255/G286 ladders moved to M140/M148/M149 (stacked; rt_ifnot2), tester found M171-176/M152
  unreachable after their chapters.
- Push 65456af (user "push to git"): all of the above + the tester's front-edge strip fix. ComfyUI was hung since
  13:15; restarted (user-authorized, memory comfyui-restart-ok). Animation agent building tools/anim_harmonize.py
  (palette pass + ComfyUI img2img with reject/retry + self-restart watchdog).
- **Floor arrows** (user: "down arrows in locations where you cant visually see the door, just put them on the floor,
  i struggled in kyuden hida finding the exits ... we will re touch them later with downward looking (texture)
  stairs"): gen_maps `floor_arrows()` in make() for INTERIORS / ROOM_OFS maps paints a vermilion (TORII) arrow
  into the floor blocks one cell inside every exit, pointing at it (inward = most same-height floor). Kyuden Hida
  1F-6F, the dark castle and the town interiors get 1-4 each. Needs a map build (`gen_maps.py <ids>`), not just regen.
- 11-12 03:15 anim_harmonize full batch running (installs; 38 sheets done, 24 frames repainted by ComfyUI, 12 "needs
  eye"; contact sheets _art/preview/agents/anim_harmonize/contact/). Moto Outrider redraw installed; Veteran nearly
  done. Kumpei confirmed facing right in game. tools/atomic_io.py = atomic writes into resource/ (game may run).

## 2026-11-12 (morning): the user's 17-point list (lead)
1. Models: user OK'd downloads -> IP-Adapter Plus SDXL + CLIP-ViT-H weights downloading into ComfyUI models/. The
   ComfyUI_IPAdapter_plus custom node (git clone) was BLOCKED by the permission check ("untrusted code
   integration") - needs the user's OK / a permission rule; animation agent checks core-node options.
2. Jobs: the Job slot was LOCKED (type.json jobslot[0].lock) -> unlocked. Traveler: +1% at JLv1 .. +50% at JLv10
   (the "+10 coffin" was J000's template death-resist option; gen_data's dict override also reset its desc). Jobs
   reworked (jobs_data.py): a job's perks work while worn (JLv 1/4/7, field rt_perks; plugin hasPerk), ONE signature
   trait per job learned at JLv 10, wearable with any job; travelers in the party together share their jobs.
   Haruki's job = Ishiken-do (start VP 1 at JLv1 -> full at 10; trait Ishiken-do = full VP).
4. Kata / kiho cost TP: 4 + learn level / 3 (dojo kata 8). Shugenja now get a TP share (apply_resources SHARES 0.25).
5. Yosai only steps out when the party is over 4, offers whenever there's room. Squeak INILV 10, sticks not doubled
   (Mend-Name 14 MP).
6. Gonta's Sumai: ::Rokugan.soloBegin/soloEnd (companions sit out, hireling allowed).
7. (answered) kata levels: kata_data.py.
8. VP: everyone starts battles at 0 (shugenja still 2); Taint (K026) level blocks that much max VP; save shrines'
   rest calls ::Rokugan.shrineCure() (all ailments but Taint and Down).
9. Weakness memory: enemy rt_species = saved int gvar G2000+ (one per enemy name); plugin RokuganJobs loads / stores.
10. Hiruma katana look still old art -> animation agent.
11. Japanese text: gen_data english_pass (ENGLISH table + blank leftover template strings). NB gen_data load() ALWAYS
    rereads the engine original - use load_built() to edit what was built this run (an english_pass on load()
    wiped the built tables once; restored from the licensed copy, rebuilt).
12. Wall M101: Takakana + a veteran tell her to train in the Egg Caves (after G054, before G216);
    gen_maps ladder_hint_pass puts a "Word on the road" line after each ladder's completion flag.
13. Egg Caves altar scene: box at z 11, wide and 4 m tall; every walk-on scene box is now 3 m tall (slopes).
14. Sayo: R1 her ronin pick (G1039); R2-R4 Forest Killers (Fool's Harvest, Canopy of Knives - Fealty & Freedom
    p.148-150 - and Ghost of the Shinomen, ours), R5 Ronin Duelist The Wind Technique (K059). Ch2/Ch4 picks are story
    only now (RokuganHazard ronin()).
15. Advanced schools at Lv 75/90/100 (MAXLV 100), real 3e schools from the index (1592510476074.txt): Hida Avenger,
    Kenshinzen, Student of the Tao, Master General, Master of the Elements, Shadow-Hunters, Master of the Courts,
    The Machi-Kanshisha (book technique names; effects ours). Skills S800-S823.
16. Spells: every magic attack still swinging a weapon now uses Death of Flame's charge + bolt cast and an element
    hit effect (gen_data, after the AoE pass).
17. Push: after the tester's load check.

## 2026-11-12 (afternoon): resume point
User's 2026-11-12 lists done (lead), pushed 514a03d, data regenerated 14:05 (sparring group added after the push):
- Void: +15/30/50% crit per VP; a Void crit plays a bust cut-in + school shout + 2-turn party gift (plugin
  RokuganVoidCrit.sk; conds K125-K131; shouts table VOID_SHOUT by player rt_school_key).
- Companion school ranks Lv 15/30/45/60 (gen_data COMP_SCHOOLS, skills S830+, effects COMP_FX in RokuganVoidCrit.sk);
  shugenja: 2 spells of their element per rank (rank_spells; Haruki +1 Void). Advanced schools S800-S823 (Lv 75/90/100).
- Kata/kiho cost TP (useKata copies consume); weapon reqs (kata_data REQ, plugin kataWeaponOk + isSkillUseable);
  shugenja kiho NO_STRIKE; Shiba naginata kata S795-S798 (P131); Stand Against the Waves S799 / K136.
- Rank techniques listed under School, greyed (rt_passive). Jobs: curve [30,0] (JLv10 ~1400), capped at 10;
  Monk J018 (Yosai), Scout shared with Squeak; Squeak 0 VP + Taint-immune. Stat curves monotonic.
- Save hang fix: dojo kata / Goro upgrade via STORY_SKILLS flags (G1224/G1225/G292), old ownoptions stripped.
- Story box: chapter cards set it; objective registry tools/_objectives.json keeps numbers stable.
- Crab Ch4 M152 (user's save, stuck): visible cellar hatch + chevron, objective after the breach (G1229), traps fire
  once. Floor chevrons now also on cave exits and invisible walk-on exits on every map (all maps rebuilt 13:55).
- Tools: tools/dumpsave.py SLOT [--shot] (reads / loads a save in its own engine; slot 0 = the user's), float_check.py.
- IP-Adapter: the user cloned ComfyUI_IPAdapter_plus; ComfyUI restarted, IPAdapterAdvanced live. Animation agent is
  adding the reference-image stage to anim_harmonize (Yosai / Natsuko contact sheets first).
- Test fight: M001 group 199 "TEST: sparring" (E998 Sparring Oni ~79k HP, 2x E997 ~33k HP, Lv 60, weak to all).
- Waiting: tester's engine verification of all of the above; bust agent on stand-in speakers (130 own busts now).
- Session crons: f67ff0a3 team check every 2 h, ef8b99f2 push every 5 h, 3ed5a951 resume at 18:11 today.

## 2026-11-12 (evening): Winter Court mini-games (user: "one inspired by links crossbow for the Yumi tourney, then one with the horse race ... tap left then right ... don't make it to difficult, and give a try again option")
- Plugin `RokuganMini.sk` (loaded from plugin.sk before RokuganBot). `::Rokugan.miniGame( "yumi" | "race")` is a
  blocking call from an event script (cmd_script sleeps on the event thread): a full-screen overlay on stageui built
  from white.png rects + labels (no copied art), ticked by addUpdateFunc, keys read with skIsKeyPressed (arrows/WASD,
  Z/Space/Enter, X/Esc), gamepad buttonmask, mouse (best effort), and the bot's virtual keys. Returns 1 won, 2 lost and
  declined "Try again?", 0 could not run. gen_maps `mini_game(kind, won, lost, fallback)` writes the result to G1231
  and branches; 0 -> the OLD narrated outcome (tested with -rtminifail), so the story never blocks.
- Yumi (M142 1F yard, Yasuki Kurako, "Shoot to win."): straw butts 1 (bullseye +1), straw goblins popping over the
  rail 2, paper lanterns 2, crows 3; 24 arrows, 45 s, goal 12 (easy: ~8 hits). Win -> the old win branch (G219 = 1)
  + G1232; lose + "No" -> narrated loss, G219 = 2 (Mutsuye: "You're kind to let him have it"). The other two archery
  choices (lose politely, the goblin's hat) stay narrated. After the contest (G205) an examine spot at the middle butt
  (25, 13) offers "Shoot another round." (Kurako herself has moved up to 4F by then).
- Race = Kitsu Takeo's side story (guests-07-12 "a cavalry race against Lion braggarts"; M142 (21, 9), "Ride with
  him."): three laps (180 m), alternate Left/Right (A/D, pad); same key twice or both at once = stumble (speed x0.55).
  Rival ~6.2 m/s (~29 s); a calm 3 taps/s wins (~23 s), 4.8 taps/s wins in 16 s, 1.25 taps/s loses. Win -> G1233,
  then the Matsu start swinging (battle 17, the old guest-join branches, TAKEO_FIGHT); lose + "No" -> Takeo laughs, no
  battle, the "?" stays so you can retry; fallback -> the old narration + battle. After Takeo joins, his talk menu has
  "Race the yard again." (guest_npc `extra`).
- Flags: G1231 (int, last mini-game result), G1232 (Yumi won with the bow), G1233 (Takeo's race won) in gen_data.
- Test: `tools/minitest.py yumi|race|both [--plan lose,win]` (playbot; kills rpgcobo.exe): -rtmini "lose,win" plays
  one round per entry (lose = idle, win = aims / taps), -rtminishot NAME saves each stage. Shots:
  _art/preview/bot/mini_yumi/, _art/preview/bot/mini_race/. All paths verified in the engine 2026-11-12: lose -> Try
  again -> win (both games), race lose -> No (no battle), forced failure -> narrated, both replays.
- Dialect gotcha: `aidown[aiside ? "right" : "left"]` (a ternary inside an index) always gave "left" - use if/else.
- Not tested: real keyboard / gamepad / mouse feel (the bot's keys only); the mouse mapping assumes stageui fills the
  window (rootview.scale). The engine's key-hint bar (Z Check / Space Jump ...) still draws over the bottom-right.
- 11-12 night: IP-Adapter live (weights hard-linked into C:\AI\StabilityMatrix\Models\IpAdaptersXl - StabilityMatrix's
  extra_model_paths maps "ipadapter" there, not ComfyUI\models\ipadapter). anim_harmonize.py "ref" pass: reference =
  stand frame 0, weight 0.6 linear, original head + weapon composited back. badframes.py bug fixed: it compared only
  frames 0-19 to detect a redrawn sheet and reverted later-frame changes (100 harmonized sheets re-installed).


## 2026-11-13: pushes go through tools/release.py (title Update / Verify)
- Push = `python tools/release.py <message file>`: sync_licensed, version.json +1, rt_manifest.json (CRC32 as signed-int TEXT - the engine's JSON reader clamps big/negative numbers), commit, push origin licensed-demo:main. Version 4 = 3c2788b.
- In game: title "Update / Verify" (gen_data title_update_entry -> RokuganUpdate.sk). Manages only _tools/rpgcobo-tool/ (engine file security: writes only in its folder, never exe/dll/bat/ps1/sakana.proj); records the install in _tools/rpgcobo-tool/rt_version.json + rt_manifest.json (gitignored). URLs carry ?t= to skip raw.githubusercontent's 5-min cache. sakana.proj allows https raw.githubusercontent.com.
- Test: `-rtupdtest fast|verify|fix` (run in D:/RokuganTraveler-licensed; the dev folder has no version.json, so the button refuses there). Engine test windows sit black while they scan - warn the user first.


## 2026-11-14: traveler select, chapter-end objectives, Journal, update notice (versions 9-11)
- One save walks all 8 roads: each path's end marker (finale_gate) sets G1234-G1241 (road walked), offers a save and opens path_menu() (gen_maps; loop on event-local Y - only W-Z exist). Walked roads are refused and marked with their level; option 9 = the finale once all 8 are walked (::Rokugan.pathFinale, then fJoinAll on M444). ::Rokugan.pathBegin empties the party, clears G608 (Yosai), G1230, G1227.
- chapter_end_pass (gen_maps, before objective_pass): 12 chapter ends had no objective (the user's Crane save was stuck after Ch1). Crane Ch1 -> Ch2 also has once-scenes for old saves (G1242/G1243).
- Journal: RokuganJournal.sk (menu_journal, menu_item.ui), RokuganJournalData.sk (journal_pass from ladders.py). Tracked entry = G1244, shown in the HUD Story box. Side quests are a hand table (JOURNAL_SIDE): add new side stories there.
- Title: yellow 'Update available' line when GitHub's version.json is newer (RokuganUpdate.sk updNoticeCheck).
- The engine runs ONE instance at a time (a second exits with code 7): test launchers must wait for a gap (scratchpad shotrun.py pattern). -rtmenuhold keeps a -rtmenutest menu open 6 s for -rtshot.
- NEXT (user): connect the overland maps with more routes (from the world map), scatter caves matched to each route's difficulty, then check every cave has a full walkable block to every object.


## 2026-11-14: side quests + job slots (version 13)
- gen_maps SIDE_QUESTS: (key, road, title, giver map/x/z/sprite/name, opens, hunt map, gids, texts, zeni, job). Flags G1250+3k (taken/hunted/done; room for 16). One giver NPC per spot carries its whole chain. Hunts = arrival scenes on the hunt map (lost fight clears the flag: retry). Journal reads JOURNAL_QUESTS (journal_pass).
- Generic jobs: jobs_data GENERIC_JOBS (J020 Yojimbo, J021 Courtier, J022 Sergeant, J023 Sohei; rt_unlock = the quest's done flag; ensureJobs gives them to every traveler).
- Job slots: jobs_data JOB_SLOTS = Job + Trait 1-4; traits jobslotbits 30; RokuganJobs fitJobSlots resizes old saves.
- Next batch: chains for Dragon, Scorpion, Unicorn, Ronin (and more generic jobs).

## 2026-11-14: tester - regression pass (versions 12-14)
- Passed: 8 new games (road begins, start maps); main menu open/close x8 leads, plain + via Equipment; updater fast/verify
  = 0 to fetch in RokuganTraveler-licensed; title "Update / Verify" message + choice + Back; end-of-road marker -> next
  traveler (party = them only, road marked, refusal of walked roads, locked finale text); all 8 walked -> M444 join;
  Journal tabs + tracking -> HUD Story box; side quests (Crab chain whole incl. J020; first quest on Crane / Lion /
  Phoenix); Job menu 5 slots; generic jobs reach every traveler.
- Reported: menu option 9 (finale) not templated (RPGEvent tmplmap stops at text7); SKView "link" exception on screen
  resize (code-made root views); Job menu bare resistance zeros.
- Engine launches now go through tools/engine_lock.py (wait until no rpgcobo.exe, retry exit 7, kill own PID only).
  Details: _art/preview/agents/team/tester.md.

## 2026-11-14: connecting routes, side caves, cave walkways (version 15)
- gen_maps ROUTES (after apply_ladders): 8 road maps M470-M477 between hubs of different paths, along world-map roads: Hoshi-no-Ichi - Yasuki Yashiki, Kudo - Floating Flowers, Shiro Akodo - Wounded Lion, Wounded Lion - Zumiki, Cakon - Kyuden Doji, Kamatori - Dragon mountain town, Buried Leaves - Dragon mountain town, Pleasant Eaves - Kyuden Bayushi. route_hub() wraps each hub builder and adds an edge portal (_edge_spot picks a dry, level spot on a free side).
- Gates: each route end needs flag G1300+ (ROUTE_GATES -> generated plugin RokuganRouteData.sk). RokuganField routeFlags (RPGStage.launch wrapper) opens an end while one of its travelers leads, once their road is walked, or when all 8 are walked. Closed end = mark_exits barricade + guard (portal "closed_msg").
- Encounters: tier = ladder band (ladders.py position: 1 after Ch1 ... 4 after Ch4); rows copied from both paths' re-levelled ladder groups (no new foe ids). Road-stones give each end's danger.
- Caves M480-M489 (1-2 per route, 1-2 bands harder than the road, Lv 22-50), route_cave(): 5 chambers, 4-wide tunnels, chests by tier; cave_sprawl grows galleries + shrine.
- Cave walkways (user: a full block to every object): walkcheck.py --wide (2x2 body) and --caves; walkcheck.widen() runs in gen_maps.make() for every cave map: cuts the narrowest path to each missed object to 2x2 (lowers rims, removes rubble, steps a chest out of a one-cell gap). All caves pass --wide; walkcheck now seeds portal landings too.
