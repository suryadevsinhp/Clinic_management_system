from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from ...extensions import mongo
from ...models import Roles

owner_bp = Blueprint("owner", __name__)


def _db():
    return mongo.cx.get_database(current_app.config["MONGODB_DB"])


@owner_bp.route("/dashboard")
@login_required
def dashboard():
    if getattr(current_user, "role", None) != Roles.OWNER:
        return render_template("errors/403.html"), 403
    db = _db()
    stats = {
        "patients": db["patients"].count_documents({}),
        "doctors": db["doctors"].count_documents({}),
        "appointments": db["appointments"].count_documents({}),
        "billing": db["billing"].count_documents({}),
    }
    return render_template("dashboards/owner_dashboard.html", stats=stats)