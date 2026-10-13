# v0.26.0-alpha — Continue completing the existing games

- KH3: known magic tiers, Links, three shortcut sets, minigame scores/counters and saved statistics. Acquisition order is identified rather than assumed; matching shortcuts synchronize, unknown/duplicate commands are protected.
- ReCoM: known card/friend acquisition flags and monotonic completion flags. Adding mapped card quantities synchronizes acquisition; decks and unknown bits are preserved.
- KH1: four shared movement-ability entries. KH2: Donald/Goofy combat and ability-use preferences.
- Elden Ring: 263 mapped map visibility flags and increasing talisman capacity. Existing world state, equipment and unrelated character data remain unchanged.
- HD Remaster: 131 documented item identities for known replacements and the next clean empty item-box entry. Unknown ID 0x59 remains excluded.
- RE6: last-selected difficulty and uncompleted Mercenaries completion records, preserving existing nonzero encodings.
- RE2/RE3/RE4 Remake/RE7/Village/Requiem: additional existing acquisition, chapter, minigame, DLC and reward-claim statistics with exact types.
- Risk of Rain 2: preserve extreme unknown statistics without an integer-to-float overflow.
- Keep the catalogue at 21 games and defer icon work. Completion is measured per feature and evidence; no full-support claim.

This release continues the existing-game completion work. It does **not** mean
that all games are complete. File preservation, adapter round trips and synthetic
tests are separate from successful in-game loading. Acquisition/completion flags
do not universally grant rewards, CP/HP, story progress, DLC or achievements.
See the completion plan and current functionality/evidence notes.

Download UniversalSaveEditor.exe under Assets. The executable is portable and
also included in Code > Download ZIP. Changes apply directly to the opened file;
no automatic backups are created.
