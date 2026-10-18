from flask import Flask

# Create Flask app
app = Flask(__name__)

# Import Blueprint from views.py
from app.views import bp

# Register Blueprint
app.register_blueprint(bp)
