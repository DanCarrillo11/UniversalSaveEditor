# UniversalSaveEditor v0.10.0-alpha

A simpler editor layout: a few main categories for each game, with section
selectors and foldable blocks inside them.

| Editor | Main categories |
|---|---|
| KH Final Mix / KH II Final Mix | Progress, Characters, Collection |
| WEBFISHING | Progress, Equipment, Collection |
| Risk of Rain 2 | Progress, Unlocks, Records |
| Alice persistent profile | Progress, Character, Collection |
| Alice configuration | Progress |

- Choose Sora, Donald, or Goofy within Characters instead of separate tabs.
- Find KH II's Drive Gauge and Drive Forms inside Sora.
- Browse inventory, equipment, collectibles, or unlock types with a section selector.
- Fold or expand sections. Search and navigation remain visible while scrolling.
- Keep pending edits when changing character, category, or save slot.
- Keep the selected category, character, search, and fold state when refreshing.
- Batch actions apply only to their own section; hidden invalid edits still
  block saving and all pending edits appear in review.

## Download and run

Download UniversalSaveEditor.exe and double-click it. No installer, Python,
or command-line setup is required. Code → Download ZIP also includes the exe.
Close the game, open its save, then use Review and apply → Apply to active save.
Changes update the opened file directly. No automatic backup or .edited copy
is created. Existing integrity failures still require explicit repair.

## Validation and scope

62 automated tests cover save editing, direct writes, UI behavior, complete field
coverage, character and slot navigation, Drive Form placement, section actions,
search, and hidden invalid edits. The release build checks packaged startup.

This update reorganizes existing features; it does not add new characters or
new game compatibility. KH II and Alice remain experimental, and in-game
validation of KH difficulty changes is still pending.

SHA256SUMS.txt contains the hash of the downloadable executable.
