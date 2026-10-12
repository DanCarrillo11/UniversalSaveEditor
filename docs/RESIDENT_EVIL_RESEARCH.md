# Resident Evil PC support and validation status

This table follows eleven Steam editions requested by the repository author.
Scoped editing is available for ten of them; **full feature support and
in-game validation are not claimed**. RE0 remains research-only.

| Steam edition | AppID | Scope / evidence |
|---|---|---|
| RE HD Remaster | 304240 | First mapped slot: difficulty, save count, defensive supplies, existing inventory and item-box quantities. Public PC-format profile checked; other slots pending. |
| RE0 HD Remaster | 339340 | A public 2,337,008-byte PC profile was decoded and matched its SHA1. Its table maps 20 game records plus system/version sections. Gameplay field mapping is unverified; no editor enabled. |
| RE2 Remake | 883710 | Player HP, existing inventory quantities, rewards and library flags. Documented profile and synthetic Steam fixtures; native Steam validation pending. |
| RE3 Remake | 952060 | Player HP, existing inventory quantities, total earned shop points, shop-item and reward flags. Shared console payload inspected; native Steam validation pending. |
| RE4 Remake | 2050650 | Extra content points, Spinels, existing inventory quantities. Lime authentication and synthetic Steam fixtures; native Steam validation pending. Separate from original RE4. |
| RE4 (2005), Ultimate HD Edition | 254700 | Currency, difficulty, player/Ashley health, statistics, existing case quantities and known weapon tune-up tiers. Four local records checked in memory. New case objects and comprehensive unlocks pending. |
| RE5 Steamworks | 21690 | Money, exchange points, costume/filter/infinite-ammo/library flags. Public Steamworks Gold profile checked for checksum, identical export and in-memory changes. |
| RE6 | 221040 | Skill Points, Mercenaries character/costume/stage flags, existing supplies and equipped campaign/Mercenaries skills. Public Steam profile checked; purchase flags, emblems and unrelated data retained. |
| RE7 Biohazard | 418370 | Player health and existing item-box quantities. Player health identified in two public console payloads; native Steam validation pending. |
| RE Village (RE8) | 1196590 | Lei, CP, current health, existing stacks and extra-content flags. Shared console gameplay payload and synthetic Steam envelopes checked; native Steam validation pending. |
| RE Requiem | 3764200 | Currency and scoped collection/shop flags. Nine native Steam files authenticated, exported identically and revalidated after in-memory edits. |

All enabled Resident Evil editors are marked experimental. No edited save has
been loaded in-game. A checksum match and byte-preserving export establish file
handling, not gameplay correctness. Public downloaded fixtures were used only in
ignored research directories and were never installed over active saves.

## Implementation and provenance

- [Original RE4 UHD](RE4_UHD_FORMAT.md)
- [RE5 Steamworks](RE5_FORMAT.md)
- [RE Engine scope, envelopes and evidence](RE_ENGINE_FORMAT.md)
- [Village scope and evidence](RE8_FORMAT.md)
- [HD Remaster / RE6 / RE0 boundaries](RE_LEGACY_PC.md)
- [Source attribution](../SOURCES.md)

The independent readers do not vendor unlicensed implementations or large SDK
assets. Google CityHash64 is an explicitly credited MIT adaptation with its full
notice. Personal saves, account identifiers, extracted game binaries, downloaded
fixtures and research checkouts are excluded from public source and packages.

## Remaining work

1. Obtain and validate native Steam fixtures for RE2, RE3, RE4 Remake, RE7 and Village.
2. Confirm edits by loading copies in the respective games.
3. Map RE0 gameplay fields independently; avoid treating runtime offsets as serialized-file addresses.
4. Expand HD Remaster beyond its first mapped slot and original RE4 case creation/unlocks.
5. Add verified names and relationships to RE Engine collection entries before claiming comprehensive unlock support.
