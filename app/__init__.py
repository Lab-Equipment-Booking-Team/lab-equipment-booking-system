from flask import Flask


def create_app():
  app = Flask(__name__)

  app.config['SECRET_KEY'] = 'your-secret-key-here'

  # Register Blueprints
  from app.views import bp as main_bp

  app.register_blueprint(main_bp)

  return app