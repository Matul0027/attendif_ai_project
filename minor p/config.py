# config.py
import os

# -------------------------------------------------
# Base Directories
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
STUDENTS_DIR = os.path.join(BASE_DIR, "students")
EMBED_DIR = os.path.join(BASE_DIR, "embeddings")

# Ensure required folders exist
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(STUDENTS_DIR, exist_ok=True)
os.makedirs(EMBED_DIR, exist_ok=True)

# -------------------------------------------------
# Database Paths
# -------------------------------------------------
STUD_DB = os.path.join(DB_DIR, "students.db")
ATT_DB = os.path.join(DB_DIR, "attendance.db")

# -------------------------------------------------
# App Settings
# -------------------------------------------------
SECRET_KEY = "supersecretkey"

# -------------------------------------------------
# Face Recognition Settings
# -------------------------------------------------
FACE_TOLERANCE = 0.5  # lower = stricter match

# -------------------------------------------------
# Miscellaneous
# -------------------------------------------------
UPLOAD_FOLDER = STUDENTS_DIR
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
