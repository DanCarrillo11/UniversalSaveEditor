# v0.37.0-alpha — Expanded Red Dead Redemption 2 editor

RDR2 PC Story Mode now offers more than carried cash:

- **Character:** current honor and its persistent statistic change together;
  Health/Stamina/Dead Eye cores, saved health, base XP and weight.
- **Inventory:** quantities of existing named supplies and ammunition in the
  active inventory. Reserve inventories remain separate.
- **Weapons:** existing copies' degradation, permanent degradation, soot, rust
  and dirt. No weapon identity or component changes.
- **Horses:** existing horses' bonding XP, dirt and hunger.
- **Compendium:** existing discovery, study and ownership records, grouped by
  category. These flags do not grant items, purchases or challenge rewards.
- **World:** saved hour, minute and second.

The reader checks embedded structure/member hashes, types and extended offsets;
inventory pointer bounds, counts, alignment, record types and GUID uniqueness;
and matching canonical/statistic honor values. Unrecognized structures and
nonstandard original values remain protected. Float32 edits are verified at
their stored precision. GUIDs, links, counts, unrelated bytes and file length
are preserved; native integrity is recalculated and output reparsed.

Three native encrypted PC saves passed all editable-field changes in memory,
exact-span comparisons, all ten payload checks and byte-identical restoration.
Original personal files were unchanged. Synthetic tests cover malformed graphs,
duplicate references, mismatched schemas/honor, bounds, both inventory modes,
encryption, previews and staged interface changes.

**RDR2 remains Limited coverage.** Edited-save game loading is unverified. New
items, weapon/clothing acquisition, stable management, camp funds, bounties,
complete unlocks and story/challenge/reward dependencies are still unsupported.
Field availability depends on the save's schema. See docs/RDR2_FIELDS.md.

Download UniversalSaveEditor.exe under Assets and double-click it, or use
Updates > Restart and update. The portable executable is also included in
Code > Download ZIP. Apply replaces the opened file directly; no automatic save
backup or .edited output is created.
