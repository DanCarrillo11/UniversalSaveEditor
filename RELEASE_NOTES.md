# UniversalSaveEditor v0.11.0-alpha

Adds five experimental editors/format adapters to the unified application:

- Re:Chain of Memories: Moogle Points, XP, difficulty and 1,139 named card quantities.
- Birth by Sleep Final Mix: per-slot character progression, Munny, medals, attributes, commands and abilities.
- Dream Drop Distance HD: Sora/Riku XP, levels, Drop Points, Munny, difficulty and existing inventory quantities.
- Kingdom Hearts III PC: encrypted Steam slots, Munny, XP, difficulty, party attributes, inventory and material counters.
- Max Payne 1 PC: weapon ownership, reserve ammunition and painkillers in original revision 48 saves.

All ten library games now have scoped editors. Each new editor uses categories,
field search and change review. Applying edits updates the opened save directly,
keeping its name and location. No automatic backup or .edited copy is created.

91 automated tests cover bounds, invalid formats, checksum/mirror updates,
account encryption, preservation, multiple slots and interface navigation.
Public PC fixture round trips are checked locally; successful in-game loading
of edited saves is still pending, so the new adapters remain experimental.
KH 0.2 and Melody of Memory are not yet supported. These editors do not expose
every game system; the README lists the exact editable scope and exclusions.

For a KH III file outside its original SaveGames account directory, the editor
asks for the original creator's platform account ID. It cannot decrypt another
person's downloaded save without that ID. Nothing is uploaded.

Download UniversalSaveEditor.exe and double-click it, or extract Code > Download
ZIP and open the executable at the root. No installer, Python or command-line
setup is required. SHA256SUMS.txt verifies the packaged executable.
