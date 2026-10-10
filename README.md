# UniversalSaveEditor

A unified, offline Windows save editor. Browse your games, edit your progress,
review changes, and keep recoverable backups in one application.

**v0.8.0-alpha** is a pre-release. This update adds difficulty editing for KH Final Mix and KH II Final Mix.

## Download and run

Download `UniversalSaveEditor.exe` from **Releases → Assets** and double-click it.
The application is portable; no installer, Python, or command-line setup is needed.

You can also select **Code → Download ZIP**, extract the folder, and open the
executable included at its root. Startup can take a few seconds.

## Features

- Responsive game library with full cover art, search, filters, and sorting.
- Click a compatible cover to open its detected save directly.
- Automatic discovery, manual file selection, and drag and drop.
- Categories and field search, including inventory IDs and unlocks.
- Change review, input validation, and preservation of unrelated save data.
- Exact backups before applying changes; backup browsing and restoration.
- Restore keeps a backup of the current file before replacing it.
- Processing stays local. No accounts or save uploads are required.

## Compatibility

| Game | Editable fields | Status / save action |
|---|---|---|
| WEBFISHING | Money, debt, earnings, level, XP, bait with automatic unlocks, capacity, upgrades, existing inventory size/quality, and fishing journal | Available; apply with backup |
| Risk of Rain 2, Steam | Lunar Coins, statistics, and 454 unlock identifiers for characters, skills, skins, artifacts, items, logs, and Newt Altars | Available; apply with backup |
| Kingdom Hearts Final Mix, Steam | Munny, difficulty, Sora/Donald/Goofy attributes, and 154 named inventory entries | Available; export a separate copy |
| Kingdom Hearts II Final Mix, Steam | Munny, difficulty, experience, character attributes/levels, bonus and summon levels, Drive Gauge, Drive Forms, and 320 inventory quantities | Experimental; export a separate copy |
| Alice: Madness Returns, Steam | Teeth, four weapon levels, abilities, health upgrades and paint pots, dress abilities, 89 memories, 83 bottles, 59 snouts, Radula rooms, chapters, difficulty, enemy journal, cinematics, and statistics | Experimental; apply with backup |
| Re:Chain of Memories / Birth by Sleep, Steam | File discovery | Coming soon |
| Max Payne 1 | Listed in the library | Coming soon |

Kingdom Hearts support targets **HD 1.5 + 2.5 ReMIX on Steam**. KH II requires a
populated slot created at an in-game save point. Containers without saved slots
cannot be edited. Its record checksums and the outer Steam-container CRC are
maintained on export. Invalid integrity checks require explicit repair.

Open **Difficulty** after selecting a saved slot to change its mode. KH Final Mix
supports Beginner, Final Mix (Standard), and Proud. KH II Final Mix also supports
Critical. Existing attributes, items, and starting bonuses are not recalculated;
changing the saved mode does not recreate a new-game setup. In-game validation
of mode changes is pending. See [difficulty format](docs/KH_DIFFICULTY.md).

Automated checks validate file preservation and editing behavior. Loading all
edited copies inside the games still requires validation; KH II and Alice are
marked experimental. Field limits do not guarantee that every combination works
in-game. Alice's checkpoint position and selected outfit are stored separately
and are not edited. Current difficulty is editable by selecting `GameConfig_PC.CFG`
in the editor's file selector. Dress controls change ability flags;
DLC content must be installed. See [Alice format and scope](docs/ALICE_FORMAT.md).
Risk of Rain 2 DLC content still requires ownership of the corresponding DLC.
WEBFISHING level and XP are independent and do not automatically grant rewards.

## Editing a save

1. Close the game, then click its cover or use **Open save**.
2. Choose a slot if the game has several. Search a category to find a field.
3. Change values, then select **Review and apply** or **Review and export**.
4. Review the changes. Applying creates a backup and replaces the active file.
   Exporting creates a separate file and preserves the original.
5. Check the edited save in-game. **Backups and restore** can recover an earlier
   file and preserves the current file before restoring.

Steam Cloud can replace local files. Keep your backups until the edited save has
been checked. A save changed by the game while editing must be reopened.

Shortcuts: **Ctrl+O** opens a save, **Ctrl+F** focuses the current search,
and **Ctrl+Enter** opens change review.

## Development

Python and PySide6. Install `requirements.txt` in a virtual environment and run
`python app.py`. Run `python -m unittest discover -s tests -v` for the automated tests.

To build on Windows, install `requirements-build.txt` and run
`python -m PyInstaller --clean --noconfirm UniversalSaveEditor.spec`.
The executable is created in `dist/`.

`core.py` handles byte-preserving save patches and backups. `app.py` provides the
interface, `catalog.py` tracks compatibility, and `version.py` stores the version.
The workflow validates the packaged executable and produces downloadable assets.

Do not commit personal saves. They can contain player names and account IDs.
Supported save extensions and development output are excluded by `.gitignore`.

## License and attribution

Source code: GPL-3.0-or-later. Cover art, game names, and visible logos belong to
their respective owners. See [SOURCES.md](SOURCES.md) and [LICENSE](LICENSE).
