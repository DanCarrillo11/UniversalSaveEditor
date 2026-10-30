# v0.52.1-alpha — Documentation and presentation refresh

This maintenance release updates the project presentation and documentation.
There are no new save-editing features or game compatibility claims compared
with v0.52.0-alpha.

- Reorganized README with a clearer introduction, downloads, usage guidance,
  compatibility notes, and development information.
- Clarified the existing limitations and evidence for supported game formats.
- Kept instructions and warnings about direct, in-place save edits visible.

The Windows portable executable and ZIP are rebuilt from the current main
branch, with automated tests and packaged-app smoke checks in the release
workflow. Test results do not establish in-game compatibility.

**Important:** Edits overwrite the opened save in place. The app does not
create an automatic backup; make your own backup before applying changes.

Download `UniversalSaveEditor.exe` or the Windows ZIP from the release assets.
