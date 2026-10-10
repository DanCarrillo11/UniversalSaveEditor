# UniversalSaveEditor v0.8.1-alpha

Change the saved difficulty of an existing Kingdom Hearts Final Mix or
Kingdom Hearts II Final Mix Steam slot from the new **Difficulty** category.

- KH Final Mix: Beginner, Final Mix (Standard), and Proud.
- KH II Final Mix: Beginner, Standard, Proud, and Critical.
- Named mode selectors and review of the chosen mode before export.
- Wider selectors so Final Mix (Standard) is displayed in full.
- Other slots, character attributes, inventory, and progress are preserved.
- The affected KH II record checksum and the outer Steam-container CRC are
  updated on export. Existing integrity failures require explicit repair.

## Download and run

Download UniversalSaveEditor.exe and open it directly. No installer, Python,
or command-line setup is required. **Code → Download ZIP** also includes the
executable. Select your saved slot, open **Difficulty**, choose a mode, then use
**Review and export** to create a copy and preserve the original backup.

## Validation and limits

54 automated tests cover the save editors, interface, backups, every supported
KH difficulty, multiple-slot isolation, exact byte preservation, and checksums.
The release build verifies executable startup and packaged resources.

A local KH I profile was exported in memory for each mode without replacing the
original. The local KH II container has no saved slots; KH II mode changes were
tested using synthetic records. Create a slot at an in-game save point before
opening that container. Actual in-game behavior after changing modes remains
unverified for both games.

Changing the saved mode does not recreate a new-game setup. Existing character
stats, starting bonuses, and awarded abilities are not recalculated. Selecting
Critical does not add its starting bonuses or rebuild existing stats. The editor
does not directly award Steam achievements.

KH II and Alice remain experimental. Alice's profile and difficulty features from
v0.7.0-alpha are included; checkpoint editing and outfit selection remain outside
its scope. Close the game before installing an edited save and keep your backup
until you have checked it in-game.

See docs/KH_DIFFICULTY.md and docs/ALICE_FORMAT.md for mapped formats and limits.
SHA256SUMS.txt contains the hash of the downloadable executable.
