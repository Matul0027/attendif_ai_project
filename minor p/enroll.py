# enroll.py
import cv2
import face_recognition
import sqlite3
import os
import numpy as np

# Create folders if not exist
os.makedirs("students", exist_ok=True)
os.makedirs("embeddings", exist_ok=True)
os.makedirs("database", exist_ok=True)

# Connect to database
conn = sqlite3.connect("database/students.db")
c = conn.cursor()

# Create students table
c.execute('''CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                roll TEXT UNIQUE,
                class_name TEXT,
                section TEXT
            )''')
conn.commit()

# Function to enroll student
def enroll_student(name, roll, class_name, section):
    # Capture image via webcam
    cap = cv2.VideoCapture(0)
    print("📸 Look at the camera. Press 's' to capture your face.")
    while True:
        ret, frame = cap.read()
        cv2.imshow("Enroll Student", frame)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('s'):  # Press 's' to save
            image_path = f"students/{roll}.jpg"
            cv2.imwrite(image_path, frame)
            break
    cap.release()
    cv2.destroyAllWindows()

    # Generate face encoding
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if len(encodings) == 0:
        print("⚠️ No face detected. Try again!")
        os.remove(image_path)
        return
    encoding = encodings[0]

    # Save embedding
    np.save(f"embeddings/{roll}.npy", encoding)

    # Insert into database
    try:
        c.execute("INSERT INTO students (name, roll, class_name, section) VALUES (?, ?, ?, ?)",
                  (name, roll, class_name, section))
        conn.commit()
        print(f"✅ Student {name} enrolled successfully!")
    except sqlite3.IntegrityError:
        print(f"⚠️ Roll {roll} already exists!")

# Example usage
if __name__ == "__main__":
    name = input("Enter student name: ")
    roll = input("Enter roll number: ")
    class_name = input("Enter class: ")
    section = input("Enter section: ")
    enroll_student(name, roll, class_name, section)
