# v0.36.0-alpha — Initial Rockstar PC Story Mode editing

Two new library entries, original cover art and offline previews:

- **GTA V:** existing cash and eight saved skills for Michael, Franklin and
  Trevor: Stamina, Shooting, Strength, Stealth, Flying, Driving, Lung capacity
  and Special ability. The editor resolves an exact typed PSO statistic table;
  absent/duplicate entries and unknown encodings are protected. Legacy and
  Enhanced profile folders are detected. Legacy native files were checked;
  **Enhanced-specific native-file verification is still pending**.
- **Red Dead Redemption 2:** current carried cash in dollars and cents, with
  strict two-decimal precision. This initial adapter edits cash only; honor,
  camp funds, health, Dead Eye, weapons, horses and inventory remain unchanged.

PC story envelopes, AES encryption, header integrity, framed PSO boundaries and
native signed-byte checksums are validated. Output is reparsed and requested
values verified. File length, unknown bytes and encryption state are preserved.
Extensionless SGTA5/SRDR files can be selected directly; existing backups are
excluded from automatic discovery.
The larger collection list scrolls independently to keep the sidebar footer
and saving note visible in smaller windows.

Two public Legacy files passed all 27 field edits per file and byte-identical
restoration. Three local RDR2 files passed cash edits/restorations with all ten
payload checks valid. Original reference/personal files remained unchanged.
Automated tests cover exact changed bytes, encryption/no-op preservation,
precision, malformed structures, duplicate identities, discovery and the UI.
These are file-level checks, **not proof of successful in-game loading**.

Both new editors have Limited coverage. This is not full Rockstar support,
a Legacy/Enhanced conversion tool or an online-profile editor. Exact scope,
references and remaining gates are documented in docs/ROCKSTAR_PC.md.

Download UniversalSaveEditor.exe under Assets and double-click it, or use
Updates > Restart and update from a recent version. The portable executable is
also included in Code > Download ZIP. No installer or terminal is needed.
Apply updates the opened save directly using the original name and location;
no automatic save backup or `.edited` output is created.
