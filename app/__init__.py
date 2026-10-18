from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lab_booking.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)


    with app.app_context():
        import app.models  # noqa: F401

        db.create_all()

    # Import routes/views inside to avoid circular imports
    from app.views import main as main_bp

    app.register_blueprint(main_bp)

    return app
