import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "dev-secure-lab-booking-university-secret-key-2026"
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'instance', 'lab_booking.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Administrative key used optionally for verified staff self-registration
    STAFF_REGISTRATION_KEY = os.environ.get(
        "STAFF_REGISTRATION_KEY", "LAB-STAFF-AUTH-2026"
    )


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True


class TestingConfig(Config):
    """Testing environment configuration."""

    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG = False
    TESTING = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
