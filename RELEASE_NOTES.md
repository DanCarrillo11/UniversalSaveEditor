# v0.43.0-alpha — GTA V story weapon tools

- Add/remove 35 identified base-slot weapons for Michael, Franklin and Trevor.
  Set ammunition for a missing base-slot weapon to add it in the same apply.
- Synchronize ammunition across carried weapons sharing its type. Conflicting
  totals are rejected; other characters retain their own ammunition pools.
- Equip mapped components and colors. Choosing a component replaces conflicting
  parts on the same attachment point. Acquisition applies recognized shop flags
  without deducting cash. Unknown component bits and other script state stay intact.
- Manage Ammu-Nation unlocks, purchases, mapped attachments and colors for 40
  weapons. Choose a protagonist and a weapon to find its inventory and shop options together.
- Distinguish old three-cell inventories with one-hot packed colors from the
  five-cell revision with separate tint/livery fields and different component bits.
- Browse all weapon tools in the offline preview; previews cannot save changes.

Native-file checks cover three references, plaintext/encrypted copies, 1,191
individual masked shop edits per reference, combined acquisition/customization,
requested-value reparsing, checksums and exact allowed spans. Original files
were unchanged. Synthetic and interface tests cover unknown layouts, duplicates,
shared-ammunition conflicts, component exclusivity, staging/reset and previews.

**GTA V remains Limited coverage.** New DLC inventory slots, vehicle creation/model
swaps/tuning, properties/clothing, collectibles and full mission/reward dependencies
remain unsupported. An Enhanced-specific native file and successful in-game loading
are still required for verification. No complete-support claim is made.

Download UniversalSaveEditor.exe under Assets and double-click it, or use
Updates > Restart and update. Code > Download ZIP includes the portable exe.
Apply replaces the opened file directly, without automatic backups or .edited files.
