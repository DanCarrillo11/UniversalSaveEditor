# UniversalSaveEditor

A unified, offline Windows save editor. Browse your games, edit your progress,
review changes, and update your saves directly in one application.

**v0.15.0-alpha** is a pre-release. Editors use a few game-specific categories
with section selectors and foldable blocks. All available editors save directly
to the opened file, keeping its name and location. No automatic backups are created.

## Download and run

Download `UniversalSaveEditor.exe` from **Releases > Assets** and double-click it.
The application is portable; no installer, Python, or command-line setup is needed.

You can also select **Code > Download ZIP**, extract the folder, and open the
executable included at its root. Startup can take a few seconds.

## Features

- Clean light and dark appearances with a header toggle and a remembered preference.
- Responsive game library with full cover art, search, filters, and sorting.
- Mark games with the star on each cover. Favorites appear first in the library;
  open **Favorites** in the sidebar to show only your starred games.
- Short view fades and animated cover highlights, with a remembered **Reduce motion** option.
- Platform logos and names below each cover; currently Steam. Editor status and
  detected saves remain in the details panel. Coming-soon games are not editable.
- Click a compatible cover to open its detected save directly.
- Automatic discovery, manual file selection, and drag and drop.
- Up to three main categories per editor, with section and character selectors.
- Foldable sections and field search, including inventory IDs and unlocks.
- Changed-only filtering, field counts, individual undo, and inline validation.
- Compact editor controls and scrollable save details for smaller windows.
- Open a detected save from its file row; view size and modification time.
- Remember favorites, appearance, motion preference, window geometry, and the last opened folder locally.
- Navigation and search stay visible while scrolling; pending edits survive
  character, category, and slot changes.
- Change review, input validation, and preservation of unrelated save data.
- Apply directly to the opened save without exports, renaming, or automatic backups.
- Browse and restore existing backups without creating additional files.
- Processing stays local. No sign-in or save uploads are required.

## Compatibility

| Game | Editable fields | Status / save action |
|---|---|---|
| Resident Evil 4 (2005), Steam Ultimate HD Edition | Pesetas, difficulty, player/Ashley health, save count, completed rounds and combat statistics | Experimental; direct apply; inventory and unlocks are not yet editable |
| Resident Evil HD Remaster, PC | Mapped slot 1: difficulty, save count, defensive supplies and existing inventory/item-box quantities | Experimental; public PC fixture checked; other slots pending |
| Resident Evil 2 (2019), Steam | Player health, existing inventory quantities, reward and library flags | Experimental; real Steam fixture validation pending |
| Resident Evil 3 (2020), Steam | Player health, existing inventory quantities, total shop points earned, shop-item possession and reward flags | Experimental; shared console payload checked; real Steam fixture validation pending |
| Resident Evil 4 (2023), Steam | Extra content points, Spinels and existing inventory quantities | Experimental; real Steam fixture validation pending |
| Resident Evil 5, Steamworks | Money, exchange points, costume flags, filters, infinite-ammo flags and library files | Experimental; public Steamworks fixture checked |
| Resident Evil 6, PC | Skill points, Mercenaries character/costume and stage flags, No Mercy stages, existing supplies | Experimental; public Steam fixture checked |
| Resident Evil 7, Steam | Player health and existing item-box quantities | Experimental; shared console payload checked; real Steam fixture validation pending |
| Resident Evil Requiem, Steam | Money, Clear Points, extra-shop availability/acquisition/received flags, bonus content, artwork/figure availability and purchases, special options | Experimental; nine native Steam files checked |
| WEBFISHING | Money, debt, earnings, level, XP, bait with automatic unlocks, capacity, upgrades, existing inventory size/quality, and fishing journal | Available; direct apply |
| Risk of Rain 2, Steam | Lunar Coins, statistics, and 454 unlock identifiers for characters, skills, skins, artifacts, items, logs, and Newt Altars | Available; direct apply |
| Kingdom Hearts Final Mix, Steam | Munny, difficulty, Sora/Donald/Goofy attributes, and 154 named inventory entries | Available; direct apply |
| Kingdom Hearts II Final Mix, Steam | Munny, difficulty, experience, character attributes/levels, bonus and summon levels, Drive Gauge, Drive Forms, and 320 inventory quantities | Experimental; direct apply |
| Alice: Madness Returns, Steam | Teeth, four weapon levels, abilities, health upgrades and paint pots, dress abilities, 89 memories, 83 bottles, 59 snouts, Radula rooms, chapters, difficulty, enemy journal, cinematics, and statistics | Experimental; direct apply |
| Re:Chain of Memories, Steam | Moogle Points, XP, difficulty and 1,139 named card quantities, including numbered and premium variants | Experimental; direct apply |
| Birth by Sleep Final Mix, Steam | Per-slot character XP, level, Munny, medals, attributes, Arena level, existing command levels/XP and acquired/active ability stacks | Experimental; direct apply |
| Dream Drop Distance HD, Steam | Munny, difficulty, Sora/Riku XP, levels and Drop Points, existing command/item quantities | Experimental; direct apply |
| Kingdom Hearts III + Re Mind, Steam | Munny, XP, difficulty, level, party HP/MP/Focus and boosts, named inventory quantities with acquisition flags, material counters | Experimental; direct apply |
| Max Payne 1, Steam | Original revision 48 weapon ownership, reserve ammunition and painkillers | Experimental; direct apply |

All Resident Evil adapters use direct apply and retain the original account and
unrelated bytes. Their scope is deliberately limited to recognized fields.
**No edited Resident Evil save has been validated by loading it in-game.**
Numbered RE Engine collection entries follow saved order; this is not yet a fully
named catalogue. System profiles and gameplay slots expose different fields.
RE4 Remake and Requiem detect the original SteamID64 from normal save paths;
copied saves need their original creator's ID. DLC ownership remains necessary.
RE0's encryption and section table have been researched, but editing is pending.
See [research and validation status](docs/RESIDENT_EVIL_RESEARCH.md),
[RE5](docs/RE5_FORMAT.md), [RE Engine](docs/RE_ENGINE_FORMAT.md), and
[HD Remaster / RE6 / RE0 boundaries](docs/RE_LEGACY_PC.md).

Kingdom Hearts support targets **HD 1.5 + 2.5 ReMIX, Dream Drop Distance HD and KH III on Steam**. KH II requires a
populated slot created at an in-game save point. Containers without saved slots
cannot be edited. Its record checksums and the outer Steam-container CRC are
maintained when applying changes. Invalid integrity checks require explicit repair.

Open **Progress > Difficulty** after selecting a saved slot to change its mode. KH Final Mix
supports Beginner, Final Mix (Standard), and Proud. KH II Final Mix also supports
Critical. Existing attributes, items, and starting bonuses are not recalculated;
changing the saved mode does not recreate a new-game setup. In-game validation
of mode changes is pending. See [difficulty format](docs/KH_DIFFICULTY.md).

Automated checks validate file preservation and editing behavior. Public PC
fixtures were used for ReCoM, BBS, DDD and KH III, and three local Max Payne saves
were inspected without modifying the active files. Loading edited saves inside
those games still requires validation. These new adapters, KH II and Alice are
marked experimental. Field limits do not guarantee that every combination works
in-game. Alice's checkpoint position and selected outfit are stored separately
and are not edited. Current difficulty is editable by selecting `GameConfig_PC.CFG`
in the editor's file selector. Dress controls change ability flags;
DLC content must be installed. See [Alice format and scope](docs/ALICE_FORMAT.md).
Risk of Rain 2 DLC content still requires ownership of the corresponding DLC.
WEBFISHING level and XP are independent and do not automatically grant rewards.

KH III automatically derives its encryption key from the account folder before
`SaveGames`. For files copied elsewhere, enter the original creator's SteamID64
when prompted. This ID is used locally and kept only in memory; it is not a login.
An unknown account ID cannot be recovered from the encrypted file. The editor
preserves encryption, validates the digest and maintains the internal CRC.

These are scoped editors, not complete exposure of every game system. ReCoM
decks and story flags, BBS decks/command identities/finishers, DDD Dream Eaters,
KH III story and equipment pointers, and Max Payne health, Bullet Time, loaded
rounds and checkpoint state are preserved. KH 0.2 and Melody of Memory PC
encryption remain unresolved and those games are not advertised as supported.

Resident Evil support currently includes only the original RE4 Steam UHD
record version `0x402`. Its account metadata and unrelated data are preserved.
The two difficulty values and the two slot CRCs are maintained together.
Inventory and unlock controls need more mapping; game-load validation is pending.
See [RE4 UHD scope](docs/RE4_UHD_FORMAT.md) and the
[prioritized Resident Evil research](docs/RESIDENT_EVIL_RESEARCH.md) for the other
games, which are not advertised as compatible yet.

## Editing a save

| Editor | Main categories |
|---|---|
| KH Final Mix / KH II Final Mix | Progress, Characters, Collection |
| Re:Chain of Memories | Progress, Collection |
| Birth by Sleep | Progress, Character, Collection |
| Dream Drop Distance HD / KH III | Progress, Characters, Collection |
| Max Payne | Equipment |
| Resident Evil 4 (2005), Steam UHD | Progress, Characters, Records |
| WEBFISHING | Progress, Equipment, Collection |
| Risk of Rain 2 | Progress, Unlocks, Records |
| Alice persistent profile | Progress, Character, Collection |
| Alice configuration | Progress |

Characters uses one selector for Sora, Donald, and Goofy. KH II's Drive Gauge and
Drive Forms are sections within Sora, rather than additional tabs. Collection,
Equipment, Unlocks, and Alice's Character category use section selectors to
browse related controls. Fold or expand a section by clicking its heading.
Section-wide actions only affect that section. BBS uses its saved-slot selector
for each protagonist; DDD and KH III use character selectors within Characters.

1. Close the game, then click its cover or use **Open save**.
2. Choose a slot if the game has several. Search a category to find a field.
3. Change values, then select **Review and apply**. If an integrity warning is
   displayed, explicitly enable repair to apply changes.
4. Review the changes and select **Apply to active save**. The opened file is
   updated in its current location with the same name, without a backup or `.edited`
   copy. You do not need to rename or install it afterward.
5. Check the updated save in-game. **Restore existing backup** can restore a
   backup you already have; it does not create a new backup of the current save.

Steam Cloud can replace local files. A save changed by the game while editing
must be reopened. Applying changes overwrites the opened file; the application
does not automatically keep its previous version.

Shortcuts: **Ctrl+O** opens a save, **Ctrl+F** focuses the current search,
and **Ctrl+S** or **Ctrl+Enter** opens change review.

Use **Changed only** within a category to inspect pending edits in the selected
section. The undo arrow beside a field or in the summary restores its original
value. Invalid values show an explanation and block applying changes, even if
they are in a different category or slot. Normal format notes appear separately
from integrity warnings. Window size and the last folder are saved locally.
Use **Dark mode** or **Light mode** in the header to switch appearance without
losing edits. Your appearance choice is remembered locally; save contents and
KH III account IDs are not stored in preferences.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, bug reports, and
pull requests. Contributions to game support, tests, UI, and documentation are welcome.

## Development

Python and PySide6. Install `requirements.txt` in a virtual environment and run
`python app.py`. Run `python -m unittest discover -s tests -v` for the automated tests.

To build on Windows, install `requirements-build.txt` and run
`python -m PyInstaller --clean --noconfirm UniversalSaveEditor.spec`.
The executable is created in `dist/`.

`core.py` handles byte-preserving save patches and verified file updates. `app.py` provides the
interface, `catalog.py` tracks compatibility, and `version.py` stores the version.
The workflow validates the packaged executable and produces downloadable assets.

Do not commit personal saves. They can contain player names and account IDs.
Supported save extensions and development output are excluded by `.gitignore`.

## License and attribution

Source code: GPL-3.0-or-later. Cover art, game names, and visible logos belong to
their respective owners. See [SOURCES.md](SOURCES.md) and [LICENSE](LICENSE).
