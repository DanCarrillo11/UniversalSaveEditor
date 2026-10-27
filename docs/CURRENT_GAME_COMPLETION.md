# Complete the current catalogue before adding games

The target is all 23 current PC editors, with useful character, inventory,
equipment, customization, unlock and persistent progression tools wherever the
supported save format can represent them. The latest user request adds GTA V
and RDR2 to this catalogue; it does not imply that the earlier editors are complete.
This document records implemented work and the actual remaining gates. No editor
is marked full support and no completion percentage is inferred from field count.

## Current GTA V pass

v0.45 adds named static wardrobe availability, purchase and seen markers, plus
guarded synchronized current garments for Michael, Franklin and Trevor. Old/new
catalogues contain 1,911/1,888 ordinary entries across the three actors. Unknown
entries, hair/beard/prop equipping, composite outfit assembly and runtime DLC
apparel remain open. Three native references pass file-level masked and combined
checks; successful loading in the game and Enhanced-native checks remain pending.

v0.44 adds named saved-vehicle paint, window tint, smoke/neon RGB and recognized
engine/brake/transmission/suspension/armor stages. Typed maps, model/kit agreement
and metadata ranges protect unsupported setups. Two native files pass individual
and combined exact-span/checksum checks. Vehicle creation/model swaps and complete
body/wheel/livery tuning are still open; no game-load validation is claimed.


v0.43 adds/removes 35 recognized GTA V base-slot weapons per character,
synchronizes carried ammo, equips mapped components/colors and manages shop
acquisition for 40 weapons. Both three/five-cell inventories are gated by their
schemas, with independent color/component encodings. Three native references pass
masked shop edits and combined acquisition/customization with requested-value
reparsing, checksums and unchanged original files. UI staging/reset and previews
include the new tools. This is partial coverage, not a completion percentage.

Full DLC slot acquisition, vehicle creation/model swaps and complete body/wheel/livery tuning, properties, complete apparel/prop acquisition/equipping,
collectible/story/reward dependencies, Enhanced-native validation and in-game
loading remain open. Earlier player, clock and occupied-vehicle tools are retained.

## Current RDR2 pass

v0.41 expands experimental acquisition to 159 explicit ordinary supplies with
custom quantities, and adds synchronized existing-horse names. Native checks
preserve all 834/233/302 original inventory records except explicitly requested
name spans; 146/129/125 missing supplies were added in memory with exact requested
amounts and all ten payload checks. Two matched names passed exact restoration;
two differing inventory/script names stayed read-only. Original files were not
modified. In-game loading and persistence remain unverified.

v0.40 added existing weapon-part selection and compatible leaf finishes. v0.39
added guarded bounties, existing catalog actions and experimental acquisition.
These implementations do not complete weapon/clothing acquisition, new part
slots, stable creation, camp upgrades or story/challenge/reward dependencies.

## Earlier equipment/spell passes

v0.38 adds synchronized camp funds and horse XP, horse cores, 17 history
statistics and horse/gang/fishing compendium counters. Named compendium identity
coverage is incomplete. v0.37 added schema-gated character attributes, synchronized honor,
active-inventory stacks, weapon condition, horse care, compendium flags and clock
time. Three native PC files passed exact-span edits and byte-identical restoration.
This is substantial partial coverage, **not full support**. Acquisitions, clothing,
stable management, bounties, story/challenge dependencies and game-load
validation remain open. [Field-level scope](RDR2_FIELDS.md).

v0.36 adds initial Rockstar PC story editors: GTA V cash/eight skills for each
of its three characters, and RDR2 carried cash. Both GTA V folders are detected;
Legacy references were checked, while Enhanced-specific native validation is
pending. [Exact scope and evidence](ROCKSTAR_PC.md). No complete Rockstar support
or successful edited-save loading is claimed.

v0.35 adds four owned ammunition assignments, ten quick items, six pouch entries
and two owned Physick tears in Elden Ring; corrects KH3 Link IDs and supports
eleven consumable shortcut commands; exposes DDD spirits' stored rank,
disposition and affinity counter; and adds recognized Re:CoM saved level.
[Scope, native checks and remaining gates](COMPATIBILITY_V35.md). None of these
file-level checks certifies game loading or full support.

v0.34 adds ten owned Elden Ring hand/armor assignments, four synchronized native
representations, exact category/ownership checks, atomic swaps and corresponding
fingerprints. Native in-memory checks covered 53 assignments and 28 upgrades;
game loading remains pending. [Scope and remaining gates](ELDEN_RING_LOADOUTS.md).

The v0.32 continuation adds bounded base-game Elden Ring physical equipment
creation: 377 armaments and 559 armor identities, separate copies, native
handles, acquisition bookkeeping and variable record growth. See
[the exact rules and evidence](ELDEN_RING_EQUIPMENT.md). Native creation/reparse
checks passed on 18 records; ten records with insufficient verified padding
stayed protected. Full loadouts, affinities/Ash attachment, world/DLC dependencies
and game-load verification remain open.

The v0.31 continuation adds KH1 shared spell tiers, Donald acquisition
synchronization, six summons, five learned Trinity colors, 99 puppy flags and
unspent Torn Pages. [Exact rules and evidence](KH1_PROGRESSION.md) distinguish
acquisition from story/reward completion. File-level checks passed on 39 native
Steam records; gameplay, AP/equipment/growth and remaining progression gates stay open.

The v0.30 continuation corrects KH2's distinct stock positions/item IDs and adds
conserved equipment transfers, recognized standard-data AP checks, six learned
spell tiers with shortcut synchronization, form/summon/report acquisition and
Drive dependencies. See [the exact rules and evidence](KH2_INVENTORY_AP.md).
File-level checks passed on 59 populated Steam records. Gameplay validation,
complete character behavior, growth/rewards and journal/puzzle/story work remain.

[Functional relationships](FUNCTIONAL_RELATIONSHIPS.md) adds owned Requiem
equipment/weapon references, Elden Ring memorized spell lists, KH1 magic
shortcuts, KH3 known Critical transitions/Munny ledger/companion AI and exact
saved RE4 Remake virtual-stack capacities. These additions have bounded edits,
related-state checks and explicit preservation rules. They do not remove the
unknown-format or gameplay-verification gates below.

The continuation adds RE4 Remake gameplay Pesetas, player/partner health
and increasing native case sizes; one-copy acquisition of 171 base-game Elden
Ring spells; and existing populated DDD spirits' stored level/XP, maximum HP,
Link Points, link count, RGB tint and recognized normal/shiny appearance.
Spell additions passed native reparse checks in 19 character records; DDD edits
passed for 13 spirits. RE4 Remake native Steam and all gameplay checks remain
pending. Unknown formats and dependencies have not been declared complete.

RE2/RE3 expose increasing inventory capacity for recognized main-survivor
records; they do not change hip-pouch events or create slots/items. RE3's shared
console payload passed a capacity reparse check, separate from native Steam
validation. KH2 also exposes seven saved camera/map/vibration/command-menu
options, with other option bits preserved; 59 native PC records passed option
edits and reparsing. In-game effects for these additions remain unverified.

## v0.26 functionality

- KH3: identify the six magic families and five Links by their saved command IDs,
  not acquisition order. Unique entries and clean empty capacity are required;
  unknown and duplicate commands stay protected. Edit learned tiers, Links and
  three four-button shortcut sets. Tier changes synchronize recognized shortcuts;
  disabling a Link clears its matching shortcuts. Explicit shortcut choices must
  reference an acquired command. v0.35 corrects Link IDs and adds owned/equipped
  item shortcuts; sea and form shortcuts remain protected.
  Add known minigame records and counters; timer units and rewards are not inferred.
- ReCoM: 26 card, 13 extra-card and nine friend acquisition flags. Adding a mapped
  card quantity enables its exact flag; conflicting removal is rejected. Known
  completion flags may be added without clearing prior completion. Unknown bits,
  decks and the current scenario are retained. Native flag changes were reparsed,
  but their in-game effect has not been confirmed; HP/CP/sleights remain unmapped.
- KH1: four shared movement-ability entries with enabled/disabled state and
  protected unknown IDs. KH2: Donald/Goofy combat and four ability-use preferences;
  character stats, ability entries and world variants remain unchanged.
- Elden Ring: 263 mapped map visibility flags, preserving existing revealed
  flags. Exact table entries are checked against the known block directory; all
  remaining positions are materialized from that directory. No guessed ID-address fallback is used. These reveal map texture, not
  map-fragment ownership, fast-travel eligibility or quests. Talisman capacity can
  increase from one to four slots; reducing it is blocked to preserve equipment.
- HD Remaster: 131 documented item IDs, compared with the PC item table. The known
  replacement/next-empty-box operations now offer these identities. Unknown 0x59,
  composite/examination state, capacities and unrelated sections remain unchanged.
  Documented single-object entries cannot be duplicated as stacks. Replacing an
  ammo stack with a single object defaults to one copy; explicit conflicts are
  rejected. Full weapon/ammunition caps still require validation.
- RE6: last-selected difficulty and monotonic Mercenaries completion entries;
  existing nonzero completion encodings remain protected. Last-selected difficulty
  does not convert a checkpoint or rewrite campaign completion.
- RE2/RE3: acquisition statistics. RE4 Remake: chapter counters and a campaign
  clear-time record. RE7: item-use statistics and additional existing DLC records.
  Village: existing Mercenaries/DLC records and challenge flags. Requiem: existing
  challenge reward-claim flags. Claim-state changes do not award points.
- Risk of Rain 2: preserve excessively large unknown numeric statistics without
  overflowing a conversion to floating point during load.
- Review screens for all editors list additional exposed values changed by
  synchronization, including KH3 shortcuts and ReCoM acquisition. Canceling the
  review preserves the file and staged edits.

Exact serialized type and object context checks remain mandatory. New RE Engine
fields edit existing records only; they do not grow arrays or synthesize rewards,
progression events, installed content or platform achievements.

## All-game implementation gates

The generated [completion plan](COMPLETION_PLAN.md) is the current concise
checklist for all 23 editors. The table below retains earlier research context;
v0.49 adds guarded Requiem gameplay difficulty and owned Elden Ring talisman
loadouts with exact accessory groups. The old unresolved items do not imply
that existing acquisitions, ammunition/tool loadouts or wardrobe tools are absent.

| Game | Principal remaining gate |
| --- | --- |
| GTA V | Enhanced-specific native-file verification and in-game loading; character availability, weapons/ammunition, vehicles/garages, properties, cosmetics, missions and rewards. Current scope includes player/world/garage fields plus guarded base-slot weapon acquisition, shared ammo, mapped components/colors and shop flags; not online or character creation. |
| RDR2 | Weapon/clothing acquisition, missing component-slot creation, stable/appearance management, camp upgrades, story/challenge/reward delivery and broader revisions. Existing weapon parts and compatible leaf finishes now have checked selectors. Bounties/catalog unlocks are mapped; 159 ordinary supplies have experimental acquisition with custom amounts. Matched existing horse names can be changed together. Runtime GUID allocation, game loading and persistence still need validation. |
| Requiem | Map active player variants, full named unlocks, item caps and complete inventory/weapon relationships. Difficulty value/hash pairs need named identity verification. |
| Village | Name item/content hashes, establish stack caps, weapon upgrades and difficulty identity relationships; validate native Steam payloads. |
| RE4 Remake | Validate the new money/player-health/case fields on native Steam files; map inventory geometry, weapon parameters and complete named rewards. Chapter difficulty records are not gameplay difficulty. |
| RE2 Remake | Full item/equipment identities, inventory-slot state and dependent reward delivery; validate native Steam files. |
| RE3 Remake | Difficulty and complete inventory/equipment/shop dependencies; validate native Steam files. |
| RE7 | Inventory outside the box, exact upgrade and unlock dependencies; validate native Steam files. Use-statistic edits are not health-upgrade grants. |
| HD Remaster | Verify character health/equipment, game-progress/system unlock records and composite item state in the PC layout. |
| RE4 (2005) | Obtain verified case footprints/placement, weapon-capacity tables, acquisition/equipment relationships and unlock state. Live-memory SDK structures alone do not establish save-array serialization. |
| RE5 | Locate Steamworks inventory/equipment/upgrade and campaign records. The inspected public reference editor only maps profile flags/currency/figures; older Xbox/GFWL offsets are not substituted. |
| RE6 | Purchase/owned-skill state, weapon word decoding and campaign checkpoint dependencies. Last-selected settings are not checkpoint conversions. |
| KH1 | Shared spell tiers, six summons, Trinity colors, puppy rescue flags and unspent pages are implemented. AP/equipment/stock dependencies, full growth/character rules, journal/story/reward relationships and in-game verification remain. Shared movement abilities are separate from character abilities. |
| KH2 | Standard AP checks, stock transfers, spell tiers/shortcuts and recognized acquisition are implemented. Complete character-specific behavior, growth/reward rules, named puzzles/journal/story systems and in-game verification remain. |
| ReCoM | Native confirmation of acquisition/completion flags; locate HP/CP, sleights and deck/card-state dependencies in gameplay data. |
| BBS | Resolve Hp1/Hp2 semantics, full command footprints/capacity, command acquisition flags, D-Link/finisher status and story dependencies. |
| DDD | Resolve Dream Eater growth/XP relationships, affinity levels, rank/disposition behavior, boards, creation and full command decks. Stored rank code, disposition index and affinity counter are independently editable; unknown encodings, derived levels and board rewards are preserved. Source deck data still contains large unknown blocks. |
| KH3 | Full character/AP/equipment rules, remaining sea/form commands, minigame rewards and named progression dependencies. Known Link IDs are corrected; eleven owned/equipped consumable shortcut commands are implemented. |
| Elden Ring | Base-game weapon/armor creation requires verified native layouts with enough zero padding. Six hand, four armor, four ammunition, ten quick-item, six pouch and two Physick assignments now synchronize their verified native state. Talisman families/loadouts, affinities/Ashes, Grace/quest/boss prerequisites, gestures, model/preset/mirror dependencies and DLC acquisition/state remain. Base-game spell acquisition and owned memorized loadouts are implemented; in-game loading remains pending. |
| WEBFISHING | Missing quest/collection creation and reward rules, complete customization dependencies and gameplay verification beyond currency. |
| Risk of Rain 2 | Remaining exact names/units/dependencies for profile records and unlocks. Live-run inventory is not represented by the profile editor. |
| Alice | Remaining persistent/configuration rules and gameplay validation. Active outfit/checkpoint stay outside scope per the earlier user preference. |
| Max Payne | Identify serialized health, Bullet Time and loaded-round semantics. Local tagged-stream research is insufficient to label all unnamed player values; public sample download access is limited. |

## Checks

Local tests cover all current adapters and UI examples. The new targeted checks
cover acquisition order/duplicates, known shortcut synchronization, encrypted KH3
output, reserved ReCoM bits, independent characters/slots, map bits/MD5, protected
capacity/completion, HD section preservation and large XML integers.

In-memory reference checks covered encrypted KH3, two ReCoM files, 59 KH2 and
39 KH1 records, eight HD records, RE6, four Elden Ring files (28 characters),
and a native Requiem system profile. All original files remained unchanged.
These checks establish reading, integrity and round-trip preservation; they do
not certify successful game loading, full reward dependencies or every variant.
