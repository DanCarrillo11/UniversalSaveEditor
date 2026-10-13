# Elden Ring — initial experimental Steam support

This adapter targets the **original Elden Ring**, Steam app 1245620, and native
`ER0000.sl2` files. It does not claim Nightreign, console or modded CO2 support.
Automatic discovery searches `%APPDATA%/EldenRing/*/ER0000.sl2`.

## Available options

- Select any active character, including files with gaps between occupied slots.
- Edit runes. Increases also increase lifetime runes; decreases preserve the total.
- Edit Vigor, Mind, Endurance, Strength, Dexterity, Intelligence, Faith and Arcane.
  Changed attributes must respect the original starting class and cannot exceed 99.
- Level is calculated as the sum of the eight attributes minus 79, capped at 713.
  Level and lifetime runes are displayed as calculated fields, never free inputs.
- Edit current HP, FP and stamina within the saved maximum. Derived maxima and
  base values remain unchanged and are recalculated by the game from attributes.
- Edit quantities of existing, positive stacks of 307 named supported goods in
  inventory and storage. Per-item carrying/storage limits apply;
  unidentified entries and key items are preserved. See the expansion below for
  supported depleted stacks and equipment reinforcement.
- Add supported held goods and restore depleted stacks with native registry/counter updates.
- Upgrade known owned armaments; matching equipped representations, menu IDs and fingerprints update together.
- Adjust NG+ difficulty scaling without restarting the story or resetting world progress.
- Review automatically related field changes before applying to the active file.

New weapons, character/account transfers, boss/quest flags, Sites of Grace,
starting a new journey and DLC unlocks remain outside this scope. Pot/perfume
stocks with shared container limits are deliberately excluded. This is not full
game support. Close the game before applying; use edited saves offline. This
editor does not promise online compatibility or protection from game sanctions.

## Container and preservation

The supported BND4 container is exactly 28,967,888 bytes. Its 12 descriptors are
checked against their actual block sizes and offsets: ten character blocks
of 0x280010 bytes, global data of 0x60010, and regulation data of 0x240020.
Each block starts with 16 bytes of MD5 covering the entire remaining payload.
Broken MD5 checks require explicit integrity repair; repair changes only MD5
bytes. Unsupported structures and player fingerprints are refused.

Character parsing walks equipment handles and every intervening variable-length
section with bounds checks. Revisions 65–261 use the documented field layout,
including the 5118/5120 handle-count boundary at revision 81. Profile locations
are derived from the global menu size; summary stride is 0x24c. There is no
name/pattern search or fixed end-of-slot assumption for player fingerprints.

Changed attributes update the saved level and its menu summary. Added runes
update lifetime totals in both locations, with overflow checks. Six affected
fingerprints use doubled Adler-32 over the documented little-endian field bytes.
The weapon fingerprint updates only for verified equipped upgrades; other
equipment fingerprints and opaque padding are retained. Only affected character
MD5s and, when necessary, global MD5 are updated. Other characters, inactive
residual slots, account IDs, settings, unedited equipment, world/quest state, regulation
and tail bytes are preserved. Repair can explicitly update all 12 MD5s.

## Revision-261 compatibility fix

v0.16.0-alpha rejected every character above revision 250 before examining its
structure. v0.16.1-alpha extends this ceiling through revision 261 and adds the
documented minimum stats for class IDs 10 (Idus Knight) and 11 (Heavy Knight).
Unknown class IDs and revisions above 261 remain rejected. Revision numbers in
the save are preserved; this fix does not convert or downgrade a character.

The field layout and new class identities/minimums are cross-checked against
[Kamikaz07's maintained editor](https://github.com/Kamikaz07/Elden-Ring-Save-Editor),
which targets game version 1.17. No implementation code from that editor is
incorporated. Synthetic tests exercise revisions 260/261, mixed 250/261 characters,
both new classes and malformed data. **No native revision-261 file was available
to validate this fix**, and no in-game loading is claimed. The full descriptor,
bounded-section, summary and player-fingerprint checks still run before edits.

## Validation and limits

Four public PC files from ClayAmore/ER-Save-Lib were inspected and patched in
memory: three with six active characters and one with ten. They share some
character data and are not four independent gameplay validations. The samples
include revisions 130, 131, 151, 211, 220, 240 and 250. Requested rune, attribute
and existing-stack changes reparse correctly; byte-level comparisons restrict
changes to authorized fields, related summaries/fingerprints and MD5s.

Synthetic regression tests cover inactive gaps, variable sections, the older
handle-count boundary, direct writes without backups, integrity repair, malformed
tables/lengths, calculated-field protection, class limits, level cap, rune-total
overflow, multiple characters and the review/apply interface. Downloaded saves
and private account identifiers are not bundled. Edited saves have **not yet
been verified by loading them in the game**; compatibility stays experimental.

Format facts were cross-checked with [ER-Save-Lib](https://github.com/ClayAmore/ER-Save-Lib),
[SaveForge's specifications](https://github.com/oisis/EldenRing-SaveForge/tree/main/spec)
and actual public bytes. Conflicting fixed hash/profile offsets in older
documentation were not used. See [source attribution](../SOURCES.md).

See [v0.18 held creation, armament mirrors and NG+ limits](EDITOR_EXPANSION.md).

## v0.25 expansion

See [functionality expansion](FUNCTIONAL_EXPANSION.md) for new mapped operations, context/type guards, native-file checks and explicit limits.
