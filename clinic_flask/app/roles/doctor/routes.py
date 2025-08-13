from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from ...extensions import mongo
from ...models import Roles
from bson import ObjectId

doctor_bp = Blueprint("doctor", __name__)


def _db():
    return mongo.cx.get_database(current_app.config["MONGODB_DB"])


@doctor_bp.route("/dashboard")
@login_required
def dashboard():
    if getattr(current_user, "role", None) != Roles.DOCTOR:
        return render_template("errors/403.html"), 403
    db = _db()
    query = {}
    if getattr(current_user, "doctor_id", None):
        try:
            query = {"doctor_id": ObjectId(current_user.doctor_id)}
        except Exception:
            query = {"doctor_id": current_user.doctor_id}
    apps = list(db["appointments"].find(query).sort("date", -1))
    return render_template("dashboards/doctor_dashboard.html", appointments=apps)