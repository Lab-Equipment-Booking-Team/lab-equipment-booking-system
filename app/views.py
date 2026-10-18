<<<<<<< HEAD
from flask import Blueprint, render_template, request, redirect, url_for, flash

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('main.index'))
    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return redirect(url_for('main.login'))
    return render_template('register.html')
=======
from flask import current_app as app, render_template

@app.route('/')
def index():
    return render_template('index.html')
>>>>>>> main
