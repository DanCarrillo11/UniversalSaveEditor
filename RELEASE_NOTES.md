# v0.22.1-alpha — Fix flashing icon windows

- Fix the small empty windows flashing before the save editor opens. Original artwork labels are now attached to their field row before they become visible.
- Keep original game icons, live equipment previews, light/dark themes and view transitions.
- Add a regression test that observes actual window-show events while opening Kingdom Hearts II and Risk of Rain 2; the previous version reproduced the unwanted windows and the fix prevents them.

Save editing behavior and artwork coverage are unchanged. No saves are modified
by opening an editor or loading an image.

Download UniversalSaveEditor.exe under Assets and double-click it. Code > Download
ZIP also includes the updated portable executable; no installation is required.
