# References and attribution

The project is distributed under GPL-3.0-or-later. It uses Python, PySide6 and cryptography. Personal save files are not included. Cover images are included as identification resources; their rights remain with their respective owners and are not covered by the source-code license.

- [Godot 3.5 binary serialization API](https://docs.godotengine.org/en/3.5/tutorials/io/binary_serialization_api.html): Variant types, sizes, and flags.
- [NotNite/webfishing-save-editor](https://github.com/NotNite/webfishing-save-editor): reference for the WEBFISHING file wrapper and field names in `src/game/types.ts` and `src/App.svelte`. Its interface and visual resources are not included.
- [Xeeynamo/KingdomSaveEditor](https://github.com/Xeeynamo/KingdomSaveEditor), GPL-3.0: reference for the PC container, Kingdom Hearts Final Mix fields, and Kingdom Hearts II Final Mix fields and record checksum in `PcSaveArchive.cs`, `PcKh1Factory.cs`, `PcKh2Factory.cs`, `SaveKh1.FinalMix.cs`, `SaveKh2.FinalMix.cs`, and their character and Drive Form models. UniversalSaveEditor adapts knowledge of these structures to a byte-preserving editor.
- [KatRewrites/kh1-save-editor](https://github.com/KatRewrites/kh1-save-editor), GPL-3.0: reference for PNG/sqEX containers and the need to preserve related records. Its tables and interface are not included.

Game names belong to their respective owners. UniversalSaveEditor is an independent project.

`re4_uhd.py` independently implements the original RE4 Steam container. Runtime
property names, mode codes and health ranges were cross-checked with
[nipkownix/re4_tweaks](https://github.com/nipkownix/re4_tweaks); file offsets and
both CRC ranges were verified against a local save without changing it. No
trainer code or personal save is bundled. See [UHD format](docs/RE4_UHD_FORMAT.md)
and [Resident Evil research](docs/RESIDENT_EVIL_RESEARCH.md).

RE4 (2005) uses official platform-free Steam library artwork; its source and
original image URL are recorded in `assets/covers/sources.json`.

Additional PC game references and public-fixture checks are recorded in
[game reference research](docs/GAME_REFERENCE_RESEARCH.md). This includes the
maintained [BFlorry/KingdomSaveEditor](https://github.com/BFlorry/KingdomSaveEditor)
fork and distinguishes source documentation from working support in this app.

`kh_pc.py`, `kh3_pc.py` and `kh_extra_tables.py` adapt ReCoM, BBS Final Mix,
DDD HD and KH III PC schemas, inventory tables, checksums and key derivation
from that fork at `e5eec7403f939d7a94a62d996130d84f59887dda`, GPL-3.0-or-later.
Copyright (C) 2020 Luciano Ciccariello; Copyright (C) 2026 Mikko Mäntylä
(BFlorry). PC contributions are credited to fungualtissue1230 and dedede123.
The adaptations preserve raw bytes, validate bounds and add Python field/UI
integration. See [format scope and public fixture provenance](docs/KH_EXTRA_FORMATS.md).

`maxpayne_save.py` is an independent implementation of the tagged stream,
cross-checked with [Tatsh/dade](https://github.com/Tatsh/dade/blob/master/dade/maxpayne/memoryfile.py).
No dade implementation or extracted Max Payne files are bundled. Factual weapon
IDs and ammunition capacities were checked against the author's local game.

The cryptography dependency is distributed under Apache-2.0 or BSD-3-Clause;
its license texts and the OpenSSL notices accompanying its wheel are included
in THIRD_PARTY_NOTICES.txt. PySide6/Qt retain their upstream licences.

The Steam icon in `assets/platforms/steam.svg` comes from
[Simple Icons](https://github.com/simple-icons/simple-icons/blob/develop/icons/steam.svg),
distributed under [CC0 1.0](https://github.com/simple-icons/simple-icons/blob/develop/LICENSE.md).
Its fill color is adapted for the dark interface. The Steam trademark belongs
to Valve; it identifies the save platform and does not imply endorsement.

KH difficulty values and byte offsets are cross-referenced with the
[KH I Final Mix record](https://github.com/Xeeynamo/KingdomSaveEditor/blob/master/KHSave.Lib1/SaveKh1.FinalMix.cs),
[KH I mode enum](https://github.com/Xeeynamo/KingdomSaveEditor/blob/master/KHSave.Lib1/Types/DifficultyType.cs),
[KH II Final Mix record](https://github.com/Xeeynamo/KingdomSaveEditor/blob/master/KHSave.Lib2/SaveKh2.FinalMix.cs),
and [KH II mode enum](https://github.com/Xeeynamo/KingdomSaveEditor/blob/master/KHSave.Lib2/Types/DifficultyType.cs).
See [difficulty format and validation](docs/KH_DIFFICULTY.md).

The memory-card icon was prepared as a transparent PNG crop from an image supplied by the repository author. Visible marks and logos belong to their respective owners and are not covered by the source-code license.

## Cover art

- Kingdom Hearts, Kingdom Hearts II, and Re:Chain of Memories: replacement cover images supplied by the repository author, without platform headers. Metadata is recorded in `assets/covers/sources.json`.
- [bbs](https://www.khwiki.com/File:Kingdom_Hearts_Birth_by_Sleep_Final_Mix_Boxart_JP.png): original file, image URL, and provenance are recorded in `assets/covers/sources.json`.
- [webfishing](https://store.steampowered.com/app/3146520/): source page and original image URL are recorded in `assets/covers/sources.json`.
- [maxpayne](https://store.steampowered.com/app/12140/): source page and original image URL are recorded in `assets/covers/sources.json`.
- [ror2](https://store.steampowered.com/app/632360/): official Steam library artwork; URL and file size are recorded in `assets/covers/sources.json`.
- [alice](https://store.steampowered.com/app/19680/): official Steam library artwork; URL and file size are recorded in `assets/covers/sources.json`.

Birth by Sleep uses original Japanese Final Mix artwork with its narrow PSP header omitted at display time. The replacement Kingdom Hearts images are shown in full. WEBFISHING, Risk of Rain 2, Max Payne, and Alice use platform-free Steam library artwork.

Risk of Rain 2 compatibility was validated against a local Steam profile supplied by the repository author. Unlock identifiers in `ror2_unlocks.py` were extracted from resource names in `Risk of Rain 2_Data/StreamingAssets/aa/catalog.json` from that installation. The content catalog and profile contain third-party or personal data and are not included.

Alice: Madness Returns research used a local Steam installation and a profile supplied by the repository author. The native persistent-archive serialization order and factual IDs were independently mapped locally. Personal profiles and extracted game files are not included. In-game validation remains pending; see [Alice format and scope](docs/ALICE_FORMAT.md).

- [Wemino/MadnessPatch generated SDK](https://github.com/Wemino/MadnessPatch/tree/main/include/SDK): factual property names and enums. GPL-2.0 implementation code is not incorporated; the reader and patcher were written independently.
- [Official Alice PC manual](https://eaassets-a.akamaihd.net/eahelp/manuals/ALICEMRpcMANOLen.pdf): weapon-upgrade and collectible context.

The `kh_items.py` table adapts `KHSave.Lib1/Types/EquipmentType.cs` from Xeeynamo/KingdomSaveEditor under GPL-3.0. It preserves attribution and excludes story items and unused entries.

The friendly names in `kh2_items.py` adapt identifiers from `KHSave.Lib2/Types/EquipmentType.cs` from Xeeynamo/KingdomSaveEditor under GPL-3.0.

## Resident Evil expansion

The new readers and byte-preserving patchers were written independently from
format facts. Other editors' implementation code, generated schema files,
translations and downloaded saves are not bundled.

- [shinneider/RE5-Save-Editor](https://github.com/shinneider/RE5-Save-Editor): RE5 chaining, additive checksum and factual flag layout; cross-checked on a public Steamworks profile.
- [lightningdotnet/resident-evil-6-save-editor](https://github.com/lightningdotnet/resident-evil-6-save-editor): factual PC RE6 header and offsets; independently checked on a public Steam profile.
- [kvasszn/ree-save-editor](https://github.com/kvasszn/ree-save-editor): RE Engine container profiles and factual property/type identifiers. No code or SDK/translation databases are incorporated.
- [bucanero/save-decrypters](https://github.com/bucanero/save-decrypters): public console examples of RE3/RE7 shared payloads, and Blowfish/SHA1 format references for legacy HD saves. Console samples are not represented as native Steam files.
- [urbanware-org/re-hd-se](https://github.com/urbanware-org/re-hd-se): PS3 field-address comparison only; PC inventory notes and public PC-format bytes are checked separately.
- [SAVE-EDITOR.com's PC HD notes](https://www.save-editor.com/tools/pc_game_save_converter_title_Resident_Evil_HD.html): factual PC inventory addresses and item identifiers.
- [Google CityHash](https://github.com/google/cityhash): CityHash64 adaptation and golden test fingerprints under MIT. Full permission notice is in `THIRD_PARTY_NOTICES.txt`.
- [NIST SP 800-38A](https://csrc.nist.gov/pubs/sp/800/38/a/final): AES-OFB known-answer test.
- [descawed/re0box](https://github.com/descawed/re0box) and [SirCabby/RE0CabbyCodes](https://github.com/SirCabby/RE0CabbyCodes): RE0 container and runtime research; no gameplay offsets are claimed as verified from these references alone.

New Resident Evil cover art comes from official Steam library assets. Source URLs
and file sizes are recorded in `assets/covers/sources.json`. Artwork and trademarks
belong to their owners and are outside the source-code licence.

See [RE5](docs/RE5_FORMAT.md), [RE Engine](docs/RE_ENGINE_FORMAT.md),
[legacy PC boundaries](docs/RE_LEGACY_PC.md), and [validation status](docs/RESIDENT_EVIL_RESEARCH.md).

## Elden Ring

- [ClayAmore/ER-Save-Lib](https://github.com/ClayAmore/ER-Save-Lib): factual PC BND4 block layout, equipment-handle records, character fields, variable section order, profile summaries and player fingerprints. The bounded Python parser and patcher are independent; Rust implementation code is not incorporated. Four public PC fixtures were checked locally in memory and are not redistributed.
- [oisis/EldenRing-SaveForge](https://github.com/oisis/EldenRing-SaveForge): cross-checks of format facts and original-class minimum stats. The `elden_items.py` names and carrying/storage limits adapt 307 existing stackable-goods entries from `backend/db/data/tools.go`, `crafting_materials.go` and `bolstering_materials.go`, under GPL-3.0. Descriptions, quest locations, images and unlock databases are not included. The project's GPL-3.0-or-later license and this attribution cover that adaptation.
- [EldenSave](https://github.com/WhoamiRAGE/EldenSave): secondary format comparison only; its code and item tables are not incorporated.
- [Official Steam artwork](https://store.steampowered.com/app/1245620/): portrait URL and byte count in `assets/covers/sources.json`. Artwork and trademarks remain owned by their respective holders.

See [Elden Ring scope and validation](docs/ELDEN_RING_FORMAT.md). The editor does not claim console or Nightreign support, nor verified in-game loading or online compatibility.

The Elden Ring revision-261 compatibility fix cross-checks the current field
layout and factual Idus Knight / Heavy Knight class IDs and starting stats with
[Kamikaz07/Elden-Ring-Save-Editor](https://github.com/Kamikaz07/Elden-Ring-Save-Editor).
No implementation code is incorporated; native revision-261 validation remains pending.

## Collection presentation and support evidence

`collection_tables.py` adapts KH III `MaterialType.cs` names/order from the
BFlorry/KingdomSaveEditor revision already referenced above, under
GPL-3.0-or-later, Copyright (C) 2020 Luciano Ciccariello. The PC material-array
location is cross-checked in `SaveKh3PC.cs`; unknown indexes remain unnamed.
Elden collection categories adapt the already attributed GPL v3 SaveForge
tools/crafting/bolstering table categories for the 307 supported goods.

`inventory_context.py` independently associates factual RE2/RE3 ItemId and RE4
Remake Item/_ItemId properties from kvasszn/ree-save-editor's schemas with
their exact saved object. SDK assets, translation databases and implementation
code are not bundled. Missing or ambiguous identities do not receive names.
Compatibility evidence summarizes this repository's format documents and the
author's WEBFISHING currency report; it does not infer gameplay confirmation
from an automated test pass. See docs/SUPPORT_AND_HISTORY.md.

## v0.18 party and inventory expansion

- `kh_party_tables.py` adapts factual ability/equipment IDs, names and categories
  from Xeeynamo/KingdomSaveEditor at `37a7a9dde19463a0d5f0c9588c634d6129e536f6`,
  `KHSave.Lib1/Types/AbilityType.cs` and `KHSave.Lib2/Types/EquipmentType.cs`,
  GPL-3.0, Copyright (C) 2020 Luciano Ciccariello. Character and DriveForm models
  cross-check fixed array bounds; the two ability view-models confirm the opposite
  equipped bits. The bounded Python party adapter and choice translation are new.
- `elden_weapons.py` adapts 487 base armament names/reinforcement limits from
  oisis/EldenRing-SaveForge's GPL v3 `melee_armaments.go`, `shields.go` and
  `ranged_and_catalysts.go`. Affinity IDs, icons and descriptions are not bundled.
  Native registry/counter facts, NG+ location and equipped mirrors were independently
  cross-checked against its specifications, regressions, current Kamikaz07 structures
  and public PC files; the bounded reader/patcher is independent.
- `re4_items.py` independently records factual item IDs/names and bounded tier limits,
  compared with nipkownix/re4_tweaks's `SDK/item.h` and `GameFlags.cpp`, and
  dubiousnerd/re4vr-save-editor's documented standard tune-up presets. VR addresses
  are not used as PC addresses; the 12-byte native case region was checked in all
  four local UHD slots. Neither editor's implementation is incorporated.
- `re6_skills.py` independently formats common factual IDs 0..60, cross-checked with
  lightningdotnet/resident-evil-6-save-editor `tables.h`/`fields.cpp` and a public
  native PC profile. Mode-specific skills, generated tables and purchase masks
  are not incorporated or claimed as understood.

See docs/EDITOR_EXPANSION.md for the editable boundaries and validation limits.

## Resident Evil Village (v0.19)

The independent Village adapter uses factual Steam AppID 1196590, Blowfish key
and property/type identifiers cross-checked in kvasszn/ree-save-editor at
`4125e497f1ae84cc746bb4a99da612c48bea161e`: `src/save/crypto/blowfish.rs`,
`src/save/mod.rs`, `src/save/game.rs` and `assets/re8/rszre8.json`.
No upstream implementation, generated schema or translation database is bundled.
`village_context.py` independently restricts existing inventory and content
records by owner ancestry and unsigned identities.

The public `village-data001Slot.bin` from bucanero/save-decrypters's
`re7-checksum-fixer/samples` was inspected in memory in an ignored research
directory. It is a console payload, not a native Steam fixture, and is not
redistributed. See [exact evidence and limits](docs/RE8_FORMAT.md).
The official Steam portrait URL and byte count appear in
`assets/covers/sources.json`; artwork and trademarks remain owned by their holders.

## Original RE2 inventory artwork (v0.20)

`assets/items/re2/supplies.png` is an exact first-two-row crop of the original
RE2 (2019) inventory atlas archived as `Resources/ui0100_iam.texout.png` in
[Squirrelies/RE2REmakeSRT](https://github.com/Squirrelies/RE2REmakeSRT/tree/07db9f610553e6a95cee24aeac99cd1bc6c48e19).
The 27-item manifest adapts its MIT `Program.cs` clipping coordinates and
`ItemEnumeration.cs` IDs, Copyright (c) 2019 Travis J. Gutjahr. The ID domain is
cross-checked with the factual RE2 Item.ID enum from the previously attributed
RE Engine schema. Uncertain herb variants and all weapon/attachment/quest maps
are excluded. Full MIT notice: `assets/items/RE2_SRT_LICENSE.txt`.

Original and cropped hashes, pinned revision and transform details are recorded
in `assets/items/manifest.json`. No AI generation, recoloring, redraw or source
upscaling occurs. Game artwork and trademarks belong to CAPCOM CO., LTD.; they
are outside GPL and are not licensed by the upstream tool's MIT notice.
The independent item resolver uses exact validated save-object identities;
unknowns have no substituted image. See docs/ITEM_ARTWORK.md.

## Original Elden Ring artwork (v0.21)

The 794-entry artwork manifest adapts ID/Name/IconPath associations from the six
already attributed GPL v3 oisis/EldenRing-SaveForge tables (tools, crafting and
bolstering materials, melee armaments, shields, ranged armaments/catalysts), at
`ee1042d7a5bd933f91e6f8a0162e0e0237a1c4c5`. Existing labels must match exactly.
The corresponding archived in-game image files from `frontend/public/items`
are copied byte-for-byte into deterministic ZIP packs; the manifest records
each original path/hash and pack hash. No upstream runtime implementation is
incorporated. No image generation, redraw, recoloring or resampling is applied.

791 images are PNG and three are WebP stored under upstream .png filenames;
Qt decodes from headers. Game artwork belongs to FromSoftware, Inc. and
Bandai Namco Entertainment Inc. and is outside the source-code license.
The software's GPL license does not convey a publisher license to game art.
See docs/ITEM_ARTWORK.md for exact coverage and runtime/validation boundaries.

## Original multi-game artwork (v0.22)
Source mappings, pinned revisions, original image hashes, preview hashes and
transform descriptions are in assets/items/manifest.json. Exact coverage and
pending games are documented in docs/ITEM_ARTWORK.md. All icons/renders are
original game content; large renders use aspect-preserving 128px previews.
No AI generation or redraws. Base ReCoM art does not depict card values/premium.

WEBFISHING ID/icon metadata: NotNite/webfishing-save-editor at
b3687a817700d2b766bf2406dfbd8a2b35bb4bf5, MIT notice in
assets/items/WEBFISHING_ICON_METADATA_LICENSE.txt. Original sprites explicitly
excluded from upstream's software license; game art belongs to lamedeveloper.

RE3 clipping/ID metadata: Squirrelies/SRTPluginUIRE3WinForms at
d70d15c880cfb262c0ced7aa8ce0857dba777897; provider enum at
813f961372ae6646200bdb4748e8fa87c58c202c. MIT notice in
assets/items/RE3_SRT_LICENSE.txt, Copyright (c) 2020 Travis J. Gutjahr.
RE1R/RE5/RE7 icon lookup metadata: SpeedrunTooling/InventoryHUD at
b1385a15c205a7a270d0949388d948712952d904, MIT notice in
assets/items/INVENTORY_HUD_LICENSE.txt, Copyright (c) 2021 Speedrun Tooling.
Resident Evil art belongs to CAPCOM CO., LTD., outside the software license.

Kingdom Hearts original renders/card sprites: edition-specific KHWiki file
pages with upload timestamps, credited individually in the manifest. Artwork
belongs to Disney and Square Enix, outside the source-code license.
Risk of Rain 2 original achievement textures: extracted from installed Steam
Addressables, using exact UnlockableDef icon GUIDs and catalog asset paths.
Artwork belongs to Gearbox Software / Hopoo Games, outside source-code license.
UnityPy and the MIT renanliberato/unity-addressables-id-re catalog parser were
research tools only; their implementation is not bundled or needed at runtime.
Software licensing does not imply a game-art license or publisher endorsement.


Requiem expansion: serialized property/class facts checked against
kvasszn/ree-save-editor at 4125e497f1ae84cc746bb4a99da612c48bea161e.
95 selected short item names and 44 three-tier part identities checked against
original English game text exposed by Synthlight/RE-Editor at
48310c16a915545dc96d254ab59ec69665c31447. Item hashes are independently
computed from UTF-16LE codes. No upstream implementation, SDK schema or
multilingual translation asset is bundled; unknowns remain explicitly unmapped.
Game names and trademarks belong to CAPCOM CO., LTD. Requiem artwork remains
pending; no modded or substitute images are shipped. See docs/RE9_FORMAT.md.

## v0.25 functionality metadata

Additional KH equipment/ability/command/Spirit labels and layout facts are adapted
from the already attributed GPL Kingdom Save Editor sources (Luciano Ciccariello;
BFlorry PC container contributions). WEBFISHING original item/cosmetic/lure names
and serialization facts use the already attributed MIT NotNite metadata at
b3687a817700d2b766bf2406dfbd8a2b35bb4bf5; no new artwork is included.

Elden Ring FACE slider positions/names and the saved death counter are checked
against the already attributed GPL SaveForge metadata at
ee1042d7a5bd933f91e6f8a0162e0e0237a1c4c5 and four public native PC files.
RE5 figure bits and RE6 extra-mode/results/emblem positions use the previously
attributed primary format references and public native profiles. Additional
RE Engine type/property facts use pinned kvasszn metadata 4125e497f1ae84cc746bb4a99da612c48bea161e;
no upstream SDK, translation database or unlicensed implementation is bundled.
See docs/FUNCTIONAL_EXPANSION.md for boundaries; identifiers/format facts are
not a certification of every dependency or in-game behavior.

## v0.25.1 menu and supply checks

KH1 bounded KHSQ pairing and level field facts were compared with the GPL
[KatRewrites/kh1-save-editor format notes](https://github.com/KatRewrites/kh1-save-editor/blob/d168c035ff392029d8fc45688cc08ad99e4dfc94/OFFSETS.md)
at d168c035ff392029d8fc45688cc08ad99e4dfc94, and cross-checked against 40 native PC
records. Difficulty mirrors were compared in those native records. Unverified
summary XP/currency widths are not implemented; no leveling tables are bundled.

Twenty short RE6 reserve ammunition/herb identities use factual IDs from the
previously attributed lightningdotnet editor's tables.h at
baa6a9e0d51f7f8ac2ce26bda6a2a64d74e04919. No upstream implementation or weapon
state decoder is included. Original native count words are retained for weapons
and unknown identities. See docs/EDITOR_POLISH.md for checks and limits.

## v0.26 existing-game completion work

KH3 PC magic/Link/shortcut and minigame positions, ReCoM bitfield models and KH1
shared-ability metadata use the already attributed GPL Kingdom Save Editor
references. KH2 combat/ability-use enum labels were additionally compared at
`e5eec7403f939d7a94a62d996130d84f59887dda` in
[BFlorry/KingdomSaveEditor](https://github.com/BFlorry/KingdomSaveEditor).
Copyright (C) 2020 Luciano Ciccariello; PC work by Mikko Mäntylä (BFlorry).
Xe.BinaryMapper's documented bit packing was inspected as a research reference;
its implementation is not bundled. Magic acquisition order is independently
resolved from unique saved command identities, with unknown/duplicate protection.

Elden Ring map names/regions, exact precomputed bit positions and talisman-slot
facts are adapted from GPL oisis/EldenRing-SaveForge at
`ee1042d7a5bd933f91e6f8a0162e0e0237a1c4c5`. The 263 MapVisible entries use exact
positions materialized from EventFlags and the known eventflag_bst directory.
Their overlapping table/directory positions are checked for agreement. No ID-linear fallback formulas, quest
or boss data, unsafe maps, new artwork or upstream runtime is incorporated.

131 HD Remaster item-ID facts were compared with the
[PC save converter's item table](https://www.save-editor.com/tools/pc_game_save_converter_title_Resident_Evil_HD.html).
Short factual labels were also compared with the previously attributed
urbanware-org/re-hd-se Inventory.cs at
`ce27876918d63151d142d225d8736d931e6fb03a`; no implementation is reused.
Unknown ID 0x59 is excluded and composite item state is not inferred.

Additional RE6 completion/last-selected setting facts use the previously
attributed lightningdotnet reference. Additional typed RE Engine record/property
facts use pinned kvasszn metadata
`4125e497f1ae84cc746bb4a99da612c48bea161e`. No upstream SDK or message database is
bundled. See docs/CURRENT_GAME_COMPLETION.md for native checks and remaining gates.

## Current equipment and spell relationships

Requiem equipment/shortcut class IDs (`df233e4a`, `1be9729e`), the exact
`_Equips`/`_Shortcuts` property contexts and RE4 Remake virtual-stack capacities
use the already attributed kvasszn metadata at
`4125e497f1ae84cc746bb4a99da612c48bea161e`. The independent implementation only
reassigns resolved owned references; no upstream SDK or serializer is bundled.

Elden Ring spell identities/names and the 213 memory-slot costs are adapted
from GPL oisis/EldenRing-SaveForge at
`ee1042d7a5bd933f91e6f8a0162e0e0237a1c4c5`,
`backend/db/data/{sorceries,incantations,spell_memory_slots_generated}.go`.
`backend/core/spell_writer.go`, `hash.go` and the application equipment code
were compared for native sentinel pairs, compact-list rules and capacity.
Only factual labels/costs are included; descriptions, original regulation
assets, images and upstream runtime code are not redistributed.

KH1 shortcut positions/family IDs use the previously attributed GPL Kingdom
Save Editor FinalMix/CommandType models. KH3 observed Critical ability words,
positive-vital transitions, Munny ledger positions and companion-AI enum facts
were cross-checked with GPL
[thirteenth-order/kh3-save-editor](https://github.com/thirteenth-order/kh3-save-editor/tree/0e09edce084c3a170dcfca404160669aced96713)
at `0e09edce084c3a170dcfca404160669aced96713`. Implementations are independent;
only recognized representations are changed. Native file reparsing and
synthetic preservation tests do not imply game-load validation.

## Following gameplay-field continuation

RE4 Remake Pesetas, player/partner backup subclasses and S–XXL case enum facts
are checked against the previously pinned kvasszn RE4 metadata. The new
[RE4R-SaveForge](https://github.com/pptt0778-boop/RE4R-SaveForge/tree/7a8b53a2d559adb5e2f5d1194d567d89dbd20409)
reference (MIT) at `7a8b53a2d559adb5e2f5d1194d567d89dbd20409` was inspected for
field names. Its pattern-scanning patchers, blanket weapon/ammo cheats and
item substitutions are not incorporated; this editor requires native object
ancestry and typed unique properties. Native Steam validation remains pending.

Base-game Elden Ring spell acquisition uses the already attributed GPL
SaveForge spell goods identities (MaxInventory 1/MaxStorage 0) and bounded
common-inventory/registry acquisition facts. 171 base-game IDs are eligible;
the 42 unowned DLC spell IDs stay protected. No quest/reward logic is copied.

Additional DDD primitive field positions are independently checked with
[osdanova/KH_Editor](https://github.com/osdanova/KH_Editor/tree/a37a708462070eb45dba1ead387557a111dac8ae)
at `a37a708462070eb45dba1ead387557a111dac8ae`,
`Model/KH_DDD/DDD_spirit/DDD_spirit_Entry.cs`, plus a native PC HD archive.
That repository has no declared license in the inspected tree. It is used
only as a reference for factual positions/encodings; no source implementation,
compiled program, assets, dictionaries or name-encoding code is redistributed.
The application patches selected existing native bytes independently and
preserves all unknown board, affinity and party/deck state.

RE2/RE3 increasing inventory capacity uses the previously pinned kvasszn
metadata for the exact gameplay section list, inventory array, survivor enum
and `_CurrentSlotSize` S32 field. Only supported even capacities of the two
primary survivors are changed. A public shared RE3 console payload from the
already attributed save-decrypters references was reparsed in memory; no
fixture or upstream SDK data is redistributed, and native Steam/gameplay
validation is not claimed.

## KH2 stock, AP, magic and acquisitions

`kh2_items.py` now adapts the stock-position names from
[BFlorry/KingdomSaveEditor InventoryType.cs](https://github.com/BFlorry/KingdomSaveEditor/blob/e5eec7403f939d7a94a62d996130d84f59887dda/KHSave.Lib2/Types/InventoryType.cs),
GPL-3.0-or-later, Copyright (C) 2020 Luciano Ciccariello. Stock positions are
independent of the EquipmentType IDs used by character slots and artwork.

Factual item/stock pairs, category/parameter links, standard AP costs,
equipment AP bonuses and level AP values were independently read from
[OpenKH/OpenKh](https://github.com/OpenKH/OpenKh/tree/7a3b945c538d32c6a285128c98aefba093f52ceb)
`OpenKh.Tests/kh2/res/item.bin` and `lvup_fm.bin`. The Item and Lvup source models
cross-check record bounds. OpenKH's Apache-2.0 license is reproduced in
THIRD_PARTY_NOTICES.txt; the original binary fixtures are not shipped. AP cost
uses entry byte +7, consistent with Scan 2 / Upper Slash 4 / Combo Plus 1 and
[published game-guide examples](https://www.piggyback.com/en/kh2_e_samplepages/).
Save-model files copied into OpenKH from KingdomSaveEditor carry their own GPL
notices; their code is not copied by this continuation.

Magic bytes and form/summon/report masks were cross-checked against
[Archipelago's KH2 Items.py](https://github.com/ArchipelagoMW/Archipelago/blob/476b0a651224288ccf84e2b11b52a7b1512814d6/worlds/kh2/Items.py)
and its `ClientStuff/RecieveItems.py`, including the one-byte Anti-point reset.
Only format facts are used; Archipelago's randomizer-specific repurposed boost,
map, stat-increase and visit-count changes are not imported. No client, live
memory access, network service, Xbox identity or reference save is bundled.

The bounded Python transactions, dependency checks and tests are new. Exact
implemented relationships and verification limits: docs/KH2_INVENTORY_AP.md.

## KH1 shared spell tiers and acquisitions

Save-relative format facts were independently translated from
[gaithern/KH1FM-RANDOMIZER](https://github.com/gaithern/KH1FM-RANDOMIZER/tree/57e701fccc71fc2220d83a86eace198a08136ff9),
particularly `Static Files/scripts/1fmRandoHandleItems.lua` and its global address
maps. Summon IDs and Trinity color order were cross-checked against
[gaithernOrg/KH1FM-AP Items.py](https://github.com/gaithernOrg/KH1FM-AP/blob/ea84da1d90324ead8b14d550e202e01772c2b257/worlds/kh1/Items.py).
The new Python reader/writer is independently written; no Lua implementation,
randomizer-specific repurposed stock, CSV tables, client or reference saves are
redistributed. Native-file checks across 39 records corroborated the shared
tiers, compact summon IDs, Trinity mask and MSB-first puppy order. No in-game
verification or automatic story/reward completion is claimed. See
docs/KH1_PROGRESSION.md for implementation bounds and remaining gates.

## Elden Ring physical equipment creation

Independent Python allocation/serialization uses format facts cross-checked with
[oisis/EldenRing-SaveForge](https://github.com/oisis/EldenRing-SaveForge/tree/ee1042d7a5bd933f91e6f8a0162e0e0237a1c4c5)
`backend/core/gaitem_native_layout.go`, `structures.go`, `writer.go`,
`slot_rebuild.go` and their native allocation/counter/tail regression tests.
The deprecated unchecked FlushGaItems truncation path is not used. Creation
consumes only proven zero slack and preserves the final anchored 178 bytes.
Existing native variable records, including Ash links, remain byte-exact.

The factual catalogue (IDs/names/categories only) is cross-checked against
SaveForge's base-game classification and `backend/db/data/{head,chest,arms,legs}.go`
with flagged entries excluded, and
[ClayAmore/ER-Save-Lib](https://github.com/ClayAmore/ER-Save-Lib/tree/664ff9e83b7022a6fdc5a8332e8b7b22dce34e0f)
`src/api/text/{weapon_name,protector_name}.rs` (base-game, non-error identities).
The Rust `src/save/user_data_x.rs` independently cross-checks record shapes.
No source implementation, original game descriptions, images, regulation or
reference saves are redistributed. Meteorite Staff's non-reinforceable status
is explicit in its game-authored item text, correcting the reference catalogue's
generic +25 limit. See docs/ELDEN_RING_EQUIPMENT.md for exact verification limits.


## Elden Ring owned equipment assignments

The independent `elden_loadouts.py` writer cross-checks factual inventory-index,
bare-ID, exact-handle and dynamic-identity relationships against the previously
pinned SaveForge `backend/core/equipment_writer.go` and ER-Save-Lib
`src/save/user_data_x.rs` definitions. Each project's offset origin is translated
independently; native files corroborate player-relative 0x280/0x2f4/0x34c and
the projectile-count-dependent dynamic block. Existing bare-ID fingerprint
orders are validated against those files; unrelated menu snapshots are not
reinterpreted or overwritten. No upstream implementation, native save,
regulation, game-load claim or unsupported placeholder provisioning is bundled.
Exact scope and verification: docs/ELDEN_RING_LOADOUTS.md.

## v0.35 owned tools, ammunition and Kingdom Hearts fields

Elden Ring tool/pouch pair positions, dynamic identities, empty sentinels and
Physick words were independently cross-checked against the pinned SaveForge
`backend/core/equipment_writer.go` and ER-Save-Lib `src/save/user_data_x.rs`.
The 16-entry quick-item fingerprint is corroborated by native records; a native
mismatch is protected. Factual names/IDs in `elden_tool_tables.py` adapt GPL
SaveForge `backend/db/data/{tools,ashes,key_items,arrows_and_bolts,item_aliases}.go`
and `backend/db/item_identity.go`, including the filled Physick variant. Only
names, identities and ammunition categories are bundled; no original item
descriptions, locations, images, regulation or upstream writer is shipped.

KH3 command and consumable enums are checked against the previously attributed
KingdomSaveEditor `KHSave.Lib3/Types/{CommandType,ConsumableType}.cs` and its PC
save layout. Link IDs are 70–74. Hi-Ether command 62 and consumable 11 illustrate
why these enums must not be conflated. The Python dependency rules and tests are
new. An encrypted public reference passed a combined Potion shortcut/equipment
change; this does not certify gameplay or Link acquisition effects.

DDD rank/disposition nibbles and affinity counter use factual offsets from the
already pinned osdanova/KH_Editor `DDD_spirit_Entry.cs`. No implementation from
that unlicensed project is copied. Native inspection corroborates the two
nibbles and nonnegative counter in 13 populated spirits; species names, rank
growth and displayed affinity levels are not inferred.

Re:CoM's saved-level offset is independently translated from
[gaithern/KH-RECOM-AP-LUA recomAPConnector.lua](https://github.com/gaithern/KH-RECOM-AP-LUA/blob/d5e5c06bb8dd803ee153d2ba47a862fc773c9901/recomAPConnector.lua).
The common player origin is corroborated by existing card/XP/money fields;
level is player-relative 0x1c, record-relative 0x2d54. No live-memory writer,
randomizer, HP/CP/sleight assumptions or reference saves are redistributed.
Native checks passed in two public Steam archives. See
docs/COMPATIBILITY_V35.md for scope and game-load limitations.

## Rockstar PC Story Mode containers and fields

The independent bounded Python reader/writer cross-checks container facts against
[hzhreal/HTOS](https://github.com/hzhreal/HTOS/tree/884e3b2975303d947b40efd5db9b8f63b2474083)
`data/crypto/rstar_crypt.py` and `data/cheats/{gtav_cheats,rdr2_cheats}.py` (GPL-3.0).
These provide the PC AES body origins, signed-byte Jenkins CHKS/header rules,
three GTA cash identities, and RDR2's unique carried-cash identity and +16 field.
The new implementation does not import its Discord UI, network/filesystem
pipeline, first-match-only behavior, trailing-byte trimming or console offsets.
GTA cash character order is independently corroborated by ScriptHookVDotNet's
public `GTA/Player.cs` mapping of SP0/SP1/SP2 to Michael/Franklin/Trevor.

Framed PSO, mapping variants and exact schema facts are cross-checked against
[dexyfex/CodeWalker Pso.cs](https://github.com/dexyfex/CodeWalker/blob/485d56bec00262ed7fa472261cce7bbc6202b96e/CodeWalker.Core/GameFiles/MetaTypes/Pso.cs).
GTA offsets include the PSIN header. Existing statistic-pair field types/offsets
and all 27 named cash/skill hashes are corroborated in two native PC files. Only
the small known statistic allowlist is exposed; no game metadata dump is shipped.
The 0–100 editor skill range is bounded independently; rewards are not inferred.

[JuliPodie/rdr2-savegame-reader](https://github.com/JuliPodie/rdr2-savegame-reader/tree/6595bfa9a8db76a00e4af4c54f06abb0b1ce7e0b)
`Rdr2PcSaveCodec.cs` (MIT) independently corroborates the PC envelope and checked
regions. Its research-only experimental campaign writers are not incorporated.
PSO names or differing bytes alone are not treated as proven gameplay semantics.

Public Legacy test saves were inspected from
[Tatsanai/GTA-V-Save](https://github.com/Tatsanai/GTA-V-Save/tree/a425b0f03fcd3ce46c4ce5dfc42541fe11497239)
and [lucazpf/gtav-savegame-lucazpf](https://github.com/lucazpf/gtav-savegame-lucazpf/tree/89874c99ad3e8b3c7370373ab0b92d6eafa833ed).
No reference save, decrypted data or personal/account information is redistributed.
Three local RDR2 files were checked in memory without changing their originals.
Enhanced save-location facts follow [GTASnP's own support page](https://gtasnp.com/help/games/gtav);
Enhanced-specific native files and all edited-save game loading remain unverified.
See docs/ROCKSTAR_PC.md for precise scope and test limits.

### GTA V saved-player and garage expansion (v0.42)

Scalar member names/types/offsets and 96/112-byte saved-vehicle revisions are
cross-checked against the native embedded schemas and
[alexguirre/rage-parser-dumps](https://github.com/alexguirre/rage-parser-dumps/tree/28785b6e4d2f4fa257f98df925a48eaa4f6b4a93)
GTA V dumps (MIT; existing notice retained). The implementation ships only small
format facts, not the metadata dump. GTA PSO array pointer low-12-bit block ID
and upper-20-bit item offset follow CodeWalker's PsoPOINTER; the second opaque
word is never rewritten. Membership is checked from the typed garage root rather
than scanning vehicle-like bytes. No scripts, proprietary editor code, private
saves or game assets are distributed. See docs/ROCKSTAR_PC.md for exact limits.

### Expanded RDR2 fields (v0.37)

[alexguirre/rage-parser-dumps](https://github.com/alexguirre/rage-parser-dumps/tree/28785b6e4d2f4fa257f98df925a48eaa4f6b4a93)
`dumps/rdr3/b1491.50.json` and `dictionary.txt` (MIT, notice included) provide
case-sensitive parser names, struct/member types, sizes and declared offsets.
Only the small recognized structures are used by the independent writer;
the complete parser dump and its executable are not distributed.

[Halen84/RDR3-Decompiled-Scripts](https://github.com/Halen84/RDR3-Decompiled-Scripts/tree/f7cb7ef3fbd30b09da85c12bfe74cf6c64de1ca2)
build 1491.50 `short_update.c` and `flow_controller.c` corroborate Global_40
attribute indices, core/XP/weight semantics and synchronized HONOR_CURRENT.
No game script implementation is copied or packaged. Integer/hash names used as
lookup facts are separate from code, artwork and game binaries.
[jonas-lundahl's player-attribute research](https://github.com/jonas-lundahl/rdr2-trainer/blob/main/docs/player-attributes.md)
independently corroborates honor/weight semantics and the difference between
runtime attribute APIs and authoritative saved globals.

[femga/rdr3_discoveries](https://github.com/femga/rdr3_discoveries/tree/477aaaccadb7f0c042286611d9939009636cff12)
weapon/ammunition/ped lists and inventory texture-name documentation, plus named
hash facts in the script research above, supply the text-only identifier catalogue
`assets/rdr2-labels.json`. No downloaded art, generated icons or executable mod is
included. A label is not evidence of item ownership, acquisition or stack capacity.

Three local PC files independently corroborate PSIN mapping origin, extended
pointer packing, active/backup inventory membership, typed quantity/condition,
horse, compendium and extended script-offset locations. The console-only honor
quick-code in [bucanero/apollo-patches](https://github.com/bucanero/apollo-patches/blob/main/PS4/CUSA08519.savepatch)
is a corroborating location clue, not a copied PC writer or sole source of field
semantics. Full encrypted restoration and declared-span checks passed; no edited
file has been loaded in-game. See docs/RDR2_FIELDS.md for exact remaining gates.

### RDR2 camp, horses and history (v0.38)

The same pinned build-1491 scripts corroborate camp funds in
`camp_clemenspoint.c` func_1828 (Global_40.f_4283.f_325 and
GANG_SAVINGS_CASH); horse SlotId mapping in `player_horse.c` func_720,
bonding XP in func_804, and health/stamina core indices and updates in
func_578/641/644/888. The independently written schema resolver follows only
inline typed PSCH members; it does not inject or distribute game scripts.
Existing history counter names are scalar lookup facts in the pinned scripts;
the writer requires unique namespace-zero CIntStatStruct/StatId records.

The pinned parser dump explicitly names CSaveCompendium__ItemHorse,
ItemGang, ItemFish and ItemFishLure members and their integer types.
Fishing-history arrays use the independently verified PC pointer layout and
bounded typed targets. Native files corroborate horse inventory/script XP,
camp/statistic agreement and exact-span history edits. Public script hash/name
facts add gang labels; unresolved compendium IDs are not assigned guessed names.
No successful game load is claimed by these structural checks.

### RDR2 bounties, catalog actions and supply growth (v0.39)

The same pinned build-1491 scripts provide monetary-bounty facts:
`short_update.c` func_790 and func_2107 (regional amount, native mirror and
chapter cap), func_783/784/2101/2102 (monetary flag mask 4), func_3274
(separate story wanted bit), `flow_controller.c` func_174/175 (mission temporary
amount), and `startup_sp.c` func_234/601 (region mapping and initialization).
The embedded scalar schemas and native arrays corroborate these locations.

The user supplied version 0.4.1.0 of
[XB36Hazard's reference editor](https://x3t-infinity.com/rdr_se).
It was inspected statically, never executed or loaded as an assembly. Its
existing-weapon action sets SUnlockInfo PackedData bits 0/1/2; its other catalog
controls corroborate the custom-unlock pair at 1/2. The pinned parser dump and
three native files corroborate the eight-byte row and typed Hash/PackedData
members. Only these format facts informed the independent masked writer.
No proprietary implementation, resource database, binary or decoded resource
is bundled. Additional component/horse labels are hash/name facts from the
same pinned primary scripts, not the reference editor's resources.

Native generic satchel records corroborate 48-byte typed records, character
parent links, SLOTID_SATCHEL and unique eight-byte identifiers. Reference static
inspection corroborates retaining the existing character namespace/parent when
creating ordinary supplies. The new allocator uses its own bounded collision
checks and random low word; matching the game's runtime allocator and in-game
persistence are **not established**. The allowlist uses independently named
ordinary supply identifiers; weapon/stable acquisition is excluded.

RSAV directory offsets, CODE/script markers, payload lengths, PMAP relocation,
extended pointers, AES alignment and checks were independently verified on three
local files and synthetic directories. Structural verification cannot establish
item behavior, shop availability, reward delivery or successful game loading.

### RDR2 existing weapon customization (v0.40)

The same pinned parser dump declares inherited ItemId, ParentGuid, SlotId,
Equipped and Quantity members. Three native files corroborate generic component
records below WeaponItem and nested grips, and one active record per parent/slot.
The pinned `femga/rdr3_discoveries/weapons/weapon_components.lua` documents
model-specific/shared families, named material/tint/engraving/rifling, barrel
and sight variants, and the unsafe FRAME_VERTDATA behavior. Only identifier and
relationship facts are used; no Lua implementation or artwork is distributed.

The independent writer selects existing owned records or replaces compatible
named leaf identities found in the save's catalog, preserving GUIDs and slots.
No game parameter table, reference-editor resource database, proprietary code
or private inventory record is packaged. Native exact-span/restoration checks
do not establish in-game compatibility or reward/stat recalculation.

### RDR2 horse names and expanded ordinary supplies (v0.41)

The pinned build-1491 parser schema declares HorseItem.Name as a fixed 64-byte
string. The pinned Halen84 player_horse.c functions 311/313 read and write the
64-byte name at the start of Global_40.f_1095.f_1[slot]; function 314 uses that
saved name for the horse prompt. Existing slot mapping and script-model checks
come from the earlier horse-mirror work. Three local files corroborate two equal
name pairs and two differing pairs; only equal canonical pairs are editable.
No reference-editor strings, databases, art or implementation are distributed.

The additional supply allowlist uses 133 explicit identifiers from the same
attributed primary script/hash facts already packaged as rdr2-labels.json.
There is no new external dataset or runtime dependency. Online/mission items and
unrecognized acquisition types are not inferred from a shared name prefix.
Native tests verify structural growth and requested quantities, not successful
game loading, capacity enforcement, acquisition rewards or runtime GUID behavior.


### GTA V story weapon expansion (v0.43)

Weapon identifiers, English labels, ammo families/capacities, attachment points,
default parts and tint names are format/name facts from
[DurtyFree/gta-v-data-dumps weapons.json](https://github.com/DurtyFree/gta-v-data-dumps/blob/b65684e00f689fdec405c5f1055322c802d3c895/weapons.json).
Only a small identifier/relationship table is packaged; no game artwork, parameter
binary, full dump or resource database is bundled.

[udoprog/gta-v-scripts](https://github.com/udoprog/gta-v-scripts/tree/82a69a01a672287e8e4677961f6aa946402fe1d0)
Scripts/player_controller.c func_113/116 and the inventory writer around line
83725 provide base slot identities, three-cell component order and one-hot tint
bits 20–27. [YimMenu/GTA-V-Decompiled-Scripts](https://github.com/YimMenu/GTA-V-Decompiled-Scripts/tree/05b0bb75009c9fecfa351f499d2593ee73a7d1ae)
build 2628 player_controller.c func_122/126/655 provide the five-cell inventory
shape, separate tint/livery fields, revised component order and shared ammo
semantics. Only numeric/identifier relationships informed the independent writer;
no decompiled script implementation is shipped.

[calamity-inc/gta-v-joaat-hash-db](https://github.com/calamity-inc/gta-v-joaat-hash-db/tree/7fa8525cad6a87c7b68bb3c35f3f0bb05fcdfc84)
extract_stats.php and extracted stat names corroborate SP0/SP1/SP2_WEAP_* bank
names. The user supplied [XB36Hazard's GTA V Save Editor v5.9](https://x3t-infinity.com/GTAV_SE).
Static resource/IL inspection, without executing the installer or editor, identified
40 shop weapon/bank/bit relationships and corroborated purchase/unlock semantics.
Only small format facts were independently normalized; no proprietary code,
encrypted/decrypted resource, artwork, installer or reference executable is bundled.
Its built-in PC template was used locally to corroborate the five-cell schema and
default-pistol component bit. No native sample is distributed.

Native PSO schemas corroborate member identities, fixed capacities, padded VM
cells and offsets. Three native files and synthetic graphs verify exact masked
writes, dependencies, unknown-bit/padding preservation and container integrity.
These checks do not establish Enhanced-specific or in-game compatibility.


### GTA V saved vehicle appearance and performance (v0.44)

The same pinned DurtyFree dump provides `vehicleColors.json`, `vehicles.json` and
`vehicleModKits.json`. Only paint labels and small model/kit/stage relationships
are packaged, not the complete dumps, art, game binaries or resources. Native
occupied garage records corroborate Voltic, Infernus and Massacro kit IDs and
the 40/48-byte variation schemas. Existing parser-dump attribution covers scalar
members, embedded variation and hash/byte ATBINARYMAP records.

[citizenfx/natives SetVehicleMod](https://github.com/citizenfx/natives/blob/master/VEHICLE/SetVehicleMod.md)
documents VMT engine/brake/gearbox/suspension/armor names; hashed names identify
the native map entries. The pinned dump supplies per-kit contiguous stage ranges.
[SetVehicleWindowTint](https://github.com/citizenfx/natives/blob/master/VEHICLE/SetVehicleWindowTint.md)
documents the seven tint values. Only enum/format facts informed the independent
writer; no Cfx implementation is copied. Smoke/neon channels are scalar member
facts, not a claim that editing color installs or enables the mod.

Only existing uniquely mapped entries are edited. New vehicle/model acquisition,
complete body/wheel/livery tuning and in-game validation are not established.
