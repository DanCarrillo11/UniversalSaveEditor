# Alice: Madness Returns — Steam PC profile

The adapter targets `PersistentData_PC.PSD`, little-endian archive revision 49
(`0x31`), second word `0xf223`. Other revisions are rejected.

## Serialized order

1. Two header words, then a counted map table. Each map has an FString name and
   a counted actor table. Each actor has an FString name and six 32-bit scalars.
2. A preserved scalar and the current map FString.
3. Game-info state: paint-pot count, three statistics, six chapter/snout/memory
   triples, three totals, a FString array, nine flags, four story/statistic values,
   and twelve dress ability flags.
4. Player state: **Teeth**, current health, four weapon levels (Vorpal Blade,
   Hobby Horse, Teapot Cannon, Pepper Grinder), spinning deflect, sixteen Radula
   flags, five major-memory flags, six chapter flags, six highest completed
   difficulties, twenty enemy-journal flags, six health upgrades, last checkpoint.
5. Five FString arrays: played cinematics, acquired abilities, memories, snouts,
   and bottles.
6. Six statistics, first-upgrade flag, completion fraction, play time, seventeen
   bytes (fifteen capabilities and two preserved globals), seventy chapter flags.

FStrings have signed 32-bit lengths: positive includes a single-byte terminator,
negative counts UTF-16 code units including the terminator, zero is empty.
Counts, lengths, terminators, scalar ranges, and total consumed length are checked.
Existing string bytes are preserved when unrelated list entries change.

The native serialization order was independently mapped from a local Steam
installation and cross-referenced with generated class/property metadata.
Game executables, extracted source, research tools, and personal profiles are not
distributed with this project.

## Catalog and coupled edits

The factual catalog contains 89 small memories, 83 bottles (29 large / 54 small),
59 snouts, sixteen paint-pot pickups, twenty-one story cinematics, and 56
non-debug chapter-select entries. Snout ID ranges follow the configured counts
14/15/11/11/8 and were cross-checked against map metadata and a local profile.
Unknown list entries and actor records are preserved.

- Weapon levels and acquired abilities update together in both directions;
  contradictory selections are rejected. Known capability bytes are synchronized.
- Memory/bottle edits change scalar 3 of matching pickup records. The other five
  values are preserved. Unrecorded acquired pickups get the observed defaults
  `0, 1, collected, 0, 0, -1`.
- Paint pots synchronize individual pickups and total. Their defaults are
  `0, 1, collected, -1, 0, -1`. Conflicting explicit pot/count edits are rejected.
  Completing a Radula room remains a separate flag.
- Snout edits update the list and total/chapter counters. Chapter completion
  updates both serialized chapter arrays.
- Affected completion is recalculated unless explicitly edited: chapters 60%
  (15/10/10/10/10/5), memories plus major memories 10% (denominator 94), snouts 10%
  (59), Radula rooms 10% (16), bottles 10% (83), clamped to 0–1.

Results are parsed again and all requested values verified. No-op is byte-identical.

## Scope and validation

The separate `GameConfig_PC.CFG` archive uses revision 16 and the same second
header word. It contains 22 four-byte settings, 66 FStrings for bindings, three
control settings, UI arrays of 100/100/100/50 integers, and a final checkpoint
flag. The adapter edits only the first two settings: current and lowest-used
difficulty (0 Easy, 1 Normal, 2 Hard, 3 Nightmare). Lowering current difficulty
also lowers the historical minimum when needed. An explicit minimum above the
current difficulty is rejected. All remaining configuration bytes are preserved.

**Experimental.** Automated tests verify preservation, variable-length edits,
new records, coupled fields, malformed input, UI controls, and direct save updates. In-game
validation of all categories is still pending.

- The previous alpha's Teeth offset selected the Ruin-defeat statistic. Walking
  the complete archive corrects it and preserves that statistic.
- `Alice2Checkpoint.sav` is a separate format and is not edited. Position and
  selected outfit are outside this adapter. Highest **completed** difficulty is
  in the persistent profile; current difficulty is in the configuration file.
- Chapter-select flags unlock menu entries; they do not relocate a checkpoint.
- Dress controls edit **ability-active flags**. DLC controls require installed
  content and do not install DLC or select an outfit.
- Base maximum health is 64; each story upgrade and each four paint pots adds 8.
  The game derives its maximum at load time. Checkpoint restoration can override
  current health.
- Statistics do not directly grant Steam achievements; some are updated by the
  game on its next save.

Close Alice before applying. Changes update the opened profile or configuration
directly, without creating an automatic backup.
