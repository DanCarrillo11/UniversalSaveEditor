# UniversalSaveEditor v0.7.0-alpha

The first feature update expands the Alice: Madness Returns persistent-profile
editor and fixes the previous Teeth offset.

## Alice editor

- Teeth, four weapon levels, and acquired abilities with related state updates.
- Current health, story health upgrades, and sixteen paint-pot pickups.
- Twelve dress ability flags and installed-content DLC weapon flags.
- 89 small memories, five major memories, 83 bottles, and 59 snouts.
- Sixteen Radula rooms, completed chapters/difficulties, and chapter-select entries.
- Twenty enemy-journal entries, story cinematics, play time, and statistics.
- Current and lowest-used difficulty in the separate `GameConfig_PC.CFG` file.
- Automatic updates to pickup records, paint-pot totals, chapter flags, snout
  counters, and affected completion statistics.
- Level selectors, toggles, search, and batch category actions.

The new reader walks the full revision-49 archive. The old Teeth field pointed
to a combat statistic, which is preserved by the corrected editor.

## Download and run

Download `UniversalSaveEditor.exe` and open it directly. No installer, Python, or
command-line setup is required. **Code → Download ZIP** includes the executable.
Exact backups are created before an active profile is replaced.

## Validation and limits

50 automated tests cover the editors, interface, backups, archive preservation,
and coupled Alice edits. The release build checks startup and packaged resources.

**Alice remains experimental.** In-game validation of all categories is pending.
This update edits `PersistentData_PC.PSD` and difficulty in `GameConfig_PC.CFG`.
Select the configuration file in the editor's file selector to change difficulty.
It does not edit the separate checkpoint: position and selected outfit are
outside its scope. Dress controls change ability flags; DLC content must already
be available. A checkpoint can override current health. Statistics do not directly
grant Steam achievements.

Close Alice before applying changes. Keep backups until the edited profile has
been checked in-game. See `docs/ALICE_FORMAT.md` for format details.

`SHA256SUMS.txt` contains the hash of the downloadable executable.
