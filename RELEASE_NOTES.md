# v0.30.0-alpha — KH2 inventory, AP, magic and acquisitions

Corrects an important KH2 inventory-label problem: bag positions are different
from equipment/item IDs. Potion is position 0; Kingdom Key is position 33.
278 recognized stock positions now use their proper labels, categories and
separate artwork IDs. Unmapped positions and unsupported quantities are protected.

- Equipment changes transfer copies between the bag and equipped slots. Multiple
  changes form one transaction, so swapping two slots needs no spare bag copy.
  Missing stock, overflowing returns and new duplicate Keyblade assignments fail
  with guidance. Valor, Master and Final expose their real offhand slots.
- Recognized standard-data AP checks include level AP, saved boosts, equipment
  bonuses and learned ability costs. Used/available AP appears under Abilities.
  Existing deficits are retained but cannot be increased by a supported edit.
- Edit all six spell families from absent to their third tier. Four shortcuts
  follow tier changes and clear on removal. Item shortcuts check Sora's carried
  supplies and follow their removal.
- Add recognized acquisitions for six forms, four summons and 13 Secret Ansem
  Reports. New playable forms initialize a zero level and reset the Anti-point
  byte; new summons initialize a zero summon level. Existing acquisitions and
  unknown bits stay protected. Anti points are no longer mislabeled as form XP.
- Lowering only maximum Drive clamps current Drive; explicit conflicts fail.
  Updated offline previews and related-edit guidance cover these functions.

On 59 public Steam reference player records, in-memory checks submitted 354
spell-tier requests, added 672 absent acquisition flags and verified 49 conserved
weapon transfers. All edited records reparsed with valid integrity; unrelated
bytes and the original file stayed unchanged. These are file checks, not proof
that every change loads or behaves correctly in the game. Modified game tables
can differ from the standard AP tables.

Full support for all 21 games has not been achieved. Character-specific rules,
growth/reward relationships, puzzles, journal/story systems and gameplay checks
remain documented work. No new games or artwork are added.

Download UniversalSaveEditor.exe under Assets and double-click it. The portable
executable is also included in Code > Download ZIP. No installer or terminal is
needed. Changes replace the opened save directly; no automatic backup is made.
