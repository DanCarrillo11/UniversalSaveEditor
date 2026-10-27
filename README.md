# UniversalSaveEditor

A portable Windows app for editing saves from multiple PC games in one place.
Open a game, find what you want to change, review your edits and save.
No installation, Python setup, account or save uploads are required.

v0.50 adds recognized KH1 equipped/available AP calculations and checks combined
ability, base-AP and accessory changes. Standard accessory bonuses and duplicate
equipped abilities count toward the budget. Unknown costs remain protected from
inference. Requiem difficulty and Elden Ring talisman additions from v0.49 are
retained. Current coverage and remaining work are documented separately; these
changes do not establish full game support.

## Download and open

Download **UniversalSaveEditor.exe** from
[the latest release](https://github.com/DanCarrillo11/UniversalSaveEditor/releases/latest)
and double-click it. If you download the Windows ZIP, extract it first.
Use the Windows ZIP under **Releases > Assets** for the portable application.

## Edit your first save

1. Close the game and click its cover. The app opens a detected save, or a
   read-only example if no save was found. Use **Open save…** to choose your file.
2. Choose the save slot or character you want. Use the category tabs and the
   section list, or search for a name such as **money**, **health** or **difficulty**.
3. Change the values. **View changes** lets you find, undo or return to any edit.
   **Fix first issue** takes you to a value that needs correcting.
4. Select **Review and save**, check the final changes, then **Apply to active save**.

The app updates the opened file in its original location and keeps its name.
**No automatic backup or renamed edited copy is created.** If the game or Steam
Cloud changes that file while you are editing, reopen it before applying edits.
An integrity warning requires explicitly selecting repair before saving.

## A simpler workspace

- **Everyday tools first.** Common gameplay controls appear in the main categories.
  Turn on **Advanced options** for records and less common settings.
- **Clear navigation.** Character buttons, named sections and a section finder
  keep large inventories manageable. **Clear filters** returns to normal browsing.
- **Searchable choices.** Long lists of items, equipment or colors open a name
  search. Cancelling leaves the value unchanged.
- **Complete change review.** Search and page through every pending edit, including
  edits in other slots or hidden Advanced views. Nothing applies while browsing.
- **Useful game groupings.** RDR2 separates Character, Inventory, Weapons and Horse;
  Owned items and Add items have different views. GTA V groups equipment and style.
- **Your library.** Favorite games, recent saves, full cover art, light/dark modes
  and optional reduced motion. Clicking a cover resumes its last-used detected save.
- **Local control.** Direct saving, optional restoration of backups you already
  have, and in-app updates with download verification. Diagnostics are shared only
  when you choose to copy them.

Shortcuts: **Ctrl+O** open a save · **Ctrl+F** search · **Ctrl+R** recent saves ·
**Ctrl+S / Ctrl+Enter** review and save.

## Compatibility

The catalogue contains 23 games. **No editor is currently labelled full support.**
Available controls depend on the save format, revision and selected slot.
Automated file checks and a successful reparse do not establish in-game compatibility.
Open **Save details > Help & details** for the selected game's evidence and limits.

| Game | Editable fields | Status / save action |
|---|---|---|
| GTA V, PC Story Mode | Character cash/skills; saved-player health/armor/flags; clock/resprays; vehicle paint/performance/protections/plates; named wardrobe ownership and synchronized current garments; base-slot weapon acquisition, shared ammo, components/colors and weapon-shop flags | Limited; Legacy native files checked; Enhanced-specific file check and game loading pending |
| Red Dead Redemption 2, PC Story Mode | Cash/camp, honor, player attributes, supplies/ammunition, weapon condition/parts/finishes, horse care/names, compendium/history, bounties, catalog unlocks and experimental common-supply acquisition | Limited; three native files checked. Weapon/clothing acquisition, stable management, story/reward dependencies and game loading pending. See [exact scope](docs/RDR2_FIELDS.md). |
| Elden Ring | Runes, attributes/vitals, automatic level, appearance sliders, deaths, inventory/storage stacks, held-goods creation, 171 base-game spell acquisitions, owned spell loadouts, existing upgrades and NG+ scaling | Experimental Steam SL2; in-game verification pending |
| Resident Evil 4 (2005), Steam Ultimate HD Edition | Pesetas, difficulty, player/Ashley health, save count, completed rounds and combat statistics, existing case quantities and known weapon tune-up tiers | Experimental; direct apply; new case objects and comprehensive unlocks pending |
| Resident Evil HD Remaster, PC | Recognized gameplay records, difficulty, defensive supplies, known inventory/item-box identities and quantities, next empty box entry | Experimental; public PC fixture checked; recognized gameplay sections selectable |
| Resident Evil 2 (2019), Steam | Difficulty, health, existing quantities, rewards/files, completion/challenge records and Ghost Survivors counters | Experimental; real Steam fixture validation pending |
| Resident Evil 3 (2020), Steam | Health, existing quantities, shop/rewards, completion/challenge/combat records | Experimental; shared console payload checked; real Steam fixture validation pending |
| Resident Evil 4 (2023), Steam | Pesetas, points, Spinels, player/partner health, increasing case capacity, existing quantities, profile-scoped costume/accessory/extra-shop and challenge records | Experimental; real Steam fixture validation pending |
| Resident Evil 5, Steamworks | Money, points, costumes, filters, infinite ammo, library files and 45 figures | Experimental; public Steamworks fixture checked |
| Resident Evil 6, PC | Skill points, equipped campaign/extra-mode slots, Mercenaries flags and results, emblems and named existing reserve ammunition/herbs | Experimental; public Steam fixture checked |
| Resident Evil 7, Steam | Difficulty, health, existing item-box quantities, restarts and existing DLC mode/completion flags | Experimental; shared console payload checked; real Steam fixture validation pending |
| Resident Evil Village (RE8), Steam | Lei, CP, saved player health, existing stacks, content flags and lifetime/completion/combat records | Experimental; shared console gameplay payload and synthetic Steam envelopes checked; native Steam and in-game checks pending |
| Resident Evil Requiem, Steam | Money/points, player health/upgrades, existing stocks, attached upgrades, content flags and lifetime/challenge/combat records | Experimental; nine native Steam files checked |
| WEBFISHING | Economy/progression, bait/lures, upgrades, cosmetics/appearance, inventory creation/replacement/removal, hotbar/locks, quests and journal | Available; direct apply |
| Risk of Rain 2, Steam | Coins, 454 unlock identifiers, additional existing numeric statistics and paged character/enemy/stage/item records | Available; direct apply |
| Kingdom Hearts Final Mix, Steam | Munny, difficulty, party attributes/XP, equipment/abilities, character magic availability and inventory | Experimental expanded party editing; direct apply |
| Kingdom Hearts II Final Mix, Steam | Munny, difficulty, XP, party attributes, equipment transfers, standard AP checks, abilities/AI, magic/shortcuts, form/summon/report acquisition and correctly mapped bag stock | Experimental; direct apply |
| Alice: Madness Returns, Steam | Teeth, four weapon levels, abilities, health upgrades and paint pots, dress abilities, 89 memories, 83 bottles, 59 snouts, Radula rooms, chapters, difficulty, enemy journal, cinematics, and statistics | Experimental; direct apply |
| Re:Chain of Memories, Steam | Moogle Points, XP, difficulty, 1,139 named card quantities, mapped acquisition/friend flags and monotonic completion flags | Experimental; native flag edits reparsed; in-game flag effects pending |
| Birth by Sleep Final Mix, Steam | Currency, difficulty, character progression, commands/abilities, equipped Keyblade, finisher XP and existing command-deck references | Experimental; direct apply |
| Dream Drop Distance HD, Steam | Currency/difficulty, Sora/Riku progression, Keyblades, inventory and existing populated spirits’ stats, level/XP, Link Points, link counts, RGB tint and normal/shiny appearance | Experimental; direct apply |
| Kingdom Hearts III + Re Mind, Steam | Currency/difficulty, progression, party attributes/equipment/active weapon/abilities, magic, Links, shortcuts, minigame records, mapped acquisition and inventory/materials | Experimental; direct apply |
| Max Payne 1, Steam | Original revision 48 weapon ownership, reserve ammunition and painkillers | Experimental; direct apply |

## Details and limits

- [Everyday and Advanced tools](docs/EDITOR_USABILITY.md),
  [navigation and saving](docs/EDITOR_NAVIGATION.md),
  [coverage by game](docs/EDITOR_COVERAGE.md) and [latest changes](CHANGELOG.md).
- [Rockstar PC Story Mode](docs/ROCKSTAR_PC.md) and [exact RDR2 scope](docs/RDR2_FIELDS.md).
  GTA V Enhanced-specific validation, edited-save game loading and complete
  progression remain pending.
- [Elden Ring format and integrity](docs/ELDEN_RING_FORMAT.md),
  [equipment creation](docs/ELDEN_RING_EQUIPMENT.md) and
  [loadouts](docs/ELDEN_RING_LOADOUTS.md). Edited saves target offline use;
  in-game verification remains pending.
- [Resident Evil research and validation](docs/RESIDENT_EVIL_RESEARCH.md).
  No edited Resident Evil save has been validated by loading it in-game.
  System profiles and gameplay saves expose different tools. RE0 editing is pending.
- [Kingdom Hearts difficulty](docs/KH_DIFFICULTY.md),
  [KH1 progression](docs/KH1_PROGRESSION.md) and [KH2 inventory/AP](docs/KH2_INVENTORY_AP.md).
  Support targets the Steam editions; unknown layouts remain protected.
- [Alice format and scope](docs/ALICE_FORMAT.md). Open `GameConfig_PC.CFG` to
  change difficulty; checkpoint position and selected outfit are not edited.
- [Original game artwork and sources](docs/ITEM_ARTWORK.md),
  [updates](docs/UPDATES.md) and [privacy and recent saves](docs/SUPPORT_AND_HISTORY.md).

Copied encrypted KH III, RE4 Remake and Requiem saves may need their original
creator's SteamID64. This is used locally to read the file, not to sign in.
DLC features still require owning/installing the corresponding game content.

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

New game additions are paused while we complete the existing catalogue. Resident Evil, starting with Requiem, is the priority. See the [completion work list](docs/COMPLETION_PLAN.md); no game is currently labelled full support.
