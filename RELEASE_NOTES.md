# v0.50.0-alpha — KH1 ability AP budgets

- See equipped and available AP in the Abilities section for recognized KH1
  Final Mix characters. Base AP and equipped accessory bonuses contribute to
  availability; each equipped duplicate has its own cost.
- Check ability, base-AP and accessory changes together. If a change would
  increase a known AP deficit, the editor explains how to resolve it before
  saving. Increase base AP, choose another accessory or unequip an ability in
  the same change.
- Preserve unknown active costs, unidentified accessories, unusual capacities,
  world/story records and stock. Character-specific behavior and modified game
  tables are not inferred. The two later unmapped ability IDs do not receive
  invented AP costs.
- Browse the AP controls without opening a save. Portable build checks regenerate
  synthetic examples before testing, including when fixtures or the build itself
  change.
- Wider ability selectors keep common names and their equipped state readable.

59 documented ability costs and 64 accessory AP rows match the original PC
battle table; 54 named supported accessories are used. File-level checks cover
39 public reference records, 345 base-AP changes and 66 enables of existing
owned abilities. Unrelated bytes are preserved and original references stay
unchanged. These checks do not establish game loading or full catalogue support.

543 automated tests pass, including combined AP changes, native preservation,
search/category navigation and preview-only behavior.

Retains v0.49's Requiem difficulty controls and Elden Ring talisman acquisition
and loadouts, plus all other existing editors and their documented limits.

Download UniversalSaveEditor.exe or the Windows ZIP under Assets. Changes apply
to the opened save in place without an automatic backup or renamed edited copy.
