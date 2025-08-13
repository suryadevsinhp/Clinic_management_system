from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from ..extensions import login_manager
from ..models import verify_user_password, find_user_by_id, Roles

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@login_manager.user_loader
def load_user(user_id):
    return find_user_by_id(user_id)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = verify_user_password(username, password)
        if user:
            login_user(user)
            role = user.role
            if role == Roles.OWNER:
                return redirect(url_for("owner.dashboard"))
            if role == Roles.RECEPTION:
                return redirect(url_for("reception.dashboard"))
            if role == Roles.DOCTOR:
                return redirect(url_for("doctor.dashboard"))
            return redirect(url_for("auth.login"))
        flash("Invalid credentials", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))