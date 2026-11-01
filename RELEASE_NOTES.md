# v0.53.0-alpha — WEBFISHING Add everything

WEBFISHING now has one **Add everything** button for supported acquisitions.

- After confirmation, stage one copy of each missing supported inventory item,
  unlock mapped cosmetics and lures, and add one unit of each empty saved bait
  type. Existing positive item and bait amounts are retained.
- Inspect all staged changes in **Review and save** before applying them.
  Confirmation alone does not write the save.
- Money, level, quests, journal records, selected equipment, rewards and unknown
  save entries are preserved. This action does not provide full game completion
  or unlock content outside the supported mappings.

The existing Windows release pipeline runs the automated tests, rebuilds the
portable executable and checks packaged resources before publishing. File-level
and interface checks do not establish successful loading of edited saves in-game.

Download **UniversalSaveEditor.exe** to open the portable app directly, or extract
the Windows ZIP first. Changes overwrite the opened save in its original location
and filename; the application does not create automatic save backups.
