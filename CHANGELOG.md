# Changelog

## 0.5

- Added a manager for 454 Risk of Rain 2 unlock identifiers discovered in the installed content catalog: characters, skills, skins and recolors, artifacts, items, logs, and Newt Altars.
- Added checkboxes, search, and actions to unlock or restore complete categories.
- Unlock entries are added or removed without reserializing the rest of the XML profile.
- Expanded the automated suite to 22 tests, including bulk unlock editing on a copy of a real profile.
- Translated the application, documentation, field labels, validation messages, and repository-facing text to English.

## 0.4

- Added initial Risk of Rain 2 XML profile support for Lunar Coins and progress, combat, and economy statistics, including automatic discovery, backups, and safe replacement.
- Added the transparent memory-card icon to the application and Windows executable.
- WEBFISHING now updates `bait_unlocked` automatically when a positive bait quantity is selected.
- WEBFISHING applies changes to the active save slot with an exact backup and atomic replacement instead of creating an `.edited.sav` file.
- Standardized the UniversalSaveEditor name across the window, navigation, guide, and executable.
- Added seven sourced original covers.
- Expanded WEBFISHING progress, upgrades, existing inventory, and journal editing.
- Expanded Kingdom Hearts Final Mix editing to 154 named items and current HP/MP.
- Added decimal type preservation, output verification, and portable PyInstaller distribution.

## 0.2 — PySide6 interface

- Replaced the Tkinter interface with a Qt Widgets application.
- Added a six-game library with explicit availability and two implemented editors.
- Added original vector card artwork, search, filters, and collection navigation.
- Added categorized editing, a live change summary, modified-field styling, and visible errors.
- Preserved pending edits when moving between tabs, records, and sections.
- Added change review, backup export, external source-change detection, an integrated guide, drag and drop, and keyboard shortcuts.

## 0.1 — Functional foundation

- Added WEBFISHING and Kingdom Hearts Final Mix Steam readers.
- Added targeted field editing, backups, and integrity validation.
