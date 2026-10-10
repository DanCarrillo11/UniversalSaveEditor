# Kingdom Hearts Final Mix difficulty — Steam PC

The editor targets the existing HD 1.5 + 2.5 ReMIX Steam PNG/sqEX containers.
Offsets below are relative to an individual game save record, not the PNG file.

| Game | Offset / type | Saved modes |
|---|---|---|
| KH Final Mix | `0x1642c`, unsigned byte | 0 Beginner, 1 Final Mix (Standard), 2 Proud |
| KH II Final Mix | `0x2498`, unsigned byte | 0 Beginner, 1 Standard, 2 Proud, 3 Critical |

The factual mapping is cross-referenced against KingdomSaveEditor's
`KHSave.Lib1/SaveKh1.FinalMix.cs`, `KHSave.Lib2/SaveKh2.FinalMix.cs`, and the
`Types/DifficultyType.cs` enums in each library (GPL-3.0). See `SOURCES.md`.

Only the selected slot's difficulty byte is changed. Other character attributes,
inventory, progress and save descriptors remain untouched. Export updates the
outer sqEX CRC and, for KH II, the changed slot's internal checksum. Existing
integrity failures require the normal explicit repair option. Unsupported mode
values are rejected instead of silently mapped to a known mode.

This is a saved-mode edit, not a conversion of a new-game setup: starting bonuses,
initial stats and awarded abilities are not recalculated. In particular, changing
to Critical does not add its starting bonuses or rebuild existing character stats.
The editor does not directly award Steam achievements.

Automated checks cover every supported mode, exact preservation of other data,
multiple slots, checksums, input rejection and UI selection. A local KH I profile
was read and exported in memory; the original was not replaced. The local KH II
container has no saved slots, so its mode edits were tested with synthetic records.
Actual in-game loading
and behavior after a mode change still require validation. Keep the original
backup and use the exported copy for testing.
