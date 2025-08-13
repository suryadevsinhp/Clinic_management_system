import os
from flask import Flask
from .config import Config
from .extensions import mongo, login_manager
from .auth.routes import auth_bp
from .roles.owner.routes import owner_bp
from .roles.reception.routes import reception_bp
from .roles.doctor.routes import doctor_bp


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config())

    # Init extensions
    mongo.init_app(app)
    login_manager.init_app(app)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(owner_bp, url_prefix="/owner")
    app.register_blueprint(reception_bp, url_prefix="/reception")
    app.register_blueprint(doctor_bp, url_prefix="/doctor")

    @app.route("/")
    def index():
        return "Clinic Management (Flask) is running"

    return app