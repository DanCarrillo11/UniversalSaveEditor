# References and attribution

The project is distributed under GPL-3.0-or-later. Its implementation uses Python and the standard library. Personal save files are not included. Cover images are included as identification resources; their rights remain with their respective owners and are not covered by the source-code license.

- [Godot 3.5 binary serialization API](https://docs.godotengine.org/en/3.5/tutorials/io/binary_serialization_api.html): Variant types, sizes, and flags.
- [NotNite/webfishing-save-editor](https://github.com/NotNite/webfishing-save-editor): reference for the WEBFISHING file wrapper and field names in `src/game/types.ts` and `src/App.svelte`. Its interface and visual resources are not included.
- [Xeeynamo/KingdomSaveEditor](https://github.com/Xeeynamo/KingdomSaveEditor), GPL-3.0: reference for the PC format and Kingdom Hearts Final Mix field positions in `KHSave.Archives/PcSaveArchive.cs`, `KHSave.Archives/Factories/PcKh1Factory.cs`, `KHSave.Lib1/SaveKh1.FinalMix.cs`, and `KHSave.Lib1/Models/Character.cs`. UniversalSaveEditor adapts knowledge of these structures to a byte-preserving editor.
- [KatRewrites/kh1-save-editor](https://github.com/KatRewrites/kh1-save-editor), GPL-3.0: reference for PNG/sqEX containers and the need to preserve related records. Its tables and interface are not included.

Game names belong to their respective owners. UniversalSaveEditor is an independent project.

The memory-card icon was prepared as a transparent PNG crop from an image supplied by the repository author. Visible marks and logos belong to their respective owners and are not covered by the source-code license.

## Cover art

- [kh1](https://www.khwiki.com/File:Kingdom_Hearts_Final_Mix_Boxart_JP.png): original file, image URL, and provenance are recorded in `assets/covers/sources.json`.
- [recom](https://www.khwiki.com/File:Kingdom_Hearts_ReChain_of_Memories_Boxart_NA.png): original file, image URL, and provenance are recorded in `assets/covers/sources.json`.
- [kh2](https://www.khwiki.com/File:Kingdom_Hearts_II_Final_Mix%2B_Boxart_JP.png): original file, image URL, and provenance are recorded in `assets/covers/sources.json`.
- [bbs](https://www.khwiki.com/File:Kingdom_Hearts_Birth_by_Sleep_Final_Mix_Boxart_JP.png): original file, image URL, and provenance are recorded in `assets/covers/sources.json`.
- [webfishing](https://store.steampowered.com/app/3146520/): source page and original image URL are recorded in `assets/covers/sources.json`.
- [maxpayne](https://store.steampowered.com/app/12140/): source page and original image URL are recorded in `assets/covers/sources.json`.
- [ror2](https://store.steampowered.com/app/632360/): official Steam library artwork; URL and file size are recorded in `assets/covers/sources.json`.

The Final Mix entries use Japanese cover art from their original releases. Kingdom Hearts II Final Mix+ also includes Re:Chain of Memories and is not presented as an individual Steam box. WEBFISHING, Risk of Rain 2, and Max Payne use Steam library artwork.

Risk of Rain 2 compatibility was validated against a local Steam profile supplied by the repository author. Unlock identifiers in `ror2_unlocks.py` were extracted from resource names in `Risk of Rain 2_Data/StreamingAssets/aa/catalog.json` from that installation. The content catalog and profile contain third-party or personal data and are not included.

The `kh_items.py` table adapts `KHSave.Lib1/Types/EquipmentType.cs` from Xeeynamo/KingdomSaveEditor under GPL-3.0. It preserves attribution and excludes story items and unused entries.
