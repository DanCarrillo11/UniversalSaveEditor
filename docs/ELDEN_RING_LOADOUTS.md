# Elden Ring owned equipment assignments

v0.34 adds **Character > Equipment loadout**, with six hand assignments and
head/chest/arm/leg armor. Choose a specific copy already in held inventory.
Supported native representations must agree before a slot can be changed.

- Synchronize the inventory-row index (row + 0x180), bare equipment identity,
  physical handle and dynamic equipment identity. Recalculate the corresponding
  native weapon or armor/talisman fingerprint and the character block MD5.
- Restrict armor to its exact body category. Unknown identities, ambiguous
  ownership, storage-only copies and invalid reference/fingerprint layouts are protected.
- Refuse assigning one physical copy to two slots. Swapping both assignments in
  one Apply operation is supported. Existing repeated technical Unarmed records
  are permitted; no missing Unarmed/bare-armor placeholder is synthesized.
- Keep ownership, quantities, acquisition order, active-hand selection, Ash links,
  affinities, talismans, unknown sections and global menu snapshots unchanged.
  Recognized held bare placeholders can be selected; clearing without an owned
  placeholder is unavailable. New creations become selectable after applying.
- Combine assignments with existing upgrades, runes, stats, other characters and
  structural equipment creation. Verify requested physical handles after reparsing,
  even if upgrade labels change the drop-down ordering.

Existing weapon upgrades now also recognize coherent native inventory/index/ID/
handle/dynamic relationships without requiring an unrelated menu snapshot to equal
the physical handle. The older recognized representation remains supported.

Four public native files passed **53 assignment changes and 28 weapon upgrades**
across 28 populated character records. Samples overlap; this is not a count of
unique players. Originals and menu snapshots remained unchanged. Synthetic tests
cover exact changed bytes, swaps, duplicate rejection, inconsistent references,
combined growth/upgrades and UI staging. Native tests are in-memory copies only.

Game-load verification is still pending. Complete Elden Ring support is **not**
claimed: talisman assignment/families, ammunition/quick items/pouch/Physick, Ash
attachment/affinities, full DLC and progression dependencies remain open.

The independent writer uses factual layout definitions cross-checked with the
already attributed pinned SaveForge equipment writer and ER-Save-Lib structures.
Their unchecked hash/window calculations are not copied; fingerprints are checked
against the known bare-ID order in native files before editing. See SOURCES.md.
