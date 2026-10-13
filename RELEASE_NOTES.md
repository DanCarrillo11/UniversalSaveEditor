# v0.25.1-alpha — Safer supplies and smoother editing

- KH1: synchronize level and difficulty with precisely identified save-menu snapshots; preserve currency, XP and unknown summary data.
- RE6: name recognized reserve ammunition and herbs, allow refilling depleted entries, and protect weapon/unknown count words from quantity editing.
- Search equipment by its currently selected item name while preserving pending edits and page changes.
- Give specific guidance for known conflicting edits without exposing paths or account IDs.
- Reject extreme numeric input normally instead of crashing validation.
- Refresh offline examples and the per-game coverage documentation; no new games or icons.

This alpha improves the current editors; it does not establish full support or
in-game verification for every game. RE6 reserve bounds are editor limits, not
verified game stack caps. KH1 summary synchronization requires an exact matching
archive entry; unidentified summary data remains untouched.

Download UniversalSaveEditor.exe under Assets and double-click it. The portable
executable is also included in Code > Download ZIP. Changes apply directly to
the opened save; no automatic backups are created.
