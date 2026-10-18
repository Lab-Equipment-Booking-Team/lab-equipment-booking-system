"""Database models for the Lab Equipment Booking System.

Assigned to: Module M3 – Booking Form & Model
Member: Imasha Chandralal (Student ID: 6302, GitHub: asp2023145)

Defines User, Equipment, and Booking database entities using the shared
SQLAlchemy database instance from database.database.
"""

from typing import ClassVar

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from database.database import db, utcnow


class User(UserMixin, db.Model):
    """User account model supporting Student and Staff laboratory roles."""

    __tablename__ = "users"

    ROLE_STUDENT = "student"
    ROLE_STAFF = "staff"
    ROLES: ClassVar[list[str]] = [ROLE_STUDENT, ROLE_STAFF]

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    student_or_staff_id = db.Column(db.String(32), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_STUDENT)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    # Relationships
    bookings = db.relationship(
        "Booking",
        back_populates="user",
        foreign_keys="Booking.user_id",
        cascade="all, delete-orphan",
        lazy="select",
    )
    reviewed_bookings = db.relationship(
        "Booking",
        back_populates="reviewer",
        foreign_keys="Booking.reviewed_by_id",
        lazy="select",
    )

    def set_password(self, password: str) -> None:
        """Hash and set the user's password using Werkzeug."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify the user's password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_staff_member(self) -> bool:
        """Check if user has staff privileges."""
        return self.role == self.ROLE_STAFF

    @property
    def is_student_member(self) -> bool:
        """Check if user is a student."""
        return self.role == self.ROLE_STUDENT

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"


class Equipment(db.Model):
    """Equipment catalogue model for laboratory resources."""

    __tablename__ = "equipment"

    STATUS_AVAILABLE = "Available"
    STATUS_MAINTENANCE = "Under Maintenance"
    STATUS_DECOMMISSIONED = "Decommissioned"
    STATUSES: ClassVar[list[str]] = [
        STATUS_AVAILABLE,
        STATUS_MAINTENANCE,
        STATUS_DECOMMISSIONED,
    ]

    CATEGORIES: ClassVar[list[str]] = [
        "Microscopes",
        "Spectrometry & Optical",
        "Centrifuges & Separation",
        "Electronics & Measurement",
        "Thermal & Heating",
        "General Laboratory Equipment",
    ]

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    category = db.Column(db.String(64), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    quantity_available = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(32), nullable=False, default=STATUS_AVAILABLE)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=utcnow, onupdate=utcnow, nullable=False
    )

    # Relationships
    bookings = db.relationship(
        "Booking",
        back_populates="equipment",
        lazy="select",
    )

    def can_be_deleted(self) -> bool:
        """Return True only if no existing booking records reference this equipment."""
        return len(self.bookings) == 0

    @property
    def is_operational(self) -> bool:
        """Return True if equipment is in operational Available status."""
        return self.status == self.STATUS_AVAILABLE

    def __repr__(self) -> str:
        return f"<Equipment {self.code} - {self.name}>"


class Booking(db.Model):
    """Booking request model connecting students and laboratory equipment."""

    __tablename__ = "bookings"

    STATUS_PENDING = "Pending"
    STATUS_APPROVED = "Approved"
    STATUS_REJECTED = "Rejected"
    STATUS_CANCELLED = "Cancelled"
    STATUSES: ClassVar[list[str]] = [
        STATUS_PENDING,
        STATUS_APPROVED,
        STATUS_REJECTED,
        STATUS_CANCELLED,
    ]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    equipment_id = db.Column(
        db.Integer, db.ForeignKey("equipment.id"), nullable=False, index=True
    )
    booking_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    purpose = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING, index=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    reviewed_by_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )
    reviewed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    # Relationships
    user = db.relationship("User", foreign_keys=[user_id], back_populates="bookings")
    equipment = db.relationship("Equipment", back_populates="bookings")
    reviewer = db.relationship(
        "User", foreign_keys=[reviewed_by_id], back_populates="reviewed_bookings"
    )

    @property
    def is_pending(self) -> bool:
        return self.status == self.STATUS_PENDING

    @property
    def is_approved(self) -> bool:
        return self.status == self.STATUS_APPROVED

    @property
    def is_rejected(self) -> bool:
        return self.status == self.STATUS_REJECTED

    @property
    def is_cancelled(self) -> bool:
        return self.status == self.STATUS_CANCELLED

    def approve(self, staff_user: User) -> None:
        """Approve a booking request and stamp the staff reviewer and timestamp."""
        self.status = self.STATUS_APPROVED
        self.reviewed_by_id = staff_user.id
        self.reviewed_at = utcnow()
        self.rejection_reason = None

    def reject(self, staff_user: User, reason: str | None = None) -> None:
        """Reject a booking request with an optional reason."""
        self.status = self.STATUS_REJECTED
        self.reviewed_by_id = staff_user.id
        self.reviewed_at = utcnow()
        self.rejection_reason = reason.strip() if reason else None

    def cancel(self) -> None:
        """Cancel a pending booking request by student."""
        self.status = self.STATUS_CANCELLED

    def __repr__(self) -> str:
        return f"<Booking #{self.id} {self.status} (Eq: {self.equipment_id})>"
