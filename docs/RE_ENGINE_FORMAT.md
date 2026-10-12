# Experimental Resident Evil RE Engine adapters

The app edits a small whitelist of fields in self-describing serialized streams.
It retains unknown properties and objects in their original byte positions;
it does not recreate the stream from a third-party SDK schema.

| Steam edition | Initial editable fields | Validation evidence |
|---|---|---|
| RE2 (2019) | Player HP, existing inventory quantities, reward and library flags | Documented Steam envelope and property identifiers; synthetic fixtures only. Real Steam fixture validation pending. |
| RE3 (2020) | Player HP, existing inventory quantities, total shop points earned, shop-item possession and reward flags | Synthetic Steam envelopes and public console examples of the shared serialized payload. Real Steam fixture validation pending. |
| RE4 (2023) | Extra content points, Spinels, existing inventory quantities | Documented Lime envelope and property identifiers; synthetic fixtures only. Real Steam fixture validation pending. |
| RE7 | Player health and existing item-box quantities | Synthetic Steam envelopes; player-health field found in two public console payloads. Real Steam fixture validation pending. |
| Village (RE8) | Lei, CP, current health, existing stacks and extra-content flags | Shared console gameplay payload and independent synthetic Steam envelopes checked. Native Steam file and game loading pending; see [Village scope](RE8_FORMAT.md). |
| Requiem | Money, carry-over money, Clear Points, extra-shop availability/acquisition/received flags, bonus content, artwork and figure availability/purchase flags, special-option unlocks | Nine native Steam files decoded and exported identically. In-memory edits revalidated with unrelated payload bytes preserved. |

All six adapters are experimental. **No edited file has been tested by loading
it in these games.** File verification does not establish gameplay compatibility.
Only fields actually present in the opened file appear. Open a gameplay slot for
health or inventory and a system profile for its unlocks and profile currency.
Files without recognized fields are rejected with an explanation.

## Scope

Collections are numbered by their saved order; labels are not a complete named
item catalogue. Existing quantities stay within 1–999 and do not change item
identity, equipment references, slot count or array lengths. Inventory counters
must be descendants of the game's inventory save object: scene objects and
enemy inventories are excluded. Player HP uses a player-specific class, never
generic enemy health properties. Difficulty, story/checkpoint state, weapons,
upgrades and item creation are not exposed by these initial adapters.

Village single-item records are read-only; only original multi-item stacks can
change quantity. Village item/content identities are checked within their exact
saved owner; labels use unsigned hexadecimal IDs, with names and game caps unmapped.

RE3's `TotalShopPoint` is the total earned counter, not a guaranteed unspent
balance; purchased items have separate possession flags. Requiem's purchase
availability, actual purchase, acquisition and received flags are distinct.
Editing flags does not purchase DLC or guarantee that its content is installed.
Uninitialized carry-over balances of -1 are retained and not offered for editing.

## Containers

All accepted files start with `DSSS`, version 2, and end in MurmurHash3 x86-32
with seed `0xffffffff`. A mismatched outer integrity hash requires explicit
repair in the app. Truncation, unknown types and invalid encrypted blocks fail
closed. Decrypted payloads and parser complexity are bounded.

- RE2, RE3, RE7 and Village: flags 3, Blowfish option 3, game-specific Blowfish-LE CBC
  keys, zero IV, payload beginning at 32. Header marker and account ciphertext
  are preserved. Incomplete final cipher blocks remain unchanged.
- RE4 Remake: flags 16, payload beginning at 16. Each Lime block has 512 bytes
  of key metadata, 4096 bytes of AES-128-OFB data, then 32 bytes of SHA3-256
  over the entire plaintext block, including padding. The original account's
  low 32 bits select its key. Metadata, padding and RSA trailer are retained.
- Requiem: flags 16, Mandarin seed `0x61f6868699c14dfa`, variable block
  capacities, account-dependent SplitMix64 key/IV and metadata masks,
  AES-128-OFB and CityHash64 over each block's used plaintext bytes. Key
  authentication, final padding, metadata and RSA trailer are retained.

Lime and Mandarin keep the original decrypted length and require edits of the
same serialized size. The original SteamID64 is detected from the normal
`userdata/<Steam account number>` path. Copied files require the original
creator's SteamID64. Accounts are not reassigned. Compressed flags, plaintext
console envelopes and other platforms are not accepted by these Steam adapters.

## References and independent verification

- [REE Save Editor](https://github.com/kvasszn/ree-save-editor): format facts,
  encryption profiles and factual SDK property identifiers. No implementation,
  schema assets or translation databases from this unlicensed checkout are bundled.
- [bucanero/save-decrypters](https://github.com/bucanero/save-decrypters/tree/master/re7-checksum-fixer/samples):
  publicly supplied **console** examples used only to check the shared payload.
  They are not represented as Steam fixtures and are not bundled.
- [Google CityHash](https://github.com/google/cityhash): MIT-licensed CityHash64
  adaptation and upstream golden vectors; full notice is in `THIRD_PARTY_NOTICES.txt`.
- AES-OFB is checked against the first block of NIST SP 800-38A F.4.1.

Tests cover key mismatch, block authentication, damaged hashes, truncation,
unsupported flags/types, size preservation, unknown data, reserved metadata,
float round trips, inventory ancestry and field limits. Personal saves, account
identifiers and downloaded fixtures remain outside the repository.
