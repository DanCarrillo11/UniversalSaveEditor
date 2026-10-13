# Requiem player, inventory and attached upgrades

This adapter targets Steam DSSS/Mandarin files. The envelope, original account,
length, metadata, padding and trailer are preserved. Gameplay slots and system
profiles contain different options. Nine native Steam files were checked for
identical exports and authenticated in-memory edits; loading an edited file in
the game remains unverified.

## Player records

The shared `CharacterHitPointData` class (`e603ebf1`) occurs on enemies as well.
Health is exposed only beneath `CharacterManager.SlotSaveObject._CharacterSaves`
(`b3b29efb`) in the same `CharacterBackupData` (`9d98c4ce`) that contains a
player-specific `PlayerCommonData` (`64582fd4`) structure. Setup must be true,
each required property unique, and current/max health consistent.

Current health is bounded by that record's saved maximum. Maximum health is
read-only. A health-level selector appears only when its level agrees with its
own complete, ordered, strictly increasing `_MaximumHPTable`. Selecting a
level updates `_CurrentHPLevel` and `_CurrentMaxHP`; current health is clamped
on reductions. Death, injury, spawn and story flags stay unchanged. Character
names and the active saved variant are not mapped; numbered player records
must not be interpreted as a guaranteed character selection.

## Existing quantities

Require `InventoryManager.SaveData._InventoryData` (`3a83076c`) and exact saved
inventory (`6dc40103`) ancestry. Backups, scene items, archive/key-item records
and notification lists are excluded. Inventory and item-box sections retain
their saved User00–User03/None identities and Hand/ItemBox/ShareItemBox boards.

Panel stock (`b00026aa`) and nested storage stock (`6b8482e9`) need unique,
non-sentinel item hashes, positive quantities and valid parent items. Loaded
rounds and chamber counts are excluded. Known ammunition can change even from
a count of one; other single-item entries remain read-only until stackability
is verified. The melee-durability pseudo-item is excluded. Quantities are
bounded to 1–999, but actual game stack caps are not mapped. No item creation,
identity replacement, inventory expansion or case-geometry edits are offered.

95 selected names identify supplies, weapons and parts. Item hashes are
independently computed with MurmurHash3 over UTF-16LE codes, seed `ffffffff`,
and checked against native identities. Unknown IDs keep hexadecimal labels.
These short factual labels do not imply original icon coverage; Requiem item
artwork remains pending.

## Attached part tiers

`Inventory.PanelAttachmentSaveData` (`1dbdde3d`) must occur in the same current
inventory's `_PanelAttachments`. Its `_ItemIndex` must identify the exact owned
part, and `_AttachTargetItemIndex` a mapped owned weapon in `_PanelItems`.
Empty, ambiguous, missing, mismatched or backup references are excluded.

44 known parts have three original labelled tiers: base, improved (+), maximum
(star). Only `_Level` changes; part/weapon identity, socket and references stay
unchanged. Capacity parts may only increase, preserving loaded ammunition.
Already maximal capacity parts are read-only. Charms, unknown tiers and adding
or attaching new parts are not supported.

## Research references

- Serialized class/property facts: [REE Save Editor](https://github.com/kvasszn/ree-save-editor/tree/4125e497f1ae84cc746bb4a99da612c48bea161e/assets/re9).
- Selected original English item names: [Synthlight/RE-Editor](https://github.com/Synthlight/RE-Editor/blob/48310c16a915545dc96d254ab59ec69665c31447/RE-Editor/Data/RE9/Assets/ITEM_NAME_LOOKUP_BY_VALUE.json).

No upstream implementation, SDK schema or multilingual translation database is
bundled. Synthetic tests cover enemy/backup/scene exclusion, ambiguous identities,
health-table consistency, coupled health updates, loaded ammunition preservation,
part ownership/reference matching, bounds and exact unrelated-byte preservation.
No personal saves or account identifiers are published.
