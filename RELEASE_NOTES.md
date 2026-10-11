# UniversalSaveEditor v0.12.0-alpha

A cleaner interface with light and dark appearances, soft grouped cards, rounded controls, and focused blue actions. Editing and reviewing saves is easier across all ten game editors.

- Switch between **Dark mode** and **Light mode** from the header without losing edits; your preference is remembered locally.
- Cleaner layouts at small window sizes, a wrapping library toolbar, and scrollable game details.
- Compact category controls with search, section selection, a field count, and **Changed only** filtering.
- Undo a single value beside its field or from the summary, including edits in another slot.
- Inline validation explains invalid input; applying remains blocked until all values are valid.
- Accurate pending-change status, a modified window title, and a **Ctrl+S** review shortcut.
- Compact detected-save rows open the selected file directly and show size and modification time.
- Normal format notes are separate from integrity warnings. Single-slot saves hide the unnecessary slot selector.
- Window geometry and the last opened folder are remembered locally. Save contents and account IDs are not stored in preferences.
- Section unlock actions update the summary once per batch.

Saving still updates the opened file directly with the same name and without automatic backups. The existing compatibility and experimental labels remain unchanged; this release does not add game formats or claim new in-game verification.

All 106 game-editor and interface tests pass. The Windows executable is checked for startup, bundled cover art, platform icons, and KH III encryption dependencies.

Download UniversalSaveEditor.exe and open it with a double click.
