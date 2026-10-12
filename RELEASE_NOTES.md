# UniversalSaveEditor v0.14.0-alpha

Initial experimental support for **Resident Evil 4 (2005), Steam Ultimate HD Edition**. Choose a populated save slot and edit it in three categories:

- **Progress:** Pesetas and Very Easy/Easy/Normal/Professional saved difficulty.
- **Characters:** current and maximum HP for the player and Ashley.
- **Records:** number of saves, completed rounds, and chapter/total continues, kills, hits and shots.

The editor preserves the account metadata, other slots, inventory, weapons and room state. Difficulty updates both mode mirrors, and edited slots receive both integrity checks. Invalid health combinations or unsupported record versions are rejected. Steam saves are discovered automatically and the new library card uses official portrait artwork.

All 123 game-editor and interface tests pass. Four local populated slots were inspected and edited in memory without changing the active file. The portable executable is checked for startup and bundled resources.

**Scope:** this is an initial scoped editor, not complete RE4 support. Inventory, weapon upgrades, costumes and unlocks are not yet editable. In-game loading of edited output still needs verification. The other prioritized Resident Evil games have research notes but are not advertised as compatible. See [Resident Evil research](https://github.com/DanCarrillo11/UniversalSaveEditor/blob/main/docs/RESIDENT_EVIL_RESEARCH.md).

Saving updates the opened file directly, retaining its name and location and creating no automatic backups.

Download UniversalSaveEditor.exe and open it with a double click.
