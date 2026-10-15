# v0.35.0-alpha — Owned loadouts and Kingdom Hearts corrections

This release expands four existing editors. No new games or icons are added.

- **Elden Ring:** four ammunition slots, ten quick items, six pouch entries and
  two Physick tears. Choose existing owned items; native references and checked
  fingerprints synchronize. Empty slots, categories, duplicates and inconsistent
  data are handled explicitly. No item, upgrade, quest or reward is granted by
  these selectors; active selection and unrelated state are preserved.
- **Kingdom Hearts III:** fix five Link command identities (70–74). Add eleven
  consumable shortcut commands with separate item/command IDs, positive owned
  stock and enabled matching Sora equipment checks. Recognized shortcuts clear
  when an explicit inventory/equipment change makes the item unavailable.
- **Dream Drop Distance:** edit existing recognized spirits' stored rank code,
  disposition index and affinity counter, preserving the other nibble and
  unknown encodings. Growth, boards and displayed affinity levels are separate.
- **Re:Chain of Memories:** edit recognized saved character level 1–99,
  independently of XP, HP, CP, sleights and level-up rewards.
- Update offline previews, source attribution and the compatibility/gap records.

408 local automated tests passed. Public native-reference checks passed for
28 ammunition, 27 quick-item and 25 Physick edits/restorations across overlapping
Elden Ring records, 39 edits across 13 DDD spirits, two Re:CoM level records,
and an encrypted KH3 item shortcut. All original reference files were unchanged.
These are file-level checks, not proof of successful in-game loading.

**Full support for the 21-game catalogue has not been achieved.** Remaining
unmapped formats, character/equipment rules, reward/progression relationships
and game-load checks are documented in docs/CURRENT_GAME_COMPLETION.md and
docs/COMPATIBILITY_V35.md. Unknown saved state remains protected.

Download UniversalSaveEditor.exe under Assets and double-click it, or use
Updates > Restart and update from v0.33 or newer. The portable executable is
also included in Code > Download ZIP. No installer or terminal is needed.
Apply updates the opened save directly, keeping its name and location;
no automatic save backup is created.
