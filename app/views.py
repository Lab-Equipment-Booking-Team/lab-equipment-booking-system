from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.models import Booking, Equipment, User

main = Blueprint("main", __name__)


# 1. Homepage Route
@main.route("/")
def index():
    return render_template("index.html")


# 2. Login Route
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_input = request.form.get("identifier")
        password = request.form.get("password")

        user = User.query.filter(
            (User.username == login_input) | (User.email == login_input)
        ).first()

        if user and (
            user.password_hash == password
            or (hasattr(user, "check_password") and user.check_password(password))
        ):
            flash("Logged in successfully!", "success")
            return redirect(url_for("main.book_equipment"))
        else:
            flash("Invalid username or password! Please try again.", "danger")

    return render_template("login.html")


# 3. Register Route
@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            flash("Username or Email already exists!", "danger")
            return redirect(url_for("main.register"))

        new_user = User(username=username, email=email)

        if hasattr(new_user, "set_password"):
            new_user.set_password(password)
        else:
            new_user.password_hash = password

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")


# 4. FR-02: Booking Request Route
@main.route("/book", methods=["GET", "POST"])
def book_equipment():
    if request.method == "POST":
        equipment_id = request.form.get("equipment_id")
        booking_date_str = request.form.get("booking_date")
        start_time_str = request.form.get("start_time")
        end_time_str = request.form.get("end_time")

        booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()

        new_booking = Booking(
            user_id=1,
            equipment_id=equipment_id,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            status="Pending",
        )

        db.session.add(new_booking)
        db.session.commit()

        flash("Booking request submitted successfully!", "success")
        return redirect(url_for("main.book_equipment"))

    equipment_list = Equipment.query.all()
    return render_template("book.html", equipment_list=equipment_list)

# 5. FR-01: Equipment Catalogue Route
@main.route("/equipment")
def equipment_list():
    equipments = Equipment.query.all()
    return render_template("equipment.html", equipments=equipments)