# v0.51.0-alpha — KH1 equipment-aware HP/MP and Max Payne compatibility

- KH1 shows recognized maximum HP/MP including equipment bonuses. Base, current,
  accessory and weapon edits are checked together. Reducing a known maximum
  clamps a previously valid current value; an explicit conflicting value is
  rejected. Increases do not heal or refill, and unknown effects are preserved.
- Fix Max Payne rejecting entire saves because untouched world data contains
  noncanonical flag bytes or nonfinite scalars. Preserve those bytes while
  checking recognized weapon ownership and retaining structural bounds.
  All 42 additional public reference saves now open; 11 previously failed.
- Show related KH1 current-value changes in the review before saving. Updated
  read-only examples use valid synthetic attributes and include the new maxima.

File-level checks: KH1 has 39 public records, 351 HP changes and 117 MP changes,
including 350 HP and 108 MP automatic clamps. Unrelated bytes are preserved and
non-CRC bytes restore exactly. Max Payne: 565 inventory edits across 42 reference
files, exact restoration, original screenshots and world state retained. Original
reference files stay unchanged. These checks do not prove successful game loading.

Max Payne health, Bullet Time and loaded rounds remain unmapped. Complete growth,
story/reward dependencies and other catalogue limits are still documented; no
full-support certification is claimed.

540 automated application tests pass, including preservation of unknown world
encodings, coupled attributes/equipment and the review of automatic HP changes.

Download UniversalSaveEditor.exe or the Windows ZIP under Assets. Changes apply
to the opened save in place, without an automatic backup or renamed edited copy.
