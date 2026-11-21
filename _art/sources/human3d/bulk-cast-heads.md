# Bulk cast head pass

The user requested batch rollout without individual approvals. Promote internal fit and in-game checks in groups. Record exceptions and continue through the queue.

- 165 of 349 catalog entries currently have the regenerated portrait route and both native files present. [Cast progress](cast-head-progress.csv)
- 129 verified in the new batch runs. Pilgrim girl, Soshi Shinobu, Soshi Bantaro, Sabu, Sariko, Tamori Rain-caller, Kitsuki Seigen, Hantei Kusada, Kakita Miyoshi, Miya Yachiko, Kitsuki clerk, Kitsuki Oharu, The hostess, Cart driver, Suzume Rika, Mantis captain, Doji poet, Doji courtier, Isawa Uona, Isawa Rujo, Guard sergeant, Mob leader, The karo, Jade clerk, Kaiu Mami, Crane make-up artist, Incense-seller, Seppun Satomi, Suzume Sweeper, Imuro, Widow, Doji Seikidera, Kitsuki Momo, Hiruma Ryoichi, Sparrow Ronin, Kaiu Yutaka, Akodo Ozaki, Kuni Miyubi, Daidoji guard, Village girl, Hida Veteran, Hida Taneo, Kitchen girl, Tattooed beggar, Drunk actor, Iuchi farmer, Crane duellist, Mirumoto drummer, Iuchi Daiyu, Shosuro Noburo, Kitsu Takeo, Akodo Seoko, Mirumoto sentry, Court actor, Mirumoto Tabezu, Iuchi soldier, Iuchi Takanobu, Shinjo Yoriki, Ashigaru Archer, Mantis Ferry Archer, Daidoji Sakura, Lamplighter, Old Mirumoto Koshi, Akodo Tama, Bayushi Shoju, Tadayasu, Hida Ren, Hida Jade Archer, Akodo Goroso, Gochu, Akodo Hiruto, Akodo Gusai, Daidoji Atsuko, Hida Masakazu, Hida Yakamo, Daidoji general, Old fisherman, Boy with a crab, Shiba Noboru, Shinjo Ryuko, Soshi Ichihito, Soshi officer, Scorpion yojimbo, Yasuki Kasamashi, Kaiu Engineer, Kaiu Sapper, Fishwife, Tsuruchi Archer, Ebisu, Old woman, Bargeman, Muika, Village Herbalist, Ume-baa, Ship's master, Pigeon-keeper, Shrine peasant, Hanabi Seller, Mask-maker, Mirumoto Sen, Masked citizen, Old pilgrim, Iuchi Karasu, Mirumoto Yari Sergeant, Akodo Nishi, Beggar, Drunk sailor, Agasha Fire-Shugenja, Akodo Hojiki, Isawa Michio, Doji Hayato, Ide Xue, Doji Sanae, Iuchi Water-Shugenja, Asako Keiki, Isawa Sanro, Hiruma Goro, Akodo Kafu, Akodo Kafu (no-sword route), Smith's apprentice, Seppun Ushimo, Shiba Ashimita, Isawa Kasiko, Akodo Rin, Hida Sachiko, Lion rider, Tamori Haku, Matsu Hanae, Hiruma Kage. [Daylight profiles](cast_heads/bulk-cast-daylight-profiles.png)
- The source audit recovered 11 usable portraits from 60 missing entries. It identified 8 actor-specific variants and 41 original design briefs. The progress CSV tracks newly generated references and exports as these are processed. [Source cross-checks](cast-missing-source-audit.json), [recovered references](cast-recovered-references.json)

## Keep moving through the remaining cast

Use the exact sources and prompts in `reframed_heads`, the corrected painted donors in `work/hunyuan-runway`, and the active 50-joint fit packages in `work/model-rigging/batch-07/evening-cast`. `work/run_cast_head_batch.py` groups up to eight screened actor packages in the real Coast Road fixture. It checks sprite aliases, skin colors, the shared joints, selected clothing and authored gear, then verifies the daylight captures and walk. If a runtime check fails it restores the prior body routes and color files.

## Companion priority

The current rollout puts human story companions first. 19 of 21 companion routes have regenerated heads bound. The current route keys come from the scripted party entries in `tools/gen_data.py` and the native picture index. Use one face design for Kafu's sword and no-sword variants and one for Kage and his chapter-three route. Check each variant with its original body and equipment. [Companion keys](companion-head-priority.json)

Moved queued jobs retain their exact workflow, image and seed. The receipt list records both the original and the new prompt ID. Upcoming companion renders and fit handoffs go ahead of the general cast work.

Kusada, Miyoshi and Yachiko passed with fitted robe and emblem aliases. The Doji Poet, Courtier and Make-up Artist also passed with Miyoshi's verified shared-female A124 fit and original Crane palette. Satomi passed her painted head and fan check on Yachiko's fitted shared-female A167 with the Imperial palette. Shinobu and Bantaro use their uncovered dialogue portraits with their fans. Their floating generic cloth mask is suppressed on the regenerated neutral route. Hats, masks and jewelry should remain separate when they are part of the actor's canonical look.

The first Haku, Kenshai, Mountain Guide, Diver, Dying Healer, Suitengu Priest, Isawa Acolyte and Hagane geometry needs a new socket silhouette. Jade-dust Pedlar and Censor Monk need revised rear neck geometry. Separate pass holds are below.

Oharu's separate gold glasses and bun crown passed at runtime. The crown follows the headwear setting, and the glasses remain on her portrait during that toggle. The portable pieces and [daylight profiles](cast_heads/oharu-daylight-profiles.png) are in `cast_heads`. Yachiko's flower pin and Kitsuki Clerk's gold streamers are accessory follow-ups.

## Deferred A100 outfit review

Kitchen Girl and Iuchi Farmer use the same peasant A100 robe. The isolated A100 renders retain the high pointed collar, forward lip and dark throat ring in rest and nod. At review time A100 was the default mesh for 189 routes, including 145 shared-male and 44 shared-female routes. The next outfit pass can compare a softer collar across both existing body types before choosing any shared change. The outfit correction is deferred. [Profile isolation](cast_heads/a100-collar-profile-isolation.png), [Front isolation](cast_heads/a100-collar-front-isolation.png)

## Set aside during the continuation

| Actor | Hold |
| --- | --- |
| Oyuki | Corrected atlas is ready. Long head locks intersect the A100 collar on a nod. Use a new separated hair fit before promoting. |
| Otomo Shinken | Existing pilot neck is too deep for the actual shared female body. Fitted upper depth is 5.90 native units against 4.69, with a double rear contour. |
| Imperial Magistrate | First bare stem is 0.714 wide, too broad for the compact head fit. Use a narrower source for the next pilot. |
| Shosuro Norie | Lower stem depth grows from 0.434 to 0.690 and shifts to the rear. Use a less flared neck reference. |
| Shinjo Tsune | Existing A155 collar crosses the long locks during a head nod. Review a separate robe or hair fit before installation. |
| Pedlar | New neck geometry is usable. Long locks cross both shoulders and the authored headcloth needs fitting. |
| Daidoji Sailor | The entry has an authored hachimaki and needs that fitted separately on the regenerated head. |
| Kakita Mizochi | Rear edge of the collarless stem drifts forward through the measured socket. Hold the first pilot. |
| Kakita Sensei | Both neck sections are centered. Long silver locks penetrate fitted A124 in rest and guard. Hold the complete route. |
| Shrine maiden | Side locks intersect A100 at rest and during a nod. The exact head and dress trial are saved for clearance work. |
| Herald | V2 neck fits but long side locks penetrate A127 in all four poses. Keep this geometry for hair clearance before paint. |
| Censor's clerk, Doorman, Ronin Cook, Rakusho teacher | First pilots have oversized neck stems for their head scales. Keep these geometry exports aside. |
| Crane duellist | First new reference has a stepped neck stem beneath the jaw. Hold this reference before GPU generation. |
| Village Elder, Hida Chuto | The first pilots have narrow neck pegs that leave a visible break at the body socket. |
| Gaijin Trader | First pilot widens to roughly 0.68 at the stem and deepens unevenly toward the head. |
| Naname | Seated neck clears the ring check, but hair contacts the Crab A112 collar through the four-pose trial. |
| Fujio | Long hair intersects the Unicorn A155 garment in rest, stride, guard and nod. |
| Nagai | V2 creates a narrow peg. The fitted upper ring is 4.03 wide and 3.18 deep against the body slot's 7.85 by 6.48. |
| Iuchi Farmer, Mirumoto Drummer, Togashi Outfitter, Mule-driver | Their first original pilots have lower stem widths from 0.86 to 1.08. Keep the identity art and prepare slimmer geometry sources before paint. |
| Nashiko, Tsuhime | The centered stems are usable in isolation. Hair and neck fuse across the lower shoulder band in the first pilots. |
| Street Musician, Hidden One, Hidden One 2 | The first isolated stems are 0.76 to 0.86 wide. Keep the hair and face designs and regenerate with slimmer stems. |
| Tamori Monk, Abbot of Osano-Wo, Pilgrim | First reference geometry has overly wide necks. The Abbot also has a deep posterior stem. |
| Old Actor | Lower neck is 0.69 wide with excessive rear drift through its base. |
| Old Mirumoto Koshi | First portrait's beard hangs past the flat neck base. A revised portrait leaves exposed skin below the tip and has been submitted for geometry. |
| Gonta's boy | Both existing donors center, but the mounted lower neck still leaves a visible rear ledge at an appropriate child head scale. |
| Hida Tomoe, Hiruma Scout | The first isolated stems are narrow and offset. Hiruma Scout also needs a cleaner separation under the ponytail. |
| Akodo Ukita | Standard A135 exposes the front ring. The fitted Lion A135 still contacts his one-sided ponytail in all four poses. |
| Shosuro Stagehand | V1 and V2 sit level, but the shallow exposed front shows a wide throat overlap above A127. Prepare a deeper cylindrical front with the same vertical rear. |
| Kami Togashi, Dock Porter, Thunder Monk | First pilots have overly broad lower stems. The Kami's revised V2 still slopes back and varies rapidly in depth. |
| Smith's apprentice | Initial raw stem is broad. The later exact rigid fit on his short body clears the dressed checks and has a separate red linen hachimaki. |
| Ide Xue, Yoritomo Rui, Akodo Kafu, Akodo Rin, Kuni Witch-hunter, Yogo Meyako | Recent reference alternatives need additional lower-hair clearance or separate ornaments before submission. Keep their original identity references. |
| Herb Seller | The old source has insufficient neck depth and a piece of fused cloth below its left lock. Keep the original leaf sprig as an accessory reference for the next version. |
| Kakita Yasurugi | New pilot remains upright but runs opposite the A124 taper and exposes a rear neck rim. Hold paint. |
| Bayushi Guard, Seppun Guard, Lion Rider, Mantis Bushi, Lion Tax Collector | First stems are broad for the fixed body proportions. Separate headwear and masks remain equipment. |
| Togashi Outfitter | V2 reduces width but moves far enough forward through the neck stem that the best rigid placement requires +11.71 degrees of head pitch. Hold paint. |
| Soshi Envoy, Beggar, Drunk Sailor, Ronin Yojimbo | First pilots run wide or change depth too quickly through the lower socket. Keep the original source identities and screen fresh geometry separately. |
| Shosuro Mayumi, Doji Siko, Hiruma Kage, Matsu Hanae | Mayumi's first neck is thin front to back. Siko's crown has holes. Kage's rear hair limits the stem to a mount with excessive lean. Hanae's low tail and raised eye contours need a fresh source. |
| Mitsue's maid route | Mechanical A127 checks passed. The actual daylight front still shows a pale horizontal neck stripe. The previous live route is active and the exact candidate and color calibration are saved for review. |
| Yogo Mai V3 | Mounted exact paint shows a broad pale scalloped overlap at the front of A127. The corrected head and collar proof are staged. |
| Yogo Meyako V2 | Bare fit clears hair and the A127 robe, but the active story mask projects visibly in both profiles. The native Noh mask stays active pending a separate fit. |
| Moto Benjiro V2 | Corrected face preserves purple paint. The registered death mask and uncovered canonical portrait disagree. Hold his neutral presentation until story equipment is confirmed. |
| Kitchen Servant, Ferry Fisherman, Kitsune Hyobe | Servant has an undersized lower neck, Fisherman has an oversized upper ring with A100 contact, and Hyobe's hair touches his A108 collar. |
| Moto Zhang | Later rigid seat reduces depth mismatch. The stock A159 still exposes a prominent rear neck window. |
| Gusai Iami, Yoritomo | Stock A168 exposes the right rear skin rim. Iami also has lock-edge contacts on the independently checked Tadayasu alias. |
| Lion Sergeant, Ryohei, Yosuke | Lower hair contacts their stock garments in the four samples. Preserve the face and hair designs while checking clearance. |
| Ikoma Yoshi, Kaiu Takakana, Crater-shrine Archer, Mirumoto Ashigaru | The first pilot stems are too narrow to meet the body ring at their intended cranium sizes. |
| Yogo Shigeru V3 | The short stem merges into a broad crossbar between the low hair shapes. Save the original hair design for a separate lock fit or source revision. |

Oyuki and Kakita Sensei's lower hair crosses both bare shoulders. Move the lower locks clear of the shared body before checking the collars again. [Oyuki profile proof](cast_heads/oyuki-hair-clearance.png), [Kakita Sensei profile proof](cast_heads/kakita-sensei-hair-clearance.png)

The accepted Sparrow package has a frozen copy of its exact source geometry and texture in the rigging stage.

Suzume, Imuro, Widow and Seikidera passed the Coast Road check with their actual outfits and matched skin. Momo passed with the corrected lower atlas and Dragon A153. Ryoichi, Sparrow Ronin, Yutaka, Ozaki, Miyubi, the Daidoji Guard and Village Girl passed with their actual gear routes. The [prior textured source audit](prior-textured-source-audit.csv) covers 104 additional actors.

The Iuchi Farmer's measured V3 source has a low stem width of 32.5 percent of the full opaque head width. The revised mesh's lower section is 0.498 by 0.457 and its rigid fit on A100 passed both profiles and nod. The older 0.926-wide mesh stays in review storage. The Farmer and Kitchen Girl are live with individually fitted cloth headpieces and passed headwear-toggle checks. [Both in daylight](cast_heads/separate-headcloths-daylight.png)

Hida Veteran and Hida Taneo passed on A173 with tetsubo. Tattooed Beggar and Drunk Actor are live on A100. Crane Duellist passed on A109. Mirumoto Drummer V3 passed on A153 with his own separately fitted woven cap and the headwear toggle.

Revised Daiyu and Noburo passed with A155 and A100. Seoko and Takeo passed with the fresh seated inputs taken from their original portraits. Takeo uses the individually fitted Lion A135 collar, including the original emblem and its native yari route. [Takeo's garment registration](wardrobe/a135-lion-takeo-registration.json)

Mirumoto Sentry V2 passed on Dragon A141 with the stock katana route after replacement of its narrow V1 stem. Court Actor A passed with the fitted male Crane A124 and his native fan. Both heads use the original character designs and the shared 50-joint hierarchy.

Tabezu, Iuchi Soldier and Takanobu V2 passed on A141 and A159. Shinjo Yoriki, Ashigaru Archer and Mantis Ferry Archer passed with their native yumi routes. The Ferry Archer's fitted A168 clears the original front flare and rear rim in both daylight profiles. [Ferry Archer's garment registration](wardrobe/a168-mantis-ferryarcher-registration.json)

Sakura, Lamplighter and Old Mirumoto Koshi passed with the named A116, A100 and A153 outfits. Tama passed with the fitted Lion A135 alias and his original yari. Shoju passed with his Scorpion A120 and katana. [Most recent daylight profiles](cast_heads/next-five-daylight.png)

Tadayasu passed with a fitted right rim specific to his A168. Hida Ren and Jade Archer passed with A112 and A173 and their native tetsubo and yumi. Goroso passed with an individual A135 collar whose side rims clear both low locks. [Tadayasu's registration](wardrobe/a168-mantis-tadayasu-registration.json), [Goroso's registration](wardrobe/a135-lion-goroso-registration.json)

Gochu passed with A100. The locked Tama, Shoju and Gochu atlases passed a second live check and now point to frozen source copies. Hiruto and Gusai passed with Lion A135's fitted collar alias. Daidoji Atsuko and Hida Masakazu passed with A109 and A173 and their original yumi and tetsubo routes.

Yakamo passed with A173 and the original tetsubo. Close authoring views retain small A173 shoulder-piping edges. The Daidoji General's fitted rear A109 collar passed both daylight profiles. Old Fisherman and Crab Boy passed with their revised V2 heads on their actual A100 routes. [General's registration](wardrobe/a109-crane-daidoji-general-registration.json)

Shiba Noboru and Shinjo Ryuko passed in A116 and A159. Ichihito passed with stock Scorpion A120. The Soshi Officer passed with an individually eased A120 outer lip that clears both lower locks. [Soshi Officer's registration](wardrobe/a120-scorpion-soshi-officer-registration.json)

Scorpion Yojimbo passed with stock A120. Kasamashi passed with an independently sculpted jade half-mask mounted in the fitted portrait's story-mask slot. Kaiu Engineer and Tsuruchi Archer passed with their fitted hachimaki and a duplicate-headband check. The Sapper and Fishwife passed with independently fitted cloth caps and the headwear toggle. [Latest mask and headwear views](cast_heads/jade-mask-and-headwear-daylight.png)

Ebisu passed with the regenerated A100 head and a separate charcoal linen cap. The fitted cap remains on the character through his stride and follows the headwear toggle.

Old Woman, Bargeman, and Muika passed on A100 with three separate fitted cloth pieces. Their profiles and walks use the shared rig and face-sampled body color.

The Village Herbalist, Ume-baa, Shipmaster, and Pigeon-keeper passed with separately fitted cloth headwear. Shipmaster uses the verified fitted male A124 cut with Crane A124 materials.

The Shrine Peasant and Hanabi passed with separate fitted headcloths. The Mask-maker and Mirumoto Sen passed their original routes. Masked Citizen passed his A100 and fan with an independently fitted porcelain mask. Old Pilgrim V2 passed with A100 and his original bo. [Citizen's fitted mask](cast_heads/masked-citizen-porcelain/rigged-citizen-porcelain-mask.png)

Karasu passed his A155 and shakujo with the separate ceremonial mask. His stock collar shows a skin edge and a rear opening in daylight. Nishi passed A100 with two separately fitted bun ornaments. Yari Sergeant, Beggar, Drunk Sailor, Agasha Fire-Shugenja and Akodo Hojiki also passed the Coast Road walk and both sides. [Karasu's mask](cast_heads/karasu-ceremonial-mask/ceremonial-painted-close.png), [Nishi's ornaments](cast_heads/nishi-ornaments/fitted-ornaments.png)

Isawa Michio, Ide Xue, Iuchi Water-Shugenja and Asako Keiki passed on their native outfit routes. Doji Hayato and Doji Sanae passed on the fitted male and female A124 aliases, preserving their Crane fabrics, decals and weapons.

Goro, Michio, Sanro, Ushimo, Ashimita, Kasiko, Sachiko, Lion Rider and Rin also loaded the regenerated heads in their actual party slots. These use the hero's equipped wardrobe, which can differ from the field model's defaults. Both Kafu field routes use the same source and rigid head fit. Smith's apprentice and Sachiko each have an independently fitted red linen hachimaki. [Sachiko's headband](cast_heads/side_sachiko_fitted-headwear/painted-headwear-fit.png)

Use `work/review_cast_geometry.py` to compare pilot silhouettes and centered sections across each group. Once a pilot clears, `work/queue_cast_texture.py` submits the exact input at seed 47. Its optional front placement only takes effect when all pending jobs belong to the recorded Traveler queue.

## Reference screening

| Batch | Cleared for geometry | Set aside at source review |
| --- | ---: | --- |
| 08 | 10 | — |
| 09 | 18 | Old Mirumoto Koshi |
| 10 | 8 | — |
| 11 | 5 | — |
| 12 | 11 | Ide Xue, Yoritomo Rui |
| 13 | 3 | — |
| 14 | 9 | Akodo Kafu, Kuni Witch-hunter, Yogo Meyako, Akodo Rin, Ide Xue, Yoritomo Rui |
| 15 | 9 | Soshi courtier, Jinnai, Old pilgrim, Yasuki Tessai |
| 16 | 7 | Shinjo Miyahana, Ikoma Sadanobu, Iuchi Hiroichi, Matsu Hisae, Matsu bushi, Matsu Rokuro, Mirumoto Yari Sergeant |
| 17 | 4 | — |
| 18 | 11 | Mirumoto Sen, Mirumoto Tsukaru, Moto Benjiro, Moto Outrider, Quartermaster, Shiba Ashimita, Yogo Mai |
| 19 | 18 | Fish-seller, Innkeeper, Kiyo, Goat-herd Archer, Child with a kite, Hida Sachiko |
| 20 | 2 | Young Sayo, Katsuo the White Brother, Masked sake-seller |
| 22 | 3 | Agasha Kusuri, Akodo Ijako, Akodo Hojato, Akodo Shogen, Akodo Toturi |
| 23 | 7 | Isawa Kamasari, Isawa Wind-Priest, Isawa Mieko, Iuchi Kurosho, Ide Keiyomi |
| 24 | 7 | Bayushi Kei, Bayushi courier, Doji Himeko, Doji Miyako, Kakita Adoru |
| 25 | 9 | Gonbei, Gonta, Mantis envoy |
| 26 | 11 | Akari |
| 27 | 11 | Togashi Sumi |
| 28 | 11 | Isawa Hoju |
| 30 | 5 | Agasha Kusuri, Akodo Ijako, Doji Himeko, Doji Miyako, Katsuo the White Brother, Soshi courtier, Young Sayo |
| 31 | 9 | Akodo Shogen, Iuchi Kurosho, Doji Tomeko |
| 32 | 3 | Gonta |

## Local Hunyuan receipts

All batch jobs use seed 47. The status is a snapshot of ComfyUI, and a successful export still needs visual review.

| Job | Prompt ID | Latest status |
| --- | --- | --- |
| `side_miyoshi_geometry` | `79bcf2e3-f6aa-4f01-81e5-6b5dd3c8585d` | Success |
| `side_seigen_geometry` | `622c3fd3-7eb8-4d59-a2e2-7224ec9dd789` | Success |
| `side_sariko_geometry` | `66c192d4-2e5c-449f-82eb-3c8d6f49ee10` | Success |
| `side_haku_geometry` | `bf78d89f-05f2-4416-8a69-cb8e0ff70cbe` | Success |
| `side_h_tamori_geometry` | `fe470076-8679-4a7a-a198-73e9faa0e962` | Success |
| `side_kenshai_geometry` | `195620bb-5023-46c7-9bed-207dbd33fc50` | Success |
| `side_oharu_geometry` | `971023ad-2797-4bca-8e2f-24d1eff5f53c` | Success |
| `side_yachiko_geometry` | `3b1c3585-18f6-4762-a2ee-085aec71fa45` | Success |
| `side_h_guide_geometry` | `f5aa6c2f-c9d7-477d-bc82-ec28934c0a5e` | Success |
| `side_kitsukiclerk_geometry` | `a1d26fe8-b7b9-41a7-875b-62f18ad269eb` | Success |
| `side_miyoshi_paint` | `37349191-032e-44ee-ab83-3b4dbabf4700` | Success |
| `side_seigen_paint` | `ce5eb081-a1c1-4e08-9be8-4d6ce1a81150` | Success |
| `side_sariko_paint` | `e4d80136-4234-4914-93f7-6e26cc9872a7` | Success |
| `side_h_tamori_paint` | `ce5764a9-3b5d-41eb-beab-030482594afd` | Success |
| `side_yachiko_paint` | `4edb8041-e5e2-49fd-a73a-8b9c8da8d20a` | Success |
| `side_hostess_geometry` | `23142a68-1c47-4d0b-a98d-66dfaabed376` | Success |
| `side_cartdriver_geometry` | `f1e7e3cc-538d-4fd9-a29e-f6a1e1dd8bc5` | Success |
| `side_diver_geometry` | `76316195-07b1-48a9-bd8e-74583be3c0cf` | Success |
| `side_oharu_paint` | `d4786a3b-829a-4a22-aeaf-2ecbc4ab71fe` | Success |
| `side_kitsukiclerk_paint` | `b6a3664c-7d11-43fa-89bd-0bf8b20ef0d7` | Success |
| `side_hostess_paint` | `0b143a32-b03f-4759-8f47-dc867d114cb4` | Success |
| `side_cartdriver_paint` | `6aa4f355-4eb1-48ad-8967-d51bc63fcce2` | Success |
| `side_rika_geometry` | `b8845561-50b1-45c7-809b-8903fe3602c8` | Success |
| `side_oyuki_geometry` | `21672716-9ea3-4ee6-852e-2e238edc6174` | Success |
| `side_dojipoet_geometry` | `de46199d-4992-4559-9ac7-09ea70608aec` | Success |
| `side_healer_geometry` | `fb02d5cc-ce9c-4c2a-8af0-d1b3daa2b644` | Success |
| `side_priest_geometry` | `366dc555-8f77-4eec-b6ba-ae26da1ef0eb` | Success |
| `side_courtier_geometry` | `c508d5ae-42a2-4a30-9d35-d513da8d7e56` | Success |
| `side_acolyte_geometry` | `7dd1d000-b95c-4ea5-b641-cc66fd05800a` | Success |
| `side_hagane_geometry` | `86e45ab4-e5f7-4a9c-a165-2627e11e8b96` | Success |
| `side_dojipoet_paint` | `4d3e1e62-a721-45d5-9c5f-578717e9b161` | Success |
| `side_courtier_paint` | `69e3732e-7c14-4fdd-a34d-7a158bfa803f` | Success |
| `side_rika_paint` | `e9621e15-a6a1-4fd8-a193-ea2a1c4456a3` | Success |
| `side_oyuki_paint` | `66b5a22a-df07-4487-bcaa-c0bf77be8e1b` | Success |
| `side_shinken_geometry` | `79029800-1c32-454d-a3bd-82f90e93de50` | Success |
| `side_sailor_geometry` | `8e5c9d5f-026a-4d8e-990e-81370eb2894a` | Success |
| `side_karo_geometry` | `c259fa9b-0a56-4219-8419-d23fb6e35d9c` | Success |
| `side_magistrate_geometry` | `27479e7b-b4c2-4cc3-8899-7f5ec6f4f81d` | Success |
| `side_mobleader_geometry` | `2f3707ec-c38b-45a2-8de2-af39674e560c` | Success |
| `side_pedlar_geometry` | `d3f5711a-d47c-46ca-af31-4a352e12ad90` | Success |
| `side_sergeant_geometry` | `69289280-8412-4c63-a967-1c608979f4f1` | Success |
| `side_norie_geometry` | `174c84e6-f158-4771-bbbe-160025fa6449` | Success |
| `side_tsune_geometry` | `a198f199-d304-4c35-9db1-cdbfb6a93ddb` | Success |
| `side_mami_geometry` | `c5c33f14-421b-4d83-97c2-6b6f693b7cef` | Success |
| `side_mizochi_geometry` | `75eb9817-d30c-4db9-8de2-1c0c77753245` | Success |
| `side_incense_geometry` | `abd9d440-be6e-4909-b125-e1d0e02f964e` | Success |
| `side_jadeclerk_geometry` | `91c0d408-6e33-4899-9cb7-ed34d53f3e78` | Success |
| `side_makeup_geometry` | `94a5b342-b1f0-4a05-9da2-596bfe57e8d0` | Success |
| `side_sailor_paint` | `11ac643f-123c-429b-b78f-07693ddcc08d` | Success |
| `side_karo_paint` | `cb0b2555-7c82-4be9-ad5b-ff3ac884c51c` | Success |
| `side_satomi_v2_geometry` | `3a81b7dc-98c8-4831-ab5f-6540405521cb` | Success |
| `side_kakita_sensei_geometry` | `a3cd0b0f-09c6-4327-bb6b-4bf927fe411d` | Success |
| `side_pedlar_paint` | `19107bad-9786-4f6e-aeb3-e94cf907a6c9` | Success |
| `side_sergeant_paint` | `e7383a04-61ab-4832-b8c0-100a3e2bf5cd` | Success |
| `side_mobleader_paint` | `87064950-ae43-4497-9432-514920b57675` | Success |
| `side_mami_paint` | `d2a4e1ec-09f9-439f-af56-4c9e0bdcbf95` | Success |
| `side_incense_paint` | `4a571e79-fa9f-4b44-9a1e-4426d86ce72f` | Success |
| `side_jadeclerk_paint` | `79211e17-707b-4030-b138-64d5629568dd` | Success |
| `side_makeup_paint` | `f9800bd8-fa73-4399-b977-9d0af22ce49e` | Success |
| `side_h_suzume_geometry` | `03cf2a89-99b2-49fa-9b5b-5198cc948409` | Success |
| `side_imuro_geometry` | `7054c9a5-2047-4e9f-8e37-b12e0ee1f2e7` | Success |
| `side_kakita_sensei_paint` | `cb627ebd-74df-4596-8649-22ae6c4fe643` | Success |
| `side_miko_geometry` | `62549a44-c495-4722-9693-9d7be1bf9d0e` | Success |
| `side_censorclerk_geometry` | `b4014fb4-2dad-48bb-8d61-2cd1f53ca1a1` | Success |
| `side_doorman_geometry` | `0be65177-637c-475e-8fbb-f5494714c6cc` | Success |
| `side_roninchef_geometry` | `d91662e4-b641-4ccd-a1ea-9c7981859609` | Success |
| `side_rteacher_geometry` | `f76ab2fe-1734-44ca-b083-da01d92ca833` | Success |
| `side_widow_geometry` | `841faff2-25e0-4fa3-acf4-d78729992cf1` | Success |
| `side_satomi_v2_paint` | `f05b446f-0a38-4d43-8f24-b24593b7441f` | Success |
| `side_herald_v2_geometry` | `4454244f-53e7-4299-8aca-4a7abc2a80c4` | Success |
| `side_h_suzume_paint` | `6c557d27-616d-4d4e-911f-96734a3973cb` | Success |
| `side_imuro_paint` | `5fefb70d-a075-41b8-9baa-76795be180b6` | Success |
| `side_widow_paint` | `da1bb4d9-72b5-4378-8610-927e69a7bb46` | Success |
| `side_takanobu_geometry` | `274c2b6c-f588-4429-888c-2e9cd2b3fa52` | Success |
| `side_seikidera_geometry` | `1fa1e03e-b49f-439e-b082-8ec689715b1f` | Success |
| `side_momo_geometry` | `fd858230-aaf4-4c25-8537-30f9b8bd9ece` | Success |
| `side_snakeelder_geometry` | `ce86d4fa-4c3c-442d-8fc8-8e3e231e90b2` | Success |
| `side_chuto_geometry` | `a4e9da1a-1395-45e2-b32c-60fb96cc0227` | Success |
| `side_mirumotosentry_geometry` | `6b095395-406d-4e4a-b356-c3044c276248` | Success |
| `side_seikidera_paint` | `e109a6ae-d081-4f2f-b9d7-a04921cc2571` | Success |
| `side_momo_paint` | `d58d17b6-dba9-49dd-8560-c7a74cdf7d8d` | Success |
| `side_h_sparrow_geometry` | `cc248ef6-38d0-4279-bb46-e906954dc494` | Success |
| `side_gaijintrader_geometry` | `a9ec85f1-6c62-4207-b1bc-b403550cbd0e` | Success |
| `side_ryoichi_geometry` | `97dbebde-8a26-4607-9bf3-1382298a8ae1` | Success |
| `side_naname_geometry` | `a000e5f6-b10d-457f-b21b-0d2b96b1267f` | Success |
| `side_ozaki_geometry` | `a8158fd9-1ae9-4ba6-bc9b-f042952ad111` | Success |
| `side_nagai_v2_geometry` | `f638c7a0-b98a-416f-9a3f-048befb5ce97` | Success |
| `side_yutaka_geometry` | `a3e4318c-e13f-43cc-ade5-c736c21cf45b` | Success |
| `side_fujio_geometry` | `c875f2e3-7670-4e14-84db-9c7ce8710a65` | Success |
| `side_ryoichi_paint` | `7c852adf-1b16-46b7-b200-07e677258347` | Success |
| `side_ozaki_paint` | `9f9fee70-7274-46de-9f60-eb7ad8a4c910` | Success |
| `side_h_sparrow_paint` | `6d300412-1e3a-4aa7-8fe1-7bbadc1dd4be` | Success |
| `side_iuchifarmer_geometry` | `425784c8-5f29-4c0f-bc43-93407fdf508f` | Success |
| `side_miyubi_geometry` | `61526129-fdaa-4142-a78e-ba829ccf3c9a` | Success |
| `side_drummer_geometry` | `e9b26438-da91-47ae-8934-e98d84440ed0` | Success |
| `side_outfitter_geometry` | `7c77b12f-8317-4eb7-ba62-e612af2b0542` | Success |
| `side_nashiko_geometry` | `88d73720-b635-43b1-8248-20bfadc11065` | Success |
| `side_tsuhime_geometry` | `1a523b31-de19-4adb-b0ee-65873909feb0` | Success |
| `side_muledriver_geometry` | `cb207afc-3622-49c5-81e1-43ed3aecd27a` | Success |
| `side_musician_geometry` | `42d48f8a-bd20-49f2-8a1e-8afa2d6284e8` | Success |
| `side_hidden1_geometry` | `d85b908d-65fb-46a4-b2d6-a9dcd29d0a9b` | Success |
| `side_hidden2_geometry` | `2f3f8311-c72e-4d56-b788-e80014fbb74e` | Success |
| `side_yutaka_paint` | `5f786684-2833-47d0-bad0-cef0a43df6bb` | Success |
| `side_h_stagehand_geometry` | `a900fbaf-1b2b-4aeb-9cc3-391d6ff6b338` | Success |
| `side_tamorimonk_geometry` | `7cf76b60-541d-47c4-880f-f139bda790c9` | Success |
| `side_abbot_geometry` | `b9f1669f-f901-42f2-aa5d-79bffa4f9dfb` | Success |
| `side_actor_c_geometry` | `b1ed5c5f-14ec-4418-84b5-95c9f75801dd` | Success |
| `side_pilgrimagent_geometry` | `67f57b8d-a581-48de-84f2-ffbc013e14cb` | Success |
| `side_craneguard_geometry` | `2cc199ef-70f4-43be-8a17-2af88ee5122d` | Success |
| `side_h_veteran_geometry` | `00415bce-9b74-4bee-a56c-eb12e3435f1a` | Success |
| `side_taneo_geometry` | `88dcda79-fc50-4a0b-b322-d5ff09e95ebf` | Success |
| `side_miyubi_paint` | `6bcdf67b-74f3-4c34-bc9d-a0b8758d1c02` | Success |
| `side_togashi_geometry` | `f16260cd-03cb-4022-870b-e2301f94ecd5` | Success |
| `side_kitchengirl_geometry` | `78b91c9b-d644-4e0c-b888-e31a7914f0ac` | Success |
| `side_twin_geometry` | `58794687-4d86-4bbc-ae0b-f336a802668a` | Success |
| `side_akuro_geometry` | `2fb4f0da-0da9-47e8-a068-dcd4ad06c899` | Success |
| `side_crabboy_geometry` | `61f41e4d-adc4-45c8-9486-44fbe25388bd` | Success |
| `side_drunkactor_geometry` | `a9a01128-b902-469b-bfb8-a7bd152c048e` | Success |
| `side_porter_geometry` | `dca473d0-f116-4ae6-bc0d-653ccd198584` | Success |
| `side_smithboy_geometry` | `56f55de6-3dbf-493e-90af-72c88c0c5a85` | Success |
| `side_tbeggar_geometry` | `94c8f6f3-6dcb-44fd-996b-bcbf337f3e6c` | Success |
| `side_thundermonk_geometry` | `6ad88293-f104-4d94-805f-1f7495f6e71a` | Success |
| `side_bayushiguard_geometry` | `4cdf9c8f-94c3-4bbc-bb8a-a7eb33651fff` | Success |
| `side_dorin_geometry` | `f9fdd853-a7a1-4972-9b0b-0e952f2776f4` | Success |
| `side_seppunguard_geometry` | `1049adc2-d8d2-4de1-a0c2-dacb2a3daf22` | Success |
| `side_craneduellist_geometry` | `9b0be9c9-a7cd-4574-ac11-4cb5db4cf8b3` | Success |
| `side_lionrider_geometry` | `3f79db93-ac35-4614-9938-aec3545dafdc` | Success |
| `side_mbushi_geometry` | `86bf2d7f-c3b1-4a64-9e79-92525f85f024` | Success |
| `side_taxman_geometry` | `62adb0fc-28d8-4f10-a917-739a91a58783` | Success |
| `side_townguard_geometry` | `34ad844a-1b57-4d3d-bf5d-821ccfb35892` | Success |
| `side_takanobu_v2_geometry` | `77091368-8722-4920-9142-bfd525a5f726` | Success |
| `side_mirumotosentry_v2_geometry` | `7f5f0657-577f-49f1-a108-6ac9afddcfff` | Success |
| `side_takeo_geometry` | `29042ec9-dcc1-43e7-bfb9-f13fc1f43c6c` | Success |
| `side_seoko_geometry` | `71e45349-91f1-48a1-b4ed-15d3c588af23` | Success |
| `side_daiyu_geometry` | `ab8630fd-2a46-4b6d-8b8a-a0bf75f49f99` | Success |
| `side_yasurugi_geometry` | `e4685d9e-ee80-405f-8f90-af91f687ff43` | Success |
| `side_noburo_geometry` | `2c352daa-2f91-44b8-b713-39864699dad1` | Success |
| `side_actor_a_geometry` | `46e167bb-b228-463d-8a0f-758b9794a970` | Success |
| `side_yoshi_geometry` | `292d9946-4d20-4405-b785-e55c1c67bce4` | Success |
| `side_iuchisoldier_geometry` | `9b3ef2b7-8af0-46f2-9452-60a58f87e631` | Success |
| `side_takakana_geometry` | `56844d99-bd10-430d-9b1d-7f300d3a521e` | Success |
| `side_h_mirumoto_geometry` | `b8dfc1c3-0596-4467-ae70-93447c372962` | Success |
| `side_tabezu_geometry` | `43c25f23-07ea-4775-8b58-f2b518b219f1` | Success |
| `side_h_shinjo_geometry` | `9851642f-9376-4d72-9be2-3b7f43cb2b8b` | Success |
| `side_h_archer_geometry` | `950f6ba4-621d-4d01-9d28-fd7f67d64e68` | Success |
| `side_h_ferryarcher_geometry` | `048e8a7e-dae2-4ccd-8ad1-f6f8913742d4` | Success |
| `side_h_shrinearcher_geometry` | `b77341b2-0a5e-466f-84cd-7c54642a2e83` | Success |
| `side_tadayasu_geometry` | `8dce10eb-bf4c-4ac7-ac4e-a1356b5bbeb5` | Success |
| `side_craneguard_paint` | `9eb59194-45cc-4213-a2ff-ed75307753b2` | Success |
| `side_shigeru_v3_geometry` | `140ffc2d-a070-4dc1-856c-10473b8e7eac` | Success |
| `side_gontaboy_geometry` | `2adf9fcf-8942-4968-90b0-2d8ed5ba3a3c` | Success |
| `side_h_lamplighter_geometry` | `18ae433e-013e-49af-9ace-5f7fc32ceec1` | Success |
| `side_koshi_geometry` | `b76de0a9-99f3-41bf-97c5-f6f0b1cb77c7` | Success |
| `side_h_veteran_paint` | `b4f77b0a-42c8-45a9-bc0c-b5ae84ff30c0` | Success |
| `side_twin_paint` | `0d5e8c72-7db6-468f-9cba-dcf9ccb937a4` | Success |
| `side_taneo_paint` | `79ea2bc3-fbc8-4277-bcd7-bdf2d760db24` | Success |
| `side_kitchengirl_paint` | `dbf6044c-31f6-4f85-83b3-7fd84945a601` | Success |
| `side_iuchifarmer_v3_geometry` | `44b347ad-5b99-425b-8504-7febda4d75e8` | Success |
| `side_iuchifarmer_v3_paint` | `181d4c73-53fb-42bb-b8df-33f6d47d3823` | Success |
| `side_sakura_geometry` | `809adce3-827b-47c6-b628-7ec1aaf804af` | Success |
| `side_h_scout_geometry` | `ba531286-102c-45fc-b508-cee7890c232f` | Success |
| `side_goroso_geometry` | `7785cbf8-0724-40d4-ae0f-d46197be8b65` | Success |
| `side_tama_geometry` | `011af0e9-4ea3-4baa-b517-a1a659deaf8e` | Success |
| `side_ukita_geometry` | `547f850c-9cd4-499d-b36f-fe9f42dfd0e2` | Success |
| `side_shoju_geometry` | `ff98731c-165f-4606-a901-59f5a3ede867` | Success |
| `side_h_jadearcher_geometry` | `ed9ad57a-e47d-4557-b017-d179a2b9efc0` | Success |
| `side_hidaren_geometry` | `b2569f6a-0cf1-4848-a1e7-f03d44c11aa4` | Success |
| `side_tomoe_geometry` | `677949ec-d709-4aea-acee-cbbfd08f25f4` | Success |
| `side_drunkactor_paint` | `a5d10c25-2c1b-45af-97d4-d00806295792` | Success |
| `side_outfitter_v2_geometry` | `5cf0aaa9-9b38-46b7-a5e6-ac76297a63e9` | Success |
| `side_soshienvoy_geometry` | `8551e4e3-425d-43cb-abe0-46ec8c1a20e7` | Success |
| `side_beggar_geometry` | `e10592c1-038d-4ce7-919f-41a657e7ff26` | Success |
| `side_drunksailor_geometry` | `a3102805-efd4-467d-8150-b6b1ecfe9ca4` | Success |
| `side_gochu_geometry` | `787d4fdc-6f91-490a-b42b-40e96694ea71` | Success |
| `side_h_yojimbo_geometry` | `6cc1eb06-43ef-42e3-a14e-4742513984b3` | Success |
| `side_kasamashi_geometry` | `0346ed20-7296-4547-929a-ca2601f68457` | Success |
| `side_gusai_geometry` | `a2e913f5-3240-4489-aa6b-2d7186139c57` | Success |
| `side_hiruto_geometry` | `17967165-b4b5-4b1d-9afd-6dd46d07cef6` | Success |
| `side_daidoji_general_geometry` | `8f41397e-8c85-451b-bdf6-abdb193b2edb` | Success |
| `side_tbeggar_paint` | `b716c6a5-4595-4b6d-a697-01f96a50e59d` | Success |
| `side_drummer_v3_geometry` | `0709757a-fec6-48f7-81d3-696caa410d39` | Success |
| `side_craneduellist_paint` | `dd5c3311-f96d-4eee-a4e4-e131ad29b790` | Success |
| `side_drummer_v3_paint` | `d7628ea1-9767-4809-b805-b579567daf6f` | Success |
| `side_mayumi_geometry` | `40b67fed-b37d-46a0-b9fd-e98928664106` | Success |
| `side_atsuko_geometry` | `f98b5cb8-743c-42ae-81bd-ec327ca15e40` | Success |
| `side_siko_geometry` | `7f6b2e77-aefa-4e8f-9a79-a4039e9de081` | Success |
| `side_masakazu_geometry` | `398dee5e-2d4f-44d5-b82b-47b45bf6b77a` | Success |
| `side_yakamo_geometry` | `a4f56f21-d007-468a-9db4-15c91ba7b215` | Success |
| `side_kage_geometry` | `3cb3e539-8e58-46cf-9fd6-5aab6428be5a` | Success |
| `side_hanae_geometry` | `e5d25797-f357-43bf-8a18-1136b8659ae7` | Success |
| `side_h_stagehand_v2_geometry` | `1d0d8d05-207d-4188-bd5e-696d9c857dc5` | Success |
| `side_crabboy_v2_geometry` | `f7bf88ca-b71a-48e8-916d-3d6076ffbb3f` | Success |
| `side_togashi_v2_geometry` | `0c669ac4-41a7-4ac7-81a0-cb559d27bc50` | Success |
| `side_akuro_v2_geometry` | `f558fc77-9a70-431f-9552-2e842f8a48e6` | Success |
| `side_takeo_paint` | `094f36a0-05d5-4c66-9270-7f018d0e7d93` | Success |
| `side_seoko_paint` | `890b51ab-512c-4275-8644-6cba33b02530` | Success |
| `side_daiyu_paint` | `1106153c-0e1b-407c-b794-b5fb45581ae2` | Success |
| `side_noburo_paint` | `00b2b493-cc3f-4c3a-9ed9-9924a228d166` | Success |
| `side_zhang_geometry` | `111d44c8-4d14-4983-9efc-46df67267722` | Success |
| `side_noboru_geometry` | `3347d4ac-90e2-4bd3-88c9-27b7723c9075` | Success |
| `side_ryuko_geometry` | `3bdc194f-0f0e-41bd-8ce5-95c200840d69` | Success |
| `side_ichihito_geometry` | `807833d9-ea1b-48f0-bba6-0965cd4eab64` | Success |
| `side_soshiofficer_geometry` | `35375017-5787-4691-b416-d49224efe46d` | Success |
| `side_iami_geometry` | `eda77fd4-029c-4ead-b30c-aa9ba7e50b3d` | Success |
| `side_lionsergeant_geometry` | `8c3339f7-fb7b-4bed-8cea-88591d6b36f6` | Success |
| `side_ryohei_geometry` | `f9d0bb7f-60d1-40a6-87f2-afa12379754e` | Success |
| `side_uyojimbo_geometry` | `6d543a0f-90f1-4017-9e50-559900ce90b7` | Success |
| `side_yosuke_geometry` | `239a21d2-77d2-4346-a723-e92d9c2529fb` | Success |
| `side_yoritomo_geometry` | `e970a5da-adcb-478a-aa3b-eea7fdbff635` | Success |
| `side_actor_a_paint` | `c8ffa98f-2fbf-434f-ad7a-ed2874215aa4` | Success |
| `side_h_engineer_geometry` | `fe26829d-d2ec-4b99-b7fc-fc0d1b41e625` | Success |
| `side_h_sapper_geometry` | `7a22173f-0631-48a7-89c6-ff7bf519afad` | Success |
| `side_h_tsuruchi_geometry` | `111cf311-7dcf-4d12-8356-0f9a00ba0082` | Success |
| `side_fishwife_geometry` | `b7901b44-4afc-444f-877e-acafcaec9144` | Success |
| `side_h_herbalist_geometry` | `c76e18eb-157b-4fd0-82de-79ae18839a8e` | Success |
| `side_mitsue_maid_geometry` | `7d684de7-101a-4ca9-bfe6-a83d9758b1d0` | Success |
| `side_muika_geometry` | `13531c36-7cde-454d-a76f-a458b073ad30` | Success |
| `side_oldwoman_geometry` | `7e8c17ed-608d-4800-a8d9-aecc8edebfe0` | Success |
| `side_umebaa_geometry` | `a3a8ea49-d63b-4023-a8b2-fb643a619a91` | Success |
| `side_bargeman_geometry` | `423d53c0-b118-4ce8-acc7-af495bdc785b` | Success |
| `side_ebisu_geometry` | `f0ff9fa7-12d3-43a4-8e19-1d7aa70d8a48` | Success |
| `side_ff_fisherman_geometry` | `24dbdb3b-86c3-4ce7-8cf1-a448376b40f1` | Success |
| `side_h_hanabi_geometry` | `c98c5834-d92a-47ff-93e2-357587a5851f` | Success |
| `side_pigeonkeeper_geometry` | `04721f3d-ef10-42b0-9f0a-59573bebb941` | Success |
| `side_servant_geometry` | `d4beb335-2667-446e-aaef-a585258715c4` | Success |
| `side_shipmaster_geometry` | `75a2afc1-8a0c-438c-ab85-c0dbf8cc8724` | Success |
| `side_shrinepeasant_geometry` | `47bf064b-0d48-4cf6-85b6-e70b49d89af0` | Success |
| `side_hyobe_geometry` | `4a162ae4-516d-4afc-9fdc-c2ef07b2730f` | Success |
| `side_takanobu_v2_paint` | `8c7b6ef5-7901-4d33-ac29-31e254e12d45` | Success |
| `side_mirumotosentry_v2_paint` | `cf1deba8-622e-47ca-86a8-b9253ee69ada` | Success |
| `side_iuchisoldier_paint` | `7cbf80a3-b8db-472f-ae71-b7dc55c79ce0` | Success |
| `side_tabezu_paint` | `3faff99b-92ea-4621-bcc8-ba7660bd72f5` | Success |
| `side_h_shinjo_paint` | `fbe80e49-16f8-4cee-91f3-2ea162de42d2` | Success |
| `side_h_archer_paint` | `a86f019f-ee0a-4c2f-b712-94fded8106f6` | Success |
| `side_h_ferryarcher_paint` | `208afd8c-f4c0-4d99-ba94-dad5c5122b66` | Success |
| `side_tadayasu_paint` | `12ec6ef5-d02a-43cb-9e15-57af40a3342e` | Success |
| `side_sakura_paint` | `b6d2c8a6-5da2-4e93-a620-4bcac9f3333d` | Success |
| `side_h_lamplighter_paint` | `515255de-073c-4c61-940a-9411c9a9f930` | Success |
| `side_koshi_paint` | `fa7f25f4-4035-431f-916c-a07444dd1224` | Success |
| `side_tama_paint` | `2fac9254-3763-4439-946a-0061e1fddad3` | Success |
| `side_hidaren_paint` | `0f4fa852-a37f-45be-aa78-ff52cf8cc3d6` | Success |
| `side_h_jadearcher_paint` | `0af5df4f-fbcf-410d-a275-29ccec5a122d` | Success |
| `side_shoju_paint` | `629345e7-f450-4428-bcd9-a8db9008e04a` | Success |
| `side_goroso_paint` | `a769bbf6-03b4-440e-8a60-aade53531ced` | Success |
| `side_gochu_paint` | `30c5fbbf-2218-423e-bf5f-8bc5ed59881a` | Success |
| `side_kasamashi_paint` | `d2b11390-e4c4-4ed6-b0d9-1192f21ed775` | Success |
| `side_gusai_paint` | `519d5d28-cf87-4833-aeb2-154e99faddeb` | Success |
| `side_hiruto_paint` | `fc8f643f-b1ef-4337-9f87-fcce127dcd60` | Success |
| `side_daidoji_general_paint` | `6297eb9a-49d1-4251-b65f-848e982b5e2b` | Success |
| `side_atsuko_paint` | `ac183341-9804-4bec-a4b6-524e719e09f4` | Success |
| `side_masakazu_paint` | `8a5c30dd-aeb2-4b8a-9fad-1e8538e62f98` | Success |
| `side_citizen_geometry` | `1609d613-fcac-4153-87d7-31347b22a37b` | Success |
| `side_maskmaker_geometry` | `929cecb4-ec23-4e9d-b89e-449587069d3b` | Success |
| `side_mirumotosen_v2_geometry` | `ec7b92aa-8159-45a7-92f9-6001a36b28e5` | Success |
| `side_benjiro_v2_geometry` | `edecb9d4-dbd2-420b-a6a8-17b1d0ddab52` | Success |
| `side_karasu_v2_geometry` | `d975f3f5-7794-40fc-8c7a-45dd4c0e9eb3` | Success |
| `side_yakamo_paint` | `16f9cce0-5e25-42ed-b4ad-876a2e075dba` | Success |
| `side_mai_v3_geometry` | `eb943571-81ce-49b1-b232-cffc877cf13f` | Success |
| `side_crabboy_v2_paint` | `c8b3acf7-4754-4f00-a170-661e5e4982f7` | Success |
| `side_akuro_v2_paint` | `80c538d6-13a4-4ab0-bf91-6af248058898` | Success |
| `side_noboru_paint` | `5e17040b-b568-427d-a438-a42010234620` | Success |
| `side_ryuko_paint` | `4d99b517-e46d-4593-a91a-1309db0242c6` | Success |
| `side_soshiofficer_paint` | `65ac5947-a483-4285-823a-e77e94c85986` | Success |
| `side_ichihito_paint` | `b1ed2195-c357-4ed5-8183-259e22a51bf3` | Success |
| `side_uyojimbo_paint` | `415e52f5-f944-41a2-a44b-660f1309ac49` | Success |
| `side_h_engineer_paint` | `e83207e5-e4cd-4de3-b264-787f385a2950` | Success |
| `side_h_sapper_paint` | `b3c9e563-8356-41c1-a244-e95a8a169d97` | Success |
| `side_h_tsuruchi_paint` | `e9a77e3e-1ab4-4ac1-a52f-11b10376693d` | Success |
| `side_fishwife_paint` | `31f7f61c-f437-48b5-8f52-c57dc0fed751` | Success |
| `side_oldwoman_paint` | `2901808f-6bf3-456c-bedf-ac929281c46a` | Success |
| `side_bargeman_paint` | `71e43ec6-5ab4-492a-95f6-a416d69ef8df` | Success |
| `side_ebisu_paint` | `b40f66dd-135b-4b5f-8f66-e549ad47faac` | Success |
| `side_muika_paint` | `7059a419-6d82-4f74-8015-a4e49149c290` | Success |
| `side_h_herbalist_paint` | `b1a36028-fe3e-4bdf-ae57-634ddc42a71a` | Success |
| `side_mitsue_maid_paint` | `b179f8aa-62ef-452d-967c-7e41dfdbc460` | Success |
| `side_umebaa_paint` | `b7fd8ff5-dee1-43e3-8e69-6ef72c552003` | Success |
| `side_h_hanabi_paint` | `5f8827f4-2ba4-4fcb-9395-f49f3fc1f456` | Success |
| `side_pigeonkeeper_paint` | `a3ac5024-7231-4ed1-86a1-5deaa7533c2d` | Success |
| `side_shipmaster_paint` | `42146b0b-8677-4c4f-a5f6-f43105610b40` | Success |
| `side_shrinepeasant_paint` | `bc39759c-cfa8-4729-86ce-1dd00cb41c84` | Success |
| `side_citizen_paint` | `5cca9eaf-37b7-4e5e-88f7-39f6edcc4d7b` | Success |
| `side_maskmaker_paint` | `afd722bd-fc9c-4c33-86a1-63c4292b48c4` | Success |
| `side_mirumotosen_v2_paint` | `82d79120-e803-422b-b8a3-b9fb78a8d6e0` | Success |
| `side_benjiro_v2_paint` | `25709510-918e-4caa-9061-d6a357c347c2` | Success |
| `side_oldpilgrim_v2_geometry` | `567cf470-42de-4b98-b149-5467813e7866` | Success |
| `side_h_yari_v2_geometry` | `42de23ca-c6f0-41d2-aa48-d77ec4f64767` | Success |
| `side_meyako_v2_geometry` | `a2193090-879a-454a-b9d2-e868ba9c9604` | Success |
| `side_karasu_v2_paint` | `8b0c11ff-74d2-4f6d-94fb-00a5873b476b` | Success |
| `side_mai_v3_paint` | `b09bfe10-3bbb-4ce5-b451-8a0a411d330b` | Success |
| `side_oldpilgrim_v2_paint` | `9ebd7ff6-dbbf-452f-a523-07e82d30e240` | Success |
| `side_h_yari_v2_paint` | `dade6002-c1d5-4b61-b597-3e77b1a51f2a` | Success |
| `side_h_agasha_geometry` | `97203d68-c234-4058-855a-e7aad574d627` | Success |
| `side_nishi_geometry` | `f2b631ac-8d18-4c57-9a6b-9cd1334e5ac1` | Success |
| `side_hojiki_geometry` | `7fa6fc90-c9cc-4e1b-8647-746d2ed5d984` | Success |
| `side_drunksailor_paint` | `0f41094a-ea3d-4b16-a46d-03365f1001c3` | Success |
| `side_beggar_paint` | `8ab5e8f6-149f-4eb8-b01c-8a2a2fea89c0` | Success |
| `side_nishi_paint` | `c763fefd-b7d3-4960-a5aa-6bb0284fb20e` | Success |
| `side_h_agasha_paint` | `1202e28e-4376-4791-9dd2-fdfd740ffa7f` | Success |
| `side_xue_geometry` | `27b0dcbb-ee42-43a3-99f1-97f127f80124` | Success |
| `side_matsuduel_geometry` | `ee168797-5d0b-4ffb-bb06-2a9414985cd8` | Success |
| `side_mayumi_v2_geometry` | `9e0967a8-672b-47f1-8b89-c45976f0ce7c` | Success |
| `side_hojiki_paint` | `84595203-6857-4017-a2ae-489bec4663a1` | Success |
| `side_h_iuchi_geometry` | `5a21ea49-9908-490f-852f-80f42602bae4` | Success |
| `side_oshito_geometry` | `f3e7abb7-7c0c-4676-84f4-bcd425c68ceb` | Success |
| `side_atsuki_geometry` | `54f10b79-5fe0-42f4-b61c-201ae2f95049` | Success |
| `side_depura_geometry` | `523b693d-0cb4-4bf8-93c7-2678a7ad6bef` | Success |
| `side_sanae_geometry` | `b142b33a-3d9a-494d-8667-0d94504dfad3` | Success |
| `side_hayato_geometry` | `925ae1b6-64ef-4e38-ae78-03146eab143a` | Success |
| `side_sanro_geometry` | `a6fcade1-4f15-4b00-9a21-3d5eac4497c9` | Success |
| `side_michio_geometry` | `732f3b1d-3d74-4288-a596-d67e308f0e97` | Success |
| `side_keiki_geometry` | `65872a9e-5417-42e2-a93a-73d47c9644b5` | Success |
| `side_kuhime_geometry` | `d67efe47-f39f-43f1-8685-57eb8a4547e9` | Success |
| `side_kasiko_geometry` | `17ac7575-6d4b-4e05-9a63-e97ef023f5b8` | Success |
| `side_kumpei_geometry` | `4e93ec0a-7a65-4e30-b344-6d12718c638f` | Success |
| `side_masanori_geometry` | `4bb2736e-d351-49c4-83ba-3f4f0353024c` | Success |
| `side_kyumi_geometry` | `ba8311f7-af16-445e-933d-43d1be554bf8` | Success |
| `side_akodorin_geometry` | `8fed9b53-82f7-40c5-8dd4-8aae72555ef0` | Moved earlier |
| `side_sadanobu_geometry` | `28f95eee-b4e4-4419-85fa-8342151193ec` | Success |
| `side_oshito_paint` | `5bab487f-8be6-4b7c-b465-40ee921071a1` | Success |
| `side_xue_paint` | `96def525-6dce-471b-b66b-24bf944f0d7e` | Success |
| `side_h_iuchi_paint` | `1dbd6140-a130-475d-be29-153e92c0b126` | Success |
| `side_beggarmonk_geometry` | `6a509352-a1e3-49fd-9714-0572137018cd` | Success |
| `side_clerk_geometry` | `8032aa9f-4474-496e-afa3-a9990090264e` | Success |
| `side_ferryman_geometry` | `a0ddca54-b0bf-4dea-9cad-8ec75e177c66` | Pending |
| `side_ff_boatman_geometry` | `168bf031-7faa-48bc-b0df-eeb5de78a040` | Pending |
| `side_gatekeeper_geometry` | `86cf39bc-3235-4305-b5dc-eb68ae56fadb` | Pending |
| `side_h_fisherman_geometry` | `765fc4e9-22d7-433b-b0fd-96d72f085c22` | Pending |
| `side_hiro_geometry` | `bdc06d7c-e179-4622-bbc1-bca7d32100aa` | Pending |
| `side_hitoro_geometry` | `e030e596-fbab-4d01-aedb-01ebfef2d969` | Pending |
| `side_kosai_geometry` | `5d451e9f-6478-4b37-8d78-51c01a55663c` | Pending |
| `side_merchant_geometry` | `2ef81db9-0d3d-459d-8b5d-7e30155d5f34` | Pending |
| `side_mosuke_geometry` | `bd163ab1-adf4-4334-a599-4eb754a1f8b1` | Pending |
| `side_riichi_geometry` | `3d6b9c31-37be-4cf6-8f4e-97002df17423` | Pending |
| `side_senior_student_geometry` | `d84dfefb-8e47-4e55-a755-323269429b1b` | Pending |
| `side_swordsmith_geometry` | `db3ee6aa-68ab-4994-8627-03736c373bee` | Pending |
| `side_veteran_geometry` | `a2125aad-cf54-4978-bb64-91d372cf1076` | Pending |
| `side_yodo_geometry` | `be937c47-dcf6-4977-9619-550ff4c19ea3` | Pending |
| `side_ushimo_geometry` | `da0c0c5a-cce0-450b-b087-8492faa42f30` | Moved earlier |
| `side_actor_b_geometry` | `195c6deb-4b95-4be4-b25b-d71f5234b449` | Pending |
| `side_campfollower_geometry` | `3c44957a-ec17-4bf2-b6fb-7245b0a2d0b6` | Pending |
| `side_kurako_geometry` | `11cca3b7-1622-4e77-bb05-1e46743b82d4` | Pending |
| `side_sanae_paint` | `f47cb5e8-b5c3-4157-b2a1-17113814972f` | Success |
| `side_hayato_paint` | `d93a5ab3-57ac-440a-9c6a-65244d014487` | Success |
| `side_h_bomonk_geometry` | `82045fa4-7743-4355-9e9f-eb04061a25a7` | Pending |
| `side_nihime_geometry` | `16d9b8c9-e6c7-4021-ba2b-314c3bd91bbb` | Pending |
| `side_yasurugi_v2_geometry` | `133e509c-6a16-4b78-93fe-6cb046e0904a` | Pending |
| `side_h_moshi_geometry` | `e370a731-37bd-4017-ab00-0170c3486e03` | Pending |
| `side_h_windpriest_geometry` | `07a0202b-e8d2-4737-961b-79a301c4c341` | Pending |
| `side_hikaru_geometry` | `2c3a3488-64dc-4582-9fbe-7e52f85b1c9f` | Pending |
| `side_hatomu_geometry` | `217cac51-4238-4dd4-aa98-5dccbac0d3c7` | Pending |
| `side_asahina_geometry` | `4dddc7a5-325e-4970-9d4d-eb43cf3f8eac` | Pending |
| `side_akuja_geometry` | `b242d9bb-141a-4edc-8c15-836978241bd3` | Pending |
| `side_shahai_geometry` | `8618478a-82ac-447d-bdd5-701726e2a620` | Pending |
| `side_ikomabard_geometry` | `7b012a47-a04a-4339-a5b0-589d42311c2d` | Pending |
| `side_dojiaoi_geometry` | `11114f20-d761-4448-9253-e97799b40740` | Pending |
| `side_empress_geometry` | `20307d38-e667-4a21-80a9-ea725ab1edeb` | Pending |
| `side_palecourtier_geometry` | `75be9c77-fc36-4377-bbfd-0dab11c5793f` | Pending |
| `side_shiruko_geometry` | `c2e7902f-f7b1-498c-abc8-9cb3cc966aac` | Pending |
| `side_akiko_geometry` | `78604aef-82e5-44ef-acb2-2dd744d2f3c2` | Pending |
| `side_mutsuye_geometry` | `3283eb9a-531d-48a7-a5de-c6e29a20ae84` | Pending |
| `side_taira_geometry` | `c15f39d8-f7db-4d10-9dbc-822d45300b8a` | Pending |
| `side_ryozo_geometry` | `516a3ecd-65de-491f-b2f8-d46679fc56cd` | Pending |
| `side_katsutoshi_geometry` | `0797e080-219d-411e-bd74-d44ac73e8b9d` | Pending |
| `side_netmender_geometry` | `b8204f56-4794-4846-b7cd-7a1e75d067d9` | Pending |
| `side_shrinekeeper_geometry` | `b484625c-6e28-49b3-8908-8ca2d6552421` | Pending |
| `side_kafu_v2_geometry` | `baf36598-0582-46db-a7c7-f4153e58fef8` | Moved earlier |
| `side_siko_v3_geometry` | `e48f23da-1ebb-4266-b951-734b9e72fcd8` | Pending |
| `side_kenshai_v3_geometry` | `e9d7e5b3-4c34-4500-b5f9-002310b66b21` | Pending |
| `side_sanro_paint` | `93bb4d4d-aa51-4af5-a640-c415984973d0` | Success |
| `side_keiki_paint` | `88a03afd-6361-4226-b56b-d209f2843ace` | Success |
| `side_kuhime_paint` | `daebda19-452b-4437-80e4-29360db7c205` | Success |
| `side_michio_paint` | `cd47d1d5-2857-44c3-9107-bfc4a5fbc1d8` | Success |
| `side_smithboy_paint` | `de3f9d1e-792b-4e3e-aa21-16401f1da3cc` | Success |
| `side_ushimo_geometry` | `d8e5ae60-b49c-4b02-9900-089bb6b41259` | Success |
| `side_kafu_v2_geometry` | `d86ba24f-108a-4c29-8060-f29e582f4fa5` | Success |
| `side_kasiko_paint` | `0efdef38-3218-48ab-a61c-fa13fe50281d` | Success |
| `side_kage_ch3_geometry` | `783da005-7245-4ad4-b0b2-feaa0a877017` | Success |
| `side_gonta_geometry` | `3d5b3e58-f246-42d7-a4fe-f7dace2eb52c` | Success |
| `side_ashimita_geometry` | `b50197c1-64b1-4b8c-9fab-d19a06d4817a` | Success |
| `side_akodorin_geometry` | `5d80dd46-42b5-4bb0-95fd-a932ee8648f4` | Success |
| `side_haku_v2_geometry` | `161d1bc8-9987-4859-8d88-95e4f091daf3` | Success |
| `side_sachiko_geometry` | `4b82772b-a39a-4243-a30f-6c829f61a741` | Success |
| `side_ushimo_paint` | `49b86d5f-8ce3-402a-9bc7-b8ab2d0f11c0` | Success |
| `side_kafu_v2_paint` | `96cfdaa0-cc31-4ae2-8868-d5ff338b2ebb` | Success |
| `side_ashimita_paint` | `b483d0d3-1cbe-4bf6-8791-810721b5522b` | Success |
| `side_lionrider_v2_geometry` | `799f3b2a-ccdf-46a8-9199-ed81ccf2bd5f` | Success |
| `side_akodorin_paint` | `1f9174aa-17ce-4bdf-b2b9-51a9d17eb951` | Success |
| `side_rui_geometry` | `c5466051-b708-42e5-a585-097c8e451690` | Success |
| `side_hanae_v2_geometry` | `2631d838-de46-44c2-b515-31fd013bd0d3` | Success |
| `side_lionrider_v2_paint` | `97a8bf85-357d-48e0-b191-38773cf4ffa7` | Success |
| `side_sachiko_paint` | `d18fc53a-228f-4ee7-94d9-40ff60b4e218` | Success |
| `side_gonta_v2_geometry` | `bd419631-91b6-4609-93c5-10a52f427655` | Success |
| `side_haku_v2_paint` | `e1fed7a0-48ac-4904-a3af-f10a63ef3242` | Success |
| `side_jinnai_geometry` | `bf0f5ad2-4c8f-4793-a2c1-7a8a5f2c334b` | Pending |
| `side_sakeseller_geometry` | `2db9d4c3-b122-4e76-8a8c-bf6c955d11dc` | Pending |
| `side_pilgrim_geometry` | `e0befde3-d27c-45d5-9d42-9dfa55d59f86` | Pending |
| `side_kitechild_geometry` | `828807bc-abc4-4c6a-9f85-cbb3336f0b74` | Pending |
| `side_hojato_geometry` | `cb408a61-3f57-4974-9f0a-620fe3c28e8c` | Pending |
| `side_toturi_geometry` | `ba29285f-5024-4479-9325-4d6af1b8acc9` | Pending |
| `side_keiyomi_geometry` | `247bc526-404b-451b-b75d-e7c992aee6db` | Pending |
| `side_tadaka_geometry` | `3bb8b865-d92d-4091-a011-0512703f2158` | Pending |
| `side_yasu_geometry` | `ce7aac32-d1ee-4e8f-8908-c6529d7a8d67` | Pending |
| `side_h_jadeseller_geometry` | `9bde18fe-087a-4576-bc8c-c51d7bc4ce5f` | Pending |
| `side_herbseller_geometry` | `93dbe08b-be1c-469d-8488-aba0035d606d` | Pending |
| `side_hanae_v2_paint` | `1421c26b-3668-4c91-b824-2be64ac32478` | Success |
| `side_rui_paint` | `3c481363-4454-4651-91bd-f773a31004ce` | Success |
| `side_kage_ch3_paint` | `01769639-935e-4599-adf3-f1be67984554` | Success |
| `side_kumpei_paint` | `78984534-95b0-4972-9560-ec6cd486ef96` | Pending |
| `side_masanori_paint` | `e4cc6c33-d046-48a0-8aec-29c5e9efeef1` | Running |
| `side_kyumi_paint` | `dcf31d5f-654d-4397-8b50-2d0e5b6d2cd7` | Success |
| `side_sadanobu_paint` | `25f78d84-a50c-4208-94c0-c30efe45baaf` | Success |
| `side_clerk_paint` | `ec2acacf-b902-42f8-8d00-92c2f708ed3e` | Success |
| `side_gonta_v2_paint` | `26740cc0-de63-48b4-be0e-e07116fc5c9f` | Success |
