# v0.42.0-alpha — GTA V player and garage tools

- Edit recognized saved-player health, armor and their maxima. Lowering a maximum
  also lowers the current value when needed. Explicit conflicting edits are rejected.
- Adjust saved stamina, fast-reload, fire-protection, drive-by and gang flags.
  These describe stored state; scripts may reset them after loading/switching.
- Set clock time and saved garage respray options.
- Edit six saved damage/tire protection flags and license plates for existing
  occupied garage vehicles. Plates accept up to eight printable ASCII characters.
  Vehicle models, upgrades, ownership and empty slots are preserved.
- Browse Characters, Progress and Equipment, including read-only offline previews.

New fields were checked in two native Legacy references, including both known
vehicle layouts, encrypted/plaintext exact-span edits, combined edits and
byte-identical restoration. Originals were not modified. Tests cover malformed
arrays, duplicate roots, unknown models, health/armor consistency, plate limits,
navigation, staging, reset and read-only previews.

**GTA V remains Limited coverage.** Weapon/ammunition inventory, vehicle creation,
model swaps/tuning, property/clothing acquisition and complete collectible/story/
reward dependencies remain unsupported. Enhanced-specific native validation and
successful in-game loading/persistence are still pending. Existing money and
eight skills for Michael, Franklin and Trevor remain available. Story Mode only.

Download UniversalSaveEditor.exe under Assets and double-click it, or use
Updates > Restart and update. Code > Download ZIP contains the portable exe too.
Apply replaces the opened file directly, without automatic save backups or
.edited output.
