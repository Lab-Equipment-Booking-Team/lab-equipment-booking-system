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
        from . import models  
        
        db.create_all()

        
        from .models import Equipment
        if not Equipment.query.first():
            e1 = Equipment(name="Microscope", category="Biology")
            e2 = Equipment(name="Centrifuge", category="Chemistry")
            e3 = Equipment(name="Oscilloscope", category="Physics")
            db.session.add_all([e1, e2, e3])
            db.session.commit()

    from .views import main as main_bp

    app.register_blueprint(main_bp)

    return app