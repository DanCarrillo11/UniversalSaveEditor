# v0.21.0-alpha — Original Elden Ring item icons

- Add original artwork for the 307 goods and 487 base armaments already recognized by the Elden Ring editor.
- Show icons in inventory, storage, supported Add items controls and existing weapon upgrades.
- Preserve the base image across reinforcement and affinity variants; unknown IDs receive no guessed artwork.
- Copy archived image bytes unchanged into offline resource packs: no AI, redraw, recoloring or source upscaling.
- Verify every image, its source hash and the separate goods/weapon identity domains. Loading icons does not change save edit permissions.

This expands presentation for the existing scoped editor. It does not add weapon
creation, armor editing, quest changes or verified in-game loading. The original
artwork belongs to FromSoftware and Bandai Namco; metadata and source attribution
are recorded in [artwork coverage](docs/ITEM_ARTWORK.md).

Download UniversalSaveEditor.exe under Assets and open it. Code > Download ZIP
also includes the portable executable; no installer or Python setup is needed.
