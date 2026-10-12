# Compatibility, diagnostics, recent saves and collection labels

## Compatibility evidence

Every game has a Compatibility details panel in the library. Help & details in
the editor opens the same information plus an optional diagnostic preview.
`compatibility.py` records the supported format, file-check evidence, gameplay
evidence and limits separately. “PC files checked” applies to researched samples,
not every version, feature or file. Elden Ring explicitly retains the native
revision-261 validation caveat. WEBFISHING's money edit is a user-reported in-game
check; its other features are not represented as gameplay-confirmed.

## Friendly errors and support privacy

Failed discovery, identification, opening, review, application and restoration
use explanations with next steps and a Copy diagnostic action. Reports are
constructed from a positive field allowlist rather than redacting raw exception
text. Recognized revision/character numbers can be included; raw errors cannot.

Reports contain application version, portable-build state, operation, selected
game/platform, known file extension, bounded file size and validation status.
When inspecting an opened save they can include record/field/warning counts and
the selected record number. They contain no file contents, hashes, filenames,
paths, account IDs, character names, field keys, field values or warning text.
Reports are previewable. Copying places the text on the clipboard; nothing is
sent, uploaded or attached to an issue automatically. Reports are not persisted.

## Recent saves

Recent saves in the application header, also available through Ctrl+R, remembers
up to ten successfully opened files on this device. Reopening restores the last
selected record. Failed opens and canceled discard prompts do not replace the
active editor or add a history record. A moved/missing file can be located again;
the old shortcut is replaced only after successful parsing.

Remove and Clear history delete shortcuts only. Remember recent saves can be
disabled, which clears the list and prevents further recording. These settings
are stored locally under `files/recent` and `files/rememberRecent`; entries contain
only game ID, absolute file path and numeric record index. Paths may include
private folder/account names and are deliberately excluded from diagnostics.
No save is reopened automatically at startup. Opening/applying still uses the
normal pending-edit prompt, integrity checks and direct saving rules.

## Collection presentation

- Elden Ring's 307 already supported goods have verified Consumables, Crafting
  materials or Upgrade materials categories, separated by Inventory/Storage.
- KH III's first 60 synthesis-material indexes use the upstream enum's names;
  the remaining indexes are explicitly unidentified. Byte offsets, keys, numeric
  limits and editable scope are unchanged.
- HD Remaster groups known inventory/item-box entries into weapons, ammunition,
  consumables and other items; unknown identities remain marked as unidentified.
- RE2/RE3 read item IDs only from a unique sibling in the same inventory object.
  RE4 Remake reads IDs only through the verified nested Item property. These
  identities are display-only. Missing/ambiguous identities remain unmapped, and
  no human-readable names are guessed. RE7 quantities remain unidentified.
- Existing named KH, WEBFISHING and Risk of Rain controls keep their mappings.

These presentation changes do not create items, expose identity editing or claim
new in-game compatibility. Tests check that all existing field keys survive the
category mapping and that quantity/material edits retain their identity bytes.
