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
