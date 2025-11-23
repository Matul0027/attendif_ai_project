# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db_utils import verify_user, create_user

auth_bp = Blueprint("auth", __name__, template_folder="../templates")

def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            flash("Please login to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)
    return wrapper

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        if verify_user(username, password):
            session["user"] = username
            flash("Logged in successfully.", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials.", "danger")
            return redirect(url_for("auth.login"))
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out.", "info")
    return redirect(url_for("index"))

# Optional: register new admin (useful during dev)
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        ok, err = create_user(username, password)
        if ok:
            flash("User created.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash(f"Could not create user: {err}", "danger")
            return redirect(url_for("auth.register"))
    return render_template("register.html")
