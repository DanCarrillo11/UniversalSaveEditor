# UniversalSaveEditor

A unified Windows save editor with local editing. Browse your games, edit your progress,
review changes, and update your saves directly in one application.

Editors use visible categories and sections, with character selection where
applicable. Changes save directly to the opened file, keeping its name and
location. No automatic backups are created. Alpha versions describe the
application's development stage; verified versions are published as GitHub Releases.

Version **v0.43.0-alpha** expands GTA V story weapons: add/remove 35 recognized
base-slot weapons per character, synchronize shared ammunition, select mapped
attachments and equipped colors, and manage shop acquisition for 40 weapons.
Adding/equipping also updates recognized shop ownership without spending cash.
Three native files cover two distinct inventory revisions; game loading and
Enhanced-specific verification remain pending. This is partial support.

v0.41 expanded RDR2 acquisition to 159 ordinary supplies,
including tonics, herbs, cooked food and Story Mode ammunition variants. Enter
the desired amount and add a missing item in one apply. Existing horses can be
renamed when their inventory and horse-slot names match; both copies update
together. Ambiguous names stay protected. This remains experimental until
in-game loading and persistence are verified.

v0.40 added RDR2 weapon customization: switch owned parts and
replace compatible existing finishes, barrel lengths and sights. Other component
slots and weapon identity are preserved. v0.39 added guarded monetary bounties,
existing catalog unlock actions and experimental acquisition of 26 ordinary satchel supplies.
Unlocks and owned items have separate sections. Adding supplies expands the native
inventory while preserving existing records and script chunks. Successful game
loading remains unverified; this is not complete RDR2 support. Existing camp,
horse, character and compendium controls remain available. GTA V also retains character cash and eight saved skills.
Legacy native files were checked; an Enhanced-specific native-file check is
still pending. Both GTA V save locations are detected; unknown formats are refused.
In-app updates remain available through
**Updates > Restart and update**.
Earlier releases expanded Elden Ring and KH progression.
**Complete support for all games has not been achieved.** The catalogue now
contains 23 games. Each editor documents its actual scope and verification limits.

## Download and run

Download `UniversalSaveEditor.exe` from **Releases > Assets** and double-click it.
The application is portable; no installer, Python, or command-line setup is needed.

You can also select **Code > Download ZIP**, extract the folder, and open the
executable included at its root. Startup can take a few seconds.

## Features

- [Rockstar PC Story Mode](docs/ROCKSTAR_PC.md): GTA V cash and eight skills for Michael, Franklin and Trevor, plus RDR2 character, inventory, horse, camp and recorded-history fields. [Exact RDR2 scope](docs/RDR2_FIELDS.md) separates records from acquisition and rewards. Enhanced native-file validation, game loading and complete progression remain pending.

- [Latest compatibility improvements](docs/COMPATIBILITY_V35.md): bounded owned loadouts in Elden Ring, stored Dream Eater rank/disposition/affinity, Re:CoM saved level and corrected KH3 Links/item shortcuts. Native-file reparsing passes; gameplay verification and full catalogue support remain pending.

- [Elden Ring equipment loadouts](docs/ELDEN_RING_LOADOUTS.md): six hand and four armor assignments using uniquely owned held copies, synchronized native references/fingerprints, swaps and protected inconsistent layouts. Unknown menu snapshots stay unchanged; gameplay validation remains pending.

- [Updates from the app](docs/UPDATES.md): check official releases, download with progress and SHA-256 verification, then restart to update the portable executable. Startup checks are optional and off by default. Editing saves works offline. Versions before v0.33 require one manual download first.

- [Elden Ring equipment creation](docs/ELDEN_RING_EQUIPMENT.md): 377 base-game armaments and 559 armor pieces, separate copies with native handles, acquisition counters and bounded structural growth. Unknown layouts and insufficient padding remain protected.

- [KH1 spell tiers and acquisitions](docs/KH1_PROGRESSION.md): seven spell families, Donald acquisition synchronization, six summons, five Trinity colors, 99 rescued puppies and unspent Torn Pages. Existing rewards and story flags are preserved.

- [KH2 inventory, AP and acquisition](docs/KH2_INVENTORY_AP.md): correct stock names/positions and artwork IDs, conserved equipment transfers/swaps, recognized standard AP budgets, six spell tiers, synchronized shortcuts, form/summon/report acquisition and current/maximum Drive checks. This corrects misleading bag labels in earlier versions.

- [Equipment and spell relationships](docs/FUNCTIONAL_RELATIONSHIPS.md): owned Requiem weapon references/shortcuts, Elden Ring memorized spells with exact memory costs, KH1 magic shortcuts, KH2 saved camera/control options, KH3 Critical transitions/companion AI and native RE4 Remake stack capacities, Pesetas/health/case capacity, base-game Elden Ring spell learning, DDD spirit details and RE2/RE3 inventory capacity.

- [Faster editor loading](docs/EDITOR_PERFORMANCE.md): large sections load on demand, with bounded pages and reused item-art archives. All saved fields remain searchable and editable where supported. Unexpected Python errors produce a local report without save contents.

- Visible editor navigation: section lists, character buttons and one search across all categories. A fixed bottom bar keeps pending changes, review and saving within reach. [Navigation and saving](docs/EDITOR_NAVIGATION.md).

- [Current completion work](docs/CURRENT_GAME_COMPLETION.md): additional KH systems, mapped Elden Ring world/capacity controls and Resident Evil records. All 21 existing games remain the priority; new games and icons are deferred.

- [Functionality expansion across 17 existing editors](docs/FUNCTIONAL_EXPANSION.md): cosmetic/item tools in WEBFISHING, KH3 equipment/abilities, BBS/DDD character tools, Elden Ring appearance, additional Resident Evil settings/unlocks/records, and searchable paged Risk of Rain 2 statistics. Icons and new games are deferred.

- Browse every editor without a save or game installation. A “No save data found” banner identifies the read-only preview; examples show real supported field types and categories. Drop-down choices remain browsable, while Apply, backups and editable values are disabled. Opening a real save restores normal editing.
- Honest [feature coverage per game](docs/EDITOR_COVERAGE.md): broad, partial or limited. No game is currently labelled full support; this rating is separate from file checks and gameplay validation.

- Original game artwork across 14 editors: all six supported Kingdom Hearts, WEBFISHING, Risk of Rain 2, Elden Ring, RE HD Remaster, RE2 Remake, RE3 Remake, RE5 and RE7. KH equipment images follow dropdown changes. Coverage varies by game; [exact counts and pending games](docs/ITEM_ARTWORK.md) are documented. No AI artwork or runtime downloads.

- Original Elden Ring item artwork: 307 supported goods and 487 known base armaments, shown in inventory, storage, Add items and weapon upgrade rows. Archived image bytes stay unchanged; variants retain their base weapon image. No AI images or runtime downloads.

- Original RE2 Remake inventory artwork: 27 mapped supplies with game icons, English names and collection groups. Exact source pixels, no AI images. Unmapped items keep their existing text display; see [artwork sources and coverage](docs/ITEM_ARTWORK.md).

- [Resident Evil Village](docs/RE8_FORMAT.md): Lei, CP, current health, existing stacks and separate extra-content flags. Experimental Steam adapter; native Steam and in-game validation pending.

- [Expanded editors](docs/EDITOR_EXPANSION.md): KH1/KH2 party equipment and abilities, Elden Ring held-goods creation, known armament upgrades and NG+ scaling, RE4 (2005) case quantities/tune-ups and RE6 equipped skills.

- Compatibility details per game: supported format, file-check evidence, gameplay evidence and known limits.
- Helpful errors with specific guidance for known conflicting edits and a Copy diagnostic button. Reports omit save contents, paths, account IDs and character names; nothing is sent automatically.
- Recent saves in the header (Ctrl+R), remembering up to ten validated files and the last selected record. Locate moved files, remove shortcuts, clear history or turn it off.
- Verified collection labels and grouped inventories: 60 KH III synthesis-material names, Elden Ring crafting/upgrade/consumable sections and clearly marked unidentified entries.
- Clean light and dark appearances with a header toggle and a remembered preference.
- Responsive game library with full cover art, search, filters, and sorting.
- Mark games with the star on each cover. Favorites appear first in the library;
  open **Favorites** in the sidebar to show only your starred games.
- Short view fades and animated cover highlights, with a remembered **Reduce motion** option.
- Platform logos and names below each cover; currently Steam. Editor status and
  detected saves remain in the details panel. Coming-soon games are not editable.
- Click a compatible cover to open its detected save directly.
- Automatic discovery, manual file selection, and drag and drop.
- Game-specific categories with visible section navigation and character selection; names include Inventory, Cards, Commands and Collectibles where appropriate.
- Foldable sections and field search, including inventory IDs, unlocks and the selected equipment name.
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

See [support privacy, recent saves and collection labels](docs/SUPPORT_AND_HISTORY.md) for details.

## Compatibility

| Game | Editable fields | Status / save action |
|---|---|---|
| GTA V, PC Story Mode | Character cash/skills; saved-player health/armor/flags; clock/resprays; vehicle protections/plates; base-slot weapon acquisition, shared ammo, components/colors and weapon-shop flags | Limited; Legacy native files checked; Enhanced-specific file check and game loading pending |
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

All Resident Evil adapters use direct apply and retain the original account and
unrelated bytes. Their scope is deliberately limited to recognized fields.
**No edited Resident Evil save has been validated by loading it in-game.**
Numbered RE Engine collection entries follow saved order. RE2 has 27 named
supplies with original icons; other entries remain unmapped. System profiles
and gameplay slots expose different fields.
RE4 Remake and Requiem detect the original SteamID64 from normal save paths;
copied saves need their original creator's ID. DLC ownership remains necessary.
RE0's encryption and section table have been researched, but editing is pending.
See [research and validation status](docs/RESIDENT_EVIL_RESEARCH.md),
[RE5](docs/RE5_FORMAT.md), [Requiem](docs/RE9_FORMAT.md), [RE Engine](docs/RE_ENGINE_FORMAT.md), and
[HD Remaster / RE6 / RE0 boundaries](docs/RE_LEGACY_PC.md).

Elden Ring targets the original Steam edition and native `ER0000.sl2` files.
Level and lifetime runes are calculated automatically; existing item stacks keep
their IDs. See [scope, integrity and validation](docs/ELDEN_RING_FORMAT.md).
Edited saves are intended for offline use; in-game verification remains pending.

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

Original Resident Evil 4 support targets the Steam UHD record version `0x402`.
Its account metadata and unrelated data are preserved.
The two difficulty values and the two slot CRCs are maintained together.
Existing case quantities and known weapon tune-up tiers are editable; new case
objects and comprehensive unlocks need more mapping. Game-load validation is pending.
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
| GTA V | Characters: cash/skills and saved player; Progress: clock; Equipment: choose a protagonist and weapon for inventory/shop options, or Vehicles for garage controls |
| Red Dead Redemption 2 | Progress: Currency / Camp / Bounties / Statistics / World clock; Character: Honor / Cores / XP; Inventory: Supplies / Ammunition / Weapons / Horses / Compendium / Catalog unlocks / Add supplies |
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

New game additions are paused while we complete the existing catalogue. Resident Evil, starting with Requiem, is the priority. See the [completion work list](docs/COMPLETION_PLAN.md); no game is currently labelled full support.
