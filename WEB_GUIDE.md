# Student Information System website

This optional web interface adds forms, buttons, search, year filters, CSV export,
JSON download/import and one-step undo to the existing Python assignment.

## How it works

GitHub Pages serves `index.html` and the files inside `web/`. JavaScript runs in
the visitor's browser. Records are serialized as JSON in localStorage, separately
for each browser and site origin. They remain after refresh when browser storage
is enabled, but clearing site data removes them. Private browsing may discard
them. Download JSON backups to keep independent copies.

This is not a hosted Python backend or a shared cloud database. The Python app
continues to run with `python -m src.main` and uses `data/students.json`. You can
import a Python-format JSON file through the web interface. To move web records
back to Python, first close the Python app and back up its data file, then replace
`data/students.json` with the downloaded web JSON file. Use fictional information.
The browser interface has no authentication and is intended for a classroom demo.

## Files to add to the EXISTING repository

- `index.html` at the repository root, next to README.md
- `web/` (keep every file inside it)
- `WEB_GUIDE.md`

Do not replace or remove `src`, `tests`, `config`, `data`, `.github`, or `.git`.
Do not upload the ZIP itself. Do not place index.html inside a second enclosing
folder. Python dependencies and tests are unchanged.

## Preview locally

Open your existing project folder in VS Code. Run:

    python -m http.server 8000 --bind 127.0.0.1

Open http://localhost:8000 in your browser. Use Ctrl+C to stop the preview.
Do not double-click index.html because its JavaScript modules need HTTP hosting.
Only start this temporary development server from a folder containing class demo
files. Binding to 127.0.0.1 limits access to your own computer.

## Upload the addition

In the existing VS Code project terminal, with the preview stopped:

    git switch main
    git pull --ff-only
    git add index.html web WEB_GUIDE.md
    git commit -m "Add browser interface for student records"
    git push origin main

If this terminal no longer recognizes Git, run this PowerShell command first:

    $env:Path += ";C:\Program Files\Git\cmd"

## GitHub Pages

In the repository, open Settings > Pages. For branch publishing, use Deploy from
a branch, branch main, folder / (root), then Save. If it is already set that way,
leave the setting alone. Wait for the Pages deployment to finish in Actions.
Then open https://ianjosh09.github.io/student-info-system/ and refresh with
Ctrl+F5 if the old README is cached. A root index.html is the website entry page.
The README remains available on the repository's Code tab.

## Verify before submission

Add a fictional student, refresh the page, edit it, search, download JSON and CSV,
delete it and undo. Try importing the downloaded JSON. Confirm the live Actions
Pages deployment succeeded. The new website files have not been uploaded merely
by downloading this package; perform the git commands above.

## Submission

Keep the repository link required by the assignment:
https://github.com/Ianjosh09/student-info-system

After the website is live, optionally add a second link labelled Web interface:
https://ianjosh09.github.io/student-info-system/

Describe the website as a browser-storage demo and the Python application as the
JSON-file implementation. Do not claim that the website runs the Python backend.
