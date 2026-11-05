# Student Management System

A beginner-friendly Flask app for keeping student records. Data is stored in
`students.json`, so there is no database to install or configure.

## What it does

- Dashboard with the total number of students, courses and year levels
- Add students with validation (required fields, valid age and email)
- View all records in a table
- Search by full name or student ID
- Edit a student (the student ID stays the same)
- Records cannot be deleted in the app: once a student is added, they stay
- Duplicate student IDs are rejected
- Success and error messages after every action

## Project files

```
student_management/
├── app.py                  # All Flask routes and validation
├── students.json           # The "database" (a list of student records)
├── requirements.txt        # Python packages
├── Procfile                # Start command for hosting services
├── templates/
│   ├── base.html           # Shared layout, navigation, flash messages
│   ├── index.html          # Dashboard
│   ├── add_student.html    # Add form
│   ├── students.html       # Records table + search
│   └── edit_student.html   # Edit form
└── static/
    └── style.css           # Blue-and-white responsive design
```

## Run it locally

```bash
cd student_management
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000/** in your browser.

The app listens on port 5000 by default. To use another port:

```bash
PORT=5001 python app.py           # Windows: set PORT=5001 && python app.py
```

Set `FLASK_DEBUG=1` if you want the page to reload automatically while you edit
the code.

## Where the data lives

Every add and edit rewrites `students.json`. You can open that file in any text
editor to see the records. If you delete the file, the app starts with an empty
list (a new file is created the next time you save a student).

The web app has no delete button or delete route, so a saved student cannot be
removed through the site. If you ever need to remove one by hand, edit
`students.json` while the app is stopped.

## Deploying it publicly (optional)

The local address `http://127.0.0.1:5000/` only works on your own computer.
To let other people use the app you need to host it somewhere. Free options:

- **Render** (free web service): the repository includes a `render.yaml`
  Blueprint, so use New + -> Blueprint in Render, pick the repository and apply.
  It sets the root directory to `student_management`, runs
  `pip install -r requirements.txt`, starts `gunicorn app:app`, and generates a
  `SECRET_KEY`. A manual Web Service works too with those same commands; the
  `Procfile` also works. Render sets `$PORT` automatically and the app reads it.
- **PythonAnywhere** (free tier): upload the folder, create a Flask web app, and
  point its WSGI file at `app`.

Important: on Render's free tier the filesystem is temporary, so new students
saved there can disappear when the service restarts or redeploys. For lasting
public data you would use a real database instead of a JSON file.

## Notes for learning

- `app.py` is heavily commented - start with `load_students()` and
  `validate_student()`.
- The templates use Jinja2, Flask's template language (`{% ... %}` and `{{ ... }}`).
- `app.secret_key` signs flash messages. It is read from the `SECRET_KEY`
  environment variable when present; the hard-coded fallback is only for local
  learning, so keep the real value out of source control.
