# v0.28.0-alpha — Faster editor loading

Large editor sections now load their visible controls on demand. Hidden
characters, items and records remain in the save model and can be reached through
navigation, search and pagination without constructing all widgets at opening.
Pending edits and invalid-value checks remain independent of the current page.

Icon loading reuses validated paths and bounded read-only archive indexes.
Validation and undo use a saved-field index. Local preview measurements showed
substantially faster UI construction; actual save parsing and another computer's
performance can differ. See docs/EDITOR_PERFORMANCE.md for the measured results.

Unexpected Python errors create a local report without exception messages,
source lines, local values or save contents. Saving is disabled until the save is
reopened. Native crashes and failures before Python starts are not covered.

The existing navigation remains:

The editor now shows sections directly in a sidebar instead of hiding them in
an All sections dropdown. Party members share one Characters category with
visible character buttons and remembered sections.

- One header search reaches names, saved IDs and selected equipment across all
  categories, sections and characters. Clearing search restores navigation.
- A fixed bottom bar shows pending changes, Review changes, Reset and Save
  changes. The pending-change dialog is read-only and supports individual undo.
- Saving keeps the existing final review, related-state synchronization,
  original-file checks and direct-file replacement. Canceling does not save.
- The library sidebar gives way to the editor; a Library link returns to your
  covers. Save details holds adapter notes, compatibility, diagnostic help and
  existing-backup restoration. Integrity warnings remain visible.
- Refined light/dark panels, selected states and responsive attribute columns.
  Original game artwork, all 21 editors, offline previews and large-profile
  pagination remain available.

This is a performance and presentation update. It does not change save-format
coverage or mean that all games are complete or gameplay-verified.

Download UniversalSaveEditor.exe under Assets and double-click it. The application
is portable, with no installer or command-line setup. The executable is also
included in Code > Download ZIP. Changes apply to the opened file; no automatic
backup is created.
