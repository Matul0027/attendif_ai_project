# routes/attendance_list.py
from flask import Blueprint, render_template
import sqlite3
from config import ATT_DB

attendance_list_bp = Blueprint("attendance_list_bp", __name__)

@attendance_list_bp.route("/attendance_list")
def view_attendance_list():
    """Display all attendance records from the database."""
    conn = sqlite3.connect(ATT_DB)
    c = conn.cursor()
    c.execute("SELECT id, roll, name, date, time FROM attendance ORDER BY date DESC, time DESC")
    records = c.fetchall()
    conn.close()
    return render_template("attendance_list.html", records=records)
