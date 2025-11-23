from flask import Blueprint, render_template, request, jsonify
from services.face_service import recognize_faces_from_base64

attendance_bp = Blueprint("attendance_bp", __name__)

# ---------- Web Page ----------
@attendance_bp.route("/attendance")
def attendance_page():
    return render_template("attendance.html")


# ---------- Face Recognition API ----------
@attendance_bp.route("/attendance/recognize", methods=["POST"])
def recognize_faces():
    """
    Receives a Base64 image from the browser (AJAX)
    and returns JSON with bounding boxes + names.
    """
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "No image provided."}), 400

    result = recognize_faces_from_base64(data["image"])
    return jsonify(result)
