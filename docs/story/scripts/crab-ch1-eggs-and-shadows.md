# Script — Crab Ch1 · "Eggs and Shadows" — DRAFT v0.1

**Source:** *Tamago Maho* (4-page adventure). Plot facts only; **all dialogue is original**.
**Traveler:** Hiruma Natsuko · **Rank 1**, Lv 1–8 · **late autumn 1122** · the Kaiu Wall → a Yasuki market town.
**Systems introduced:**
- battle basics: weapons and elements, **Suki** (Resolve shields), **Void Points (VP)**
- Talent **Razor's Edge**; path action **Sumai**
- inn rest, Travel Banter
- field: Hunting (wild camp) and Stealth (sneak-walk)

Format key: `NAME:` · *(direction)* · `[CHOICE]` · `[BATTLE]` · `[FLAG]` · `[SYS]`

---

## Scene 1 — "The Long Grey Line" (prologue / battle tutorial)
**Where/When:** atop the Kaiu Wall, a rain-black night
**Cast:** Natsuko, Hiruma Ryoichi (her friend, peasant-weapon specialist), Hida Sachiko (a loud Wall veteran)
**Beat:** A goblin raiding party climbs the Wall. Tutorial: attack, weaknesses (goblins are weak to **Yari** and
**Jade**), Resolve shields, **Suki** at zero, Boosting with Void Points. Natsuko's **Razor's Edge** stance draws
attacks and dodges them.

*(Rain. Torches hiss. Natsuko leans on her yari, a rolled map case strapped across her back.)*
HIDA SACHIKO: Hiruma! Your little friends are back. Twelve of them. Thirteen. One has a hat.
NATSUKO: Then I'll take the one with the hat. Fashion should be punished.
`[BATTLE]` Goblin raiders ×4 → ×3 + "Goblin in a Hat" (mini-leader).
`[SYS]` Tutorial prompts, in order:
- "Yari icon flashes: this enemy fears spears."
- "Its Resolve is gone — it's open (**Suki**)! Hit it while it's reeling."
- "You gained a Void Point. Spend it to strike harder."
- "**Razor's Edge**: stand in the gap. Draw their blows. Make them miss."
*(After the battle. Ryoichi bandages her arm.)*
HIRUMA RYOICHI: Your father's map got wet.
NATSUKO: *(checking it, too quickly)* It's oiled. It's fine. It's been through worse than rain.
HIRUMA RYOICHI: You still look at it every night. Thirty years of Hiruma have died looking for that road home.
NATSUKO: Then the thirty-first should at least look at the map first.

## Scene 2 — "Leave, Unwanted"
**Where/When:** the Wall garrison, dawn
**Beat:** Her commander orders Natsuko on a week's leave after three straight months on the Wall. ("Rest is an order.
Disobey it and I'll have you guard the latrines.") She's sent to escort a supply cart to a Yasuki market town and
"enjoy herself". She has no idea how to.
`[SYS]` World map unlocks. Travel to **Hoshi-no-Ichi** *(orig.: "Star Market", a Yasuki trade town on the coast
road)*.

## Scene 3 — "The Town With No Eggs" (hub)
**Where/When:** Hoshi-no-Ichi · day 1
**Beat:** The town is short of rice and, oddly, of **eggs**. A Crab bushi is shouting at a serving girl over
egg-drop soup that has no egg in it. Trinkets are going missing (fans, mirrors). The townsfolk blame a ronin gang,
**the Hidden Ones**, who camp by the old quarry.
- **Inn:** first inn rest; **Travel Banter** unlocks once a second traveler is recruited.
- **NPCs:** the serving girl **Kiyo** *(orig.)*; the egg merchant (ruined); a Yasuki magistrate who wants it all to
  go away; a courtier from the capital, **Seppun Satomi**, here on "family business" and visibly worried.

ANGRY CRAB BUSHI: Egg-drop soup! Where. Is. The egg.
KIYO: *(near tears)* There are no eggs in the whole town, my lord!
NATSUKO: *(sitting down beside him)* Then it's drop soup. Very pure. Very Crab. Drink it and let the girl go.
*(He stares. Then drinks. Then laughs.)*
`[SYS]` **Path action Sumai** introduced: NPCs blocking the way can be wrestled (odds by Jiujutsu rank vs. NPC
rank). Failing costs a little town Honor.

## Scene 4 — "The Hidden Ones"
**Where/When:** the old quarry camp · day 2
**Beat:** Town guards are about to raid the ronin camp. Natsuko gets there first. The gang's leader, **Gonta**
*(orig.)*, a mountain of a man, won't talk to "Crab dogs".
`[CHOICE]` **Sumai** with Gonta (he respects strength) · *talk* (fails until you've seen inside the camp) ·
*leave* (the guards raid; the town loses face later)
- On a Sumai win: the gang has no mirrors, no fans and no eggs. They're starving too. Someone else is robbing
  everyone.
GONTA: *(flat on his back, laughing)* All right, scout. You throw like a landslide. Look around: do we look like we're
eating anyone's eggs?
`[FLAG hidden_ones_cleared]` → they become **hired help** (`04-cast`: Allies' Muster) later in the Crab arc.

## Scene 5 — "Something in My Pack" (night)
**Where/When:** the inn, night
**Beat:** Natsuko wakes to a small furry thief rummaging through her pack: a young **nezumi**,
**Squeak-of-Many-Eggs** *(orig.)*, from the **Grasping Paw** tribe. It grabs her father's map case and runs. **She
chases it**: a rooftop and alley chase, a stealth/tracking minigame.
NATSUKO: *(half-dressed, yari in hand, sprinting across a roof)* Not. The. MAP!
`[SYS]` Field skills: **Stealth** sneak-walk and **Hunting** tracking are introduced (`skills.md`). The trail leads
out of town to caves that stink of rotten eggs.
*(At the cave mouth the nezumi drops the case and squeaks frantically, pointing inside: not a thief, a messenger.)*
SQUEAK: Big-man-sad! Big-man-*wrong!* Eggs-eggs-eggs, no-good! You come, scout-who-fights-at-night!
NATSUKO: …You stole my map to get me here.
SQUEAK: *(proudly)* Yes-yes. Smart-smart.

## Scene 6 — "The Egg Caves" (dungeon)
**Where/When:** unstable caves above the coast
**Beat:** A short dungeon. Nezumi warrens; piles of stolen trinkets (all the town's missing mirrors and fans) laid
out in odd patterns; baskets of eggs painted with crude, wrong-looking symbols.
- `[BATTLE]` Grasping Paw nezumi who don't trust Squeak; cave beetles.
- **Hazard:** loud fights shake the ceiling. A **"Rumble" meter** fills with big AoE attacks or Boosted multi-hits.
  When it's full, a cave-in hits everyone (`[SYS]`: teaches restraint and Suki timing).
- **Discovery:** a **Seppun Imperial guard's** armour, carefully polished, on a stand made of driftwood.

## Scene 7 — "Seppun Ryozo, Sorcerer of Eggs"
**Where/When:** the deepest cave, around an "altar" of eggs
**Cast:** **Seppun Ryozo** (a deranged Imperial guardsman), his nezumi "children"
**Beat:** Ryozo believes the marked eggs let him cast **maho without blood**, without sin. He has no power at all. The
orphaned nezumi he raised love him and will fight for him.

SEPPUN RYOZO: *(holding up an egg, radiant)* You see? You *see*? No blood! The life inside the shell is the
offering. A clean magic, Crab. The Emperor's own guard, purifying sorcery! They laughed at me in the capital.
NATSUKO: Did anything happen when you tried it?
SEPPUN RYOZO: *(beat)* The eggs must be *fresher*.
`[CHOICE]`
- *"Your aunt is in town. She's frightened for you."* (needs: talked to Satomi in Scene 3) → he wavers.
- *"The nezumi will die for you. Is that clean?"* → the nezumi hesitate.
- *"Blood or no blood, you're stealing from starving people."* → he flies into a rage.
- Talking him down needs **two** of the first two. Then `[FLAG ryozo_talked_down]`.

## Scene 8 — BOSS: "The Grasping Paw"
- **If talked down:** the tribe's **nezumi shaman**, who hates Ryozo's hold over the young ones, attacks anyway.
  Squeak sides with Natsuko (temporary guest).
- **If not:** Ryozo and the shaman fight together. Ryozo hits weakly but heals the nezumi with "egg rites"
  (placebo: it works because they believe).

`[BATTLE]` **Nezumi Shaman + Grasping Paw pack** (+ Ryozo if he wasn't talked down):
- Shaman: Resolve 6. Weak: **Yari**, **Fire**, **Bo**. It casts nezumi "name-magic" (Silence: "*You forget your
  own name!*").
- The **Rumble meter** stays active. A full cave-in damages everyone *and* stuns the shaman. Using it on purpose is
  a valid tactic.

## Scene 9 — "Something Without a Name" (ending)
- **Talked down:** Ryozo surrenders his "rites". Natsuko walks him out to his aunt. Satomi pays the town for every
  stolen egg and quietly asks Natsuko never to speak of it. `[CHOICE]` *accept her gift* (a fine Seppun tanto) ·
  *refuse* (Honor +).
- **Not talked down:** Ryozo, wounded, crawls off into a side tunnel. *(Camera stays behind as the party leaves.
  Darkness. Something wet moves.)*
  ??? : *(a voice like a door creaking)* …a name… give me… a name…
  *(Ryozo, delirious:)* …Seppun… Ryozo…
  ??? : …Ryozo… *(pleased)* …yes.
  `[FLAG oni_named_ryozo]` → it returns in **Crab Ch3** among the Shadowlands horrors, *wearing Ryozo's name*.
- **Both:** Squeak and the young nezumi have nowhere to go. Natsuko, against every Crab instinct, tells them about a
  dry cave near her Wall post. `[FLAG nezumi_friends]` → nezumi allies in Crab Ch3, and they meet Stich'Kik in the
  finale.

## Scene 10 — "Back to the Wall"
**Beat:** Natsuko returns from "rest" with a bruise, a nezumi following at a distance, and the map case. A runner is
waiting: **Kaiu Takakana**, karo of Kyuden Hida, has summoned her. Nobody knows why a junior Hiruma scout is wanted at
the Crab Champion's court.
HIDA SACHIKO: Kyuden Hida! What did you *do*?
NATSUKO: I went on leave.
HIDA SACHIKO: Fortunes help us. Never let her rest again.
→ **Ch2 "Winter Court at Kyuden Hida."**

`[SYS]` **Rewards:**
- Lv ~8.
- Squeak's charm (accessory: +item-find).
- Seppun tanto, or Honor +.
- The Hidden Ones as hired help.
- First kata pick at Lv 5: *Striking as Earth* (`kata.md`).
