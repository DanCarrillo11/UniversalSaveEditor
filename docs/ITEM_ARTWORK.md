# Original item artwork

## Current coverage (v0.22)

The offline catalogue contains **3,155 artwork associations across 14 editors**.
An association is a field/identity mapping, not necessarily a unique image:
ReCoM card values share their original base card art and KH3 materials share
matching inventory art. This does not mean every item or field in those games
has an image. Unknown, ambiguous and unsupported identities keep text labels.

| Game | Associations | Where images appear |
| --- | ---: | --- |
| Elden Ring | 794 | Known goods, storage, Add items and base weapon upgrades |
| RE2 Remake | 27 | Mapped inventory supplies |
| Kingdom Hearts | 42 | Known weapons in inventory and party equipment |
| Kingdom Hearts II | 135 | Consumables, weapons, armor, accessories and equipped items |
| Re:Chain of Memories | 1,123 | Recognized card quantities; shared base artwork |
| Birth by Sleep | 47 | Existing command entries with matching original artwork |
| Dream Drop Distance | 56 | Existing item entries with matching original artwork |
| Kingdom Hearts III | 408 | Known inventory objects and 60 materials |
| WEBFISHING | 169 | Seven baits and recognized fish/tool/prop IDs in inventory/journal |
| Risk of Rain 2 | 93 | Unlocks with an exact installed achievement-icon reference |
| RE HD Remaster | 25 | Recognized inventory/item-box objects |
| RE3 Remake | 76 | Original atlas supplies, attachments and key items |
| RE5 | 19 | Weapon images beside existing infinite-ammo flags |
| RE7 | 141 | Item-box rows with a matching, unique ItemDataID string |

### Sources and mapping

- [Kingdom Hearts Wiki](https://www.khwiki.com): original game renders and isolated card sprites, using exact edition-specific file titles matched to existing editor tables. Opaque gameplay screenshots are excluded. Card values and premium state stay in the field label/save; shared base art does not depict those variants. Large original renders receive aspect-preserving 128px previews; smaller sprites keep their original pixels. Lossless PNG packing can remove nonvisual metadata without changing pixels. Individual file pages, upload timestamps, original hashes, preview hashes and transforms are in the manifest.
- Installed Steam Risk of Rain 2 Addressables: UnlockableDef achievementIconRef GUID to catalog asset to exact texture name. Original textures decoded to PNG; no guessed associations. Includes base-game and DLC assets present in the installation; a picture does not grant DLC ownership. The MIT [catalog parser](https://github.com/renanliberato/unity-addressables-id-re/tree/c7eb4be551516e7a60c2c353e7fd9682e1219b08) and [UnityPy](https://github.com/K0lb3/UnityPy) were research tools only, not runtime dependencies or shipped code.
- [NotNite/webfishing-save-editor](https://github.com/NotNite/webfishing-save-editor/tree/b3687a817700d2b766bf2406dfbd8a2b35bb4bf5): extracted original sprites and resource ID/name/icon tables. Inventory position is never used as item identity. Artwork is expressly separate from that project's MIT code license.
- [Squirrelies/SRTPluginUIRE3WinForms](https://github.com/Squirrelies/SRTPluginUIRE3WinForms/tree/d70d15c880cfb262c0ced7aa8ce0857dba777897): unmodified original atlas, exact upstream clipping rectangles and separately pinned provider enum. Full MIT notice included.
- [SpeedrunTooling/InventoryHUD](https://github.com/SpeedrunTooling/InventoryHUD/tree/b1385a15c205a7a270d0949388d948712952d904): RE1R numeric item filenames, RE7 internal item-name filenames and RE5 named weapon CSS rectangles. RE5 sprite crops retain original pixels. RE7 identity strings are inspected only in the same serialized quantity object; duplicate/invalid strings cannot select an image. Full MIT notice included.

One WEBFISHING .png filename contains the original GIF image; Qt detects its
actual format and shows the first frame. Resource packs deduplicate shared images,
decode offline and use bounded caches. Tests decode every association, check
hashes/dimensions and verify equipment image changes and save-byte preservation.

### Pending artwork

Alice: Madness Returns, Max Payne, RE4 (2005), RE4 Remake, RE6, RE8 and RE9
currently have **no verified item artwork** in this release. Research found
modified/fan-made imagery, inaccessible archives, or resources without a safe
mapping to existing save fields. These are not presented as completed collections.
Those editors retain their existing text controls.

Adding artwork does not add save-edit permissions, remove experimental status,
or establish in-game validation. Publisher art belongs to its respective owners
(Disney/Square Enix, lamedeveloper, Gearbox/Hopoo and Capcom); source-code licenses
do not convey game-art licenses or publisher endorsement.

## Initial RE2 collection

The first artwork collection covers **27 Resident Evil 2 (2019) supply IDs**:
First Aid Spray; green, red and blue herbs; seven herb mixtures; ten ammunition
types; Ink Ribbon; Wooden Boards; and four gunpowder variants. Inventory rows
show the original game icon, an English label and the editable existing quantity.
Healing, Ammunition, Crafting materials and Supplies are separate foldable groups.

Images come from the original game's texture atlas archived in
[Squirrelies/RE2REmakeSRT](https://github.com/Squirrelies/RE2REmakeSRT/tree/07db9f610553e6a95cee24aeac99cd1bc6c48e19),
`RE2REmakeSRT/Resources/ui0100_iam.texout.png`. The archive's item enumeration
and clipping table establish the identity-to-image mapping. The game item-ID
enum in the separately researched RE Engine schema cross-checks the ID domain.
Only the first two atlas rows are retained, using an exact pixel crop. No AI,
redraw, recoloring, sharpening or image upscaling is applied. Qt scales previews
to fit the editor while preserving aspect ratio; the packaged source pixels
remain intact. A neutral dark tile keeps the originals legible in both themes.

`assets/items/manifest.json` records the pinned source revision, original and
cropped SHA256 hashes, display names, groups and pixel rectangles. `item_art.py`
provides a game-specific lookup and bounded cached image decoding. Identities
come from the validated object's read-only ItemId property; image labels do not
change what the save patcher can edit. Same-number IDs from other games never
reuse an RE2 icon. Unknown or ambiguous IDs remain unidentified and receive
no guessed image, generic substitute, generated picture or automatic download.

Three uncertain herb variants, weapons, attachments, quest items, DLC-specific
content and other games are not included in this first collection. Adding more
art requires an original-game source and a verified identity mapping, then a new
manifest entry. Changing names or images does not establish in-game validation
of the experimental Steam save adapter.

The clipping/ID table adaptation is MIT, Copyright (c) 2019 Travis J. Gutjahr;
the complete notice is `assets/items/RE2_SRT_LICENSE.txt`. **Game artwork and
trademarks belong to CAPCOM CO., LTD. and are outside the application's source-code
license.** The upstream software license is not a license from Capcom to game art.
This independent, free fan utility is not affiliated with or endorsed by Capcom.

## Elden Ring (v0.21)

Elden Ring now has images for all **307 goods and 487 base armaments** already
recognized by the editor. Icons appear beside inventory/storage stacks, supported
Add items controls and existing weapon upgrades, including their read-only rows.
Reinforcement and affinity variants use the verified base armament's image.
This adds presentation, not support for creating new weapons, armor, quests or
unmapped objects. Existing save-format and in-game validation limits remain.

Source: the archived in-game images and six ItemData IconPath tables in
[oisis/EldenRing-SaveForge](https://github.com/oisis/EldenRing-SaveForge/tree/ee1042d7a5bd933f91e6f8a0162e0e0237a1c4c5),
already used for this application's labels. Names must match the existing tables
exactly before an icon is included. Goods use their full `0x40000000`-prefixed
identity; base weapon IDs occupy their separate domain. Registry handles and
reinforced IDs are never interpreted as image IDs. Unknowns receive no substitute.

All archived image bytes are copied unchanged into deterministic ZIP packs.
791 files are PNG; three upstream `.png` filenames contain WebP images, which
Qt identifies from their actual headers. No AI, source resampling, recoloring,
cropping or additional image optimization is applied. Preview scaling preserves
aspect ratio. Each manifest entry records the upstream path, table and SHA256;
source records also include the pinned revision and ZIP-pack hashes.

Images are decoded directly from the packaged archives, with bounded sizes and
caches; nothing is extracted to disk or downloaded during normal use. Every
mapped image is decoded by automated UI checks, including the WebP variants.
Tests also check exact archive-member hashes, separate ID domains and icons after
weapon edits. The packaged startup check loads representative goods, weapons
and WebP artwork.

The metadata adaptation follows SaveForge's GPL v3 attribution in SOURCES.md.
**Game artwork and trademarks belong to FromSoftware, Inc. and Bandai Namco
Entertainment Inc., outside the source-code license.** The utility is independent
and does not claim the publishers' endorsement or a game-art license from the
upstream software license.
