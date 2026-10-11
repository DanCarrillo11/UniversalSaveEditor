# UniversalSaveEditor v0.10.1-alpha

The library now shows the Steam logo and platform name below each game cover.
Editor availability and detected saves remain in the details panel and tooltip.
Coming-soon games remain unavailable for editing.

Platform labels and filters use explicit per-game metadata, ready for future
verified platforms. This release does not claim Switch or PCSX2 compatibility.

Includes the game-specific categories and section selectors from v0.10.0-alpha.
All available editors update the opened save directly, with no automatic backup
or .edited copy. Existing integrity failures require explicit repair.

## Download and run

Download UniversalSaveEditor.exe and double-click it. No installer, Python,
or command-line setup is required. Code → Download ZIP also includes the exe.
Close the game, open its save, then use Review and apply → Apply to active save.

## Validation and scope

62 automated tests cover save editing, direct writes, editor navigation, and
library behavior, including platform filtering and Steam logo rendering.
The release build also verifies packaged startup and the platform icon.

KH II and Alice remain experimental. In-game validation of KH difficulty
changes is still pending. Game compatibility and editable fields are unchanged.

SHA256SUMS.txt contains the hash of the downloadable executable.
