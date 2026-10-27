# v0.52.0-alpha — KH1 equipment and inventory together

- Selecting a normal KH1 weapon or accessory automatically adds any missing
  ownership. Accessory quantities include equipped copies across recognized
  companions, including duplicates. Unequipping does not remove owned copies.
- Carried consumables transfer copies to/from reserve stock. Apply simultaneous
  swaps without a spare copy, or adjust the reserve quantity in the same change.
  Insufficient stock, overflow and conflicting ownership requests explain what
  needs changing before saving.
- Review shows automatic inventory changes. AP and equipment-aware HP/MP checks
  still apply to the complete transaction. Unknown equipment, unsupported counts
  and hidden entries stay protected. Temporary story weapons cannot be acquired
  through normal equipment/inventory controls; existing story context is retained.

File-level checks: 113 changes across 39 public native records (39 accessory,
39 consumable and 35 weapon changes), exact non-CRC restoration and preservation
of unrelated bytes. The reference remains unchanged. 405 recognized owned
equipment configurations and 66 carried/reserve comparisons corroborate the
distinct quantity representations. These checks do not prove game loading.

549 automated application tests cover transactions, bounds, unknown state,
AP/HP/MP interactions and review without writing the original file. Updated
examples remain synthetic and read-only.

Complete growth, story/journal/reward systems, character-specific rules and
gameplay checks remain pending. Other catalogue limits, including Max Payne's
unmapped health, Bullet Time and loaded rounds, remain documented. No game is
declared full support.

Download UniversalSaveEditor.exe or the Windows ZIP under Assets. Changes apply
to the opened save in place, without an automatic backup or renamed edited copy.
