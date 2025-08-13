from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from ...extensions import mongo
from ...models import Roles

reception_bp = Blueprint("reception", __name__)


def _db():
    return mongo.cx.get_database(current_app.config["MONGODB_DB"])


@reception_bp.route("/dashboard")
@login_required
def dashboard():
    if getattr(current_user, "role", None) != Roles.RECEPTION:
        return render_template("errors/403.html"), 403
    db = _db()
    apps = list(db["appointments"].find({}).sort("date", -1).limit(20))
    return render_template("dashboards/reception_dashboard.html", appointments=apps)