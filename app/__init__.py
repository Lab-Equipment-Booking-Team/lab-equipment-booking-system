from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lab_booking.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "dev-secret-key"

    db.init_app(app)

    with app.app_context():
        # app.models වල තියෙන Models ටික Load කරගැනීමට:
        from . import models  # noqa: F401

        db.create_all()

    # Views/Routes Register කිරීම:
    from .views import main as main_bp

    app.register_blueprint(main_bp)

    return app