# PRODUCTION — Unicorn Ch3 · "The Noblest Blood"

**Traveler:** Ide Tamotsu · **Lv** 30–35 · **Outline:** `scripts/unicorn-ch3-the-noblest-blood.md`
**Flags read:** `rin_joined`, `camps_fed`, `nihime_told` · **Flags set:** `shahai_trusts`, `daiyu_state`
(comforted / shattered), `mirumoto_terms` (jade / honour), `karasu_joined`
**Maps:** `star_field`, `shiro_iuchi_tower`, `iuchi_woods`, `mirumoto_camp`, `jade_mines_1–3`
**Battles:** `b_tower_servants` (silent), `b_mine_dead_a/b`, `b_boss_mine_guardian`
**Set-piece:** **Covered Ears** (wax earplugs). While on, spoken path actions are disabled and dialogue appears as
handwritten notes (shown in a brush font, in `NOTE:` lines). Random encounters in the tower are silent battles.
**Storyboard:** `storyboards/unicorn-ch3.md` (Mirumoto camp hub table; tower = 3-floor silent dungeon)

---

## S01 — The Eight-Pointed Star
MAP: `star_field` · TRIGGER: start
NARRATION: A field outside Shiro Iuchi. An eight-pointed star burned into the frost. And at its centre, a messenger
in Seppun colours who will never deliver his message.
(Akodo Rin stands at the edge of the burned star, very pale.)
AKODO RIN: A Seppun courier. Royal blood. (beat) It was meant to be me.
TAMOTSU: (gently) It wasn't you. Because of you. Because you were careful.
AKODO RIN: Because *you* were careful.
(A man in a white porcelain mask with faintly glowing eyes kneels by the body, sniffing the air: IUCHI KARASU.)
IUCHI KARASU: (deadpan) Regret. My great-uncle Kurosho has summoned the Shuten Doji of Regret.
IUCHI KARASU: Its servants sing. If you hear them, you belong to it.
IUCHI KARASU: I was a prisoner in the Shadowlands for six months. I never once regretted anything.
IUCHI KARASU: (beat) Except leaving. And now, coming back.
[GUEST +Iuchi Karasu] [SET karasu_joined] (skills: Jade Strike — anti-Taint, 2 uses; passive: deadpan quips)
(G-1: Karasu is story-locked as the active guest this chapter; Rin waits on the roster.)
### SYSTEM — Covered Ears
"Use the **Wax Earplugs** to **cover your ears**. Possession-by-hearing can't touch you — but **spoken path
actions are disabled**, and you'll talk in **written notes**. Uncover at safe points."
[SAVE]

## S02 — The Girl in the Tower (silent set-piece)
MAP: `shiro_iuchi_tower` · TRIGGER: approach the castle, ears covered
(Shiro Iuchi's servants wander the halls, swaying, humming the same tune. The party moves through silently.)
NOTE (Tamotsu to party): DON'T STEP ON THE HUMMING ONES. THEY'LL REMEMBER IT.
NOTE (Karasu): AGREED. ALSO MY FEET ARE COLD.
[BATTLE b_tower_servants] (silent — possessed servants; break them to wake them, not kill)
(The top of the tower: a barricaded door. A small hand pushes a note out underneath, in a child's writing.)
NOTE (Shahai): ARE YOU REAL OR ARE YOU SINGING
NOTE (Tamotsu): REAL. I BROUGHT RICE CAKES.
(Pause. The door opens a crack. A small hand takes the rice cake. Then the door opens wider: IUCHI SHAHAI, nine, wax
in her own ears, a kitchen knife in her other hand.)
NOTE (Shahai): YOU'RE THE FAT EMISSARY. FATHER SAYS YOU'RE NICE.
NOTE (Tamotsu): YOUR FATHER IS VERY WISE. (beat) ALSO I'M ROUND, NOT FAT.
NOTE (Shahai): (a small smile, the first in days) OK.
[SET shahai_trusts]
(As they lead her down, Shahai hums, very softly, without noticing — the same tune as the servants. Karasu notices.)
NOTE (Karasu, to Tamotsu, small): SHE'S HUMMING IT.
NOTE (Tamotsu): I KNOW. NOT NOW.

## S03 — The Lord in the Woods
MAP: `iuchi_woods` · TRIGGER: search for the daimyo (ears uncovered — the woods are clear)
(A sunlit clearing. Animals everywhere: woodchucks, a fox, sparrows on his shoulders. IUCHI DAIYU sits in the middle of them.)
IUCHI DAIYU: The woodchucks told me everything, Tamotsu. Everything my karo wouldn't.
IUCHI DAIYU: The war. The camps. The salted fields. My father.
IUCHI DAIYU: (broken) Twenty years I listened to animals so I wouldn't have to listen to men.
> CHOICE "Daiyu"
  - "Comfort him." → [SET daiyu_state comforted]
      TAMOTSU: (sitting down in the grass beside him) You're listening now, my lord. That's what counts. Animals tell the truth. So will you.
      IUCHI DAIYU: (wiping his eyes) …I'll tell the truth. Gods help me. I'll tell all of it.
  - "Tell him the whole truth about Kurosho." → [SET daiyu_state shattered] (Honor +1)
      TAMOTSU: Your father summoned a demon, my lord. With a Seppun boy's blood. He's in your castle now.
      IUCHI DAIYU: (very still; a woodchuck climbs into his lap) …Then I am the son of a monster.
      TAMOTSU: You're the son who'll stop him.
[IF shahai_trusts] (Shahai runs into the clearing and throws herself at her father. He holds her. The animals scatter.) [END]

## S04 — Ride In Deaf
MAP: `mirumoto_camp` · TRIGGER: seek the Dragon army
(A Dragon war-camp. Blunt, resentful generals: MIRUMOTO TSUKARU and MIRUMOTO TABEZU.)
MIRUMOTO TSUKARU: A Unicorn family feud. Shugenja against shugenja. Why should three thousand Dragons bleed for it?
MIRUMOTO TABEZU: And you want us to ride in with *wax* in our ears.
TAMOTSU: I want three thousand Dragons to ride *out* again, general. The wax is the cheap part.
[IF gendo_in_party]
GENDO: (stepping forward, speaking in the clipped Dragon way) General. It's not a feud. It's a Shuten Doji. Regret. It'll be in your camp by the next moon.
MIRUMOTO TSUKARU: (squinting) …A Kitsuki. With gaijin glass on his face.
GENDO: And excellent hearing, general. For now.
[END]
### Barter / persuasion
[PA Barter Tsukaru] (supplies, a trade route through the valleys) + Etiquette
> CHOICE "Their price"
  - "Promise them the mine's jade." → [SET mirumoto_terms jade] (they ride; a trade cost later)
      MIRUMOTO TABEZU: (grinning) Jade, you said? (to Tsukaru) …I *like* jade.
  - [IF Honor ≥ 3] "Appeal to honour alone." → [SET mirumoto_terms honour] (free)
      TAMOTSU: There are children in that castle with wax in their ears, general. That's all I have to offer.
      MIRUMOTO TSUKARU: (a long silence; then he takes the wax) …Saddle up.
(The demonstration: Tamotsu has the Dragon officers put the wax in, then claps behind their heads. Nobody turns.)
MIRUMOTO TSUKARU: (pulling one plug out) …What?
TAMOTSU: (laughing) Exactly.

## S05 — The Jade Mines (dungeon)
MAP: `jade_mines_1–3` · TRIGGER: they need jade for the fight to come
NARRATION: The jade mines. Silent for months. The miners didn't leave.
(Low mounds by the entrance. Prayer strips. Flowers someone has planted, and kept watering. Karasu stops in front of
them and says nothing at all for a long time.)
TAMOTSU: (quietly) Karasu-san?
IUCHI KARASU: (finally) …My great-uncle ordered this. I was in the Shadowlands while he did it.
IUCHI KARASU: (beat) I was a prisoner in hell, and I came home to find my family had built one for the neighbours.
[BATTLE b_mine_dead_a]
### Battle note
"The **risen dead** don't feel fear (Terror immune). **Raw jade** lies everywhere — use it as an item for free
**Jade** damage."
[IF camps_fed] (Refugees from the camps have followed as porters.) GOCHU (or a refugee): "We'll carry the carts, Ide-sama.
You carry the fight." (the party keeps every raw-jade node) [ELSE] (half the raw-jade nodes go to the carts) [END]
[BATTLE b_mine_dead_b]
(Carts of jade, green-glowing in the dark. The miners' tools, laid neatly in rows.)
[SAVE]

## S06 — What the Mine Remembers (BOSS)
MAP: `jade_mines_3` (the deep gallery) · TRIGGER: the deepest seam
(The deepest gallery. A corpse in old Iuchi armour, three hundred years old, rising from a cracked shrine: the mine's
guardian, woken by the Regret above. Around it, the dead of the mine.)
MINE GUARDIAN: (a voice like stone grinding) …Who digs… in the deep places…
TAMOTSU: Someone who needs the jade, ancestor. To stop the thing that woke you.
MINE GUARDIAN: …All who dig here… stay here…
IUCHI KARASU: (raising his hands, eyes glowing) Not today, grandfather.
[BATTLE b_boss_mine_guardian]
### Barks
- Guardian swing: MINE GUARDIAN: "Stay! Stay with us! The dark is quiet!"
- Raw jade item: TAMOTSU: "Ancestor — forgive the rudeness — (throwing a stone) — catch!"
- Karasu's Jade Strike: IUCHI KARASU: "I learned this one from a very angry oni. He was a terrible teacher."
- Defeat: (the guardian kneels; the dead around it become motes of light, rising up the shaft)
MINE GUARDIAN: (fading) …quiet… at last…
(Karasu kneels and prays without words. Tamotsu kneels beside him.)

## S07 — Ending
MAP: `mirumoto_camp` (dusk) · TRIGGER: return with the jade
(Carts of jade rolling into camp. A Dragon army stuffing wax into its ears. Shahai holding her father's hand.
Ahead, in the gathering storm: Shiro Iuchi, howling in its wind tunnel.)
TAMOTSU: (loading the last cart; to Karasu) Do you regret it? The six months?
IUCHI KARASU: (beat) I regret that I came back to *this*.
IUCHI KARASU: (beat) No. I don't. (holding out his hand) Pass me another stone.
[IF nihime_told] (A runner from Perfume Petal Blossom, with a note in a courtesan's perfect hand.)
NOTE (Soshi Nihime): "My son goes to the castle. Bring him home, if there is a home."
TAMOTSU: (folding it carefully into his sleeve, next to the pebble) …I'll try, my lady. [END]
[CHAPTER COMPLETE]
### Chapter complete card
**"The Noblest Blood" — complete.**
Journal: *A star burned in the frost, a little girl who wrote "are you real or are you singing", a lord who listened
to animals for twenty years, and a mine full of the quiet dead. Tamotsu has jade, a deaf army, and a castle ahead
that howls.*
[UNLOCK] Jade weapons (one per party member) · Dragon army (Allies' Muster in Ch4) · Rank 3 at 41: *When the Veil Moves*

---
## Travel Banter unlocked by Unicorn Ch3
### TB-unicorn3-a "Notes" (Tamotsu + Gendo)
GENDO: Your notes in the tower. I saw them afterwards. "I'm round, not fat."
TAMOTSU: It was important to be accurate.
GENDO: (completely serious) You were under possible demonic attack and you corrected a nine-year-old's description of your waistline.
TAMOTSU: (beaming) Accuracy is the foundation of trade, Gendo.
### TB-unicorn3-b "Karasu" (Tamotsu + Natsuko)
NATSUKO: The porcelain-mask one. He was really six months in the Shadowlands?
TAMOTSU: As a prisoner. He came back with glowing eyes and no sense of humour.
NATSUKO: He makes jokes constantly.
TAMOTSU: (sighing) Yes. That's what he does instead of having one.
