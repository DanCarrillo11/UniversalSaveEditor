# v0.24.0-alpha — Requiem health, inventory and attached upgrades

- Add current health for player-specific saved records, excluding enemy health.
- Add health upgrade levels when the record's own ordered health table and saved maximum agree. Update maximum health automatically and clamp current health on reductions.
- Add existing inventory/item-box/storage stacks with exact item/parent identities. Identify 95 mapped supplies, weapons and parts by their original names.
- Add base/improved/maximum tiers for 44 mapped attached weapon parts when owned part and target weapon references agree. Capacity tiers can only increase; maximal capacity parts are read-only.
- Preserve loaded/chamber ammunition, item identities, equipment/socket references, geometry, backups, enemy records, story state and original account encryption.
- Expand Requiem's offline preview to Progress, Characters and Collection. Disable unsupported/readonly real-save choices while keeping preview choices browsable.
- Pause new game additions while completing functionality and original artwork for the current catalogue; track remaining work per game.

Requiem remains partial support. Character names/active saved variants, actual
stack caps, item creation, difficulty, full weapon/story systems and original
item icons remain pending. Single objects are read-only except mapped ammunition.
Gameplay/system profiles expose different fields. Nine native Steam files pass
identical-output and authenticated in-memory edit checks; game loading is not
yet confirmed. No editor is labelled full support.

Download UniversalSaveEditor.exe under Assets and double-click it. Code > Download
ZIP also includes the portable executable; no installation is required.
