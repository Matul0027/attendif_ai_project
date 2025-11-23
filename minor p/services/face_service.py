"""
services/face_service.py
Handles face encoding, recognition, and attendance marking.
"""

import os
import cv2
import numpy as np
import face_recognition
import base64
from datetime import datetime
from PIL import Image
from io import BytesIO

from database.db_utils import get_db_connection


# === Helper: Load stored face encodings ===
def load_known_encodings():
    """
    Loads all stored encodings and metadata from the database.
    Returns: (encodings, rolls, names)
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT roll, name, encoding FROM students")
    rows = cur.fetchall()
    conn.close()

    encodings, rolls, names = [], [], []

    for roll, name, blob in rows:
        try:
            enc = np.frombuffer(blob, dtype=np.float64)
            encodings.append(enc)
            rolls.append(roll)
            names.append(name)
        except Exception:
            continue

    return encodings, rolls, names


# === Helper: Mark attendance once per day ===
def mark_attendance_once_per_day(roll, name):
    """
    Inserts a record into the attendance table if not already marked today.
    Returns True if marked, False if already marked.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT 1 FROM attendance WHERE roll = ? AND date = ?", (roll, today))
    exists = cur.fetchone()

    if not exists:
        cur.execute(
            "INSERT INTO attendance (roll, name, date, time) VALUES (?, ?, ?, ?)",
            (roll, name, today, datetime.now().strftime("%H:%M:%S")),
        )
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False


# === Encode face from base64 webcam image ===
def encode_face_from_base64(data_url):
    """
    Takes a base64 image string and returns a 128D face encoding or None.
    """
    try:
        # Decode base64 → bytes
        if data_url.startswith("data:"):
            _, encoded = data_url.split(",", 1)
        else:
            encoded = data_url

        img_bytes = base64.b64decode(encoded)
        pil_img = Image.open(BytesIO(img_bytes)).convert("RGB")  # ensure RGB mode
        img = np.array(pil_img)  # already RGB, no need for cv2.cvtColor()
    except Exception as e:
        print("❌ Error reading base64 image:", e)
        return None

    try:
        encodings = face_recognition.face_encodings(img)
        if len(encodings) == 0:
            print("⚠️ No face detected in the provided image.")
            return None
        return encodings[0]
    except Exception as e:
        print("❌ Face encoding error:", e)
        return None


# === Recognize faces from webcam frame (base64) ===
def recognize_faces_from_base64(data_url, tolerance=0.5):
    """
    Accepts a base64-encoded image from the frontend,
    detects faces, compares with known encodings,
    returns matches + bounding boxes for overlay.
    """
    try:
        if data_url.startswith("data:"):
            _, encoded = data_url.split(",", 1)
        else:
            encoded = data_url
        img_bytes = base64.b64decode(encoded)
    except Exception:
        return {"matches": [], "error": "Invalid image data."}

    try:
        pil_img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img = np.array(pil_img)
    except Exception:
        return {"matches": [], "error": "Could not read image."}

    # Detect faces
    face_locations = face_recognition.face_locations(img)
    face_encodings = face_recognition.face_encodings(img, face_locations)

    if not face_encodings:
        return {"matches": [], "error": None}

    known_encodings, known_rolls, known_names = load_known_encodings()
    if not known_encodings:
        return {"matches": [], "error": "No registered students found."}

    matches_output = []
    seen_rolls = set()

    for enc, loc in zip(face_encodings, face_locations):
        comparisons = face_recognition.compare_faces(known_encodings, enc, tolerance)
        distances = face_recognition.face_distance(known_encodings, enc)
        best_index = np.argmin(distances) if len(distances) > 0 else None

        if best_index is not None and comparisons[best_index]:
            roll = known_rolls[best_index]
            name = known_names[best_index]
            marked = False
            if roll not in seen_rolls:
                try:
                    marked = mark_attendance_once_per_day(roll, name)
                except Exception:
                    marked = False
                seen_rolls.add(roll)

            # Face box: (top, right, bottom, left)
            top, right, bottom, left = loc
            matches_output.append({
                "roll": roll,
                "name": name,
                "marked": marked,
                "box": [left, top, right, bottom]
            })
        else:
            top, right, bottom, left = loc
            matches_output.append({
                "roll": None,
                "name": "Unknown",
                "marked": False,
                "box": [left, top, right, bottom]
            })

    return {"matches": matches_output, "error": None}
