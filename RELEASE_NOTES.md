# v0.38.0-alpha — RDR2 camp, horses and saved history

This update expands the existing RDR2 PC Story Mode editor:

- **Camp funds:** edit dollars and cents; the ledger balance and its saved
  statistic change together when both are unique and agree.
- **Horses:** health and stamina cores for recognized existing horse slots.
  Bonding XP now updates both inventory and script copies, matched by SlotId.
  Unknown slots, absent models and disagreeing XP values are protected.
- **Statistics:** 17 existing history counters, including kills, headshots,
  deaths, horse sales, stable visits, baths and item use.
- **Compendium history:** horse breaking/highest recorded bonding, gang
  encounter counters and fish caught per existing bait/lure record.

History and compendium records do not deliver items, rewards, challenge
completion or platform achievements. Recorded bonding history is separate from
an existing horse's actual progression. Many compendium species/breed names
remain unidentified and display their hashes rather than guessed labels.

Three native encrypted PC files passed all editable-field changes in memory,
all ten payload checks, exact-span comparisons and byte-identical restoration.
Personal originals were unchanged. Synthetic cases cover camp/horse mismatch,
unknown slots, malformed schemas/counts, duplicate statistics, foreign
namespaces, fishing-array bounds/aliasing, previews and staged UI edits.

**RDR2 remains Limited coverage.** Edited-save loading/persistence in the game
has not been verified. Item/weapon/clothing acquisition, components, stable
management, full named compendium identities, regional bounty dependencies and
story/challenge/reward delivery still need mapping. No full-support claim is
made. See docs/RDR2_FIELDS.md for exact scope and unresolved dependencies.

Download UniversalSaveEditor.exe under Assets and double-click it, or use
Updates > Restart and update. The portable executable is also included in
Code > Download ZIP. Apply replaces the opened file directly; no automatic save
backup or .edited output is created.
