# Resident Evil PC support research

The author's Steam library sets the first priority: HD Remaster, 0 HD, 2 Remake,
3 Remake, 4 Remake, 4 (2005), 5, 6, 7 Biohazard, and Requiem.
Owning a game or finding a third-party editor does not establish compatibility
in UniversalSaveEditor. Only implemented, bounded adapters belong in the
editable catalogue. Other PC releases can follow this group.

| Priority group | Steam AppID | Current implementation / evidence |
|---|---|---|
| RE4 (2005), Ultimate HD Edition | 254700 | Initial scoped adapter: currency, saved difficulty, player/Ashley health, save and combat statistics. Four local slots inspected without altering the active file. In-game validation pending. |
| RE HD Remaster | 304240 | Research pending. The urbanware-org/re-hd-se project is explicitly for PS3; its offsets must not be presented as verified PC offsets. |
| RE0 HD Remaster | 339340 | descawed/re0box documents a 2,337,008-byte vanilla container and 20 slots. This is an in-game mod with additional save data, not a verified standalone PC editor schema. |
| RE5 | 21690 | shinneider/RE5-Save-Editor documents chained XOR encoding, two additive-checksum ranges, currency and profile flags. No local RE5 fixture was found yet; its assumptions and bit ordering need independent validation. |
| RE6 | 221040 | No sufficiently verified PC save schema has been established in this research pass. Do not apply RE5's encoding or offsets to it. |
| RE2 Remake | 883710 | REE Save Editor provides a RE2 profile, DSSS container handling, Blowfish and dynamic RSZ layouts. UniversalSaveEditor has no adapter yet. |
| RE3 Remake | 952060 | REE Save Editor provides a distinct RE3 Blowfish key and schema. UniversalSaveEditor has no adapter yet. |
| RE4 Remake | 2050650 | REE Save Editor provides an account-derived key and encrypted DSSS parsing. Separate from the original RE4 format. UniversalSaveEditor has no adapter yet. |
| RE7 Biohazard | 418370 | REE Save Editor provides a distinct RE7 Blowfish key and schema. UniversalSaveEditor has no adapter yet. |
| RE Requiem | 3764200 | REE Save Editor provides Mandarin encryption and a Requiem RSZ schema. Local containers exist, but they have not been decrypted or edited in this app. Its README AppID table is inconsistent; the source profile supplies 3764200. |

## References and licensing boundaries

- [nipkownix/re4_tweaks](https://github.com/nipkownix/re4_tweaks): UHD runtime property names, difficulty codes and health ranges. [global.h](https://github.com/nipkownix/re4_tweaks/blob/master/dllmain/SDK/global.h) describes runtime structures, not file offsets.
- [NathanJRollins/re4-save-reattribution-utility](https://github.com/NathanJRollins/re4-save-reattribution-utility): original Steam file size and account-related bytes. Account reattribution is outside the current adapter's scope.
- [dubiousnerd/re4vr-save-editor](https://github.com/dubiousnerd/re4vr-save-editor): secondary comparison only. VR record offsets and stride differ from UHD and must not be copied into the PC reader. No VR implementation is bundled.
- [urbanware-org/re-hd-se](https://github.com/urbanware-org/re-hd-se): PS3-specific reference, not PC support.
- [descawed/re0box](https://github.com/descawed/re0box): RE0 container size and modded-save context.
- [shinneider/RE5-Save-Editor](https://github.com/shinneider/RE5-Save-Editor): source reference for RE5 encoding and checksum ranges. Its MIT licence must accompany any substantial adaptation; no code is incorporated currently.
- [kvasszn/ree-save-editor](https://github.com/kvasszn/ree-save-editor): RE Engine format and game profiles. No explicit repository licence was found in the inspected checkout. Its code and large schema assets are not incorporated or bundled. A compatible independent implementation or explicit reuse permission is needed before any incorporation.

## Next verification steps

1. Complete the original RE4 fixture checks and confirm that edited values load in-game.
2. Map inventory packing and weapon upgrades independently before exposing them.
3. Obtain existing or public Steam fixtures for each remaining format; downloaded saves must retain their original account metadata during inspection.
4. Check decode/encode identity, byte preservation, integrity repair, field boundaries and different slots before enabling an editor.
5. Use Progress, Characters, Equipment, Collection or Records categories according to verified fields, with at most three categories per game.

Research saves, source checkouts, account identifiers and extracted game binaries
stay in ignored local work directories and are not included in public commits.
