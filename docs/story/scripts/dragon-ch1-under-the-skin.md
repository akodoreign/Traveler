# Script — Dragon Ch1 · "Under the Skin" — DRAFT v0.1

**Source:** *Hindsight Part I* (Hepler & Hepler, 2000), re-dated from 1120 to **late autumn 1122**. Plot facts
only; **all dialogue is original**.
**Traveler:** Kitsuki Gendo · **Rank 1**, Lv 1–8 · Mantis isles: the **Isle of Silk** and Rakusho.
**Systems introduced:**
- Talent **Deduce**; path action **Discern** (Investigation-gated)
- the code-breaking puzzle on the Gusai stairs
- the tide battle (a terrain timer)
- guests: **Togashi Yosai** (orig., tattooed monk), **Kitsuki Momo**
- `skills.md` Underworld (a Bugei skill for the Kitsuki)

---

## Scene 1 — "The Junior Yoriki" (prologue)
**Where/When:** a Mantis trading ship, then the docks of the Isle of Silk
**Cast:** Gendo; senior magistrate **Kitsuki Oharu** *(orig.)*, sharp and kind and very tired
**Beat:** Lord **Kitsuki Yasu** has sent Oharu to look into a body found in a garbage heap: a Dragon matter. Gendo,
newly made her yoriki after years as an archive clerk, carries her case of tools and polishes his scandalous gaijin
spectacles.
KITSUKI OHARU: *(on deck)* Tell me what you see, Gendo.
GENDO: A trading ship. Forty crew. The captain is lying about his cargo: the waterline's too low for silk.
KITSUKI OHARU: Good. And?
GENDO: …And you're seasick, and pretending you're not.
KITSUKI OHARU: *(laughing)* Better. Never tell anyone that second one.
`[SYS]` **Discern** tutorial: examine NPCs for hidden facts (gated by Investigation rank).

## Scene 2 — "Hospitality"
**Where/When:** Yoritomo's audience hall
**Beat:** An audience with **Yoritomo**, the blunt Mantis lord, careful not to offend the Dragon. He hands them a
"minder", **Kosai**, from the Storm Legion captain **Tadayasu** (shaved head, armour at court, thugs with kama).
Gendo stands three paces behind Oharu and is never addressed.
*(That night, at the guest house, Oharu's tea is poisoned. She lives, barely, and can't rise from her bed.)*
KITSUKI OHARU: *(whispering, feverish)* My seal. Take my seal, Gendo. They will not respect it in your hands. Use it
anyway.
`[FLAG oharu_poisoned]` `[SYS]` The Rank-1 rule in action: Tadayasu openly mocks Gendo's authority. Doors need
**Discern**, money or patience, never rank.

## Scene 3 — "Blood! Fire! Pain!"
**Where/When:** the island dump, the body's location
**Beat:** The skinned body is **Togashi Nobue**, a tattooed troubleshooter of Togashi Yokuni. Earth kami at the dump
scream only "BLOOD! FIRE! PAIN!", maddened by Togashi blood. The cheerful eta mortician **Muika** helps.
- **Guest joins: Togashi Yosai** *(orig.)*. A second tattooed monk sits on the garbage heap, eating a persimmon.
TOGASHI YOSAI: That's Nobue. He owed me three strings of coin and a poem. I suppose I'll never get the poem.
GENDO: You knew him?
TOGASHI YOSAI: We were brothers in the Order. *(cheerfully)* He's the third brother to die like this. If the
pattern holds, I'm next! So I thought I'd come and see who's doing it before it's my turn. Saves time.
MUIKA: *(delighted)* Oh, I like him.
`[SYS]` Yosai's guest skills: *Dragon's Breath*, *Arrowroot*; passive **Crow** (`04-cast` #27, `kiho.md` §2).
**Banter tag:** Yosai counts the Fortunes' attempts on his life ("Seventeen. The poison on the boat was eighteen —
no, that was meant for Oharu-sama. I'll allow it as half").

## Scene 4 — "The Boy Who Remembers Wrongly"
**Where/When:** the temple school at Rakusho
**Beat:** Simple, eidetic **Riichi** recites Tao verses *deliberately altered* by three successive monks (Ayaru,
Jotaro, Nobue): a code. Gendo must spot the wrong lines (a dialogue puzzle). Gendo is kind to the boy, who has been
mocked all his life.
RIICHI: The teacher says I say it wrong. But the monk said: *say it exactly wrong, Riichi. Exactly.*
GENDO: *(softly)* Then you've said it perfectly. Say it again. Slowly.
- **Guest option: Kitsuki Momo** (a magistrate who was born a plum farmer's daughter) is at the school
  investigating a lesser case. She joins for her side story.

## Scene 5 — "The Stairs of Kyuden Gusai" (puzzle dungeon)
**Where/When:** the ruined castle of the Gusai, torn down after Gusai Rioshida's hostage plot
**Beat:** The code is a path: fourth step → footpath; three stones 33 paces apart with arrows; 20 stones up a wall →
hidden notes. An exploration puzzle under falling-rubble hazards, with Storm Legion thugs tailing them.
- `[BATTLE]` Tadayasu's kama thugs (weak to **Bo**, **Katana**; they surrender to **Cite the Law** once Gendo has
  Lore: Law 3).
- **The notes:** all three monks were tracking **Togashi Akuro**, an elderly ise zumi whose final tattoo showed him a
  vision he could not bear. He can change his face, and leaves no Taint where he walks.
TOGASHI YOSAI: *(reading over Gendo's shoulder, very quiet for once)* Akuro taught me to sit still. When I was
nine. *(beat)* Well. That's ruined that memory.

## Scene 6 — "The Terrified Artist"
**Where/When:** a boathouse on the shore
**Beat:** **Kakita Kumpei**, a failed Crane artisan who "helped" Nobue, hides here acting terrified. **Deduce/Discern
reveals contradictions** (paint on his hands of the same rare blue as the skin-painting; he knows things only the
killer would). **Gendo can't prove it.** If he accuses Kumpei now, he loses face and Tadayasu has Gendo thrown out.
`[CHOICE]` *accuse now* (fails: Glory −, but Gendo was right) · *wait and watch* (correct; `[FLAG kumpei_watched]`)
GENDO: *(internal monologue, a habit)* Evidence: paint, timing, a lie about the tide tables. Testimony against it:
a Crane with good manners. Every court in the Empire believes the manners.

## Scene 7 — BOSS: "The Tide" (beach battle)
**Where/When:** the departure beach for Tortoise Island, at dusk
**Beat:** Kumpei slips away by boat toward **Tortoise Island**. The party's boat is waiting, but so are **hypnotised
ronin shugenja and Mantis thugs** (Akuro's suggestion-tattoo work: dull eyes, one repeated phrase).
`[BATTLE]` **Hypnotised ronin shugenja ×2 + Mantis thugs**:
- **Tide timer:** every 3 turns the tide advances. Front-row combatants become "Waist-deep" (Speed −20%, Evasion
  −20%), then "Drowning" (damage per turn) for everyone still on the low sand. Kill the shugenja first, or move the
  formation.
- Shugenja: Resolve 5. Weak: **Air**, **Bo**. Cutting their suggestion (the **Interrogate** skill, or Haruki's
  *Know the Mind*) makes them **stop fighting**. They are victims.
- Thugs: Resolve 3. Weak: **Katana**, **Yari**.
*(After: the boat is wrecked; the shugenja wake with no memory. Yosai finds them a blanket each.)*

## Scene 8 — "No Authority, All the Same" (ending)
**Beat:** Oharu, still bedridden, hears his report. She formally names him to continue the case under her seal.
Tadayasu laughs. Gendo borrows a fishing boat with his own money.
KITSUKI OHARU: They will not respect you, Gendo.
GENDO: No, Oharu-sama. *(polishing his spectacles)* But they'll remember being wrong about me. That will have to do.
→ **Ch2 "The Painting"** (Tortoise Island, the cave, the portal of skin).
`[SYS]` **Rewards:**
- Lv ~8.
- Oharu's seal (a key item: some Discern targets need it).
- Yosai and Momo as guests.
- First picks: Interrogate, Feint (`battle-skills.md`). Gendo has no kata until R2.
