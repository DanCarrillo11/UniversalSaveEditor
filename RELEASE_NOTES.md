# v0.18.0-alpha — Expanded party, equipment and inventory editors

- **Kingdom Hearts Final Mix:** saved combat companions, level/XP, equipment slots and known ability entries with equipped/unequipped choices.
- **Kingdom Hearts II Final Mix:** saved party equipment and ability lists; weapons and abilities for the five main Drive Forms. Characters remain grouped in one selector.
- **Elden Ring:** add supported stackable goods to held inventory, restore depleted stacks, upgrade known owned armaments and adjust NG+ difficulty scaling. Native counters, item registry, equipped representations, menu snapshot and fingerprints synchronize when affected.
- **RE4 (2005) Ultimate HD Edition:** existing case quantities and per-weapon firepower, firing-speed, reload and capacity tiers. Case geometry and loaded rounds stay intact; capacity only increases.
- **RE6:** equipped skill selection for campaign and eight Mercenaries sets, keeping purchase flags and progression untouched.

Unknown identities, unsupported structures and unrelated bytes are preserved.
File-level edits were checked against public KH/Elden/RE6 fixtures and four local
RE4 records, with independent synthetic and UI regressions. Loading edited files
in-game remains pending; native Elden revision-261 and several RE Engine Steam
variants still need validation. KH1's expanded party editing is experimental.

This is not full game support: quest/boss changes, new weapons, RE4 case-object
creation/comprehensive unlocks and a full RE5 inventory editor are not implemented.
KH ability AP/character rules and equipment-derived attributes are not recalculated;
RE6 skill selection is not a purchase guarantee; NG+ scaling does not restart the story.
See [precise scope and limits](docs/EDITOR_EXPANSION.md).

Download UniversalSaveEditor.exe under Assets and open it. Code > Download ZIP
also includes the portable executable; no installer or Python setup is needed.
