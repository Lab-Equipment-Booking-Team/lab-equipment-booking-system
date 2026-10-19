from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/lab_booking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Blueprints Import & Register 
    from app.auth import auth_bp
    from app.bookings import bookings_bp
    from app.equipment import equipment_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(bookings_bp, url_prefix='/bookings')
    app.register_blueprint(equipment_bp, url_prefix='/equipment')

    @app.route("/")
    def home():
        return "Lab Equipment Booking System is running!"

    return app