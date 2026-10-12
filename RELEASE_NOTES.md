# v0.16.1-alpha — Elden Ring compatibility fix

Fixes the “unsupported save revision 261” rejection introduced by the previous
editor's revision-250 limit. Characters through revision 261 can be opened when
their structure, progression summaries and player fingerprints match the known
format. Mixed old/new character revisions are supported without rewriting or
downgrading their revision markers.

Also recognizes Idus Knight and Heavy Knight and preserves their original
attribute floors. Future unknown revisions/classes and malformed data remain
blocked. Existing rune, attribute, vital and inventory/storage options retain
their integrity and byte-preservation checks.

## Validation

Regression tests cover revisions 260/261, mixed 250/261 characters, both new
classes, class floors and invalid fingerprints/structures. A native revision-261
file was not available for verification. Support remains experimental; edited
saves have not been loaded in-game. Use edited saves offline.

Download `UniversalSaveEditor.exe` under Assets and double-click it. The portable
executable is also included in Code > Download ZIP. No installer is needed.
