# routes/add_student.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db_utils import add_student
import numpy as np

add_student_bp = Blueprint("add_student_bp", __name__)

@add_student_bp.route("/add_student", methods=["GET", "POST"])
def add_student_page():
    if request.method == "POST":
        name = request.form.get("name")
        roll = request.form.get("roll")
        class_name = request.form.get("class_name")
        section = request.form.get("section")

        if not all([name, roll, class_name, section]):
            flash("⚠️ Please fill in all fields!", "warning")
            return redirect(url_for("add_student_bp.add_student_page"))

        # placeholder encoding (0s array until face added)
        encoding = np.zeros((128,), dtype=np.float64)
        success = add_student(name, roll, class_name, section, encoding)

        if success:
            flash(f"✅ Student '{name}' added successfully!", "success")
            return redirect(url_for("students_bp.students_list"))
        else:
            flash("⚠️ Roll number already exists or error occurred.", "danger")
            return redirect(url_for("add_student_bp.add_student_page"))

    return render_template("add_student.html")
