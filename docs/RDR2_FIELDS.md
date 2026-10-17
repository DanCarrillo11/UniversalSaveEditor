# RDR2 PC Story Mode — v0.38 field expansion

This editor is still Limited coverage. It does not claim to expose everything
RDR2 can store. New controls appear only when their structures are recognized;
a save with a different schema can expose fewer fields.

| Section | Editable scope | Preserved / important distinction |
| --- | --- | --- |
| Currency | Carried dollars/cents | Historical income records are separate. |
| Camp | Camp ledger dollars/cents and matching GANG_SAVINGS_CASH statistic together | Both values must be unique and agree. Purchases, upgrades, donations and chapter availability are separate. |
| Honor | Current value and persistent HONOR_CURRENT statistic, together | Both must be unique and agree before editing. Early story limits may clamp to ±240; full range is ±320. Story/reward milestones are not synthesized. |
| Player cores | Health, Stamina and Dead Eye cores, plus saved health | Core values 0–100. Saved health is separate and may be clamped by the game. Overpower timers are preserved. |
| Player progression | Base Health/Stamina/Dead Eye XP, weight | XP 0–1100; weight −100–100. Challenge-equipment bonuses and story Dead Eye abilities remain separate. |
| Inventory | Existing named consumable/provision/ammunition quantities in the active inventory | No item creation, deletion, ID swaps or capacity upgrades. Existing trinket/talisman ownership is protected. Game capacity rules may clamp edited counts. |
| Weapon condition | Existing weapons' degradation, permanent degradation, soot, rust and dirt | 0 clean/undamaged, 1 maximum deterioration. Does not add guns, components or purchase unlocks. Individual copies are distinct. |
| Horses | Existing active-inventory horses' bonding XP, dirt, hunger and saved health/stamina cores | XP is synchronized with the saved horse script slot. Missing/ambiguous slots, missing models and disagreement protect XP. Core values 0–100; temporary effects/timers are preserved. Does not create horses, change breed/coat, move slots, rename horses or grant bonding rewards. |
| Compendium | Existing animal discovery/study, weapon/equipment ownership, plant/fish/horse study flags; horse breaking/highest recorded bonding, gang history and fish catches per existing bait/lure record | Records only: no item grants, purchase unlocks, challenge completion or rewards. A recorded highest bonding level is separate from a living horse's actual rank. Names for many native species/breed IDs remain unidentified and are shown with their hashes. |
| Statistics | 17 existing integer history counters: kills, headshots, deaths, escaped fish, horses broken, stolen horse/wagon sales, stable visits, baths, bar drinks/meals, theatre visits, shows, medicine/Dead Eye/provision use and people antagonized | Unique namespace-zero typed records only. These do not perform actions or unlock platform achievements. Mission progress, hashes, historical money, reward dependencies and honor statistics are excluded from this generic section. |
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

## Campaign mirrors and recorded history

The embedded ROOT schema must uniquely resolve an inline scalar of the correct
type at a known build-1491 script cell. Script cells occupy eight bytes; only
their declared four-byte scalar is written. No raw-offset fallback is used.
Camp funds are Global_40.f_4283.f_325 and the unique namespace-zero
GANG_SAVINGS_CASH integer statistic. Both store cents and are written together.

Owned horse slots are identified by the inventory SlotId mapping in
player_horse.c func_720, not by a matching name or coincidentally equal XP.
Global_40.f_1095.f_1 has seven serialized 436-cell entries; only the five mapped
inventory slots are recognized. A nonzero saved model and the expected array
count are required. Bonding XP (entry.f_372.f_1, float32) must agree with the
integer inventory BondingXp before editing. Both copies change together; rank
and reward/event state are not synthesized. The game derives progression from
its own model rules. Health/stamina cores are entry.f_398[0/1], a two-element
array with four-cell elements; timers and overpower data are preserved.

Statistics retain their original typed StatId and namespace. Duplicate records
are protected. Fishing-history pointers must target the correctly typed lure
array within mapping bounds and row alignment, with bounded counts/capacity,
unique fish/lure identities and no shared writable count locations. These
arrays are not resized. Compendium counts do not acquire bait, fish or horses.

## Native-file verification

In v0.38, three local encrypted PC saves (755712, 686160 and 702880 bytes) expose 1632,
1100 and 1116 fields respectively; counts include compendium records and separate
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
GUIDs/targets, wrong member types, honor/camp/horse disagreement, unknown horse
slots, invalid core counts, duplicate/foreign-namespace statistics, overlapping
fishing-history pointers, precise changed spans, float32 precision, encryption
state, undo-by-restoration, bounds, preview navigation and staged UI edits.
No personal sample is packaged.

**Successful game loading and persistence have not been verified.** Full support
still needs weapon/clothing acquisition and dependencies, stable management,
camp upgrades, challenge/story/reward dependencies, broader revisions and in-game
checks. Unidentified bytes are retained. The additions below are limited to
recognized structures and do not establish full compatibility.

Specific unresolved dependencies: weapon acquisition needs owned-weapon records,
components and appropriate relationships; horse creation needs stable/script
state. Knowing an item's name hash does not establish those rules. The current
bounty region has not been identified reliably in an offline save, so edits
which require choosing between inconsistent candidate regions are refused.
Successful parse and checksum repair do not prove gameplay.

## v0.39 monetary bounties

Six build-1491 region records begin at Global_40.f_358: amounts are cells
359 + region*12, flags are five cells later. Amounts store cents. Both the
inline scalar schema and the six-element array header are required. A unique
CBountySaveStructure.CurrentBounty supplies the native current amount.
Mission-temporary Global_40.f_11957 must be zero. Individual edits synchronize
the native amount only when all matching current-region candidates have the
same final amount. Otherwise the edit is refused. The clear action zeros all
six amounts and the native amount and clears only monetary flag bit 2 (mask 4).
Story/dead-or-alive bit 1, pursuit state, timers and all other flags are retained.
The game can apply its own chapter-specific 300/500/1500-dollar cap.

## v0.39 existing catalog unlocks

Only the CODE frame's unique CUnlockSaveStructureSP.UnlockItemList is followed,
with observed data/XML versions zero, bounded counts/capacity, extended-pointer
validation and aligned eight-byte SUnlockInfo rows. Hash must be the declared
ATNSHASHSTRING member at zero; PackedData is the UCHAR at four. Duplicate hashes,
unknown names and story-document entries do not receive controls.

Apply sets only PackedData bits 0, 1 and 2 (mask 7), matching the reference
editor's existing-weapon catalog action. Bits 1/2 are its custom-unlock pair;
visibility is bit 0. This action does not clear any other bit, acquire inventory,
buy/equip a component or create a horse. Applied actions are read-only, not a
reversible toggle or a claim about the game's current derived availability.
Seven collections separate weapons, ammunition, clothing, satchels, weapon
components, horse equipment and horse breeds. Text names are primary script/hash
facts; no reference editor code, resources or images are distributed.

## v0.39 experimental ordinary-supply acquisition

An explicit 26-item allowlist offers one unit of a missing ordinary satchel
supply. Existing items remain under quantity controls. This requires a checked
RSAV version-3 directory, a valid active inventory, a typed cash record and its
unique active CharacterItem parent. Online profiles, weapons, clothing, quest
objects and arbitrary hashes cannot use this path.

New 48-byte SavegameInventoryItem records retain the same typed-record header
and character parent, set SLOTID_SATCHEL, Equipped=false and Quantity=1. Their
opaque GUID retains the cash record's namespace and uses a random unique low
word. Collisions are checked against all mapped item GUIDs and parent GUIDs,
including inactive/backup records; allocation has a bounded retry limit. This
is an independently implemented allocation strategy, **not a verified replica
of the game's runtime allocator**. Its successful in-game persistence is pending.

The writer appends new records and a new active pointer array, preserves all
old records and backup references, and updates only the active descriptor.
Mapped CODE blocks relocate with stable block IDs and checked types/strides.
PSIN length, PMAP entries, CODE length, later RSAV offsets and the CODE checksum
are rebuilt; PSCH, PSIG, old opaque bytes, encryption state and every script chunk
are preserved. Growth is bounded to 64 MiB. No-op output remains identical.

Current native checks expose 4369/3834/3853 fields including catalog actions,
not a completion percentage. Applying all available catalog actions retained
all ten checks and could be restored exactly at the byte level. Adding missing
allowlisted supplies created 19/13/13 records while preserving the 834/233/302
original records, all existing field values and all nine script chunks. Original
personal files were read only. These are structural checks, **not game validation**.
