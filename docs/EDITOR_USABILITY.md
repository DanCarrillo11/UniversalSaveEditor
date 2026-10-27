# Everyday tools and Advanced options

All current editors start with their everyday controls. Advanced options adds a
separate tab containing records, counters, ambiguous/unidentified entries and
less common settings. This does not delete fields, rewrite saves, expand format
coverage or establish gameplay compatibility. All fields retain their original
identity, validation, dependencies and writer.

RDR2 has Character, Inventory, Weapons and Horse views. Character includes money,
honor, cores, progression and recognized ordinary bounties. Inventory separates
Owned items (change an existing quantity) from Add items (acquire supported
missing supplies). Existing-item acquisition duplicates and the native current
bounty mirror are advanced. Catalogue flags are availability, not acquisition;
compendium entries are recorded history, not reward delivery. Both stay advanced.

Repair weapon stages zero wear/soot/rust/dirt only for recognized condition fields
of one saved weapon. Same-model weapon copies have separate sections. Refill
player/horse cores stages 100 only for the corresponding recognized 0–100 cores;
it does not guess maximum health or change unrelated actor state. Actions are
reviewable and never write until Save changes is applied.

GTA V keeps carried weapons and wardrobe purchases in everyday Equipment and
style. Raw weapon-shop flags, wardrobe availability/seen markers, clock, respray
and special player flags are advanced. Selecting garments and inventory weapons
still uses the existing writer's dependencies. This presentation adds no unlock
relationships or new gameplay validation.

Elden Ring hides run statistics/journey changes; Kingdom Hearts hides companion
AI and game configuration; Resident Evil hides recorded statistics/results;
Risk of Rain 2 hides historical counters/logs; Alice hides chapter/story and DLC
flags. Webfishing hides catch totals and journal-quality records. Games with no
advanced fields simply omit the mode switch. Actual available fields still depend
on the opened save, slot and revision.

Search covers the visible tools and points out matching hidden advanced entries.
Turning on Advanced options keeps the query. Switching mode, theme, section or
slot preserves pending edits. Hidden invalid edits still prevent saving and remain
in Review changes. Reopening a save returns to everyday mode.

Generic enable-everything buttons are removed from mixed boolean sections. Named
Risk of Rain 2 unlock and GTA garment-purchase actions remain. Long field notes
are available through Details and tooltips; section descriptions explain important
acquisition/record distinctions. Offline examples remain read-only.


## Finding and correcting values (v0.47)

Option lists with 18 or more entries open a searchable picker. Filtering never
changes the native option index; duplicate names retain distinct indexes.
Disabled entries remain unavailable. Choosing stages the corresponding original
index, while Cancel closes without an edit. Preview pickers are browsable and
never enable saving.

Editor search matches terms in any order, ignores accents/common punctuation
and recognizes a small currency/health/XP/ammunition/difficulty vocabulary.
It does not interpret arbitrary instructions, change saved values or enable
Advanced mode automatically. Hidden advanced matches are explained explicitly.

Fix first issue navigates to the first invalid staged value. Go to field in
View changes navigates to that actual field, selecting its slot/page and enabling
Advanced mode when necessary. Both preserve all staged changes and never write
the save. The final Review and save dialog continues to show requested and
recognized automatic related changes before Apply to active save.

## Completing the journey (v0.48)

View changes now includes search and pages of up to 80 entries. Every staged
edit can be reached or undone, including the final entry of a large bulk action.
Filtering or removing an entry clamps the current page safely. Invalid-value
guidance remains outside the filtered list; filtering never bypasses validation.

Section lists with more than eight entries have a name finder. Long titles wrap.
Filtering the list does not change its active section, values or staged edits;
selecting a result navigates normally. Go to field clears this navigation filter.
Clear filters restores normal section browsing after editor search/Changed only.
Record pagination is hidden when a single page is sufficient.

Clicking a game cover still opens directly. When multiple files are detected,
the last-used detected file and remembered slot take precedence; an already-open
editor is reused with its pending edits. File choices show modification dates
and full paths in tooltips. Open save inside an editor keeps that game's format.
Library search accepts title words in any order. All navigation remains local
and never applies edits, creates backups or expands gameplay compatibility.
