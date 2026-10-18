# v0.45.0-alpha — GTA V wardrobe and saved clothing

- Browse named single-player wardrobe entries separately for Michael, Franklin
  and Trevor, including clothes, ordinary outfits, props and barber purchases.
- Manage each entry's availability, purchase and seen marker. Buying an item
  also makes it available, without charging money. Acquire a whole wardrobe
  section or restore its pending changes.
- Change recognized currently worn garments using named style/texture choices.
  The writer synchronizes the saved character outfit and, for the active actor,
  its native drawable/texture maps. Selecting another garment acquires it.
- Use the new sections under Equipment, with character filters, search,
  pagination, review/reset and offline previews.

The older and newer catalogues contain 1,911 and 1,888 named static entries
across the three characters, respectively. Unknown, special/unnamed and runtime
DLC entries are preserved. Three native references pass masked bit checks and
combined changes in plaintext/encrypted copies, with checksums, exact byte-span
checks and unchanged originals. Synthetic and interface tests cover conflicting
requests, bit 31, padding, actor isolation, bad headers/schemas, active snapshot
disagreement, resource overrides and broken pointers.

**GTA V remains Limited coverage.** Hair/beard and prop equipping, composite
outfit assembly, dynamic DLC apparel, complete vehicle/body/wheel/livery tools,
full DLC weapon acquisition, properties and story/reward dependencies remain
pending. Enhanced-native and successful in-game loading/persistence verification
are not claimed. Earlier vehicle and weapon tools remain available.

Download UniversalSaveEditor.exe under Assets, use Updates > Restart and update,
or extract Code > Download ZIP and open the included exe. Applying changes
overwrites the opened save in place, without automatic backups or .edited files.
