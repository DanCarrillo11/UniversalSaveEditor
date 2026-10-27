# Max Payne 1 PC save research

Status: **experimental inventory editing**. Weapon ownership, reserve ammunition
and painkillers are exposed. Game-load validation remains pending; health,
Bullet Time, loaded rounds and checkpoint/story state remain uneditable.

## Evidence

Three locally generated Steam PC `.mps` saves were inspected on October 10, 2026.
They contain save revision 48, a `(1, 1)` header chunk, a caption and a
size-prefixed preview image. Following roots are `(16, 13)`, `(0, 1)` and `(0, 4)`.
The first root contains the level identifier and an entity section `(17, 1)`.
The actual player is named by a `(18, 1)` chunk with the exact string `player`,
followed by its `(0, 13)` state chunk. Other entities reference `player` too:
searching for the first occurrence or using a fixed file offset is incorrect.

All three files pass the independent reader in `maxpayne_save.py` without writes.
The header preview is treated as opaque bytes. Chunks carry an identifier, a
revision and a total length including their 13-byte header. The revision is
**not a child count**. Integer values use signed or unsigned encodings of varying
width. The writer retains each original encoding when it fits, otherwise widens
the signed integer and rebuilds every enclosing chunk length. It preserves
unaffected chunks verbatim. Synthetic tests verify both fixed-size weapon flag
changes and growing inventory values through nested ancestors.

The tagged-stream facts were cross-checked against
[Tatsh/dade's R_MemoryFile format documentation](https://github.com/Tatsh/dade/blob/master/dade/maxpayne/memoryfile.py).
The application reader was independently written. The author's RAS tooling was
used only in ignored local research to inspect factual weapon and inventory IDs
from the installed game's `x_data.ras`. Extracted game files, research tools,
personal saves and their previews are not distributed.

## Pending validation

- Obtain public reference saves with documented ammunition and compare their
  inventory state. The user does not need to prepare controlled save pairs.
- Compare externally documented painkiller and health values across reference saves.
- Verify weapon ownership flags and shared inventory groups in a loaded save.
- Determine whether reserve ammunition and loaded ammunition need coordinated
  updates, including dual weapons and reload state.
- Test edited inventory values in a running original PC game.

The inventory is located structurally within the named player, with exactly
14 verified shared groups and their original weapon IDs. Unknown layouts and
modded IDs are rejected. Ammunition limits come from the installed game's
shooting.h definitions. Preview, entities, current level and unknown state are
preserved. All three local saves passed inventory read/patch/reparse checks on
ignored copies; the active saves are untouched. Experimental status explicitly
distinguishes these checks from successful loading in the game.

## Additional public reference checks (v0.51)

The user supplied Endurance's public [Full Game & Individual Level Saves](https://www.speedrun.com/max_payne_1/resources/p78jl)
archive after its download required human verification. It contains 42 PC `.mps`
files across gameplay levels and difficulty variants; no original is installed,
overwritten or redistributed. The complete set now opens. Eleven previously
failed because the reader treated noncanonical flag bytes or nonfinite floating
values in untouched world records as a corrupt save.

Those unknown encoded values remain original byte sequences. They are never
exposed as health, Bullet Time or editable ownership. Known inventory ownership
still requires canonical boolean values, exact identities and structure.
Unknown tags, truncation, nesting limits and chunk bounds remain guarded.

565 supported inventory edits across all 42 references passed full reparsing,
unrelated-leaf checks and byte-identical restoration, including changes that
widen compact integer encodings. Original screenshots and world records remain
unchanged. These checks do not prove successful game loading or identify health,
Bullet Time or loaded-ammunition fields.
