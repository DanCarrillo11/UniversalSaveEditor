# Contributing to UniversalSaveEditor

Thanks for helping make save editing easier. Useful contributions include game
format research, reproducible bug reports, interface improvements, tests, and
documentation.

## Report a problem or request a game

Use the templates in [Issues](https://github.com/DanCarrillo11/UniversalSaveEditor/issues/new/choose).
Include the application version, game edition and platform, steps to reproduce,
and expected versus actual behavior. For display problems, include Windows
display scaling and the window size.

Personal saves may contain player names, account IDs, and other private data.
Use screenshots with personal details removed and synthetic examples where possible.
Check existing issues before opening a new report.

## Set up development on Windows

Use Python 3.12 or 3.14 and a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Run the existing checks:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

To build the portable executable:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm UniversalSaveEditor.spec
```

The build is created in `dist/`. Generated files and personal saves should not
be included in a source pull request.

## Submit a focused pull request

1. Fork the repository and create a branch from `main`.
2. Make one independently useful change.
3. Explain the problem, resulting behavior, and how you checked it.
4. Open a pull request against `main` and wait for the automated checks.

Keep application text and repository documentation in English. For shared work,
credit actual contributors with Git's `Co-authored-by` trailer using an email
associated with their GitHub account.

## Adding or extending an editor

- Map the save format from evidence and record sources and scope in `SOURCES.md`
  and the relevant file in `docs/`.
- Use synthetic fixtures for meaningful parsing and editing regression tests.
- Preserve unrelated bytes or records and update required checksums.
- Keep direct saving compatible with existing concurrent-write checks.
- Set limits and validation for every editable field.
- Expose only fields that the parser and writer can support. Keep unverified
  games or platforms out of compatibility claims.
- Organize controls with the existing game-specific categories and sections.
- Separate automated validation from checks performed in the actual game.

See [README.md](README.md) for compatibility, current limitations, and licensing.
