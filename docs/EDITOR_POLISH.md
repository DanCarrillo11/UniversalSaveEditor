# v0.25.1 editor polish

## Kingdom Hearts Final Mix

Changing Sora's level or saved difficulty also updates the matching KHSQ menu
snapshot when the archive directory identifies the exact data/summary pair.
The summary must have the matching slot name, 1,024-byte declared size and KHSQ
header, and lie inside the PNG save payload. Similar bytes with a different
directory identity are preserved. Currency, XP, location and other summary data
are not inferred or rewritten. This synchronizes displayed metadata; it does
not simulate leveling, recalculate equipment/AP or recreate new-game bonuses.

In-memory verification covered one local and 39 public gameplay records. Levels
and difficulties were compared between data and summaries; edited outputs were
reparsed with their updated PNG CRC. Originals were not overwritten. In-game
loading remains a separate pending check.

## Resident Evil 6

Known existing ammunition and herb entries have names and quantities of 0–999.
An existing depleted reserve can be refilled without changing its item identity
or upper flag bits. This does not create new records or grant weapons. The upper
bound is an editor bound; actual game stack caps are not established.

Weapon and unknown entries are read-only because their count word can contain
state rather than a supply quantity. Negative and large words are left
unexposed. This replaces the previous generic quantity editing for any small
positive item word. A public native profile exposed ten mapped editable reserve
entries and 63 protected entries; in-memory edits preserved profile identity,
weapon words and unrelated bytes, with a valid checksum and successful reparse.
No edited RE6 save has been confirmed by loading it in-game.

## Common editing controls

Field search includes the currently selected equipment name, including pending
changes. Search/page changes preserve other staged edits. Extreme integers are
rejected with regular range validation instead of causing an overflow. Known
conflicts receive fixed corrective guidance for ownership, removals, hotbar
references, ability stacks, equipment, item boxes and health. Diagnostics still
exclude exception text, file paths, player names and account identifiers.

New games and icon work remain deferred. The 21-game coverage table and completion
plan track remaining work; no editor is classified as complete.
