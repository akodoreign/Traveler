# Enemies of the Empire (L5R 4e) — new foes for Rokugan Traveler

Source: *Enemies of the Empire* (AEG, L5R 4th edition), read 2026-11-14 for the new-foe batch (user: "generate a whole
new batch of types of monsters and human foes, new types (based on all the reference books)"). *The Way of the
Shadowlands* (1e) is a scan without a text layer; its creatures overlap EotE ch. 11.

## What the book has, and what the game already had

| EotE chapter | Creatures | Already in the game |
|---|---|---|
| 1 Beasts of Rokugan (p.11-18) | ape (ozaru), badger (anaguma), bat, bear, boar, cat, crane, crocodile (wani), eagle, elephant, flying squirrel, fox, goat, hare, monkey, sharks, octopus, snakes, stag, tiger | boar, bats, wolves, snow bear, snakes |
| 2 Bloodspeakers (p.19-34) | cult cells, maho | acolytes, adepts, maho-tsukai |
| 3 Kolat (p.35-52) | assassins, agents | Kolat agent, Kolat-paid brigand |
| 7 The Nothing (p.129-149) | lesser / greater shadowspawn, shadowbeast | shadow-in-black, fear shade |
| 8 Oni (p.151-174) | named oni lords and their spawn | several oni and spawn (bosses) |
| 9 Five Ancient Races (p.175-196) | kenku, ningyo, trolls, tsuno, zokujin | trolls, tengu crow-warrior |
| 10 Ronin (p.197-212) | bandit lord, disavowed assassin, disgraced yojimbo, pirates, ronin shugenja, wandering swordsmen | hungry ronin, sword-for-hire, wave-man duelist |
| 11 Shadowlands Beasts (p.213-238) | aka-name, Dokufu spawn, goblin breeds (berserker, chucker, shaman, sneak, warmonger), hanemuri, kumo, mamono, monstrous plants (fudoshi, lava tree, takesasu), nikumizu, obake, ogres (free ogre, ogre mage / hag), onibaba, onikage, sanshu denki, trolls, umibozu, yamauba, tsumunagi | goblins, warmonger, kumo, lava tree dryad, onikage, ogre, troll, umibozu |
| 12 Spirits (p.239-258) | kitsune, buruburu, hannya, mokumokuren, bakeneko, mujina, orochi, baku... | gaki, yurei, kitsune guides |
| 13 Undead (p.259-279) | ghul, harionago, hyakuhei, nukekubi, nuppeppo, plague zombie, gaki kinds | zombie, gaki, risen dead |

## The new batch (tools/new_foes.py)

38 types, each where the book puts it and at that place's level:

- **Connecting roads, Lv 8-11:** Anaguma Badger, River Wani, Aoizame Shark (coastal shallows), Desperate Fisherman,
  Scourge of the Seas (pirate), Bakeneko, Mujina, Ronin Shugenja, Monkey Troop, Banished Duelist.
- **Connecting roads, Lv 24-25:** Tora Tiger, Bandit Lord, Ozaru, Disgraced Yojimbo.
- **Side caves, Lv 23-48:** Tsumunagi (blood eel), Aka-name, Sanshu Denki (muck monster), Nukekubi, Feral Ningyo,
  Fudoshi (tanglevines), Goblin Sneak, Goblin Chucker, Conspiratorial Madman, Kolat Master Killer, Nikumizu (heart
  grubs), Ghul, Goblin Berserker, Hanemuri, Ogre Hag, Free Ogre, Takesasu (stinger plant), Zokujin Miner, Zokujin
  Stonehunter.
- **Deep Shadowlands (post-game), Lv 62-66:** Onibaba, Tsuno Ravager, Lesser Shadowspawn, Hyakuhei, Plague Zombie.

Left for a later batch: the oni lords (boss material), kenku swordsmen (too close to the tengu), harionago, nuppeppo,
hannya, mokumokuren, buruburu, Dokufu spawn, obake, yamauba, the larger beasts (elephant, eagle).

Sprites are placeholders (hue-shifted copies of the nearest sheet, `ph_<key>.png`, EP2600-EP2637) until drawn.
