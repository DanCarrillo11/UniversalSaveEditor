# UniversalSaveEditor v0.9.0-alpha

Save changes directly to the opened file for every available editor, including
Kingdom Hearts Final Mix and Kingdom Hearts II Final Mix on Steam.

- Review your changes and select **Apply to active save**.
- Keep the same filename and location. No `.edited` export, destination dialog,
  manual renaming, or installation of a separate save is needed.
- No automatic backups are created when editing or restoring an existing backup.
- Explicit integrity repair updates the opened KH save and refreshes its status.
- Keep the selected KH slot after applying and reload its updated values.
- Preserve validation, checksum updates, verified atomic writes, and detection
  of files changed by the game while editing.

## Download and run

Download UniversalSaveEditor.exe and open it directly. No installer, Python,
or command-line setup is required. **Code → Download ZIP** also includes the
executable. Close the game, open its save, edit values, then review and apply.
If an integrity warning appears, explicitly enable repair before applying.

Applying overwrites the opened file. The application does not automatically
keep its previous version. **Restore existing backup** works with backups you
already have and does not create another backup.

## Validation and limits

58 automated tests cover the save editors and interface, including direct KH
writes, CRC repair, selected-slot preservation, cancellation, failed writes,
concurrent game saves, and the absence of backup or exported files.
The release build verifies executable startup and packaged resources.

Actual in-game behavior after changing KH difficulty remains unverified. Changing
the mode does not recreate starting stats, bonuses, or abilities. KH II requires
a populated saved slot and remains experimental, as does Alice. All previous
editing features are included; Alice checkpoint editing and outfit selection
remain outside its scope.

See docs/KH_DIFFICULTY.md and docs/ALICE_FORMAT.md for mapped formats and limits.
SHA256SUMS.txt contains the hash of the downloadable executable.
