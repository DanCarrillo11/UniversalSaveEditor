# v0.41.0-alpha — RDR2 supplies and horse names

- Add custom amounts of 159 ordinary supplies: tonics, herbs, food, cooked food,
  horse supplies and Story Mode cartridge/arrow variants. Enter an amount for a
  missing item under Add supplies and apply once. Existing stacks remain editable
  under Inventory. Game capacity limits still apply.
- Rename an existing horse when its inventory and saved horse-slot names agree.
  Both copies update together; ambiguous names stay read-only. Names accept up to
  63 UTF-8 bytes, preserve numeric-looking text and can be reset before applying.
- Browse the same fields in read-only previews. No personal saves are packaged.

Native checks exercised 146/129/125 missing supply additions with custom amounts
and preserved existing records in three files. Two matched horse-name pairs
passed exact-span edits and byte-identical restoration; two differing pairs
stayed protected. All ten payload checks remained valid and originals were not
modified. Tests cover UTF-8 boundaries, invalid/control text, mismatches, unknown
slots, combined inventory growth, staging, reset and read-only preview behavior.

**RDR2 remains Limited coverage.** Acquisition is experimental; successful
in-game loading and persistence have not been verified. Full weapon/clothing
acquisition, new component slots, stable creation, camp upgrades and complete
story/challenge/reward dependencies remain pending. Earlier weapon customization,
bounty, camp, character, compendium and catalog tools remain available.

Download UniversalSaveEditor.exe under Assets and double-click it, or use
Updates > Restart and update. Code > Download ZIP contains the portable exe too.
Apply replaces the opened file directly, without automatic save backups or
.edited output.
