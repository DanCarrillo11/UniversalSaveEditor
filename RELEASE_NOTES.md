# UniversalSaveEditor v0.11.1-alpha

Fixes KH II Steam saves failing to open with "The KH2 record has an unexpected
size." A normal archive can contain both a 1 KB KH2S system metadata record and
full-size player records. The reader now preserves system metadata and lists
only the playable saved slots. Unknown or oversized records are still rejected.

Verified by opening a local Steam save and changing money and difficulty in an
in-memory copy. The result reopened with valid integrity, the entire system
region remained unchanged, and the active save was not modified.

Five new regression tests cover system records before or after player records,
integrity repair, preservation and malformed or system-only containers.
All 96 game-editor and interface tests pass.

The ten existing game editors and their experimental scope are unchanged.
Download UniversalSaveEditor.exe and open it with a double click.
