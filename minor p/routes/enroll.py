# routes/enroll.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
import numpy as np
import face_recognition
import cv2
import base64
from io import BytesIO
from PIL import Image

from database.db_utils import add_student
from services.face_service import encode_face_from_base64

enroll_bp = Blueprint("enroll", __name__, url_prefix="/enroll")


@enroll_bp.route("/", methods=["GET", "POST"])
def enroll_student():
    if request.method == "POST":
        name = request.form.get("name")
        roll = request.form.get("roll")
        class_name = request.form.get("class_name")
        section = request.form.get("section")
        image_data = request.form.get("image_data")  # from webcam (base64)

        # Check all fields
        if not all([name, roll, class_name, section, image_data]):
            flash("⚠️ Please fill all fields and capture a photo!", "warning")
            return redirect(url_for("enroll.enroll_student"))

        # Encode face from base64 data
        encoding = encode_face_from_base64(image_data)
        if encoding is None:
            flash("❌ No face detected. Try again.", "danger")
            return redirect(url_for("enroll.enroll_student"))

        # Save to database
        success = add_student(name, roll, class_name, section, encoding)
        if success:
            flash(f"✅ {name} enrolled successfully!", "success")
        else:
            flash("⚠️ Roll number already exists!", "danger")

        return redirect(url_for("enroll.enroll_student"))

    return render_template("enroll.html")
