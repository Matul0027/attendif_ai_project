# app.py
from flask import Flask, render_template
import os

# -------------------------------------------------
# Create Required Project Directories
# -------------------------------------------------
os.makedirs("database", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# -------------------------------------------------
# Flask App Initialization
# -------------------------------------------------
app = Flask(__name__)
app.secret_key = "supersecretkey"

# -------------------------------------------------
# Initialize Databases Before Routes
# -------------------------------------------------
from database.db_utils import init_databases
init_databases()

# -------------------------------------------------
# Blueprints Import (AFTER DB INIT)
# -------------------------------------------------
from routes.enroll import enroll_bp
from routes.attendance import attendance_bp
from routes.students import students_bp
from routes.attendance_list import attendance_list_bp
from routes.add_student import add_student_bp

# -------------------------------------------------
# Register Blueprints
# -------------------------------------------------
app.register_blueprint(enroll_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(students_bp)
app.register_blueprint(attendance_list_bp)
app.register_blueprint(add_student_bp)

# -------------------------------------------------
# Home Route
# -------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -------------------------------------------------
# Run Flask
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
