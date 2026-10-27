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
claimed: Ash attachment/affinities, full DLC and progression dependencies remain open.

v0.35 adds four ammunition slots plus ten quick items, six pouch assignments
and two Physick tears. [Exact ownership, synchronization and verification
rules](COMPATIBILITY_V35.md) are documented separately.

The independent writer uses factual layout definitions cross-checked with the
already attributed pinned SaveForge equipment writer and ER-Save-Lib structures.
Their unchecked hash/window calculations are not copied; fingerprints are checked
against the known bare-ID order in native files before editing. See SOURCES.md.

## Owned talisman loadouts (v0.49)

Four named slots select existing inventory-backed held talismans from 155 mapped
identities. Inventory counts, unlocked slot capacity, ownership and all four
native representations must agree before editing. Storage and unknown items
are not acquired or moved. Locked slots stay read-only; apply a supported
capacity increase before assigning their newly unlocked positions.

Each assignment synchronizes held-row equip index, bare ID, direct accessory
handle and dynamic ID, followed by the checked armor/talisman fingerprint.
Empty slots use their observed native sentinels. Multi-slot edits are atomic,
so swaps and replacement of an exclusive tier can be reviewed together.
Exact accessory groups enforce incompatible tiers, including mapped DLC
variants. Graven-School and Graven-Mass have separate groups and may coexist;
groups are not guessed from adjacent item numbers. Existing conflicts are not
silently repaired, and edits cannot introduce or worsen a group conflict.

Four public native files with 28 characters passed 98 combined assignments,
masked changed-span checks, authenticated reparsing and byte-identical
restoration. Synthetic cases cover missing/ambiguous ownership, locked slots,
reference disagreement, group conflicts, compatible stacking and combined
armor/weapon creation. Original files, inventory and global/menu state remain
unchanged. Derived stats and gameplay effects are not recalculated or verified.

Legitimate additional copies in held inventory or storage do not disable the
loadout: accessory handles identify a type, so the current valid held-row index
is preserved. Choosing another type uses a deterministic held copy. Storage
never supplies equipped ownership, and no copy is moved or deleted.

### Missing base-game talismans

Inventory / Add talismans can acquire one missing identity from 116 mapped
base-game talismans. Any existing held/storage record, including an ambiguous
or depleted entry, excludes acquisition of that identity. DLC acquisition is
not offered. Only a clean empty held record is used. Item registration, held
count and acquisition/equip counters update together; no physical GaItem,
equipment assignment, story flag, quest or achievement reward is synthesized.
Full inventory, unknown registry layouts and counter overflow block writing.

Four native files passed 871 missing-talisman acquisitions across 28 characters.
Existing inventory records, equipment and unrelated payload bytes stayed
unchanged; output length and authenticated reparsing were checked. Originals
were never written. Synthetic cases combine additions with goods/physical
equipment creation and protect already-owned or DLC identities. Engine loading,
new-item persistence and derived gameplay effects still need in-game checks.
