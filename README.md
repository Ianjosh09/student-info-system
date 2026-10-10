# Student Information System

A Python terminal application for managing student records with JSON storage.
GitHub account: **Ianjosh09**. Intended repository:
https://github.com/Ianjosh09/student-info-system

## Run locally

Install Python 3.10 or newer and open a terminal in this repository folder.

```bash
python -m src.main
```

On Windows, use `py -m src.main` if `python` is unavailable. No external Python
packages are needed. Run from the repository root, not from inside `src`.

## Features

- Add, view, update and delete records through a numbered menu.
- Store student ID, name, age, course, year level and email in JSON.
- Reject duplicate IDs (case-insensitive), invalid email formats and invalid ranges.
- Search by ID, name, course or email.
- Export CSV with protection against spreadsheet formula interpretation.
- Preserve the previous saved version and restore it with confirmation.
- Use rotating logs without storing names or email addresses in log messages.

Choose a menu number and follow the prompts. During update, leave a field blank
to keep its existing value. IDs cannot be changed. Deletion requires `YES`;
backup recovery requires `RESTORE`. Use menu 0 to exit.

## Repository structure

| Path | Purpose |
| --- | --- |
| src/main.py | Menu and user interaction |
| src/models/student.py | Record model and validation |
| src/services/student_service.py | CRUD, persistence, recovery, search and export |
| src/utils/config.py | Configuration loading |
| src/utils/logger.py | Rotating activity logs |
| config/config.json | External paths |
| data/students.json | Initial empty JSON dataset |
| logs/ | Runtime log directory |
| tests/test_students.py | Automated tests |
| .github/workflows/tests.yml | Tests on pushes and pull requests |
| requirements.txt | Standard-library-only dependency note |
| .gitignore | Excludes generated files |

## Configuration and cloud readiness

Edit `config/config.json`, or override it using `SIS_CONFIG`. The environment
variables `SIS_DATA_FILE`, `SIS_LOG_FILE` and `SIS_EXPORT_FILE` override paths.
Relative data/log/export paths resolve from the project root. An alternate
`SIS_CONFIG` relative path resolves from the terminal's working directory.

Separation of model, service and interface makes the application easier to move
to a server. On a cloud VM, use a persistent writable volume for data and backups.
GitHub hosts the source and runs tests; it does not host this interactive program.
GitHub Pages cannot run the Python menu. This project has no web server or cloud
database and does not claim that remote deployment has been completed.

## Storage, errors and recovery

Writes use a temporary file and atomic replacement. Before a successful change,
the previous valid data is copied to `data/students.json.bak`. The backup is one
version behind; restoring it can undo the latest change. Corrupt JSON is never
silently replaced with an empty dataset. Use menu 7 to restore a valid backup;
current content is retained in `students.json.before-restore`. A failed first
save has no older backup. Keep independent copies for longer-term protection.

Configuration and file permission problems produce readable errors. Logs rotate
at 200,000 bytes with three retained backups. Generated logs and exports are
ignored by Git. The initial JSON file is tracked: use fictional records only and
reset it to `[]` before publishing. Do not commit real student information.

## Tests

```bash
python -m unittest discover -s tests -v
```

The 12 tests cover CRUD and reload, duplicate IDs, invalid values and boundaries,
missing records, search, corruption, restore, missing data with an available
backup, failed writes, safe CSV export and invalid saved schemas. Tests use
isolated temporary directories. The supplied code passed all 12 tests locally
with Python 3.12. GitHub Actions is configured for Python 3.10 and 3.12; remote
results must be checked after pushing.

## GitHub workflow

Use `main` for the working application and `feature/tests-and-ci` for tests and
GitHub Actions. Commit related files together with descriptive messages. Open a
pull request, check its Actions result, then merge it. The accompanying upload
guide gives the commands. Commit history and hosted checks are created only when
you perform those steps in your GitHub account.

## Limitations

This is a classroom, single-user terminal application. It has no authentication,
role management, encryption or concurrent-write protection. It is not suitable
for production student records. Email validation checks format, not ownership.
