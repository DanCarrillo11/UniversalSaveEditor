# Faster editor loading

Large categories construct the selected section in pages of at most 100 fields,
instead of creating widgets for every hidden character, item and record during
opening. The complete save model stays loaded. Navigation and search can reach
every field, including the last page, and edits remain independent of widgets.
Hidden invalid edits still block saving; section actions still affect the entire
specified section. Small categories keep their normal layout.

Saved fields are indexed once for validation and undo. Icon manifest validation
resolves the asset root once and reuses each archive's validated path. Archived
member paths retain traversal, absolute-path and drive-prefix checks. Read-only
archive indexes are reused with eight open archives at most; eviction closes
the file handle. The scaled-image cache holds at most 512 entries. Original
artwork bytes and save adapters are unchanged.

## Local measurements

The same seven offline previews were profiled with cProfile in an offscreen Qt
window on this development PC, before and after the changes. The first editor
includes a cold item-art catalogue. These are UI construction measurements,
not promises for another computer or the time needed to decrypt a real save.

| Editor | Before | After | Initially constructed controls |
| --- | ---: | ---: | ---: |
| KH1 | 2.974 s | 0.266 s | 347 → 165 |
| KH2 | 0.748 s | 0.057 s | 545 → 28 |
| KH3 | 2.343 s | 0.244 s | 1398 → 119 |
| Elden Ring | 1.365 s | 0.336 s | 685 → 213 |
| WEBFISHING | 0.583 s | 0.102 s | 627 → 71 |
| Risk of Rain 2 | 0.594 s | 0.053 s | 474 → 35 |
| Requiem | 0.126 s | 0.066 s | 55 → 55 |

## Unexpected Python errors

The application stores its last unexpected Python error in
`%LOCALAPPDATA%/UniversalSaveEditor/last-error.json` and shows where to find it.
The report contains the application version, exception type and code locations.
It excludes exception messages, source lines, local values and save contents.
Nothing is sent automatically. Saving is disabled after an unexpected error
until a save is reopened successfully.

This report does not catch native crashes, forced termination, antivirus blocks,
or failures before the Python application starts. A reported crash without a
reproduction, error report or Windows failure details remains undiagnosed.
