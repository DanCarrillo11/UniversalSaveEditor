# Additional Kingdom Hearts PC adapters

The catalogue and README define the editable scope. All new adapters are
experimental: fixture round trips are verified, game-load validation is pending.
They keep the opened file's name and location and do not create backups.

## Re:Chain of Memories

The PNG sqEX block contains a 100-entry table with 0x158-byte descriptors and
0x3A30-byte record allocations. Player records are 0x3630 bytes, including their
16-byte header. Never confuse the allocated stride with the recorded length.
Moogle Points at 0x2D58 are mirrored at 0x14. Both copies are updated before
recomputing the internal checksum; then the outer PNG CRC is updated.

XP is at 0x2D50, difficulty at 0x481 (byte, Beginner/Standard/Proud), and card
counts begin at 0x1FC4. The source inventory order defines 1,180 positions, of
which 1,139 are named usable entries. Attack and magic/summon cards include
normal/premium variants and values 0-9. Unused entries, decks, story and unlock
flags are preserved. Inventory quantity editing is not a story unlock operation.

## Birth by Sleep Final Mix

100 PC allocations of 0x13C00 bytes. Public PC descriptors record 0x12000 bytes,
while the BBSD header declares the 0x11E50-byte Final Mix record, revision 0x1D.
The remaining descriptor bytes are padding and are preserved. The internal
checksum adds little-endian uint32 words from 0x10 to the declared record end.

Character data begins at 0x59D0; the character identity belongs to the slot.
Difficulty at 0x5CAC uses 0x08/0x48/0x88/0xC8, represented by four labelled UI
choices rather than writing a dropdown index directly. Commands use 10-byte
entries at 0x3498. Only known existing command entries expose level and XP;
identities and deck references are preserved. Ability records are 4-byte entries
at 0x4D64. Active stacks cannot exceed acquired stacks.

HP1/HP2 remain uneditable: the primary model does not establish how the two
counters relate to displayed HP. Their names are not sufficient evidence.

## Dream Drop Distance HD

100 PC allocations of 0x16600 bytes. Player records have SOMD magic and version
0x14; SOMS system records remain untouched. Difficulty at 0x92 is mirrored at
0x20. Sora XP at 0xD1F0 is mirrored at 0x28. Sora and Riku have separate XP,
level and Drop Point offsets. Existing inventory identities and equip flags
remain unchanged; only the amount byte of known entries is exposed.

## Kingdom Hearts III

PC plaintext is 0x94F4F0 bytes, with S@vE magic and FileSize 0x94F4D8. The
CRC covers FileSize bytes starting at 0x10; the last eight bytes are preserved.
Encrypted saves contain AES-256-ECB ciphertext, a 0x08 marker and the MD5 of
plaintext through FileSize + 0x10. Key derivation uses the original account ID,
never the current Windows username or a hardcoded author's ID.

An original account path supplies the ID automatically. A copied/downloaded
file requires its creator's ID. Wrong IDs, invalid lengths, console layouts and
digest mismatches are rejected. The ID is held in memory for reloading and
existing-backup restoration; it is not transmitted or stored in the repository.
Nonzero inventory counts set Obtained while preserving the other flag bits.

## Reference and validation

Schemas, tables and checksum/key derivation are adapted from
[BFlorry/KingdomSaveEditor](https://github.com/BFlorry/KingdomSaveEditor/tree/e5eec7403f939d7a94a62d996130d84f59887dda)
under GPL-3.0-or-later. Copyright: Luciano Ciccariello (2020), Mikko Mäntylä
(2026); PC layout/key contributions by fungualtissue1230 and dedede123.

ReCoM and KH III public fixtures come from that repository's KHSave.Tests/Saves.
BBS and DDD PC archives come from
[Aneita-the-human's public PC save collection](https://www.reddit.com/r/KingdomHearts/comments/113q5v5/).
The latter is an Epic PC collection using the documented shared PC record layout;
Steam game-load validation is still pending. Downloaded samples and patched
copies stay under ignored work/ and are not redistributed. All committed tests
construct synthetic records and assert bounds, integrity, mirrors, account
handling, slot isolation and preservation of unrelated bytes.

The public 0.2 PNG contains encrypted sqEX data with a different wrapper; no
verified decryption pipeline was found. Melody of Memory also lacks a verified
standalone PC pipeline. Neither is marked editable.
