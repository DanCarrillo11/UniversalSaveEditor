# Editor navigation

The editor uses visible categories and sections instead of a section dropdown.
Inventory, Cards, Commands, Collectibles and Library names reflect the game.
Characters share one category; character buttons show the sections available for
that character. Each character's last section is remembered while browsing the
opened save. All exposed fields remain accessible.

Use **Search this editor** to search names, saved IDs and currently selected
equipment across categories. Search results include sections and characters
outside the current selection. Clearing search restores the selected section.
**Changed only** shows pending changes throughout the current category so edits
in another section remain easy to find. Both searches and navigation preserve
edits; reopening a file clears its search filters.

The fixed bottom bar shows the number of pending changes. **Review changes**
opens a read-only summary with individual undo controls and validation errors.
**Save changes** retains the final review and apply dialog, including automatic
related changes. Canceling either dialog does not write the save. Applying keeps
the existing filename and performs the normal original-file and integrity checks.
No automatic backup is created.

**Save details** contains feature coverage, adapter notes, diagnostic help,
existing-backup restoration and saving guidance. Integrity warnings and the
repair option remain visible outside this panel. Invalid edits disable saving,
including errors in hidden sections or other records. Pending changes remain
available for inspection and undo.

Short attribute sections use two columns when space allows and one column in
narrower content areas. Character lists scroll horizontally when necessary;
sections and fields scroll independently. Large record categories retain their
100-row pages, field search and scoped section actions rather than constructing
thousands of widgets.

This release changes navigation and presentation. It does not extend game-format
coverage or imply that all game features have been verified in gameplay.
