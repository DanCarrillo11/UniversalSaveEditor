# References and attribution

The project is distributed under GPL-3.0-or-later. Its implementation uses Python and the standard library. Personal save files are not included. Cover images are included as identification resources; their rights remain with their respective owners and are not covered by the source-code license.

- [Godot 3.5 binary serialization API](https://docs.godotengine.org/en/3.5/tutorials/io/binary_serialization_api.html): Variant types, sizes, and flags.
- [NotNite/webfishing-save-editor](https://github.com/NotNite/webfishing-save-editor): reference for the WEBFISHING file wrapper and field names in `src/game/types.ts` and `src/App.svelte`. Its interface and visual resources are not included.
- [Xeeynamo/KingdomSaveEditor](https://github.com/Xeeynamo/KingdomSaveEditor), GPL-3.0: reference for the PC container, Kingdom Hearts Final Mix fields, and Kingdom Hearts II Final Mix fields and record checksum in `PcSaveArchive.cs`, `PcKh1Factory.cs`, `PcKh2Factory.cs`, `SaveKh1.FinalMix.cs`, `SaveKh2.FinalMix.cs`, and their character and Drive Form models. UniversalSaveEditor adapts knowledge of these structures to a byte-preserving editor.
- [KatRewrites/kh1-save-editor](https://github.com/KatRewrites/kh1-save-editor), GPL-3.0: reference for PNG/sqEX containers and the need to preserve related records. Its tables and interface are not included.

Game names belong to their respective owners. UniversalSaveEditor is an independent project.

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
