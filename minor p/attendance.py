# attendance.py
import cv2, os, sqlite3
import numpy as np
import face_recognition
from datetime import datetime

STUD_DB = "database/students.db"
ATT_DB = "database/attendance.db"
STUDENTS_DIR = "students"
EMBED_DIR = "embeddings"


def mark_attendance_with_camera():
    known_encodings = []
    known_rolls = []
    known_names = []

    # Load all known faces
    conn = sqlite3.connect(STUD_DB)
    c = conn.cursor()
    c.execute("SELECT name, roll FROM students")
    for name, roll in c.fetchall():
        path = os.path.join(EMBED_DIR, f"{roll}.npy")
        if os.path.exists(path):
            known_encodings.append(np.load(path))
            known_rolls.append(roll)
            known_names.append(name)
    conn.close()

    cap = cv2.VideoCapture(0)
    print("📸 Attendance marking started. Press 'q' to stop.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.45)
            face_distances = face_recognition.face_distance(known_encodings, encoding)
            best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else None

            if best_match_index is not None and matches[best_match_index]:
                name = known_names[best_match_index]
                roll = known_rolls[best_match_index]
                mark_attendance(name, roll)

        cv2.imshow("Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def mark_attendance(name, roll):
    conn = sqlite3.connect(ATT_DB)
    c = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")

    c.execute("SELECT * FROM attendance WHERE roll=? AND date=?", (roll, date))
    exists = c.fetchone()
    if not exists:
        c.execute("INSERT INTO attendance (roll, name, date, time) VALUES (?, ?, ?, ?)",
                  (roll, name, date, time))
        conn.commit()
        print(f"✅ Marked {name} ({roll}) present at {time}")

    conn.close()
