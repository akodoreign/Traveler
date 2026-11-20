# Combat pop-ups

The opening card uses the enemy's current display name and the authored encounter epithet. Its text is set before the card is attached. The card and both labels fade together, then leave the picture layer. The original flash, shake, thud, stance and hold timing are preserved.

## Boss title ownership

The title register is in the game resource tree at efx/battleui/boss_titles/index.json. Match by enemy data ID where possible. The original English-name lookup also covers matching encounters added by event scripts. Each entry carries a localized epithet table and an optional backdrop name. Keep the title layer text-free in art files so one art treatment works for every language. The distinct designs for the Nezumi Shaman, Orochi, Okura, Kommei, Tsukakoro, Yasurugi and Nashiko stages use tailored pigment and original emblems. Remaining registered encounters use a shared ink treatment. Rebuild the backdrops with tools/gen_boss_title_backdrops.py.

When a title appears empty, first identify the owning event and inspect the source content. The old E106 entrance reached its expected 300 ms fade but faced a genuinely blank EP450 PNG. All 46 banner PNGs in the licensed snapshot share the same content. Earlier notes and tools/gen_bossart.py preserve the old brush and epithet design. The licensed sync skips the old placeholder asset paths, so the new backdrops live outside those paths. Battle skill-name notices and the Void critical cut-in already use live labels with their own content and stay on those paths.

## Daylight review

On M811, add E106 to the existing mixed-foe fixture. The opening card should show Nezumi Shaman and Name-keeper of the Egg Caves throughout the visible fade and hold. Confirm the card fades as the first turn begins, then try a second named boss with a different crest, an ordinary Kappa group, a skill-name notice, and a Void critical. In Japanese mode, confirm the registered epithet changes and the card still uses the enemy's game display name. The archive contains an English fallback for epithets that have no Japanese entry yet.
