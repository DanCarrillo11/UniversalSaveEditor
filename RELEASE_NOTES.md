# v0.40.0-alpha — RDR2 weapon parts and finishes

RDR2 PC Story Mode now includes checked weapon customization:

- Switch between owned components in the same weapon slot, keeping exactly
  one installed part.
- Replace compatible existing leaf finishes, barrel lengths and sights with
  named variants recognized in the save's catalog. New variants synchronize
  their existing catalog unlock.
- Keep weapon copies and stored finishes for nested grips separate. Weapon
  identity, ownership GUIDs, part slots and unrelated components are preserved.
- Browse the new controls in read-only previews without a personal save.

Unknown names, duplicate choices, invalid quantities/flags, parent cycles,
components with dependent children and unsafe vertex-data parts are protected.
This does not spawn weapons, create missing component slots or install arbitrary
hashes. The earlier bounty, catalog and experimental satchel-supply tools remain.

Three native files passed all 350/41/65 component-selector changes in memory,
all ten payload checks, exact-span comparisons and byte-identical restoration.
Original personal files were not changed. Tests cover owned-part selection,
new-finish catalog synchronization, nested grips, malformed relationships,
combined supply acquisition, navigation and staged edits.

**RDR2 remains Limited coverage.** Successful in-game loading/persistence,
weapon/clothing acquisition, stable management, camp upgrades and complete
story/challenge/reward relationships remain pending. Structural checks do not
establish full support. See docs/RDR2_FIELDS.md for the precise scope.

Download UniversalSaveEditor.exe under Assets and double-click it, or use
Updates > Restart and update. Code > Download ZIP also contains the portable
executable. Apply replaces the opened file directly, without automatic save
backups or .edited output.
