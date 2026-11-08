# Script — Phoenix Ch2 · "The Silent Court" — DRAFT v0.1

**Source:** *Howl of the Phoenix* (Kosiedowski; fan contest entry), **rebuilt** for 1122. The late-era canon cast is
replaced by our NPCs; its structure and ideas are kept. Plot facts only; **all dialogue is original**.
**Traveler:** Isawa Haruki · Rank 1→2, Lv 20–25 · **winter 1122–23** · the mountain pass below the Zumiki-mihari
watchtower → **Honored Treaty City** (Mamoru Kyotei Toshi, built for Lion–Phoenix peace).
**Octopath shape:** village of three inns → snowbound pass (dungeon) → treaty city (hub, path actions) → the torii
→ boss.
- **Set-piece:** the **torii defence debate** (a rehearsal of the finale's debate).
- **Choices:** 2.

---

## Scene 1 — "A Court Where No One Speaks"
**Where/When:** a village below the old Otomo watchtower Zumiki-mihari; three inns (the White Songbird, the Yellow
Lantern, the Hidden Poem geisha house)
**Beat:** The idealist monk **Asako Keiki** invites every clan to a **"silent court"**: a memorial for Isawa Hoju and
the dead of the Magonojo raid, where grief is spoken only through ritual. Every clan sends envoys with a private
agenda (these become side stories).
- A **drunk Matsu** (who is faking it) tests the guests' manners. **Bless** or Etiquette calms her; she reveals she
  was testing them.
- Two **Imperial magistrates** accuse the Phoenix of harbouring road bandits. Kamasari proposes a ritual to *erase
  the night's memory* from everyone. Haruki objects.
ASAKO KEIKI: Speak with the ritual, not with your tongue. Grief that shouts is only anger in a mourning robe.
HARUKI: *(after a long silence)* …I've been silent about something for twelve years, Keiki-sama. It doesn't get
quieter.

## Scene 2 — "The Pass" (dungeon)
**Where/When:** the snowbound pass to the treaty city
**Beat:** The embassy caravan is ambushed by a mob of **tattooed peasant cultists**, followers of the mad
**Togashi Kokujin** (canon: he went mad in 1120), led by the cowardly bloodspeaker **Hioninmaru**. Uninvited Unicorn
and Mantis envoys ride to the rescue.
- `[BATTLE]` Kokujin cultists (false tattoos; they fight in a frenzy). Weak to **Water**, **Bo**, **Air**; they
  surrender if Hioninmaru flees.
- Hioninmaru **flees** at the first sign of losing. He returns in Scene 6.
- **Cameo:** if Dragon Ch2 isn't cleared yet, **Togashi Yosai** is here hunting these cultists. ("Kokujin's
  children! They copied our tattoos and got the ink wrong. It's *embarrassing*.")

## Scene 3 — "Honored Treaty City" (hub)
**Beat:** A week of memorial ritual. The clan side stories run here (offered as Octopath side-story icons):
- a Crab–Shiba dojo friendship
- a Crane yojimbo stealing a spell scroll
- a Shiba commander to be sobered up
- a blood-feud duel to stop
- a Mantis trade stall burned (arson)
Main beats:
- **The second ceremony master is Isawa Mieko**: gracious, kind, a gardener turned priest. She greets Haruki warmly.
  *She doesn't remember him at all.*
- A Lion historian, **Ikoma Sadahisa** *(orig.)*, finds an old scroll about **"the Consumer"**, an undying dark side
  of the Phoenix reborn in great shugenja, and is **murdered** for it that night.
ISAWA MIEKO: *(arranging winter camellias)* Haruki-san? What a lovely name. Have we met? You look at me as though we
have.
HARUKI: *(counting on his fingers, stopping)* …Once. A long time ago. You wouldn't remember.
`[SYS]` **Discern** (Gendo), **Eavesdrop** (Mitsue) and **Bless** (Haruki) all work on the murder.
- The scroll's handwriting matches *Mieko's own*. Haruki's **Speak to the Soul** on it reads "written in fear, by a
  gentle hand".

## Scene 4 — "Midnight" (the clue)
**Beat:** At midnight Haruki finds Mieko in the snow garden, barefoot, humming, with eyes like black glass. In the
morning she is herself again and remembers nothing.
`[CHOICE 1]` *Tell Keiki what you saw* (truth; Keiki begins to watch her, which is useful in Ch3) · *protect Mieko
by saying nothing* (the guilt deepens; banter changes)
`[FLAG mieko_midnight_seen]`

## Scene 5 — "The Traitor's Torii" (set-piece: debate)
**Where/When:** a hidden mountain torii honouring **Shiba Mitsuhide** *(orig.)*, a Phoenix Champion branded a traitor
centuries ago for refusing an order to burn a village
**Beat:** A mob of grieving envoys and townsfolk wants to burn it as "an insult to the dead". **Haruki must defend it
with words.**
`[SYS]` **The debate UI** (the same as the finale's; low stakes). The mob raises three claims; each party member can
answer from their clan's view. Haruki's *Righteousness* answer is the key:
HARUKI: He refused an order to burn people. You'd burn his shrine for it. *(beat)* Which of those is the insult to the
dead?
- Win → the mob disperses and the torii stands (Honor +). Lose → the torii burns, but the chapter continues (a
  different epilogue line).

## Scene 6 — BOSS: "Hioninmaru"
**Beat:** That night **Hioninmaru** returns with the last cultists to burn the torii, and to recover the "Consumer"
scroll (he thinks it's a ritual).
`[BATTLE]` **Hioninmaru + cultist mob** (in the snow at the torii):
- Hioninmaru: Resolve 10. Weak: **Jade**, **Water**, **Void**. Maho: pays HP to cast; Taint on hit. A **coward**:
  if his allies all fall, he loses 1 Resolve per turn from fear (rules, `enemies.md`).
- No extra gimmick (the budget went to the debate).
HIONINMARU: *(backing away)* The Consumer! Isn't it beautiful? A darkness that never dies, that lives inside the
best of you!
HARUKI: *(Attune: Water)* It's not a prophecy. It's a warning. And you can't even read the difference.
`[CHOICE 2]` After the battle: *give the scroll to the Council* (they lock it away) · *keep it* (key item; it
unlocks a Ch3 dialogue in which Haruki shows Mieko her own warning)

## Scene 7 — Ending
**Beat:** The memorial closes with lanterns on the lake. Two envoys are found dead by morning, and both last saw
Mieko. The Council's investigators look at her. Haruki looks at the eclipse calendar.
ASAKO KEIKI: You know her, don't you, Haruki-san.
HARUKI: I'm the reason she's two people.
→ **Ch3 "The Darkfever."**
`[SYS]` **Rewards:**
- Lv ~25 (R2: Attune can be changed for free once per battle; ML2–3 spells).
- *Courage of the Seven Thunders* scroll.
- Side-story guests.
- The "Consumer" scroll (if kept).
