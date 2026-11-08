# PRODUCTION — Scorpion Ch2 · "City of Masks"

**Traveler:** Shosuro Mitsue · **Lv** 20–25 · **Outline:** `scripts/scorpion-ch2-city-of-masks.md`
**Flags read:** `iron_box_held` · **Flags set:** `giseiki_mask_held`, `masks_got` (0–4), `mitsue_wore_giseiki`,
`city_freed` / `city_sealed`
**Maps:** `plains_road`, `hisatu_kensu` (hot springs), `city_gate`, `hospitality_district`, `merchant_district`,
`temple_district_1–2`, `monastery_silent_self`
**Battles:** `b_stitched_monks_a/b`, `b_boss_munashii`
**Set-piece:** the mask gate. Equipped masks drain 5% max SP per district visit; masks are removed at shrines.
**Storyboard:** `storyboards/scorpion-ch2.md`

---

## S01 — Rumours on the Road
MAP: `plains_road` · TRIGGER: travel north of Shiro no Soshi
NARRATION: The plains north of Shiro no Soshi. A day's ride from Seikitsu Pass. Last week, there was nothing here.
### Rumour NPCs (travellers on the road; talk to all for flavour)
| NPC | Line |
|---|---|
| Rice farmer | "A city! Overnight! I went to bed and it was a field. I woke and it had a *wall*." |
| Pilgrim | "The people there have no faces. Just masks. Smooth as eggs." |
| Ronin | "They say the Emperor's lost heir hides there. They say a lot of things." |
| Merchant | "Being there is like watching a play. They talk to each other. Never to you." |
| Lion scout (hurrying past) | "Don't go. My whole patrol went in. Only half came out. The half that came out isn't right." |
(Hisatu Kensu: a Unicorn hot-spring village, too hospitable. Free baths. Free sake. Nobody will say a word about the
city.)
INNKEEPER: (bright, fixed smile) What city? Have another bath, lady!
### Mask dream (night; each party member, one line)
(Fog. A faceless monk. A smith at an anvil, hammering a face out of hot metal — *your* face.)
MITSUE: (waking, touching her own face) …Still mine.
MITSUE: (beat) Probably.
[IF haruki_in_party] HARUKI: "I dreamed of a puppet with my face. Worn smooth by sand." [END]
[IF sayo_in_party] SAYO: "I dreamed somebody sold my face at market. For a *good* price, at least." [END]

## S02 — Meant for You
MAP: `plains_road` (morning) · TRIGGER: leave the village
(A Lion scout, dying in the grass by the road. He grabs Mitsue's wrist with surprising strength.)
DYING SCOUT: You — you. It's meant for you.
(He presses a red-and-black mask into her hands, and folded papers bearing a lord's chop three hundred years dead.)
DYING SCOUT: It told me. It said — give it to the woman with many faces.
MITSUE: (quietly) Who told you?
DYING SCOUT: (looking at the mask) …He did.
(He dies. The mask is warm in her hands, like skin.)
GISEIKI (a faint second voice, only Mitsue hears — shown in pale text): …Thank you for coming. I've waited a long time.
MITSUE: (to the mask, very calm) Masks don't usually say thank you.
GISEIKI: Masks don't usually have anyone inside.
[ITEM +Giseiki's Mask (key item: equipping it lets Giseiki speak)] [SET giseiki_mask_held]

## S03 — The Faceless Are Not Answered (set-piece)
MAP: `city_gate` → `hospitality_district` · TRIGGER: approach the city
NARRATION: A city that isn't on any map. Its gates are open. Its people wear masks, and clothes three hundred years old.
(Masked citizens in antique silk. A sake-seller pours cups that no one drinks.)
MITSUE: (unmasked) Good morning.
MASKED SAKE-SELLER: (looking straight through her) I have nothing to say to the faceless.
### SYSTEM — the mask gate
"**The city's people ignore the unmasked.** Get masks: the smith, the carver, the tattooist, the silk seller.
While **equipped** in the city, a mask **drains 5% of max SP** each time you enter a district. Take it off at a
shrine to recover. **Mask materials** change how people react."
### Mask vendors (each gives 1 mask; [SET masks_got +1])
| Vendor | Mask | Material | Notes |
|---|---|---|---|
| **Kaiu Naname** (smith, Merchant District) | Iron mask | Metal | "I forged the first masks. I'd rather not forge more. Here. Please don't keep it on long." |
| **Ichiro Itami** (Badger carver) | Cedar mask | Wood | A cultist; cheerful; *Discern:* "His smile never reaches the mask." |
| Tattooist (nameless) | Ink-mask (painted on) | Water | "It washes off. Mostly." |
| Silk seller | Silk mask | Silk | "Soft. Fears nothing but stone." |
### Material reactions (dialogue gates on 4 key NPCs)
- Wood fears metal · metal fears fire · fire fears water · water fears earth · earth fears wood ·
  porcelain/glass fears stone · stone fears silk.
- The **right** mask makes an NPC talk; the **wrong** one makes them flee.
- **Rule:** a masked citizen welcomes the mask their own material **fears**; they flee from the material they overcome.
| Key NPC | Their mask | Welcomes | Gives |
|---|---|---|---|
| Masked sake-seller (Hospitality) | wood | Iron | "three hundred years"; points to the Merchant District |
| Kakita Yuko (Merchant) | fire-lacquer | Ink | the puppet faces; Munashii's fear |
| Miya Hatomu (Merchant) | clay | Cedar | Hatomu's Map |
| Temple District gatekeeper | stone | **Silk** | **opens the Temple District** (required) |
(Masked — iron — Mitsue tries the sake-seller again.)
MASKED SAKE-SELLER: (warmly) Ah! Welcome, welcome. You've been away so long.
MITSUE: (into the mask) …How long?
MASKED SAKE-SELLER: (pouring) Three hundred years, at least. Drink, drink.
(The sake sits untouched.)
[SAVE] (the shrine at the district gate — "Remove masks?")

## S04 — The Districts (investigation)
MAP: `merchant_district`, `temple_district_1` · TRIGGER: explore
### Key NPCs
- **Yasuki Kasamashi** (con man; sells fake-jade trinkets, wears a real jade mask):
  YASUKI KASAMASHI: Jade! Genuine jade! (lowering his voice) Except mine. Mine's *real*. That's why I still remember my name.
- **Togashi Sumi** (a riddler, tattooed face, no mask — the only unmasked citizen who speaks):
  TOGASHI SUMI: You seek Master Giseiki?
  TOGASHI SUMI: He's on the face of the one who wears him.
  MITSUE: (holding up the red-and-black mask) …I'm not wearing him.
  TOGASHI SUMI: (smiling) *Yet.*
- **Kakita Yuko** (12, puppeteer; her puppets have the party's faces):
  KAKITA YUKO: I made these before you came. The masks told me what you'd look like.
- **Miya Hatomu** (old cartographer, disgraced for mapping a city that "didn't exist"; here, weeping, vindicated):
  MIYA HATOMU: Thirty years they called me mad. I mapped this city from a dream. (holding up a map) Look — every street. Every one.
### Set piece (softened): the market
(A masked citizen collapses in the market. The crowd steps around him without looking. Mitsue kneels.)
MITSUE: (lifting his mask a little) …There's no one behind it. Just a body, breathing.
### Eavesdrop on 3 masked pairs → the history
1. "The masks began to *eat* us. Old Soshi Giseiki found out."
2. "He bound every soul into a mask, so the masks couldn't spread beyond our walls."
3. "And then he hid the whole city in the Realm of Dreams. Until the dreams broke."
GISEIKI (from the mask in Mitsue's sash): …I did. And I'd do it again. The masks are hungry, Shosuro. They want the Empire.
[SAVE]

## S05 — The Shadow Hunters
MAP: `hospitality_district` (the Sweet Cup sake house, back room) · TRIGGER: after S04
(Black-clad figures in a back room. A woman in a white porcelain mask, unhurried: SHOSURO OSUKO, the city's governor.)
SHOSURO OSUKO: You're a Shosuro. (studying her) No. You're *several*. Good.
SHOSURO OSUKO: We've hunted the mask-monks for three hundred years of dream-time. They pray to something under the Temple District.
SHOSURO OSUKO: Giseiki can end it. The counter-ritual. But it needs a body to work through.
SHOSURO OSUKO: (a hunter opens a chest of crystal) And take some of these. Crystal is the only thing the abbot fears.
(Shop opens: **Crystal Shard** 400 zeni each · **Crystal Rosary** ×1.)
GISEIKI: Hers, or yours, Osuko. I'm not choosy. I'm only a mask.
> CHOICE "Giseiki's mask"
  - "Give it to Osuko." → (Osuko performs the ritual; safer)
      SHOSURO OSUKO: (taking it) Brave and sensible. A rare Shosuro.
  - "I'll wear it myself." → [SET mitsue_wore_giseiki] (stronger ritual; Void −1 until chapter end; Giseiki speaks
    through her in battle)
      MITSUE: (putting it on; her voice doubles for a moment) …Oh. He's very *polite* in here.
      GISEIKI (through Mitsue): Forgive the intrusion. I'll be brief.

## S06 — The Temple District (dungeon)
MAP: `temple_district_1–2` · TRIGGER: go
(Monks with cloth faces sewn over their own guard every gate. They reach for the party's masks.)
STITCHED-FACE MONK: Give us your face. Give us your face. Give us your face.
[BATTLE b_stitched_monks_a]
### Battle note
"**Break** a stitched-face monk and its sewn face **tears free** — the soul inside escapes, and it falls, at peace."
(A monk falls; for a second, under the cloth, a young man's face, relieved.)
STITCHED-FACE MONK (freed): …thank you…
[BATTLE b_stitched_monks_b]
[SAVE] (the monastery steps)

## S07 — Abbot Munashii (BOSS)
MAP: `monastery_silent_self` · TRIGGER: enter
(The Monastery of the Silent Self. A vast shadow shaped like a mask fills the far wall. Before it kneels the abbot,
an old Akodo in a plain mask: MUNASHII.)
ABBOT MUNASHII: A mask is a mercy, child.
ABBOT MUNASHII: No more being anyone. No more having to *choose* who.
MITSUE: (Many Faces — her face, unmasked, for once) Choosing is the only part that's mine.
[BATTLE b_boss_munashii]
### Battle notes / barks
- "Only **crystal** hurts Munashii fully. Everything else does half." (crystal shard from the hunters, if bought)
- Phase 2 — he puts on his true mask: "He **copies your buffs**!"
  ABBOT MUNASHII: "Your courage. Your speed. I'll wear those too."
- [IF mitsue_wore_giseiki] GISEIKI (through Mitsue): "Now, Shosuro — the counter-word, while he's reaching for you!"
- Defeat: ABBOT MUNASHII: (his mask cracking) "…I only wanted to stop being frightened…"
> CHOICE "The city"
  - "Free it." → [SET city_freed] (every soul is released; the city fades at dawn; Hatomu's map becomes true history)
  - "Seal it again." → [SET city_sealed] (it slips back into dreams; Osuko's people remain)

## S08 — Ending
MAP: `plains_road` (dawn) · TRIGGER: after the boss
[IF city_freed]
(Dawn. The city is a mist, then a field, then nothing. Motes of light rise from where the walls stood.)
SHOSURO OSUKO: (her white mask the last thing to fade) Thank you, many-faced girl. I'd almost forgotten mine.
[ELSE]
(The city folds back into fog, a dream with the lid on. Somewhere inside, Osuko keeps hunting.)
[END]
MIYA HATOMU: (holding his map up to the morning light, laughing and crying) Thirty years they laughed.
MIYA HATOMU: I'll never prove it now. I don't care. I *saw* it.
(Mitsue takes off her last mask and checks her reflection in a puddle.)
MITSUE: …Still mine.
[IF mitsue_wore_giseiki] (Her reflection, for one moment, is someone older — then it's her again.) [END]
[CHAPTER COMPLETE]
### Chapter complete card
**"City of Masks" — complete.**
Journal: *A city that wasn't on any map, people who wouldn't speak to the faceless, and masks that ate souls. Mitsue
wore other faces to save the souls inside them, and checked afterwards that hers was still there.*
[UNLOCK] Rank 2: *The Shadow Has No Mercy* · Hatomu's map (world-map reveal) · Acting +1

---
## Travel Banter unlocked by Scorpion Ch2
### TB-scorpion2-a "Still Mine" (Mitsue + Gendo)
GENDO: You checked your face in a puddle.
MITSUE: Everybody checks their face in puddles.
GENDO: Not with that expression.
MITSUE: (pause) …What expression?
GENDO: Relief. (beat) I've filed a lot of faces. That one's the most honest I've seen you wear.
### TB-scorpion2-b "Polite" (Mitsue + Sayo; requires mitsue_wore_giseiki)
SAYO: What was it like? Wearing a dead man?
MITSUE: Crowded. He kept apologising.
SAYO: Sounds like a good houseguest.
MITSUE: (laughing) The best I've ever had. He even left when he said he would.
