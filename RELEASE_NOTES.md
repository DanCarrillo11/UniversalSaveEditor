# v0.44.0-alpha — GTA V saved vehicle customization

- Select named primary/secondary, pearlescent and wheel paint for recognized
  occupied garage vehicles. The catalogue includes 161 named paint indexes.
- Edit window tint and the saved RGB colors for tire smoke and neon lighting.
  Color editing does not install or enable the corresponding modification.
- Select supported engine, brake, transmission, suspension and armor stages.
  Only existing uniquely mapped modification entries and matching vehicle kits
  qualify. A model with one known kit can initialize it when applying an upgrade.
  Unknown stages, unsupported kits and ambiguous maps stay protected.
- Show each recognized vehicle's model name as read-only information. Keep its
  identity, location, garage membership, body kit, wheels and other state intact.
- Browse the new fields through Equipment > Vehicles, including offline examples.
  All earlier character, weapon, shop, clock, garage-service and plate tools remain.

Two native Legacy files cover the 96/112-byte vehicle layouts. Individual and
combined edits pass reparsing, checksum and exact-span checks in encrypted/plain
copies; the originals remain unchanged. Synthetic and interface tests cover
palette bounds, bad pointers, duplicate map keys, unknown kits, opaque node bytes,
kit initialization, staging/reset and read-only previews.

**GTA V remains Limited coverage.** Vehicle creation/model swaps, complete body/
wheel/livery tuning, full DLC weapon acquisition, clothes/properties, collectibles
and story/reward dependencies are still pending. No Enhanced-native or successful
in-game loading/persistence verification is claimed.

Download UniversalSaveEditor.exe under Assets, use Updates > Restart and update,
or extract Code > Download ZIP and open the included exe. Saves are overwritten
in place when you apply changes, without automatic backups or .edited files.
