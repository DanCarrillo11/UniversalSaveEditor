# Public references for additional game support

Research date: October 10, 2026. This document records implementation references,
not newly advertised compatibility. The public catalogue remains authoritative.
Use public reference fixtures and local research instead of asking the repository
author to play unfinished games or prepare controlled save pairs.

Implementation update: ReCoM, BBS, DDD HD, KH III PC and Max Payne inventory
adapters are now implemented as experimental editors. See
[additional KH formats](KH_EXTRA_FORMATS.md) and [Max Payne scope](MAX_PAYNE_FORMAT.md).
The findings below preserve the earlier research snapshot; pending statements
describe the state before this implementation. BBS and DDD subsequently used
public PC archives; KH III was decrypted, edited and re-encrypted successfully.

## Kingdom Hearts

Primary reference:
[BFlorry/KingdomSaveEditor](https://github.com/BFlorry/KingdomSaveEditor), inspected
at commit `e5eec7403f939d7a94a62d996130d84f59887dda`. This maintained fork includes
Steam-specific examples and newer KH III PC support absent from the archived
[Xeeynamo version](https://github.com/Xeeynamo/KingdomSaveEditor).

| Game | Useful source | Evidence and remaining work |
| --- | --- | --- |
| KH I Final Mix | `KHSave.Lib1`, `PcKh1Factory.cs`; [KatRewrites/kh1-save-editor](https://github.com/KatRewrites/kh1-save-editor) | Public Steam archive opens in our existing adapter with 39 populated slots. A Munny edit reparses with the requested value and valid integrity after explicit CRC repair. Additional useful reference features include abilities, equipped weapons, party equipment and coordinated level growth. |
| Re:Chain of Memories | `KHSave.LibRecom`, `PcKhRecomFactory.cs`, `RecomTests.cs` | Downloaded two public Steam fixtures with 1162 and 1244 Moogle points. Both their primary and mirrored currency values match the stated amounts; both internal checksums validate independently. Experience, difficulty and card inventory have documented fields. Our editor is still pending. |
| KH II Final Mix | `KHSave.Lib2`, `PcKh2Factory.cs`; [OpenKH](https://github.com/OpenKH/OpenKh) | Public Steam archive opens in our existing adapter with 59 populated slots. A Munny edit reparses with the requested value and valid integrity after explicit CRC repair. Further reference models cover abilities, equipment and records. In-game loading remains a separate validation step. |
| Birth by Sleep Final Mix | `KHSave.LibBbs`, `PcKhBbsFactory.cs` | Downloaded a public raw character record: revision 0x1D, 73,296 bytes, declared size and additive checksum both match. Source maps character XP, money, medals, attributes, difficulty, commands, decks, abilities and finishers. A raw record does not establish a tested Steam container. |
| Dream Drop Distance HD | `KHSave.LibDDD`, `PcKhDddFactory.cs`; [osdanova/KH_Editor](https://github.com/osdanova/KH_Editor) | PC container and HD record models exist. Reference fields include money, character XP, droplets, commands, decks and Dream Eaters. The downloaded reference fixture is a 3DS record and must not be treated as PC validation. |
| 0.2 A Fragmentary Passage | `KHSave.Lib02`, especially `SaveKh02.cs` and its slot model | Reference editor advertises PS4 support. Source documents attributes, inventory and other slot data, but a verified PC wrapper and PC sample are still needed. Do not reuse console offsets against an encrypted PC file without proving the decoded layout. |
| KH III + Re Mind | `KHSave.Lib3/SaveKh3PC.cs`, `SaveKh3PcCrypto.cs`, `KHSave.Tests/Kh3PcCryptoTest.cs` | Downloaded an upstream encrypted Steam slot fixture. Source provides account-ID-derived AES-256-ECB encryption, integrity handling, PC field mappings and automated round-trip tests. The file has not been decrypted or edited by our application. Account handling is part of this adapter, not just renaming a file. |
| Melody of Memory | [WaterKH/MoM-ReChart-Analysis](https://github.com/WaterKH/MoM-ReChart-Analysis), [ReChart](https://github.com/WaterKH/ReChart), [OpenKH database notes](https://openkh.dev/mom/database.html) | The Analysis repository contains `SaveData.cs`, `SaveProcessor.cs` and models for party data, items, music unlocks, collection cards, rhythm points, world progress and records. These are useful plaintext-schema references. Its encryption experiment is incomplete and relies on a native DLL; it was not run. A verified PC encrypted sample, standalone read/write pipeline and licence review are still required. |

The PC 1.5+2.5 release contains **four playable games**. 358/2 Days and Re:coded
are HD cutscene compilations, as the
[publisher's Steam listing](https://store.steampowered.com/app/2552430/) states.
Do not offer them as combat/XP/inventory editors. The 2.8 collection also includes
the Back Cover film; cinematic/theatre records are a separate potential feature.

### Re:Chain of Memories findings

Offsets below are relative to the start of an individual decoded record, not to
the PNG file. The PC container has 100 entries with stride `0x3A30`; populated
record lengths need to be read from the archive table. The observed fixtures use
length `0x3630`, so requiring length == stride would reject valid saves.

- Header: magic 7, internal checksum, payload length and reserved zero, 16 bytes.
- Moogle points: record offset `0x2D58`, signed 32-bit integer.
- Mirrored Moogle points: record offset `0x14`, signed 32-bit integer.
- Experience: record offset `0x2D50`, signed 32-bit integer.
- Card quantities: record offset `0x1FC4`, 0x49C byte entries. Card identities,
  acquired flags and deck validity need coordinated handling before mass unlocks.
- Difficulty: reference Table1 starts at payload offset `0x410`; the enum follows
  byte 0x60. Verify the enum's underlying width before implementing a patch.
- Internal checksum: reproduce `SaveKhRecom.CalculateChecksum` exactly. It is
  distinct from the containing PNG chunk's CRC and is not interchangeable with
  KH II's checksum routine.

## Max Payne 1

- [Tatsh/dade R_MemoryFile documentation](https://github.com/Tatsh/dade/blob/master/dade/maxpayne/memoryfile.py)
  documents tagged integers, strings and chunk bounds. Our read-only foundation
  already parses all three locally generated saves.
- The installed game's `x_data.ras` contains factual weapon and shared inventory
  IDs. Those extracted files stay in ignored local research; they are not bundled.
- [Endurance's End Level Saves](https://www.speedrun.com/max_payne_1/resources/0f9h5)
  explicitly describes full ammunition, guns, painkillers, health and bullet time.
  This is a useful externally documented comparison dataset. Its linked ZIP
  download returned HTTP 403 during this research, so no downloaded/validated
  Max Payne sample is claimed here.
- No usable open-source Max Payne 1 `.mps` field editor was located in these
  searches. Max Payne 2, Max Payne 3, mobile and GBA offsets are not substitutes.

Next research should obtain public `.mps` examples with documented state and
compare their structural player/inventory records. Unknown values must remain
uneditable until corroborated. The user does not need to generate those samples.

The Melody of Memory Analysis source was inspected at commit
`9fb027eaadc2ad75914b160ffe9536437d24b6e0`. GitHub reports no declared licence for
that repository; do not incorporate its implementation on the assumption that
public visibility grants redistribution rights. Use it to locate factual schema
information for an independent implementation and review any further reuse.

## Validation and distribution

Local research produced `work/reference-research/validation.json`. Source copies,
downloaded third-party fixtures and experimental edits remain under ignored
`work/`; no fixture has replaced a live game save. No game binary, trainer or
third-party executable was run. Fixture parsing and round trips do not prove
that an edited save loads in the game.

When adapting GPL-3.0-or-later source, preserve the contributors' copyright and
attribution, document the source revision and retain this project's compatible
licence. Do not redistribute third-party fixtures without reviewing their terms.
Finding a reference is not grounds for adding a supported-platform logo.
