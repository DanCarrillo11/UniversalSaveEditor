# v0.16.0-alpha — Elden Ring joins the library

Initial experimental support for the **original Elden Ring on Steam**, bringing
the library to 20 games. Open `ER0000.sl2` manually or select its detected save
from the Elden Ring cover. Choose an active character, then use Progress,
Character and Collection to edit:

- Runes, with automatic lifetime-rune accounting.
- All eight attributes, with automatic level and character-menu synchronization.
- Current HP, FP and stamina within the saved maximum.
- Quantities of supported existing goods in inventory and storage, including
  crafting and upgrade materials. Item identities and carrying limits are retained.

Level and lifetime runes appear as calculated values. The change review lists
automatic related changes before applying directly to the active file. Character
fingerprints and block integrity checks update together. Other characters,
account data, world/quest state, equipment and regulation remain unchanged.
No automatic backup or `.edited` copy is created. Close the game before applying.

## Validation and limits

Four public PC-format files were read and patched in memory, including six- and
ten-character containers; the samples share some character data. Regression
coverage checks integrity, unknown-byte preservation, calculated values,
malformed structures, limits, character switching, change review and direct writes.
The portable executable is checked for startup and all 20 covers.

**Edited Elden Ring files have not yet been loaded in-game.** This is experimental
support for native Steam SL2 files, not full feature/variant support. Item creation,
weapon upgrades, boss/quest flags, NG+, character transfers, console saves and
Nightreign are outside this release. Use edited saves offline; online compatibility
is not guaranteed. See [format and validation details](https://github.com/DanCarrillo11/UniversalSaveEditor/blob/main/docs/ELDEN_RING_FORMAT.md).

Download `UniversalSaveEditor.exe` under Assets and double-click it. No installer,
Python or command-line setup is needed. Code > Download ZIP also includes the
portable executable at the root.
