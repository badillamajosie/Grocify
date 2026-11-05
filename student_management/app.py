"""
Student Management System
=========================
A beginner-friendly Flask web application that keeps student records in a
plain JSON file (students.json) instead of a database.

How to run it:
    python app.py

Then open this address in your browser:
    http://127.0.0.1:5000/

The code is commented step by step so it is easy to follow.
"""

import json
import os
import re

from flask import Flask, flash, redirect, render_template, request, url_for

# ---------------------------------------------------------------------------
# 1. Basic application setup
# ---------------------------------------------------------------------------
app = Flask(__name__)

# Flask uses this secret key to sign "flash" messages (the little success and
# error notices). The fallback below is only for local learning; a public
# hosting service should set a SECRET_KEY environment variable instead, so the
# value never lives in the source code.
app.secret_key = os.environ.get("SECRET_KEY", "student-management-demo-secret-key")

# Build the path to students.json so the app works from any folder.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "students.json")

# Options used by the drop-down menus on the forms.
GENDERS = ["Male", "Female", "Other"]
YEAR_LEVELS = ["1st Year", "2nd Year", "3rd Year", "4th Year"]

# A small pattern for checking an email address: something@something.something
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


# ---------------------------------------------------------------------------
# 2. Helpers that read and write the JSON file
# ---------------------------------------------------------------------------
def load_students():
    """Return the list of students stored in students.json.

    If the file does not exist yet, or contains broken JSON, we return an
    empty list so the website still opens instead of crashing.
    """
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    # Only trust the file if it contains a list of records.
    return data if isinstance(data, list) else []


def save_students(students):
    """Write the full list of students back to students.json (pretty printed)."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(students, file, indent=2, ensure_ascii=False)
        file.write("\n")


# ---------------------------------------------------------------------------
# 3. Form validation
# ---------------------------------------------------------------------------
def validate_student(form, students, editing_id=None):
    """Check a submitted form.

    Returns two things:
        student -> a clean dictionary built from the form values
        errors  -> a list of error messages (empty when everything is valid)

    `editing_id` is the ID we are currently editing, so a student does not
    count as a duplicate of itself when saving an edit.
    """
    student = {
        "student_id": form.get("student_id", "").strip(),
        "full_name": form.get("full_name", "").strip(),
        "age": form.get("age", "").strip(),
        "gender": form.get("gender", "").strip(),
        "course": form.get("course", "").strip(),
        "year_level": form.get("year_level", "").strip(),
        "email": form.get("email", "").strip(),
    }

    errors = []

    # --- Student ID: required, simple characters only, and unique ----------
    if not student["student_id"]:
        errors.append("Student ID is required.")
    elif not re.fullmatch(r"[A-Za-z0-9\-]+", student["student_id"]):
        errors.append("Student ID may only contain letters, numbers and dashes.")
    else:
        for existing in students:
            # Skip the record we are editing (it is allowed to keep its ID).
            if editing_id is not None and existing.get("student_id") == editing_id:
                continue
            if existing.get("student_id", "").lower() == student["student_id"].lower():
                errors.append(
                    "Student ID " + student["student_id"] + " is already used by "
                    "another student. Please choose a different ID."
                )
                break

    # --- Full name: required ---------------------------------------------
    if not student["full_name"]:
        errors.append("Full name is required.")
    elif len(student["full_name"]) < 2:
        errors.append("Full name must be at least 2 characters long.")

    # --- Age: required, a whole number, and realistic ---------------------
    if not student["age"]:
        errors.append("Age is required.")
    elif not student["age"].isdigit():
        errors.append("Age must be a whole number (for example 20).")
    elif not 10 <= int(student["age"]) <= 100:
        errors.append("Age must be between 10 and 100.")
    else:
        # Store the age as a number, not as text.
        student["age"] = int(student["age"])

    # --- Gender: required and one of the allowed options ------------------
    if not student["gender"]:
        errors.append("Please select a gender.")
    elif student["gender"] not in GENDERS:
        errors.append("Please choose a valid gender option.")

    # --- Course: required -------------------------------------------------
    if not student["course"]:
        errors.append("Course is required.")

    # --- Year level: required and one of the allowed options --------------
    if not student["year_level"]:
        errors.append("Please select a year level.")
    elif student["year_level"] not in YEAR_LEVELS:
        errors.append("Please choose a valid year level.")

    # --- Email: required and must look like an email ----------------------
    if not student["email"]:
        errors.append("Email address is required.")
    elif not EMAIL_PATTERN.match(student["email"]):
        errors.append("Please enter a valid email address (example@school.edu).")

    return student, errors


# ---------------------------------------------------------------------------
# 4. Routes (the pages of the website)
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Dashboard: total number of students plus a few quick statistics."""
    students = load_students()

    # A "set" removes duplicates, so this counts unique courses / year levels.
    courses = {student.get("course", "") for student in students if student.get("course")}
    year_levels = {
        student.get("year_level", "") for student in students if student.get("year_level")
    }

    # Show the newest records first (we append new students to the end of the file).
    recent_students = list(reversed(students))[:5]

    return render_template(
        "index.html",
        total_students=len(students),
        total_courses=len(courses),
        total_year_levels=len(year_levels),
        recent_students=recent_students,
    )


@app.route("/students")
def students_page():
    """List every student, with an optional search.

    The search ignores upper/lower case and looks in the student ID, name,
    course, year level and email address, so one box finds a record however
    you remember it.
    """
    query = request.args.get("q", "").strip()
    students = load_students()

    if query:
        needle = query.lower()
        searchable_fields = ("student_id", "full_name", "course", "email", "year_level")
        students = [
            student
            for student in students
            if any(
                needle in str(student.get(field, "")).lower()
                for field in searchable_fields
            )
        ]

    return render_template("students.html", students=students, query=query)


@app.route("/add", methods=["GET", "POST"])
def add_student():
    """Show the add form (GET) and save a new student (POST)."""
    if request.method == "POST":
        students = load_students()
        student, errors = validate_student(request.form, students)

        if errors:
            # Show every problem, then send the form back with what was typed.
            for message in errors:
                flash(message, "error")
            return render_template(
                "add_student.html",
                form=request.form,
                genders=GENDERS,
                year_levels=YEAR_LEVELS,
            )

        # No errors: save the new student at the end of the list.
        students.append(student)
        save_students(students)
        flash(
            "Student " + student["full_name"] + " was added successfully.",
            "success",
        )
        return redirect(url_for("students_page"))

    # GET request: show an empty form.
    return render_template(
        "add_student.html",
        form={},
        genders=GENDERS,
        year_levels=YEAR_LEVELS,
    )


@app.route("/edit/<student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    """Show the edit form (GET) and save the changes (POST)."""
    students = load_students()

    # Find the student we want to edit.
    student = next(
        (item for item in students if item.get("student_id") == student_id), None
    )
    if student is None:
        flash("No student with ID " + student_id + " was found.", "error")
        return redirect(url_for("students_page"))

    if request.method == "POST":
        updated, errors = validate_student(
            request.form, students, editing_id=student_id
        )

        if errors:
            for message in errors:
                flash(message, "error")
            return render_template(
                "edit_student.html",
                form=request.form,
                student=student,
                genders=GENDERS,
                year_levels=YEAR_LEVELS,
            )

        # Replace the old record with the updated one. The form may hold a
        # corrected student ID, so `updated` can have a different ID than the
        # one in the URL; the duplicate check above already made sure the new
        # ID is not used by another student.
        for index, item in enumerate(students):
            if item.get("student_id") == student_id:
                students[index] = updated
                break

        save_students(students)
        flash(
            "Student " + updated["full_name"] + " was updated successfully.",
            "success",
        )
        return redirect(url_for("students_page"))

    # GET request: pre-fill the form with the current values.
    return render_template(
        "edit_student.html",
        form=student,
        student=student,
        genders=GENDERS,
        year_levels=YEAR_LEVELS,
    )


# There is deliberately no delete route. Once a student is added, the record
# stays in students.json; you can correct details with the edit form instead.


# ---------------------------------------------------------------------------
# 5. Start the development server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # PORT lets a hosting service choose the port. Locally it stays 5000.
    port = int(os.environ.get("PORT", 5000))

    # host="0.0.0.0" allows the app to be reached from outside this machine
    # (for example through a preview link). Use 127.0.0.1 for local only.
    # Set FLASK_DEBUG=1 to auto-reload the page whenever you edit the code.
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"

    app.run(host="0.0.0.0", port=port, debug=debug)
