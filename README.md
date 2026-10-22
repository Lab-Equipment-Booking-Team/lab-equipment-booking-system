# Lab Equipment Booking System

<<<<<<< HEAD
## 1. Project Description

The Lab Equipment Booking System is a web-based application developed to manage laboratory equipment and student booking requests. Students can request equipment bookings, while staff members can manage equipment and approve or reject booking requests.
## 2. Group Members

- A.R.P.T. Bandara - 6251
- M.P.S. Peiris - 6308
- H.G. Rathnayaka - 6312
- V.I. Chandralal - 6302
- N.P.S.T. Wickramasinghe - 6317

## 3. Team Members and Module Allocation

The project is divided into five modules. Each team member is responsible for the development tasks assigned to their module and also has a coordination role within the team.

| Member | Module | Development Task | Coordination Role |
|---|---|---|---|
| Pawani(PawaniThathsaraniBandara) | M5: Approval & Integration | Staff Approval/Reject Page (FR-04) and System Integration | Overall Team Leader |
| Prabhashi (asp2023155) | M1: Accounts & Auth | Student & Staff Login, Registration (FR-00) | Review Lead |
| Shashinika (Shashithathsarani2003) | M2: Equipment Catalogue | Equipment Listing, Add/Edit/Delete Equipment (FR-01) | Coordinator |
| Imasha (asp2023143) | M3: Booking Form & Model | Booking Request Form & Database Schema (FR-02) | GitHub / CI Lead |
| Hashini (Hashini-123) | M4: Booking Validation | Overlapping Logic & Validation Tests (FR-03) | QA Lead |

## 4. Module Responsibilities

### M1 – Accounts & Authentication (FR-00)
**Assigned Member:** Prabhashi

- Implement student and staff registration.
- Implement student and staff login/logout.
- Manage user sessions.
- Support authentication and access control.

### M2 – Equipment Catalogue (FR-01)
**Assigned Member:** Shashinika

- Display laboratory equipment.
- Allow staff to add new equipment.
- Allow staff to edit equipment details.
- Allow staff to delete equipment.

### M3 – Booking Form & Model (FR-02)
**Assigned Member:** Imasha

- Develop the booking request form.
- Allow students to create booking requests.
- Design the booking database schema.
- Store booking information in the database.

### M4 – Booking Validation (FR-03)
**Assigned Member:** Hashini

- Implement booking validation logic.
- Detect overlapping booking requests.
- Validate booking conditions and rules.
- Write automated validation tests using Pytest.

### M5 – Approval & Integration (FR-04)
**Assigned Member:** Pawani

- Develop the staff booking approval/rejection page.
- Integrate all modules into the final system.
- Coordinate the integration of team members' work.
- Support the final system testing and integration process.

## 5. Coordination Responsibilities

- **Overall Team Leader – Pawani:** Coordinate the overall project, monitor progress, and support module integration.
- **Review Lead – Prabhashi:** Coordinate code reviews and help ensure code changes are reviewed before merging.
- **Coordinator – Shashinika:** Coordinate team tasks and follow up on assigned work.
- **GitHub / CI Lead – Imasha:** Manage the GitHub workflow and support the GitHub Actions CI setup.
- **QA Lead – Hashini:** Coordinate testing, validation, and checking of the system's functionality.

## 6. Technologies Used

- **Programming Language:** Python
- **Web Framework:** Flask
- **Database:** SQLite
- **Testing Framework:** Pytest
- **Code Quality Tool:** Ruff
- **Version Control:** Git and GitHub
- **Continuous Integration:** GitHub Actions

## 7. Team Development Workflow

The team will use GitHub to collaborate and manage the project.

- **GitHub Issues:** Track development tasks and problems.
- **GitHub Project Board:** Monitor task progress.
- **Feature Branches:** Develop features separately.
- **Pull Requests (PRs):** Submit changes for review before merging.
- **Code Reviews:** Review code changes to improve quality.
- **Automated Testing:** Use Pytest to test application functionality.
- **Code Quality Checks:** Use Ruff to check Python code.
- **Continuous Integration (CI):** Use GitHub Actions to run automated checks and tests.

## 8. Project Goal

The goal of this project is to develop a functional laboratory equipment booking system that supports user authentication, equipment management, booking requests, booking validation, and staff approval/rejection through a collaborative and structured software development process.

# lab-equipment-booking-system
Web-based Lab Equipment Booking System
=======
An enterprise-grade, modular web application built with **Python 3.11** and **Flask** for university laboratories. The system streamlines laboratory equipment reservations, eliminates double-booking conflicts through mathematical interval validation, and provides administrative oversight for lab staff.

Developed as a collaborative university Software Engineering project organized into five cleanly separated, independent modules.

---

## 1. Group Members & Module Allocation

| Module | Title | Member | Student ID | GitHub Username | Key Responsibilities |
|---|---|---|---|---|---|
| **M1** | Accounts & Authentication | **Prabhashi Peiris** | 6308 | `asp2023155` | Registration, login, logout, password hashing, session management, RBAC decorators, auth tests. |
| **M2** | Equipment Catalogue | **Shashinika Rathnayaka** | 6312 | `Shashithathsarani2003` | Equipment catalogue listing, category filters, search, equipment CRUD, availability API, deletion safety checks, equipment tests. |
| **M3** | Booking Form & Model | **Imasha Chandralal** | 6302 | `asp2023145` | Booking form, equipment selection, date/time inputs, booking creation, Pending status, ORM models (`models.py`), booking tests. |
| **M4** | Booking Validation & QA | **Hashini Wickramasinghe** | 6317 | `Hashini-123` | Date/time validation, past booking rejection, overlapping interval conflict checks, peak capacity calculation, validation tests, `TESTING.md`. |
| **M5** | Approval & Integration | **Pawani Thathsarani Bandara** | 6251 | Overall Lead | Staff dashboard, pending requests queue, approve/reject workflow with reason logging, system integration, end-to-end tests. |

For detailed module boundaries, file ownership, and collaboration protocols, refer to [docs/MODULE_ALLOCATION.md](file:///C:/Users/PAWANI/.gemini/antigravity/scratch/lab-equipment-booking-system/docs/MODULE_ALLOCATION.md).

---

## 2. Project Architecture & Modular Folder Structure

The project is organized so each group member can develop, test, and maintain their assigned module independently without code collisions:

```
lab-equipment-booking-system/
├── app.py                         # Application factory & CLI commands
├── config.py                      # Development, Testing, Production configurations
├── conftest.py                    # Root pytest discovery proxy
├── pyproject.toml                 # Ruff & Pytest configuration
├── requirements.txt               # Project dependencies
├── README.md                      # Project documentation
├── .gitignore                     # Git ignore rules
│
├── modules/
│   ├── M1_accounts_auth/          # Assigned to: Prabhashi Peiris (6308)
│   │   ├── routes.py              # Auth Blueprint (/auth/register, /auth/login, /auth/logout)
│   │   ├── service.py             # User authentication & registration service
│   │   ├── decorators.py          # @staff_required and @student_required decorators
│   │   ├── templates/auth/        # login.html, register.html
│   │   └── tests/                 # test_auth.py
│   │
│   ├── M2_equipment_catalogue/    # Assigned to: Shashinika Rathnayaka (6312)
│   │   ├── routes.py              # Equipment Blueprint (/equipment, /equipment/<id>, API)
│   │   ├── service.py             # Catalogue search, filter, and equipment CRUD service
│   │   ├── templates/equipment/   # catalogue.html, detail.html
│   │   └── tests/                 # test_equipment.py
│   │
│   ├── M3_booking_form_model/     # Assigned to: Imasha Chandralal (6302)
│   │   ├── routes.py              # Student Booking Blueprint (/student/dashboard, /student/book, etc.)
│   │   ├── service.py             # Booking submission service (uses M4 validation)
│   │   ├── models.py              # User, Equipment, and Booking ORM database models
│   │   ├── templates/student/     # create_booking.html, my_bookings.html, dashboard.html
│   │   └── tests/                 # test_booking.py, test_models.py
│   │
│   ├── M4_booking_validation/     # Assigned to: Hashini Wickramasinghe (6317)
│   │   ├── validation.py          # Pure validation algorithms (interval overlap, capacity check)
│   │   ├── service.py             # Validation services consumed by M2, M3, and M5
│   │   └── tests/                 # test_validation.py
│   │
│   └── M5_approval_integration/   # Assigned to: Pawani Thathsarani Bandara (6251)
│       ├── routes.py              # Staff Blueprint (/staff/dashboard, /staff/requests/pending, etc.)
│       ├── service.py             # Staff approval, rejection, and metrics calculation service
│       ├── templates/staff/       # dashboard.html, pending_requests.html, all_bookings.html, etc.
│       └── tests/                 # test_approval.py
│
├── database/
│   ├── __init__.py
│   └── database.py                # Central shared SQLAlchemy db instance & utcnow()
│
├── templates/                     # Root shared layouts
│   ├── base.html                  # Master navbar, alerts, responsive grid, footer
│   ├── index.html                 # Public landing page
│   ├── about.html                 # System Overview & Guide
│   └── errors/                    # 403.html, 404.html, 500.html
│
├── static/
│   ├── css/style.css              # Custom university navy/gold responsive stylesheet
│   ├── js/script.js               # Dynamic client-side scripts & live availability calculator
│   └── images/                    # Image assets
│
├── tests/                         # Shared integration & end-to-end tests
│   ├── conftest.py                # Shared fixtures (app, client, runner, users)
│   ├── test_assets_and_templates.py # Static file and CSS/JS linkage tests
│   └── test_cli_and_integration.py  # CLI commands and whole-application routing tests
│
└── docs/
    ├── MODULE_ALLOCATION.md       # Team responsibilities & collaboration guide
    └── TESTING.md                 # Complete testing strategy & coverage report
```

---

## 3. Technology Stack

- **Backend**: Python 3.11+, Flask 3.1
- **Database**: SQLite with Flask-SQLAlchemy 3.1
- **Authentication**: Flask-Login 0.6 & Werkzeug 3.1 salted hashing
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Testing**: Pytest 9.1, pytest-cov 7.1 (**53 tests, 95% coverage**)
- **Code Quality**: Ruff 0.17 linter
- **Continuous Integration**: GitHub Actions (`.github/workflows/ci.yml`)

---

## 4. Quickstart Installation & Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/pawani-bandara/lab-equipment-booking-system.git
cd lab-equipment-booking-system
```

### Step 2: Create & Activate Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database & Seed Demo Data
```bash
# 1. Initialize SQLite database tables
flask init-db

# 2. Seed realistic equipment, demo staff, students, and bookings
flask seed-data
```

### Step 5: Run the Development Server
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 5. Pre-Configured Demo Accounts

| Role | Username | Password | Access Privileges |
|---|---|---|---|
| **Staff Administrator** | `staff_admin` | `StaffPass123!` | Equipment inventory CRUD, pending request approval/rejection queue, full booking archive. |
| **Student (Primary)** | `student_alex` | `StudentPass123!` | Equipment catalogue viewing, booking request creation, personal booking history tracking. |
| **Student (Secondary)** | `student_maya` | `StudentPass123!` | Additional student account for testing multi-user concurrent capacity scenarios. |

---

## 6. Running Tests & Quality Verification

### Run the Complete Automated Test Suite (53 Tests)
```bash
python -m pytest
```

### Run Module-Specific Test Suites
```bash
# M1: Accounts & Authentication
python -m pytest modules/M1_accounts_auth/tests/

# M2: Equipment Catalogue
python -m pytest modules/M2_equipment_catalogue/tests/

# M3: Booking Form & Models
python -m pytest modules/M3_booking_form_model/tests/

# M4: Booking Validation
python -m pytest modules/M4_booking_validation/tests/

# M5: Staff Approval & Integration
python -m pytest modules/M5_approval_integration/tests/

# Shared Integration Tests
python -m pytest tests/
```

### Run with Coverage Analysis
```bash
python -m pytest --cov=. --cov-report=term-missing
```

### Run Code Quality Linter (Ruff)
```bash
python -m ruff check .
```

---

## 7. How the Modules Work Together

```
                  ┌───────────────────────────────┐
                  │            app.py             │
                  │   (Factory & ChoiceLoader)    │
                  └──────┬─────────────────┬──────┘
                         │                 │
           ┌─────────────┴────────┐  ┌─────┴──────────────┐
           │                      │  │                    │
┌──────────▼──────────┐ ┌─────────▼──▼────────┐ ┌─────────▼───────────┐
│ M1: Accounts & Auth │ │ M2: Equip Catalogue │ │ M3: Booking Form    │
│  - User Login/Reg   │ │  - Search & Filters │ │  - Booking Request  │
│  - Session & RBAC   │ │  - Equipment CRUD   │ │  - User/Eq/Bk Model │
└──────────┬──────────┘ └─────────┬───────────┘ └─────────┬───────────┘
           │                      │                       │
           │                      │      Validates via    │
           │                      │     ┌─────────────────▼───────────┐
           │                      └────►│   M4: Booking Validation    │
           │                            │  - Interval overlap check   │
           │                            │  - Peak capacity check      │
           │                            │  - Past date/time rejection │
           │                            └─────────────────┬───────────┘
           │                                              │
           │   Re-validates capacity on approval          │
           └──────────────────────┬───────────────────────┘
                                  │
                        ┌─────────▼───────────┐
                        │ M5: Staff Approval  │
                        │  - Approve / Reject │
                        │  - System Integrate │
                        └─────────────────────┘
```

1. **Shared Database & Models**: The single central database instance resides in [database/database.py](file:///C:/Users/PAWANI/.gemini/antigravity/scratch/lab-equipment-booking-system/database/database.py). Canonical models reside in [modules/M3_booking_form_model/models.py](file:///C:/Users/PAWANI/.gemini/antigravity/scratch/lab-equipment-booking-system/modules/M3_booking_form_model/models.py).
2. **M3 Uses M4 Validation**: When a student submits a reservation in M3, `modules.M3_booking_form_model.service.create_student_booking()` directly calls `modules.M4_booking_validation.service.validate_booking_submission()` to check operational availability, interval syntax, and overlapping capacity limits before persisting with status `Pending`.
3. **M5 Integrates M3 Bookings**: In M5, staff inspect pending bookings created by M3. When approving, `modules.M5_approval_integration.service.approve_booking_request()` re-verifies capacity using M4 to prevent concurrent capacity violations, then calls `booking.approve(staff_user)`.
4. **M5 Integrates M2 Equipment CRUD**: Staff inventory management routes in M5 call `modules.M2_equipment_catalogue.service` functions (`add_equipment`, `update_equipment`, `delete_equipment`), preserving M2's referential deletion safety checks.
5. **Role-Based Access Control**: Protected views across student and staff routes utilize decorators (`@staff_required`, `@student_required`) defined in M1.
>>>>>>> bb65f6993f366d1677e41c35990b582a2073cecc
