# Resident Evil Village (RE8), Steam — experimental

The editor discovers `Steam/userdata/<account>/1196590/remote/win64_save/data*.bin`
and also accepts manual selection. System profiles and gameplay slots expose
different fields; only recognized properties actually present in a file appear.
Changes apply directly to the opened file, retaining its name and account.

## Editable scope

| Category | Fields | Editor bounds / limits |
|---|---|---|
| Progress | Lei; Challenge points (CP) | Lei 0–99,999,999; CP 0–9,999,999 |
| Character | Current player health | Finite float, 0–10,000; maximum health and secondary player health retained |
| Collection / Inventory | Quantities of existing multi-item stacks | 1–999; original quantity must exceed one; single-item records remain read-only |
| Collection / Extra content | Owned, opened and unlocked flags | Separate booleans for existing identified content records; DLC dependency flags retained |

Bounds are editor input limits, not verified in-game carrying caps. Item and
content entries display their unsigned 32-bit hexadecimal identities rather than
guessed names. Quantities of zero and negative sentinels are retained. Single-item
records are read-only because stackability is not yet mapped; no new objects are
created. Loaded ammunition, weapon upgrades, difficulty, story, checkpoint state,
challenge completion and DLC entitlement are not edited.

## Context and property checks

Inventory quantity edits target `StackSize` of `app.ItemCore.InstanceWork`
(`0x10b5eaa5`) only beneath `app.InventoryManager.SaveData` (`0x3a83076c`),
through a `SaveData.Unit` (`0x0431bf51`) `work` property. ItemID must be a unique
positive unsigned 32-bit property of that same object. Scene/shop copies and
ambiguous identities are excluded. The inventory owner's `money` is signed 32-bit.

Health targets only `SaveHealth` in `app.PlayerInfo_SaveSection` (`0x00346547`)
with the expected float type. CP targets the signed 32-bit `CP` property of
`app.CPManager.SystemSaveData` (`0xe94db9b8`). Content flags target its `Units`
array's `SystemSaveData.Unit` (`0xf033f1ce`) objects, with unique positive unsigned
`Hash` identities and boolean `Has`, `IsOpened` and `IsUnlocked` properties.
Unrelated objects bearing the same property names are excluded.

## Steam envelope and preservation

Accepted envelopes use DSSS version 2, flags 3 and Blowfish option 3. The
32-byte header preserves the encrypted account identifier and marker. Payload
uses Blowfish-LE CBC, zero IV, with the factual game key
`j1lL1AOR31sd4HKJS90fs`. Final unaligned bytes are retained. The trailing
MurmurHash3 x86-32 uses seed `0xffffffff` and is recalculated after edits.
An invalid hash requires explicit repair; unsupported flags and malformed
serialized streams are refused. Account reassignment is not supported.

Patches retain stream size, arrays, identities and unknown bytes. Only approved
scalar bytes change before re-encryption, followed by a full parse and value
check. There are no automatic backups or renamed `.edited` files.

## Evidence and remaining validation

A public console gameplay payload of 693,276 bytes was inspected in memory:
28,387 nodes parsed; one currency value, one health value and four stack
quantities were changed and reparsed, with exact unrelated-byte preservation
and a matching integrity hash. This checks the **shared serialized payload**,
not a native Steam envelope; no console file was installed or redistributed.

Independent synthetic Steam fixtures check the key, account preservation,
game/profile layouts, wrong-game detection, unsigned identities, context guards,
single-item restrictions, damage handling, direct saving and UI categories.
**A native Steam Village file and in-game loading have not been validated.**
Extra-content flags do not establish challenge completion or a DLC purchase.

Sources: [REE Save Editor](https://github.com/kvasszn/ree-save-editor) at
`4125e497f1ae84cc746bb4a99da612c48bea161e` for factual encryption and SDK
property identifiers; [save-decrypters](https://github.com/bucanero/save-decrypters)
for the public shared console example. No upstream implementation, generated
SDK schema, translation database or downloaded save is bundled.
