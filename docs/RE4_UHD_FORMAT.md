# Resident Evil 4 (2005), Steam Ultimate HD Edition

Initial experimental scope: Pesetas, saved difficulty, player/Ashley health,
number of saves and completed rounds, and continue/kill/hit/shot counters.
v0.18 adds existing case quantities and known weapon tune-up tiers; identities,
case geometry, loaded rounds, costumes, unlock flags and room state are preserved.
See [case layout and limits](EDITOR_EXPANSION.md).

## Verified container

- Exact file size: 1,047,200 bytes (`0xFFAA0`).
- Twenty records at `0x1EE8`, stride `0xCAFC`; zero-filled records are skipped.
- Supported populated record version: little-endian `0x402` at `+4`.
- Header CRC at `+0`, over bytes `+4..+0x200`.
- Record CRC at `+0xCAF8`, over bytes `+0..+0xCAF8`.
- Both use MSB-first CRC-32, polynomial `0x04C11DB7`, initial/final XOR zero.
- Header/account data before the records, the eight-byte footer and untouched
  slots are preserved exactly. There is no account-transfer feature.

These dimensions differ from the VR editor's `0x1F30` base and `0xCA48` stride.
They were verified independently against all four populated slots of a local
Steam file, including both checksums. The active file was not altered.

## Fields relative to the selected record

| Field | Offset | Encoding |
|---|---|---|
| Pesetas | `0x4C` | signed 32-bit LE, editor range 0..99,999,999 |
| Difficulty | `0x3D`, `0x3520` | mirrored byte: 1 Very Easy, 3 Easy, 5 Normal, 6 Professional |
| Player current / max HP | `0x58`, `0x5A` | signed 16-bit LE, max 2,400 |
| Ashley current / max HP | `0x5C`, `0x5E` | signed 16-bit LE, max 1,200 |
| Number of saves / completed rounds | `0x40`, `0x42` | unsigned 16-bit LE |
| Chapter / total continues | `0x3504`, `0x3506` | unsigned 16-bit LE |
| Chapter / total kills | `0x3508`, `0x350C` | unsigned 32-bit LE |
| Chapter / total hits | `0x3510`, `0x3514` | unsigned 32-bit LE |
| Chapter / total shots | `0x3518`, `0x351C` | unsigned 32-bit LE |

Current HP must not exceed maximum HP. Change both values together when needed.
Difficulty edits update both stored mode values but do not recreate a new game
or recalculate previously spawned enemies, rewards or progression flags.
The player field may refer to Leon or another saved player character.

Unknown dimensions, record versions or inconsistent difficulty mirrors are
rejected. CRC mismatches require the existing explicit repair choice. Changing
a field refreshes the two CRCs of that slot only; explicit repair refreshes all
populated slots. Requested values are reparsed before applying the file.

Synthetic tests check corruption, unknown records, sparse physical slots,
health relationships, no-op identity and exact preservation outside edited
fields and CRCs. In-memory edits of the local file also round-trip correctly.
Loading edited output inside the game remains pending; this adapter must retain
its experimental label until that is verified.

See [Resident Evil research and sources](RESIDENT_EVIL_RESEARCH.md).
