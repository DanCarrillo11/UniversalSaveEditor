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
