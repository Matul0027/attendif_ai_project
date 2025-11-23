# database/db_utils.py
import sqlite3
import os
import numpy as np

# ---------- Absolute Paths ----------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(BASE_DIR, "database")

STUD_DB = os.path.join(DB_DIR, "students.db")
ATT_DB = os.path.join(DB_DIR, "attendance.db")

os.makedirs(DB_DIR, exist_ok=True)


# ---------- Safe Connection (Windows-Safe, No Delete) ----------
def safe_connect(db_path):
    """Connect to SQLite DB and auto-fix corruption safely on Windows."""
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Run integrity check
        cur.execute("PRAGMA integrity_check;")
        result = cur.fetchone()

        # If corrupted
        if result[0] != "ok":
            print(f"⚠️ Corruption detected in: {db_path}")

            # Close BEFORE renaming
            conn.close()

            corrupted_path = db_path + ".corrupted"

            # Rename instead of delete (Windows safe)
            if os.path.exists(db_path):
                # remove old backup if exists
                if os.path.exists(corrupted_path):
                    os.remove(corrupted_path)
                os.rename(db_path, corrupted_path)

            print("🔄 Created backup:", corrupted_path)
            print("🆕 Creating new database...")

            return sqlite3.connect(db_path)

        return conn

    except Exception as e:
        print(f"❌ Fatal DB error: {e}")

        corrupted_path = db_path + ".corrupted"

        # Attempt to close and rename
        try:
            conn.close()
        except:
            pass

        if os.path.exists(db_path):
            if os.path.exists(corrupted_path):
                os.remove(corrupted_path)
            os.rename(db_path, corrupted_path)

        print("🔄 DB renamed due to corruption →", corrupted_path)
        print("🆕 Creating new database...")

        return sqlite3.connect(db_path)


# ---------- Get DB Connection ----------
def get_db_connection(db_name="students"):
    db_path = STUD_DB if db_name == "students" else ATT_DB
    return safe_connect(db_path)


# ---------- Initialize Databases ----------
def init_databases():
    """Create tables safely."""
    # Students DB init
    conn = safe_connect(STUD_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll TEXT UNIQUE,
            class_name TEXT,
            section TEXT,
            encoding BLOB
        )
    """)
    conn.commit()
    conn.close()

    # Attendance DB init
    conn = safe_connect(ATT_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll TEXT,
            name TEXT,
            date TEXT,
            time TEXT
        )
    """)
    conn.commit()
    conn.close()

    print("✅ Databases initialized at:", DB_DIR)


# ---------- Add Student ----------
def add_student(name, roll, class_name, section, encoding):
    conn = get_db_connection("students")
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO students (name, roll, class_name, section, encoding) VALUES (?, ?, ?, ?, ?)",
            (name, roll, class_name, section, encoding.tobytes()),
        )
        conn.commit()
        print(f"✅ Added student: {name} (Roll: {roll})")
        success = True
    except sqlite3.IntegrityError:
        print(f"⚠️ Roll number '{roll}' already exists.")
        success = False
    except Exception as e:
        print("❌ Error adding student:", e)
        success = False
    finally:
        conn.close()
    return success


# ---------- Get Students ----------
def get_students():
    conn = get_db_connection("students")
    c = conn.cursor()
    c.execute("SELECT id, name, roll, class_name, section FROM students ORDER BY id ASC")
    data = c.fetchall()
    conn.close()
    return data


# Alias
def get_all_students():
    return get_students()


# ---------- Mark Attendance ----------
def mark_attendance(roll, name, date, time):
    conn = get_db_connection("attendance")
    c = conn.cursor()
    c.execute(
        "INSERT INTO attendance (roll, name, date, time) VALUES (?, ?, ?, ?)",
        (roll, name, date, time),
    )
    conn.commit()
    conn.close()
