# Production Scripts — format spec (v1)

The **final, line-by-line dialogue** for every chapter, written to drop straight into RPG-Cobo map events. The
`scripts/` folder holds the approved scene outlines. This folder holds the full text.

**Order of work (user, session 2):**
1. All chapter dialogue: the production pass, applying `OCTOPATH-FIT.md` §3.
2. Side stories for the 27 guests.
3. Boss stat sheets.

## File layout
One file per chapter: `production/<traveler>-ch<N>.md` (e.g. `crab-ch1.md`), plus `finale.md`.

Each file has:
1. **Header**: chapter id, traveler, recommended level, flags read and set, maps used, battles used.
2. **Scenes** `S01, S02…`, each with:
   - `MAP:` the map id · `TRIGGER:` what starts it (enter area / talk / after battle)
   - dialogue lines: `SPEAKER: text`. **One text box ≈ 2 lines of ~45 characters** (Octopath box size). Longer
     speeches are split into several lines with the same speaker.
   - `(stage direction)` in parentheses: camera, emotes, SFX.
   - `> CHOICE "label"` then indented options `- "Option text" → …`
   - `[SET flag]` / `[IF flag] … [ELSE] … [END]`
   - `[BATTLE id]`: id from `rules/bosses.md` (the stat sheets: work item 3)
   - `[ITEM +name]` / `[GUEST +name]` / `[PA type target]` path-action hooks
   - `[SAVE]`: save-point placement
3. **Town NPCs**: a table per map: NPC · default line · **Discern/Eavesdrop/Inquire info** (what the path action
   reveals) · **Sumai/Duel/Charm/Bless/Pilfer/Barter result**.
4. **Travel Banter**: the optional inn conversations unlocked by this chapter (only when the named travelers are
   in the party).
5. **Chapter complete** text (Octopath's chapter-end card) and the summary line that appears in the journal.

## Writing rules
- **Names: family name first, and often** (user rule, 2026-10-19; the setting is lightly based on Japanese and Chinese
  history). Speaker labels are always full (`HIRUMA NATSUKO:` in new scripts; the generator maps older `NATSUKO:`
  labels to the full name). Narration names a samurai in full at the first mention in each scene. In dialogue,
  samurai address each other by family name (+ -san/-sama: "Hiruma!", "Kakita-san"). Given names alone are for
  family, close friends, children and commoners. Ronin, commoners and nezumi have one name.
- **Original dialogue only.** Never reuse adventure or rulebook text (sources are for facts).
- Voices:
  - **Natsuko:** gallows humour, short.
  - **Rensei:** over-formal until he forgets.
  - **Gendo:** dry, mutters, precise.
  - **Shizue:** go-metaphors, calm.
  - **Haruki:** gentle, counts on his fingers, self-blaming.
  - **Mitsue:** light, layered, never quite honest about herself.
  - **Tamotsu:** warm, jokes, sincere underneath.
  - **Sayo:** cheerful, irreverent, plain words.
  - **Lords:** few words (the Rank-1 rule).
- System terms in ASCII: **Bo, Suki, VP** (memory: ascii-terms).
- Recruitment: if the chapter's traveler is recruited while others are in the party, the others are present but
  silent except in Travel Banter (Octopath I rule).
