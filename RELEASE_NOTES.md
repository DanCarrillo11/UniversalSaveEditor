# UniversalSaveEditor v0.6.0-alpha

First consolidated preview of the portable Windows application.

## Download and run

Download `UniversalSaveEditor.exe` from the release assets and double-click it.
No installer or Python setup is needed. Alternatively, use **Code → Download ZIP**,
extract the folder, and open the included executable.

## Included

- Eight-game library with full cover art, compact responsive cards, filters, and direct editor access.
- Five editors: WEBFISHING, Risk of Rain 2, Kingdom Hearts Final Mix, Kingdom Hearts II Final Mix, and Alice: Madness Returns.
- Search within every editor category, change review, validation, and exact backups.
- Backup browsing and restoration, with a new backup of the current file before restoration.
- Automatic discovery, manual opening, and drag and drop for supported files.
- Memory-card application and executable icon.
- 35 automated tests and packaged-executable startup verification.

## Compatibility limits

This is an alpha preview. Automated checks do not establish that every edited
combination loads correctly in a game.

- WEBFISHING: economy, level/XP, bait with automatic unlocks, upgrades, existing inventory, and fishing journal.
- Risk of Rain 2: Lunar Coins, statistics, and 454 unlock identifiers. DLC content still requires the relevant DLC.
- Kingdom Hearts Final Mix: Munny, character attributes, and 154 named inventory entries. Export copies only.
- Kingdom Hearts II Final Mix: **experimental** Munny, experience, character attributes and levels, Drive Forms, and 320 inventory quantities. Both internal checksums and the Steam-container CRC are maintained. Export copies only; a populated in-game save slot is required.
- Alice: Madness Returns: **experimental** Teeth currency in the validated persistent-profile layout. Weapons, outfits, and collectibles are not editable yet.
- Re:Chain of Memories, Birth by Sleep, and Max Payne: listed as coming soon.

Close the game before applying or restoring a save. Steam Cloud can replace local
files. Keep backups until you have checked the edited save in the game.

`SHA256SUMS.txt` contains the hash of the downloadable executable.
