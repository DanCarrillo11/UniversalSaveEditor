# v0.35 compatibility work

This continuation expands four existing games. No game is classified as full
support. Successful reparse, encryption and checksum checks do not establish
successful game loading or complete progression/reward behavior.

## Elden Ring

Character > Equipment loadout now includes Arrows 1/2 and Bolts 1/2. Choose a
uniquely owned supported physical ammunition stack already in held inventory,
or Empty. Arrow/greatarrow and bolt/greatbolt categories remain separate.
All four native representations and the weapon fingerprint synchronize.
Quantities and physical records remain unchanged; one stack cannot occupy two
slots. Unknown direct-goods/legacy representations remain protected.

Character > Tools and Physick provides ten quick items, six pouch assignments
and two Crystal Tears. The tool catalogue recognizes 1,240 factual tool/flask/
Spirit Ash identities, including saved variants; this is a lookup catalogue,
not item acquisition. Only uniquely owned held tools are offered. Native
handle/index pairs, dynamic IDs and their checked 16-entry fingerprint update
together. Flask variants are treated as a family when preventing duplicates
within the quick bar or within the pouch. A tool may appear in both groups.
Active selection, unknown assignments, quantities and events are preserved.

Physick requires the held flask and uniquely owned supported tears from held
or key-item inventory. Forty known tear identities are mapped. Independent
Crimson Crystal Tear variants remain distinct. Each position can be empty;
the third serialized word is preserved and the two positions are not compacted.
No flask, tear, Spirit Ash, upgrade or reward is granted by these selectors.

Four public native files contain 28 overlapping populated records. In-memory
clear/restore checks passed for 28 ammunition, 27 quick-item and 25 Physick
assignments; restorations were byte-identical to their baseline after any
explicit initial integrity repair. One native quick-item fingerprint mismatch
remained protected. Other unavailable tool operations remained protected.
Synthetic checks cover exact byte scopes, duplicates, cross-category rejection,
ownership, inconsistent references, upgrades and structural equipment growth.

Remaining gates include talisman assignment/families, affinities/Ash attachment,
full DLC acquisition, gestures, world/quest/reward dependencies and game loading.

## Kingdom Hearts III

The five Link CommandType IDs are 70–74. The old 65–69 mapping confused Link
commands with consumables/unused entries. Unknown acquisition entries using old
or unsupported IDs are preserved; the editor does not rewrite them as Links.

The twelve shortcut positions also offer eleven consumables. CommandType and
ConsumableType are separate enums: for example, Hi-Ether command 62 refers to
consumable 11, while Mega-Ether command 63 refers to consumable 5. An item
requires positive acquired stock and an enabled matching Sora equipment entry.
Acquisition/equipment edits can be combined with shortcut selection. Explicit
stock depletion or Sora consumable changes clear recognized item shortcuts
that become unavailable; explicit conflicting shortcut requests are rejected.
Untouched unsupported sea/form/unknown commands remain preserved.

Encrypted native-reference testing passed for a Potion shortcut combined with
Sora equipment; the original file remained unchanged. Link acquisition and
consumable dependency rules also have synthetic tests and pinned enum evidence.
Game loading, full AP/character rules and remaining progression are unverified.

## Dream Drop Distance

Existing populated recognized spirits expose stored rank code 0–6 and
disposition index 0–3, independently editing two nibbles in one byte. Unknown
codes are protected and the other nibble is retained. Species-specific names
are not guessed. The stored affinity counter is independently editable within
its serialized nonnegative int32 range; that range is not an in-game cap or
displayed affinity level. Growth, board rewards, affinity levels and petting
state are not recalculated. Creating spirits or rebuilding boards is unavailable.
Native-file checks passed for 39 edits across 13 populated spirits, with the
original unchanged. Gameplay effects still require confirmation.

## Re:Chain of Memories

Recognized native saved levels 1–99 are editable under Level and experience.
The field is the gameplay level, independently corroborated by the player block
and existing XP/money positions. XP, HP, CP, sleights, deck costs and rewards are
not recalculated. Native-file edits passed in two public Steam archives and
preserved originals. Missing/unknown level encodings are not overwritten.

## Evidence and scope

See SOURCES.md for pinned primary references. Research files, reference saves,
account identities and game assets are not shipped. No automatic save backup
or renamed output is introduced: Apply still updates the opened file directly.
The all-game remaining gates are maintained in CURRENT_GAME_COMPLETION.md.
