# Editor coverage and previews

No editor is currently classified as **full support**. Coverage describes which
functions are exposed, not compatibility with every save variant or successful
in-game loading. Automated checks and native-file inspection are separate evidence;
the application's Help & details view explains both for each game.

| Game | Feature coverage | Current scope / principal gaps |
| --- | --- | --- |
| ELDEN RING | Partial | Revisions 65–261 with the known layout. Supported stackable goods can be added to held inventory; known existing weapons can be upgraded when their saved references agree. NG+ edits scaling only, not a story restart. Named FACE appearance sliders and the saved death counter are editable; models, unknown face blocks, body type and presets are preserved. No new weapons, quests, transfers, console or Nightreign support. Use edited saves offline. |
| RESIDENT EVIL | Partial | Recognized gameplay sections from the native directory. Known inventory/item-box identities and the next clean empty box entry are editable. Other sections, capacities, player identity and story remain unchanged; no new campaign slot is synthesized. |
| RESIDENT EVIL 2 | Limited | Saved difficulty, player health, existing quantities, reward/library flags, completion/challenge records and Ghost Survivors counters. Unknown identities, adaptive rank, story and reward delivery are not synthesized. |
| RESIDENT EVIL 3 | Limited | Health, existing quantities, shop/reward flags and existing completion/challenge/combat records. Difficulty IDs, complete inventory and reward dependencies remain unmapped. Console samples do not prove native Steam compatibility. |
| RESIDENT EVIL 4 | Limited | Points, Spinels, existing quantities and profile-scoped costume/accessory/extra-shop/challenge flags. Unlocks use exact identities where present; several names, money, player health, complete weapons/inventory and dependencies remain unmapped. Copied files need the original SteamID64. |
| RESIDENT EVIL 4 (2005) | Partial | Pesetas, difficulty, health and statistics; existing supported case quantities and weapon tune-up tiers. Capacity can only increase; loaded ammunition and geometry are preserved. No new case objects, costumes or comprehensive unlocks. |
| RESIDENT EVIL 5 | Partial | Profile currency, costume/ammo/filter/library and 45 figure flags only. Infinite-ammo flags do not grant weapons. Weapon upgrades, inventory and story remain unchanged. |
| RESIDENT EVIL 6 | Partial | Skill points, Mercenaries flags/results, uncollected emblems, named existing ammunition/herb reserves and equipped campaign/extra-mode slots. Depleted mapped reserves can be refilled; weapon and unknown count words remain read-only. Existing nonzero emblem encodings are preserved. Mode-specific skill compatibility, purchase/unlock state, weapon identities and campaign progress are not recalculated. |
| RESIDENT EVIL 7 BIOHAZARD | Limited | Saved difficulty, player health, existing item-box quantities, restarts and existing DLC mode/completion flags. Inventory beyond the box, upgrade rules and complete unlock dependencies remain unmapped. Console samples do not prove native Steam compatibility. |
| RESIDENT EVIL VILLAGE | Limited | Lei, CP, saved player health, existing stacks, separate content flags and existing lifetime/completion/combat records. Single-item records, loaded ammunition, upgrades, story, challenge completion and DLC dependencies are preserved. Item/content names and game stack caps remain unmapped. |
| RESIDENT EVIL REQUIEM | Partial | Player-specific saved health records, health-table upgrades, existing stacks, mapped attached parts and existing completion/combat/crafting/challenge records. Player names/active variants, unknown item names, stack caps, item creation and original icons remain pending. Capacity upgrades can only increase; loaded ammunition, story and backup inventories are preserved. Gameplay/system files expose different options; content flags are separate. |
| WEBFISHING | Broad | Known item creation/replacement/removal, hotbar and item locks, original cosmetics/appearance/lures, existing quest progress and journal qualities. Selecting equipment grants mapped cosmetic/lure ownership; adding bait synchronizes acquisition. Missing quest records, rewards and unknown dependencies are preserved. |
| RISK OF RAIN 2 | Broad | Profile unlock identifiers and existing numeric statistics, including saved character/enemy/stage/item records. Unknown units/dependencies are explicit. DLC requires ownership; no live-run inventory editing. |
| KINGDOM HEARTS | Broad | Currency, difficulty, saved companion attributes, equipment slots and known ability entries. Identified save-menu level/difficulty mirrors are synchronized. Unknown IDs and unexposed records are preserved. Equipment changes do not exchange bag quantities; per-character magic availability does not upgrade spell tiers. Ability AP and character-specific rules are not recalculated. |
| RE:CHAIN OF MEMORIES | Partial | Card quantities do not rebuild decks or unlock story progress. Existing deck references are preserved. |
| KINGDOM HEARTS II | Broad | Populated save-point records only. Saved party attributes, equipment and ability lists; five main Drive Forms expose equipment/abilities. Known item auto-reload identities are editable for existing slots. Slot counts, story and world variants are preserved; no AP-cost or character-specific ability validation. |
| BIRTH BY SLEEP | Partial | Known commands/abilities, equipped Keyblades, finisher XP and references to existing commands. Observed multi-slot and unknown deck entries are protected. HP counters, complete deck-capacity rules and progression dependencies remain unmapped. |
| DREAM DROP DISTANCE | Partial | Sora/Riku progression, equipped Keyblades, known inventory and existing recognized spirit Attack/Magic/Defense. Spirit creation, boards, XP, party/deck references, story and theater records are preserved. |
| KINGDOM HEARTS III | Partial | Copied files need the original owner’s SteamID64. Party equipment, active weapon and known ability learned/equipped states are editable. Exact mapped equipment acquisition synchronizes; reserved flags are retained. AP costs, character-specific behavior, derived stats and story dependencies are not recalculated. |
| MAX PAYNE | Limited | Weapon ownership, reserve ammunition and painkillers only. Health, Bullet Time, loaded rounds and checkpoint state are preserved. |
| ALICE: MADNESS RETURNS | Partial | Persistent upgrades, flags and collectibles; configuration edits difficulty. Checkpoint position and active outfit are preserved. |

## No-save browsing

Clicking a game with no detected/recent available save opens its editor preview.
The header says **No save data found**. You can browse categories, sections,
search and supported drop-down choices. Numbers and flags are examples, not your
progress. Apply and restoration are blocked, and previews do not enter history.
Use **Open save…** to load a real file; the regular editing controls then return.

Some fields exist only in specific files, characters or populated item entries.
For example, Alice has separate persistent-profile/configuration examples, and
Requiem gameplay/system files expose different groups. A preview illustrates
supported functions; it does not promise that every real file has those fields.

`assets/editor-previews.json` is generated by `tools/build_editor_previews.py`
from the project's synthetic fixtures through the same adapters used for editing.
The packaged resource contains labels, groups, choices, ranges, example values
and artwork identities only. No raw saves, credentials or writable offsets are
included. Runtime preview objects reject patches, and the UI blocks save actions.
The generator/test helpers are developer tools and are not runtime dependencies.
