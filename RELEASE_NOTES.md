# v0.19.0-alpha — Resident Evil Village

- Add an experimental Steam Resident Evil Village (RE8) editor and original cover art.
- Edit Lei, Challenge points (CP), current player health and existing multi-item stack quantities.
- Edit owned, opened and unlocked flags of existing extra-content records independently.
- Organize fields into Progress, Character and Collection; detect Steam data*.bin files automatically.
- Keep single-item records read-only and preserve identities, loaded ammunition, unknown data, account metadata and DLC dependencies.

Shared console gameplay payload edits were checked in memory, and independent
synthetic Steam fixtures verify parsing, encryption, integrity, byte preservation,
direct saving and UI behavior. Native Steam Village files and in-game loading
still need validation. Item/content names and actual game stack caps are unmapped;
weapon upgrades, new objects, story changes and challenge completion are not offered.
See [Village scope and evidence](docs/RE8_FORMAT.md).

Download UniversalSaveEditor.exe under Assets and open it. Code > Download ZIP
also includes the portable executable; no installer or Python setup is needed.
