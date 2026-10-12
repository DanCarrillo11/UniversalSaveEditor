# Changelog

## v0.17.0-alpha

- Add explicit compatibility evidence and scope for all 20 editors, separating PC file checks from gameplay confirmation.
- Replace raw opening/saving errors with explanations, next steps and a diagnostic-copy action; build reports from an allowlist that excludes personal identifiers and save contents.
- Add a previewable Help & details panel and optional local recent-save history with ten entries, last-record restoration, missing-file location, removal and clearing.
- Group Elden Ring inventory/storage goods by verified type, add 60 verified KH III material names and organize HD Remaster collections.
- Display verified RE2/RE3/RE4 Remake inventory IDs only when tied unambiguously to the same saved object; mark missing names explicitly without making identities writable.
- Preserve direct saving, field keys, limits, pending edits, format checks and byte preservation; add support/privacy, history, inventory-context and UI regression coverage.

## v0.16.1-alpha

- Fix the arbitrary Elden Ring revision-250 ceiling: allow the documented character layout through revision 261, while retaining descriptor, section, progression and fingerprint validation.
- Support the original minimum attributes of Idus Knight and Heavy Knight instead of rejecting their class IDs.
- Add regression coverage for mixed old/new character revisions, new class floors, unknown layouts and unknown future revisions; improve the unsupported-revision error message.
- Native revision-261 and in-game validation remain pending; synthetic tests are not represented as real game verification.

## v0.16.0-alpha

- Add experimental original Elden Ring Steam SL2 support with up to ten active characters and automatic save discovery.
- Edit runes, eight attributes, current vitals and supported existing goods in inventory/storage; retain item identities and carrying limits.
- Calculate level and lifetime runes automatically, synchronize character-menu summaries and affected player fingerprints, and maintain block MD5s.
- Bound every variable section and validate the descriptor table; preserve inactive slots, unrelated characters, account data, world state, regulation and opaque tail bytes.
- Add calculated read-only fields and show their automatic changes in review before direct saving.
- Include official Steam portrait artwork, three editor categories, regression coverage and documented public-PC validation; in-game verification remains pending.

## v0.15.0-alpha

- Add eight scoped experimental Resident Evil editors: HD Remaster, RE2, RE3, RE4 Remake, RE5, RE6, RE7 and Requiem.
- Implement bounded, independent Steam envelopes and a self-describing RE Engine reader with a small field whitelist; preserve unknown payload bytes and original account encryption.
- Authenticate encrypted blocks, retain padding and trailers, maintain file integrity, reject unsupported variants and restrict inventory counters to inventory save objects.
- Distinguish Requiem purchase availability from purchase/acquisition/received state; preserve uninitialized carry-over balances and RE6 emblem encodings.
- Add official Steam portraits, discovery, at most three editor categories and a general original-SteamID64 prompt for copied saves.
- Validate public RE5/RE6/HD PC profiles and nine native Requiem files in memory. Document console-only shared-payload checks and missing Steam/gameplay validation honestly.
- Add format, integrity, preservation, authentication and UI regression coverage; verify CityHash64 against Google's golden vectors and AES-OFB against NIST.
- Research RE0's native PC encryption and section table without exposing unverified gameplay fields.

## v0.14.0-alpha

- Add an initial experimental Resident Evil 4 (2005) Steam Ultimate HD adapter for record version 0x402.
- Edit 16 values per populated slot: Pesetas, mirrored saved difficulty, player/Ashley HP, save/round counters, and combat statistics.
- Maintain both slot CRCs, reject unknown records and invalid health relationships, and preserve account metadata, untouched slots and unrelated bytes.
- Add the official Steam portrait, automatic save discovery and Progress/Characters/Records navigation.
- Verify all four local slots in memory without changing the active save and add eleven editor/interface regression tests.
- Record the ten prioritized Resident Evil Steam editions and research boundaries. Other Resident Evil formats, inventory and unlocks are not claimed as supported by this release. In-game validation remains pending.

## v0.13.0-alpha

- Add accessible cover stars, a dedicated Favorites view, and favorites-first sorting within the chosen order and search filters.
- Remember favorite game IDs locally; starring a game does not open or change its save.
- Add interruptible 160 ms view fades and 140 ms cover highlights without zooming, cropping, or moving the cover art.
- Add a persistent Reduce motion option that immediately stops animations.
- Preserve keyboard focus, library scroll position, and pending edits while managing favorites and navigating views.
- Keep sidebar controls visible in compact windows and add six interface regression tests.

## v0.12.0-alpha

- Introduce a clean light/dark design with soft grouped surfaces, rounded controls and cover corners, blue actions and a persistent appearance toggle.

- Improve small-window layouts with a wrapping library toolbar, scrollable game details, and compact editor search/section controls.
- Add changed-only filtering, matching field counts, individual undo beside each field and in the change summary, including edits in other slots.
- Explain invalid values inline, normalize equivalent numeric input, and show accurate pending-change status and a modified window title.
- Separate format notes from integrity warnings and hide the slot selector for single-slot saves.
- Open detected saves directly from compact file rows showing size and modification time.
- Remember window geometry and the last folder locally; add Ctrl+S for review and improve keyboard focus and control labels.
- Batch unlock updates without rebuilding the summary for each individual field.
- Preserve direct saving and the existing game compatibility scope; add ten interface regression tests.

## v0.11.1-alpha

- Fix KH II Steam archives containing a 1 KB `KH2S` system record being rejected as an unexpected player record size.
- Preserve system metadata and its full reserved region while opening, editing and repairing player slots. Unknown or oversized records remain rejected.
- Verify against a local Steam save in memory and add regression checks for record ordering, byte preservation and system-only containers.

## v0.11.0-alpha

- Add experimental ReCoM editing: Moogle Points, XP, difficulty and named card quantities; maintain currency mirrors and both checksums.
- Add experimental BBS Final Mix editing: character progression, money, medals, attributes, existing commands and ability stacks. Preserve PC padding and deck references.
- Add experimental DDD HD editing: Sora/Riku progression, Drop Points, currency, difficulty and existing inventory quantities; maintain loading mirrors.
- Add experimental KH III PC editing with account-derived encryption, digest/CRC checks, party attributes and inventory acquisition flags.
- Add experimental Max Payne 1 inventory editing, bounded to original weapon IDs and ammunition capacities. Rebuild nested chunk lengths when values grow.
- Organize every new editor into at most three categories, add cover art and extend packaged-resource verification to AES.
- Expand automated checks to 91 tests. Game-load verification remains pending; KH 0.2 and Melody of Memory PC support remain unresolved.

## v0.10.2-alpha

- Fix Steam logos being cropped on screens with display scaling above 100%.
  Render SVG bounds in logical pixels and fit the image to its label.
- Add a rendering regression check for 100%, 125%, 150%, 175%, and 200% scale.

## v0.10.1-alpha

- Replace the status/save-count line below library covers with the Steam logo
  and platform name. Keep editor availability and save files in the details panel
  and card tooltip.
- Define platforms explicitly per game and use that metadata for the platform
  filter, ready for future verified platform support. Switch and PCSX2 support
  are not claimed by this release.
- Package the Steam SVG and validate its rendering in source and executable checks.

## v0.10.0-alpha

- Replace the long row of field-group tabs with up to three categories per game.
- KH I / KH II: Progress, Characters, Collection. Select Sora, Donald, or Goofy
  within Characters; KH II Drive Gauge and foldable Drive Forms belong to Sora.
- WEBFISHING: Progress, Equipment, Collection. Risk of Rain 2: Progress, Unlocks,
  Records. Alice: Progress, Character, Collection; configuration difficulty is
  grouped under Progress.
- Add section selectors, foldable sections, and fixed navigation/search controls
  above the field list. Batch actions affect only their own section.
- Group named KH II inventory entries; retain all other entries in their own
  section without changing the save parser or available fields.
- Preserve pending edits, the selected category/character, and search/fold state
  when switching slots or refreshing the editor. Hidden invalid edits still
  block saving and all pending edits remain in the review.
- Add navigation regression coverage and retain direct saving without backups.

## v0.9.0-alpha

- Apply edits directly to the opened file for every available editor, including
  Kingdom Hearts Final Mix and Kingdom Hearts II Final Mix.
- Keep the original filename and location; remove the export destination dialog
  and automatic backup creation from editing and restoration.
- Retain input validation, explicit integrity repair, checksum updates, verified
  atomic writes, and checks for changes made by the game while editing.
- Keep the selected KH slot after saving and refresh its values and CRC status.
- Update the interface and guide to describe direct saving without backups.
- Test direct KH CRC repair, slot preservation, cancellation, failed writes,
  concurrent game saves, and the absence of extra output files.

## v0.8.1-alpha

- Widen mode selectors so Final Mix (Standard) is displayed in full.
- Include all difficulty-editing features from v0.8.0-alpha.

## v0.8.0-alpha

- Add a difficulty selector per saved slot for Kingdom Hearts Final Mix and
  Kingdom Hearts II Final Mix on Steam.
- Support Beginner / Final Mix (Standard) / Proud in KH I, and
  Beginner / Standard / Proud / Critical in KH II.
- Preserve other slots, existing attributes and inventory; refresh the affected
  KH II record checksum and outer container CRC on export.
- Reject unsupported mode values; document that existing stats and starting
  bonuses are not recalculated and in-game validation remains pending.
- Test all modes, slot isolation, exact byte preservation, checksums and selectors.

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
