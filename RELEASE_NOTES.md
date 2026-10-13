# v0.22.0-alpha — Original artwork across game editors

- Extend original artwork to all six supported Kingdom Hearts editors, WEBFISHING, Risk of Rain 2, Resident Evil HD Remaster, RE3 Remake, RE5 and RE7.
- Show game resources beside recognized inventory entries, baits, cards, commands, unlocks and RE5 infinite-ammo flags.
- Update KH1/KH2 equipped-item images immediately when a dropdown changes or resets; use the actual saved equipment ID rather than the choice index.
- Add exact, read-only RE7 ItemDataID string lookup within the same serialized object; duplicate, invalid and unknown identities receive no substitute.
- Ship 3,155 verified artwork associations across 14 editors, with source references, hashes and explicit per-game coverage. Shared base card art does not imply premium-card appearance or a displayed card value.
- Keep original sprite pixels and game renders, with smaller aspect-preserving previews for large renders. No AI artwork, recoloring or runtime downloads.

Artwork remains pending for Alice, Max Payne, RE4 (2005), RE4 Remake, RE6, RE8
and RE9. Coverage within the other games is also scoped; unknown IDs stay as
text. This release improves presentation, not editing permissions or in-game
validation. See [artwork coverage and sources](docs/ITEM_ARTWORK.md).

Download `UniversalSaveEditor.exe` under Assets and open it. Code > Download ZIP
also includes the portable executable; no installer or Python setup is needed.
