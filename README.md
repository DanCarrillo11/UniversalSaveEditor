# UniversalSaveEditor

A local Windows save editor with a PS2-era menu-inspired interface. Version 0.5 is built with Python and PySide6 (Qt Widgets), includes a visual game library, and runs offline without accounts or uploading saves to a server.

## Run as a user

On GitHub, select **Code → Download ZIP**, extract the downloaded folder, and double-click **UniversalSaveEditor.exe**. The app is portable: Python and command-line setup are not required. The first launch may take a few seconds while its packaged components are extracted.

The executable is included in the repository root beside the source code. Previous builds are also available under **Releases → Assets**.

### Run from source

For development only: install 64-bit Python, create a `.venv`, install `requirements.txt`, and run `app.py`.

### Build the executable

On Windows, install `requirements-build.txt` in the development environment and run `python -m PyInstaller --clean --noconfirm UniversalSaveEditor.spec`. The result is `dist/UniversalSaveEditor.exe`.

## Interface

- Game library with original cover art, search, and availability filters.
- Collections for WEBFISHING, Risk of Rain, Kingdom Hearts, and Max Payne.
- Drag a save onto the window or use **Open save**.
- Game-specific categories for economy, progress, combat, bait, characters, and inventory.
- Live change summary, modified-field highlighting, and validation before writing.
- Navigation between the library, tabs, and save slots preserves pending edits.
- Integrated guide. Shortcuts: **Ctrl+O** to open, **Ctrl+F** to search, and **Ctrl+Enter** to review and export.

Three games currently have working editors. Four additional games are listed as work in progress.

## Current compatibility

| Game | Available editing |
|---|---|
| WEBFISHING | Money, debt, total earnings, level, XP, catches, bait quantities and automatic bait unlocks, capacity, six upgrades, existing item size and quality, journal catches, and records. |
| Risk of Rain 2, Steam | 454 unlock identifiers from the installed content catalog: characters, skills, skins and recolors, artifacts, items, logs, and Newt Altars. Lunar Coins, progress, combat, and economy statistics are also editable. |
| Kingdom Hearts Final Mix, HD 1.5 + 2.5 ReMIX, Steam | Save-slot selection; Munny; current and base HP/MP; AP, strength, and defense for Sora, Donald, and Goofy; quantities for 154 identified items, materials, weapons, and accessories. |
| Re:Chain of Memories, Steam | File detection; editing pending. |
| KH II Final Mix and Birth by Sleep, Steam | Editing pending. Compatibility with the entire collection is not claimed. |
| Max Payne 1 | Format research and validation require example saves. |

Input limits are conservative safety limits and do not guarantee game balance or acceptance of every combination. In Kingdom Hearts, base attributes can differ from effective equipment-adjusted values. Level, experience, story progress, and abilities are not edited. WEBFISHING does not add or remove inventory items, unlock cosmetics, or modify quests. Its level and XP values are independent and do not automatically grant rewards. Risk of Rain 2 can record unlock identifiers in the profile, but the game may still require ownership or installation of the corresponding DLC.

## Usage

1. Select **Open editor** on a game card, or use **Open save**.
2. Choose the Kingdom Hearts slot you want to edit. In Risk of Rain 2, use individual checkboxes, **Unlock category**, or the category search.
3. For WEBFISHING or Risk of Rain 2, select **Review and apply**. The app creates an exact `.bak` copy and safely replaces the active file without changing its name.
4. For Kingdom Hearts, select **Review and export** and choose another file. Direct replacement remains disabled until edited copies are validated in the game.
5. Close the game before applying changes. Steam Cloud may replace a local save when it holds another version.
6. Load the save in the game and verify the changes. Restore the generated `.bak` file if needed.

If the Kingdom Hearts `sqEX` block has a mismatched CRC, the app allows inspection and explains the problem. Exporting requires **Repair the integrity check when exporting the copy**. Repairing that CRC does not repair other possible internal corruption.

## Verification

- 22 automated tests cover input limits, invalid XML, individual and bulk unlocks, preservation of unrelated data, automatic bait unlocks, atomic replacement with backups, multiple Kingdom Hearts records, CRC handling, overwrite rejection, search, filters, navigation, cancellation, and Qt dialog application.
- The library and editor were visually reviewed from Qt-rendered screenshots.
- Real local WEBFISHING, Risk of Rain 2, and Kingdom Hearts Final Mix Steam files were read and edited in memory. Personal saves are not included in the project.
- All 454 Risk of Rain 2 identifiers were applied to a copy of a real profile, reparsed successfully, and backed up exactly. Original files were not modified. **Loading edited copies inside each game still requires validation.**

Run tests with `.venv\Scripts\python -m unittest discover -s tests -v`.

## Development

`core.py` separates save formats and writes from the `app.py` interface. Readers expose slots and fields with positions, types, and limits. `catalog.py` stores game metadata and availability, `artwork.py` presents full cover art, and `theme.qss` defines the interface style. Patches change only selected fields and required checksums; the editor does not rebuild entire saves from scratch.

Planned work includes in-game validation, friendlier names and descriptions for more Risk of Rain 2 internal identifiers, format readers in separate modules, Re:Chain of Memories checksum support, specific KH II and Birth by Sleep fixtures, and Max Payne research using saves that differ by one known value.

Do not publish personal saves. They may contain account identifiers, player names, or other private data. `.gitignore` excludes the supported save extensions.

## License

GPL-3.0-or-later. See [SOURCES.md](SOURCES.md) for format references and attribution.
