# routes/students.py
from flask import Blueprint, render_template
from database.db_utils import get_all_students

students_bp = Blueprint("students_bp", __name__)

@students_bp.route("/students")
def students_list():
    """Display all registered students."""
    students = get_all_students()
    return render_template("students.html", students=students)
