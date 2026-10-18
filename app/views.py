from flask import Blueprint, render_template

# Create Blueprint
bp = Blueprint('main', __name__)

# Home page route
@bp.route('/')
def index():
    return render_template('index.html')

# Login page route
@bp.route('/login')
def login():
    return render_template('login.html')

# Register page route
@bp.route('/register')
def register():
    return render_template('register.html')

print("Blueprint routes loaded")
