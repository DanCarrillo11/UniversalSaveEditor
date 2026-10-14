# Changelog

## v0.28.0-alpha — Faster editor loading

- Build large sections on demand, with bounded pages; preserve all field access, pending edits and whole-section actions.
- Index saved fields for validation/undo and reuse validated icon paths and bounded read-only archive indexes.
- Preserve the visible navigation, responsive attribute grids and original artwork while reducing initially constructed controls.
- Add a private local report for unexpected Python errors and disable saving until a save is reopened. Native crashes remain outside this reporter's coverage.
- Configure future publication as a normal GitHub Release; alpha naming still describes the development stage.

## v0.27.0-alpha — Clearer editor navigation

- Replace visible section dropdowns with a section list; choose party members with character buttons and remember each character's section.
- Search every category from the editor header, including fields outside the current section or character. Clearing search restores navigation; reopening a file clears stale searches.
- Replace the right-hand change panel with a fixed bottom action bar and a read-only pending-change dialog. Saving keeps the existing review, related-state synchronization and direct-file validation.
- Hide library navigation while editing, with a visible Library link; put compatibility notes, backup restoration and technical guidance under Save details. Integrity warnings stay visible.
- Polish light/dark selection, rounded panels, field hints and responsive attribute columns. Preserve all 21 adapters, original artwork, previews and paged large profiles.


## v0.26.0-alpha — Continue completing the existing games

- KH3: known magic tiers, Links, three shortcut sets, minigame scores/counters and saved statistics. Acquisition order is identified rather than assumed; matching shortcuts synchronize, unknown/duplicate commands are protected.
- ReCoM: known card/friend acquisition flags and monotonic completion flags. Adding mapped card quantities synchronizes acquisition; decks and unknown bits are preserved.
- KH1: four shared movement-ability entries. KH2: Donald/Goofy combat and ability-use preferences.
- Elden Ring: 263 mapped map visibility flags and increasing talisman capacity. Existing world state, equipment and unrelated character data remain unchanged.
- HD Remaster: 131 documented item identities for known replacements and the next clean empty item-box entry. Unknown ID 0x59 remains excluded.
- RE6: last-selected difficulty and uncompleted Mercenaries completion records, preserving existing nonzero encodings.
- RE2/RE3/RE4 Remake/RE7/Village/Requiem: additional existing acquisition, chapter, minigame, DLC and reward-claim statistics with exact types.
- Risk of Rain 2: preserve extreme unknown statistics without an integer-to-float overflow.
- Keep the catalogue at 21 games and defer icon work. Completion is measured per feature and evidence; no full-support claim.

## v0.25.1-alpha — Safer supplies and smoother editing

- KH1: synchronize level and difficulty with precisely identified save-menu snapshots; preserve currency, XP and unknown summary data.
- RE6: name recognized reserve ammunition and herbs, allow refilling depleted entries, and protect weapon/unknown count words from quantity editing.
- Search equipment by its currently selected item name while preserving pending edits and page changes.
- Give specific guidance for known conflicting edits without exposing paths or account IDs.
- Reject extreme numeric input normally instead of crashing validation.
- Refresh offline examples and the per-game coverage documentation; no new games or icons.

## v0.25.0-alpha — Equipment, cosmetics, unlocks and records

- Expand 17 existing editors; defer new games and icons while completing functionality.
- WEBFISHING: cosmetics/appearance/lures, known item creation and replacement, removal/reference cleanup, hotbar, item locks, quest progress and journal qualities.
- KH3: party equipment, active weapon, mapped acquisition and known learned/equipped abilities with bulk actions. KH1: magic availability. KH2: item auto-reload. BBS: Keyblades, finishers and existing deck references. DDD: Keyblades and existing spirit attributes.
- Elden Ring: 96 named appearance sliders per recognized character and saved deaths.
- HD Remaster: recognized gameplay sections, known item replacement/clearing and the next empty item-box entry. RE5: 45 figures. RE6: emblems, Mercenaries results and extra-mode skill slots.
- RE2/RE7: saved difficulty. RE2/RE3/RE4 Remake/RE7/Village/Requiem: additional existing unlock, completion, challenge and combat records with exact context/type checks.
- Risk of Rain 2: additional existing numeric statistics, full search/section filtering and 100-record pages for large profiles.
- Preserve unknown data, identities and original encryption; regenerate offline previews from synthetic fixtures. No personal saves are shipped.


## v0.24.0-alpha — Requiem gameplay expansion

- Add scoped player health and health-table upgrade levels with dependent maximum/current-health updates.
- Add existing inventory/item-box/storage stocks, 95 selected original item names, and 44 mapped attached-part tiers with ownership/reference checks.
- Preserve enemy state, backups, loaded ammunition, single objects, geometry and story data. Capacity tiers may only increase.
- Expand the offline preview and disable invalid/read-only real-save dropdown choices.
- Pause new game additions and document pending functionality/artwork for every current game. No full-support claim.

## v0.23.0-alpha — Browse editors without saves

- Open all 21 game editors without a save file or installation, with a clear preview banner and example categories/fields.
- Generate the offline preview catalogue from synthetic adapter fixtures; ship field metadata without saves, private data or writable offsets.
- Allow browsing example drop-down options without creating edits; block applying changes, backups and preview history entries.
- Restore normal controls when a real save is opened and retain the existing unsaved-change prompt.
- Show broad/partial/limited feature coverage in editor headers, library details and compatibility information. No full-support or gameplay guarantee is implied.

## v0.22.1-alpha — Fix flashing icon windows

- Fix small native windows flashing while opening an editor: icon labels now belong to their field row before visibility is set.
- Preserve existing artwork, equipment previews and view transitions.
- Add a regression check that monitors window-show events while opening Kingdom Hearts II and Risk of Rain 2.

## v0.22.0-alpha — Original artwork across game editors

- Extend original artwork to all six supported Kingdom Hearts editors, WEBFISHING, Risk of Rain 2, Resident Evil HD Remaster, RE3 Remake, RE5 and RE7.
- Show game resources beside recognized inventory entries, baits, cards, commands, unlocks and RE5 infinite-ammo flags.
- Update KH1/KH2 equipped-item images immediately when a dropdown changes or resets; use the actual saved equipment ID rather than the choice index.
- Add exact, read-only RE7 ItemDataID string lookup within the same serialized object; duplicate, invalid and unknown identities receive no substitute.
- Ship 3,155 verified artwork associations across 14 editors, with source references, hashes and explicit per-game coverage. Shared base card art does not imply premium-card appearance or a displayed card value.
- Keep original sprite pixels and game renders, with smaller aspect-preserving previews for large renders. No AI artwork, recoloring or runtime downloads.

Artwork remains pending for Alice, Max Payne, RE4 (2005), RE4 Remake, RE6, RE8
and RE9. Coverage within the other games is also scoped; unknown IDs stay as
text. This release improves presentation, not editing permissions or in-game
validation. See [artwork coverage and sources](docs/ITEM_ARTWORK.md).


## v0.21.0-alpha — Original Elden Ring item icons

- Add original artwork for the 307 goods and 487 base armaments already recognized by the Elden Ring editor.
- Show icons in inventory, storage, supported Add items controls and existing weapon upgrades.
- Preserve the base image across reinforcement and affinity variants; unknown IDs receive no guessed artwork.
- Copy archived image bytes unchanged into offline resource packs: no AI, redraw, recoloring or source upscaling.
- Verify every image, its source hash and the separate goods/weapon identity domains. Loading icons does not change save edit permissions.

This expands presentation for the existing scoped editor. It does not add weapon
creation, armor editing, quest changes or verified in-game loading. The original
artwork belongs to FromSoftware and Bandai Namco; metadata and source attribution
are recorded in [artwork coverage](docs/ITEM_ARTWORK.md).


## v0.20.0-alpha — Original inventory icons

- Display 27 original Resident Evil 2 Remake supply icons beside their names and quantities.
- Group mapped items into Ammunition, Healing, Supplies and Crafting materials.
- Use exact cropped game-atlas pixels, with no AI images, redraws or upscaled source assets.
- Keep unknown objects and other game editions in their existing text view; never guess an image from a matching number in another game.
- Preserve saved item identities, encryption, unknown data and existing edit behavior. Read-only fields now clearly say they are preserved.

This first collection covers healing items, ammunition and supplies in RE2
Remake. Weapons, quest items and artwork for other games remain pending.
Names and images do not establish in-game validation of the experimental Steam
adapter. The original atlas and coordinate table are attributed to their sources;
Capcom retains ownership of game artwork. See [coverage and sources](docs/ITEM_ARTWORK.md).


## v0.19.0-alpha — Resident Evil Village

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


## v0.18.0-alpha — Expanded party, equipment and inventory editors

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
