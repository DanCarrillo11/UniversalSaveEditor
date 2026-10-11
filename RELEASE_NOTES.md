# UniversalSaveEditor v0.10.2-alpha

Fixes the cropped Steam logo below game covers when Windows display scaling
is above 100%. Platform icons now render at the correct size and fit their labels.

63 automated tests pass, including a regression check for complete logo rendering
at 100%, 125%, 150%, 175%, and 200% display scale. The release build also verifies
packaged startup and the platform icon.

## Download and run

Download UniversalSaveEditor.exe and double-click it. No installer, Python,
or command-line setup is required. Code → Download ZIP also includes the exe.
Close the game, open its save, then use Review and apply → Apply to active save.
Changes update the opened file directly without automatic backups or .edited copies.

Compatibility and editable fields are unchanged. KH II and Alice remain
experimental, and Switch or PCSX2 compatibility is not claimed.

SHA256SUMS.txt contains the hash of the downloadable executable.
