# RDR2 PC Story Mode — v0.37 field expansion

This editor is still Limited coverage. It does not claim to expose everything
RDR2 can store. New controls appear only when their structures are recognized;
a save with a different schema can expose fewer fields.

| Section | Editable scope | Preserved / important distinction |
| --- | --- | --- |
| Currency | Carried dollars/cents | Camp funds and income records are separate. |
| Honor | Current value and persistent HONOR_CURRENT statistic, together | Both must be unique and agree before editing. Early story limits may clamp to ±240; full range is ±320. Story/reward milestones are not synthesized. |
| Player cores | Health, Stamina and Dead Eye cores, plus saved health | Core values 0–100. Saved health is separate and may be clamped by the game. Overpower timers are preserved. |
| Player progression | Base Health/Stamina/Dead Eye XP, weight | XP 0–1100; weight −100–100. Challenge-equipment bonuses and story Dead Eye abilities remain separate. |
| Inventory | Existing named consumable/provision/ammunition quantities in the active inventory | No item creation, deletion, ID swaps or capacity upgrades. Existing trinket/talisman ownership is protected. Game capacity rules may clamp edited counts. |
| Weapon condition | Existing weapons' degradation, permanent degradation, soot, rust and dirt | 0 clean/undamaged, 1 maximum deterioration. Does not add guns, components or purchase unlocks. Individual copies are distinct. |
| Horses | Existing active-inventory horses' bonding XP, dirt and hunger | Does not create horses, change breed/coat, move stable slots, change names or grant bonding rewards. |
| Compendium | Existing animal discovery/study, weapon/equipment ownership records, plant/fish/horse study flags | These are records only: they do not grant the item, unlock its shop purchase, complete a challenge or trigger rewards. |
| World clock | Hour, minute, second | Calendar date, mission timers and schedules are preserved. |

## Format identification and bounded writes

Parser names use case-sensitive Jenkins hashes; game item/stat names use their
lowercase game hashes. PMAP byte offsets include the PSIN header. The embedded
PSCH must match each referenced structure, named member, type and subtype. Bit
0x40 in a member's subtype extends the 16-bit data offset by 65536. Unknown
subtypes and mismatched types are not used as writable fields.

The recognized build-1491 script root 0x41D6F894 contains the attribute member
0xB5D75947 at 88760, referencing structure 0x41D6F933 (568 bytes). Current honor
is its signed member 0xA53CDE40 at +280. The separate typed integer StatId
HONOR_CURRENT entry must have namespace zero and exactly one matching value.
Both words are patched together. Core and XP arrays require the exact child
schemas, native count bytes and floating-point elements, preserving eight-byte
script-cell padding. No first-match integer or string search is used for them.

Active inventory follows CPedInventorySaveStructure.playerInventory or
backupInventory according to usingBackupInventory, rather than editing every
mapped item in the file. Extended PC pointer block IDs, reserved bits, byte
offsets, counts/capacity, typed targets, row alignment, unique target offsets and
unique GUIDs are checked before any inventory controls are exposed. A malformed
or duplicate pointer graph disables these controls. GUIDs, parent links, types,
slot IDs, equipment flags, array counts, unrelated inventories and file length
are preserved. Integer quantities are signed 64-bit values; condition/core/XP
values are IEEE float32. Output comparison uses the stored float32 value.

## Native-file verification

Three local encrypted PC saves (755712, 686160 and 702880 bytes) expose 1268,
736 and 750 fields respectively; counts include compendium records and separate
weapon copies, and are **not a completion percentage**. Their active inventories
contain 834, 233 and 302 records. Two saves have nonstandard original values
which remain read-only.

All editable fields were changed in memory, reparsed and restored. Each file
retained all ten valid payload checks; decrypted differences stayed inside
declared field spans and checksum words. Restoration was byte-identical to each
original encrypted file. Personal originals were read only and not modified.
Parsing took approximately 0.18–0.40 seconds in the development environment;
this is not a startup-time guarantee for other computers.

Synthetic tests exercise both active-inventory modes, pointer bounds, duplicate
GUIDs/targets, wrong member types, honor disagreement, precise changed spans,
float32 precision, encryption state, undo-by-restoration, bounds, preview
navigation and staged UI edits. No personal sample is packaged.

**Successful game loading and persistence have not been verified.** Full support
still needs item/weapon/clothing acquisition and dependencies, stable management,
camp funds, regional bounties, challenge/story/reward dependencies, unlock-bit
semantics, broader revisions and in-game checks. Unidentified bytes are retained;
the interface does not expose guessed unlock switches.
