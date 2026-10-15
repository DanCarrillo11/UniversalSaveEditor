# Updates from the application

The portable Windows application supports in-app updates starting with
**v0.33.0-alpha**. Older versions need one manual download from the
[official Releases page](https://github.com/DanCarrillo11/UniversalSaveEditor/releases/latest).
Open that executable normally; no installer or command line is needed.

## Updating

1. Open **Updates** in the header. The dialog checks the latest official release
   and displays its release notes as plain text.
2. Select **Download update**. A progress bar shows the download; the app checks
   its exact size and SHA-256 against the release checksum and available asset digest.
3. Select **Restart and update**. Resolve any unsaved edits first. The app closes,
   replaces its executable in the same folder and starts the new version.

Updates do not modify saves, favorites, appearance preferences or recent history.
The helper temporarily retains the previous **application executable** for recovery;
this does not create save-file backups. A synchronous replacement/restart failure
restores the old executable where possible. A successful new process cleans its
known temporary update files. Subsequent startup crashes are not automatically detected.

## Control and privacy

- Startup checks are **off by default**. Enable **Check for updates on startup**
  if desired; these checks are limited to once per 24 hours.
- Downloads and installation always require your action. Closing an active
  download cancels it. Editing saves works without an internet connection.
- Checks contact the official GitHub release API; downloads use HTTPS GitHub
  asset hosts. Save contents, paths and account information are not uploaded.
- Corrupt, truncated, oversized, incomplete or unexpected downloads are rejected.
  SHA-256 verifies download integrity; it is not an independent code signature.
- Connection failures and GitHub rate limits leave editing available. Retry later
  or use **Official releases**.
- If Windows denies replacing the executable, use **Open download folder**, close
  the app and replace the old executable manually. Administrator elevation is not requested.
  Verified downloads remain in that folder after closing; incomplete downloads
  are removed. You may delete a retained download after manual replacement.
- Source-code runs can check and download; automatic executable replacement is
  offered only by the packaged Windows app.

Implementation uses [Qt networking](https://doc.qt.io/qtforpython-6/PySide6/QtNetwork/QNetworkAccessManager.html)
and the [GitHub latest release API](https://docs.github.com/en/rest/releases/releases#get-the-latest-release).
