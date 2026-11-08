# PRODUCTION — Crane Ch3 · "The White Squid"

**Traveler:** Kakita Rensei · **Lv** 30–35 · **Outline:** `scripts/crane-ch3-the-white-squid.md`
**Flags set:** `tessai_ally`, `ryohei_released`, `tadanobu_letters`, `katsuo_alive`
**Maps:** `crane_port`, `ship_deck`, `cove_fort`, `temples_of_sun`, `storm_sea`, `heavenly_sheen_isle`,
`squid_shrine_1–2`
**Battles:** `b_midboss_chihaya`, `b_storm_yosuke`, `b_boss_katsuo` (fake-charm gimmick, + Ryohei if not released)
**Ship:** coastal travel unlocks in S01. The ship cabin works as an inn (rest, save, party swap).
**Storyboard:** `storyboards/crane-ch3.md`. Sea nodes are revealed in order: Cove Fort → Temples of the Sun → the
south islands.

---

## S01 — A Head for a Gift
MAP: `crane_port` · TRIGGER: start
NARRATION: The Crane coast. A tribute meant for the Emperor's own hands was taken at sea. The Crane do not take embarrassments lightly.
LADY SANAE: The White Squid pirates took the tribute. A lacquered screen for the Emperor's winter palace.
LADY SANAE: The Emperor will receive a new gift, Rensei-san.
RENSEI: What gift, my lady?
LADY SANAE: The pirate captain's head.
(A ship. A crew. A grizzled SHIP'S MASTER who looks at Rensei the way a horse looks at a new rider.)
LADY SANAE: You are a captain now.
RENSEI: I've never been on a boat.
LADY SANAE: Then you'll learn, the way Kakita learn everything. Perfectly, and while terrified.
### On deck (first sailing)
RENSEI: (gripping the rail, grey) Is it supposed to… move like this?
SHIP'S MASTER: It's the sea, captain.
RENSEI: Yes. Yes, of course. (beat) All of it?
SHIP'S MASTER: (deadpan) Mostly the bits underneath, captain.
### Rival (story clock)
LADY SANAE: One more thing. The Imperial magistrate Otomo Shinken is also hunting these pirates.
LADY SANAE: If she reaches them first, the Emperor gets the credit and the Crane get nothing. (beat) Not that I'd mind. But the court would.
[UNLOCK] Ship travel (coastal)
[SAVE]

## S02 — One Ship, Four Places
MAP: `crane_port` (docks) · TRIGGER: investigate
### Dock NPCs (path actions → the four brothers)
| NPC | Line | Info |
|---|---|---|
| Fishwife | "They struck Shimo-ura and Kitahama on the same morning. Forty ri apart!" | *Discern:* "Four ships, all the same, all painted white." |
| Drunk sailor | "Ryohei the Eldest. Fights with a little stick-and-chain. Deadly." | *Eavesdrop:* "Yosuke the Bold drinks in the south islands." |
| Net-mender | "Chihaya the Quick — walked along an oar like a road." | — |
| Charm-seller | "White Squid charms! Bless your boat! (whispering) Theirs work. Mine don't." | *Discern:* "The pirates' charms come from 'the White Brother' — Katsuo — at a shrine." |
(A Crab lord in damp silk elbows through the crowd: YASUKI TESSAI.)
YASUKI TESSAI: You're hunting the Squid? So am I. They've cost me three ships and my best cook.
YASUKI TESSAI: Ally with me. I bring a second ship and gold. I want the loot.
> CHOICE "Tessai"
  - "Ally with him." → [SET tessai_ally] (his ship fires a broadside in the storm battle; he claims two of the
    shrine's loot chests)
  - "Go alone." → (no help at sea; you keep all the loot)
      RENSEI: Forgive me, Tessai-sama. The Crane prefer to owe no one.
      YASUKI TESSAI: (laughing) The Crane owe *everyone*. They just pay in compliments.

## S03 — Chihaya the Quick (mid-boss)
MAP: `cove_fort` · TRIGGER: sail to the first island
(A cove fort. A barefoot ronin woman balancing on a mooring rope over the water, laughing: CHIHAYA.)
CHIHAYA: A Crane! On a *boat*! You look like a heron in a bathtub!
RENSEI: (green) I'm told the bits underneath are the problem.
[BATTLE b_midboss_chihaya]
### GIMMICK tutorial — fake charms
"Chihaya wears a **pirate charm** (see her status icons). **Steal it** or **break it with Suki** to strip its buff."
### Barks
- CHIHAYA: "You fight like a painting, Crane! Pretty and *still*!"
- RENSEI (Iaijutsu: Strike): "Paintings don't miss."
- Charm broken: CHIHAYA: "My charm! It was guaranteed!"
(Defeated, she sits on the rope, dripping, unconcerned.)
CHIHAYA: Take me in if you like. Ryohei'll buy me back. He always does.
(In her sash: letters. Signed by a patron. Lion.)
RENSEI: (reading) "…Matsu Tadanobu." A Lion. Paying pirates to bleed the Crane.
[SET tadanobu_letters] [ITEM +Tadanobu's Letters]

## S04 — The Temples of the Sun
MAP: `temples_of_sun` · TRIGGER: bring a charm to the Asahina
(An Asahina temple of white wood and sunlight. A shugenja-priest examines Chihaya's charm and goes very pale.)
ASAHINA PRIEST: It's false. But it *works*. It's made with — (lowering his voice) — with Bloodspeaker techniques.
ASAHINA PRIEST: The craft of Asahina Yajinden. Iuchiban's artificer. One of *ours*, long ago.
ASAHINA PRIEST: Someone of his line is making these. (beat) The Asahina would be grateful if this… stayed in the family.
RENSEI: (a long pause) …Lady Sanae would understand that request.
[ITEM +Asahina Ward-paper (accessory: halves the fake charms' buffs on nearby enemies)]

## S05 — Gathering Storm
MAP: `storm_sea` · TRIGGER: sail south
(Night. A storm. Waves over the bow. A sailor screams and points: a vast coil rising in the black water — and
sinking again.)
SAILOR: The Orochi! I saw it! I *saw* it!
SHIP'S MASTER: You saw a wave, boy.
SAILOR: Waves don't have *eyes*!
(Through the rain: a white ship, and a ronin at its prow, laughing into the storm: YOSUKE THE BOLD.)
YOSUKE: Crane! You picked a fine night to die!
[BATTLE b_storm_yosuke]
(Yosuke's ship veers away into the dark.)
RENSEI: (soaked, clinging to the mast; to the ship's master) …Is it always like this?
SHIP'S MASTER: No, captain. Usually it's worse.

## S06 — Island of the Heavenly Sheen
MAP: `heavenly_sheen_isle` · TRIGGER: dawn landfall
(A shining white-sand island. A Mantis bushi with a nunchaku waits alone on the beach under a white flag:
RYOHEI THE ELDEST, tactician, tired.)
RYOHEI: Captain Kakita. I'm the eldest. Ryohei.
RYOHEI: My brothers will die for the White Brother. I'd rather they didn't.
RYOHEI: Give me safe passage and I'll give you the shrine's back door. And my brothers' surrender.
> CHOICE "Ryohei's offer"
  - "Accept." → [SET ryohei_released] (the back door: enter at the inner shrine's save point; Katsuo fights alone;
    Sanae will ask whose head he brought)
      RENSEI: Go. Take your brothers. Leave Katsuo to me.
      RYOHEI: (bowing) You're a strange Crane. I'll tell my children about you.
  - "Refuse." → (Ryohei fights beside Katsuo)
      RENSEI: You've had your brothers raid forty villages. No.
      RYOHEI: (sighing, unwinding the nunchaku) …I thought you'd say that. You have that face.

## S07 — The White Squid Shrine (dungeon)
MAP: `squid_shrine_1–2` · TRIGGER: enter
(A sea-cave shrine. Charm-workshops: brushes, bones, ink. Tide-pools glowing faintly. Deep in the water, something
very large and white moves, and stops.)
[IF tessai_ally] YASUKI TESSAI: (eyeing the loot) My cook's knives! Those are my cook's knives! (two loot chests
are his) [END]
[SAVE] (the shrine's outer gate)
[SAVE] (the inner door — the back-door entrance arrives here if `ryohei_released`)

## S08 — Katsuo the White Brother (BOSS)
MAP: `squid_shrine_2` · TRIGGER: enter the inner shrine
(An albino in white robes, eyes pink as coral, painting a charm with blood: KATSUO.)
KATSUO: Every charm I make is a lie.
KATSUO: (holding one up, smiling) And look how well they work. Believing is the only magic left, little Crane.
RENSEI: (drawing) Then believe this.
[BATTLE b_boss_katsuo]
### GIMMICK — fake charms
"Each turn Katsuo hands a new **charm** to a pirate (or himself): +attack, +evasion, or regeneration.
**Steal** charms, or **break** them with Suki. A **shattered** charm stuns its wearer for a turn."
### Barks
- New charm: KATSUO: "Here, brother. Be brave. It says so on the paper."
- Charm shattered: KATSUO: "You don't believe in it? How *rude*."
- Maho (pays HP; Taint): KATSUO: "My blood is very good ink."
- At 25%: KATSUO: "Kill me and the charms keep working. Isn't that funny? Lies outlive their makers."
- RENSEI: "Then I won't kill you."

## S09 — The Head of My Enemy
MAP: `crane_port` · TRIGGER: after the boss
(The order was the captain's head. Rensei stands over Katsuo. Then he sheathes his sword, binds the albino's wrists
with his own sash, and walks him onto the ship.)
[SET katsuo_alive]
(Back at port. The Imperial magistrate Otomo Shinken arrives with a fleet, just too late, and takes the credit very
gladly.)
OTOMO SHINKEN: The Emperor's justice prevails! Thanks to my diligence!
RENSEI: (bowing exactly as deep as protocol requires) Indeed, magistrate.
(Sanae's quarters. She reads Tadanobu's letters. A very small, very satisfied smile.)
LADY SANAE: You were told to bring a head.
RENSEI: I brought a confession, my lady. (beat) It has a head attached.
LADY SANAE: (laughing for the first time in the game) …Adequate.
RENSEI: (startled) My lady?
LADY SANAE: I've heard your father uses that word. I thought you might like to hear it from someone who means it kindly.
LADY SANAE: And the Emperor's screen? RENSEI: In the hold, my lady. (beat) Slightly damp.
[IF ryohei_released] LADY SANAE: And the brothers? RENSEI: Gone home, my lady. To raise children who'll tell stories about a seasick Crane. [END]
[CHAPTER COMPLETE]
### Chapter complete card
**"The White Squid" — complete.**
Journal: *Four brothers, four white ships, and a charm-maker who made lies work. Rensei learned to sail, refused to
take a head, and found a Lion's signature behind the piracy.*

---
## Travel Banter unlocked by Crane Ch3
### TB-crane3-a "Seasick" (Rensei + Natsuko)
NATSUKO: I heard you threw up over the side for three days.
RENSEI: Two and a half. (stiffly) On the third I threw up over the *other* side. For variety.
NATSUKO: (laughing) That's the most Crab thing you've ever done.
### TB-crane3-b "Adequate" (Rensei + Shizue)
RENSEI: Lady Sanae said "adequate" to me. And meant it as praise.
SHIZUE: The word was the same as your father's.
RENSEI: Yes.
SHIZUE: So it was never the word. It was who said it.
RENSEI: (long pause) …That's very annoying to realise.
SHIZUE: Most good moves are.
