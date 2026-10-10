# Changelog

## v0.7.0-alpha

First feature update after the consolidated alpha release.

- Replace Alice's guessed Teeth offset with a full revision-49 archive reader;
  the previous offset pointed to the Ruin-defeat statistic.
- Expand the persistent-profile editor to weapons, abilities, health, paint pots,
  dress abilities, memories, bottles, snouts, Radula rooms, completed chapters and
  difficulties, chapter select, enemy journal, cinematics, DLC flags, and statistics.
- Synchronize related weapon/ability state, pickup records, paint-pot totals,
  chapter flags, snout counters, and completion when affected.
- Add level selectors, category toggles, and field explanations.
- Discover the separate revision-16 GameConfig_PC.CFG archive and edit current
  and lowest-used difficulty while preserving settings, bindings, and UI records.
- Add automated checks for variable-size archives, new records, preservation,
  coupled fields, malformed saves, and the Alice UI.
- Keep Alice experimental; document the separate checkpoint format and
  pending in-game validation.

## v0.6.0-alpha

First consolidated preview release.

- Eight-game cover library with compact responsive cards, filters, and sorting.
- Five save editors: WEBFISHING, Risk of Rain 2, KH Final Mix, KH II Final Mix, and Alice: Madness Returns.
- Original cover art, including Kingdom Hearts images supplied by the author.
- Transparent memory-card application and executable icon.
- Search within every editor category without discarding pending changes.
- Change review, exact backups, atomic replacement, and export-copy validation.
- Backup manager and restore, preserving the current save before restoration.
- Correct manual opening and drag and drop for KH II and Alice profiles.
- Alice applies Teeth changes to its active profile after backing it up.
- Improved library resizing without horizontal scrolling or clipped cards.
- KH II internal checksum validation and explicit repair; unchanged saves are byte-identical.
- Experimental labels for KH II and Alice; pending entries remain clearly unavailable.
- 35 automated tests plus packaged-executable startup verification.
- Portable executable, ZIP, SHA-256 hash, and English release notes.
