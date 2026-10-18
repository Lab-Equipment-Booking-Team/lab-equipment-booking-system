from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.models import Booking, Equipment

main = Blueprint("main", __name__)


# 1. Homepage Route
@main.route("/")
def index():
  return render_template("index.html")


# 2. Login Route (කලින් නොතිබූ නිසා 404 ආවේ)
@main.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    # Login process logic
    return redirect(url_for("main.index"))
  return render_template("login.html")


# 3. Register Route (කලින් නොතිබූ නිසා 404 ආවේ)
@main.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "POST":
    # Register process logic
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