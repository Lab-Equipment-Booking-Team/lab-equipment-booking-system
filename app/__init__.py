from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

# Create Flask app
app = Flask(__name__)

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lab_booking.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "dev-secret-key"

    db.init_app(app)
    
   
    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    from .views import main as main_bp
    app.register_blueprint(main_bp)

    return app
