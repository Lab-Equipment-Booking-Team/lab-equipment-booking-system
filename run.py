from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Database tables ටිකauto create කිරීමට
    app.run(debug=True)