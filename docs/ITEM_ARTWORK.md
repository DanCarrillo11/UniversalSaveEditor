# Original item artwork

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
