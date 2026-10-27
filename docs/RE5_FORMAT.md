# Resident Evil 5 Steamworks profile

Initial experimental support targets the 23,888-byte `savedata.bin` profile.
The Steam account, timestamp, story progress and unrelated regions are retained.
GFWL, console and differently sized variants are rejected.

The independent adapter exposes money, exchange points, Chris and Sheva costume
flags, screen filters, 19 infinite-ammunition flags, 12 library-file flags and
45 named figure flags.
An infinite-ammunition flag does not create or upgrade its weapon. DLC ownership
is still required for DLC content. Navigation is Progress / Unlocks / Collection.

## Encoding and integrity

Each encrypted eight-byte block is XORed with the previous encrypted block;
the first uses `00 21 11 08 c0 4b 00 00`. The checksum at plaintext offset 8
is the modulo-2^32 sum of little-endian words in `[0x10,0x3bac)` and
`[0x3bb0,0x52b0)`. The excluded gap and profile tail are preserved.

Money and exchange points are at `0x194` and `0x198`. Costume flags occupy
`0x124` / `0x128`, filters `0x12c`, infinite ammunition `0x130` and library
files `0x134`. Only the selected bit is replaced; reserved bits remain intact.

## Evidence and limits

Format facts were compared with [shinneider/RE5-Save-Editor](https://github.com/shinneider/RE5-Save-Editor).
An author's [public Steamworks Gold profile](https://steamcommunity.com/app/21690/discussions/0/618463106371419005)
was independently decoded, matched its stored checksum, exported identically,
and reparsed after in-memory currency and flag edits. The fixture is not bundled.

Synthetic tests cover checksum boundaries, reserved bits, identity, rejected
variants, limits and explicit integrity repair. Edited saves have not been loaded
in-game. Inventory ownership, upgrades and chapter editing are pending.
