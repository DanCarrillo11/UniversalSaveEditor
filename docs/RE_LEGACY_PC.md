# Initial HD Remaster and RE6 PC scope

## Resident Evil HD Remaster

The adapter accepts a 457,376-byte PC container. Blowfish ECB uses little-endian
word order; the key is independently checked against a public PC-format fixture.
Its plaintext header begins with `(1, 0, 36)` and declares the payload length
at offset 32. The SHA1 at `[12,32)` is stored with each word reversed and covers
the bytes from 64 to the end. Explicit integrity repair is required on mismatch.

**Only the first mapped save slot is editable in this release.** The adapter
exposes saved difficulty, save count, daggers, flash grenades and quantities of
existing inventory and item-box entries. It does not change item IDs, character,
costume, health, other slots or story state. An item quantity can also represent
loaded ammunition. Limits do not guarantee that all combinations work in-game.

PC inventory addresses were compared with the [PC save converter's format notes](https://www.save-editor.com/tools/pc_game_save_converter_title_Resident_Evil_HD.html).
Other field-address comparisons used [urbanware-org/re-hd-se](https://github.com/urbanware-org/re-hd-se),
which is a **PS3** editor; it is not itself evidence of PC gameplay compatibility.
The [public PC fixture](https://savegame.info/resident-evil-hd-remaster/)
was checked for header, SHA1, identical export and in-memory edit/reparse.

## Resident Evil 6

The adapter accepts the verified 39,416-byte PC layout with version bytes
`01 18 07 12`. Offset 4 declares its total size; the checksum at offset 8
is the modulo-2^32 sum of little-endian words from `0x18` through the end.
Header/profile identity bytes are retained. Unknown sizes and versions fail closed.

Initial fields are Skill Points, Mercenaries character/costume and stage
unlock bits, No Mercy stage bits and quantities in existing character loadouts.
Weapon IDs and their upper flag bits are preserved. Supply quantities have a
minimum of 1; creating, removing or reassigning items is outside this scope.
v0.18 adds equipped campaign/Mercenaries skill selectors; purchase/unlock state,
mode-specific skills, difficulty, story progress, records and Serpent Emblems
are retained. See [skill bounds and limitations](EDITOR_EXPANSION.md).
In particular, a native emblem byte can be 3; it must not be treated as a plain
0/1 flag based on a different editor's simplified control.

Factual PC offsets were compared with [lightningdotnet's RE6 editor](https://github.com/lightningdotnet/resident-evil-6-save-editor).
The author's [public Steam fixture](https://steamcommunity.com/sharedfiles/filedetails/?id=2942882660)
matched the stored checksum and survived identical export and in-memory changes
to currency/unlocks with profile, emblem and unrelated bytes preserved.
No upstream implementation code or large generated name table is bundled.

## RE0 research boundary

A [public PC-format RE0 fixture](https://savegame.pro/pc-resident-evil-zero-hd-remaster-savegame/)
has been obtained, decoded with Blowfish-LE and matched to its word-swapped SHA1.
It has the 2,337,008-byte size described by [re0box](https://github.com/descawed/re0box).
Its bounded section table identifies 20 `GAMEDATA` records by their complemented
name CRC32s, plus system/version sections. Their ordering differs from slot order.

This establishes container reading, not editable gameplay fields. The source of
[RE0CabbyCodes](https://github.com/SirCabby/RE0CabbyCodes) describes live-memory
save management and field discovery, but does not establish a verified mapping
from this fixture's serialized records to every field. RE0 is therefore **not
offered as an editor yet**. Public fixtures are never installed over active saves.

All newly introduced adapters remain experimental; edited files have not been
loaded in-game. Research downloads, source checkouts and account data are not bundled.
