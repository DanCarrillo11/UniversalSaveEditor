# v0.39.0-alpha — RDR2 catalog unlocks, supplies and bounties

This update expands RDR2 PC Story Mode while keeping its compatibility status
**Limited**:

- **Catalog unlocks:** apply existing saved unlocks for named weapons, clothing,
  satchels, ammunition, components, horse equipment and breeds. These controls
  are separate from ownership: they do not add, buy or equip the object.
- **Add supplies:** experimental one-unit acquisition of 26 ordinary satchel
  items, including medicine, food, horse supplies and ammunition. The writer
  validates the active character graph, creates unique record IDs and expands
  the native blocks with checked directory relocation. Existing item quantities
  remain in their usual sections.
- **Bounties:** edit recognized regional monetary amounts or clear them together.
  The current native bounty is synchronized. Mission-temporary state and edits
  requiring an ambiguous current region are protected; story wanted flags stay.
- **Cash and loading:** resolve cash through typed active-inventory membership
  and reuse the validated inventory graph across editor sections.
- **Offline previews:** browse the new sections without owning the game or
  opening a personal save. Preview controls remain read-only.

Three native files passed in-memory catalog edits, all ten payload checks and
exact-span preservation. Supply acquisition retained all 834/233/302 original
inventory records and all nine script chunks. Original personal files were not
modified. Tests also cover malformed pointers/schemas, GUID collisions, separate
backup inventory, action staging and previews.

**Successful in-game loading and persistence remain unverified.** Supply
acquisition is experimental; its allocator has not been confirmed against the
game's runtime allocator. Weapon/clothing acquisition, stable management, camp
upgrades and complete story/challenge/reward dependencies are still pending.
This release does not claim full RDR2 support. See docs/RDR2_FIELDS.md for details.

Download UniversalSaveEditor.exe under Assets and double-click it, or use
Updates > Restart and update. The portable executable is also included in
Code > Download ZIP. Apply replaces the opened file directly; no automatic save
backup or .edited output is created.
