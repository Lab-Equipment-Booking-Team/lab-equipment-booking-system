# Lab Equipment Booking System — Module Allocation & Collaboration Guide

This document defines the team module allocations, assigned responsibilities, file boundaries, shared architecture rules, and Git collaboration guidelines for the **Lab Equipment Booking System** group project.

---

## 1. Group Member Allocations & Assigned Responsibilities

| Module | Title | Assigned Member | Student ID | GitHub Username | Core Responsibilities |
|---|---|---|---|---|---|
| **M1** | Accounts & Authentication | **Prabhashi Peiris** | 6308 | `asp2023155` | User registration, login, logout, password hashing, session management, role-based access control (RBAC), and authentication tests. |
| **M2** | Equipment Catalogue | **Shashinika Rathnayaka** | 6312 | `Shashithathsarani2003` | Equipment catalogue listing, category filtering, search, equipment CRUD operations, inventory availability status, deletion safety checks, and equipment tests. |
| **M3** | Booking Form & Model | **Imasha Chandralal** | 6302 | `asp2023145` | Student booking form, equipment selection, date & time inputs, booking request creation, Pending status initialization, database models (`models.py`), and booking tests. |
| **M4** | Booking Validation & QA | **Hashini Wickramasinghe** | 6317 | `Hashini-123` | Server-side booking validation, date/time logic, past booking prevention, overlapping conflict detection, concurrent capacity calculation, validation tests, and `TESTING.md`. |
| **M5** | Approval & Integration | **Pawani Thathsarani Bandara** | 6251 | Team Lead | Staff dashboard, pending requests queue, approve/reject workflow with reason logging, system integration across all modules, and end-to-end integration tests. |

---

## 2. Modular File Boundaries (Which Files Each Member Should Edit)

To ensure that group members can work independently without encountering Git merge conflicts, code is strictly partitioned into dedicated module directories under `modules/`.

### Module M1 – Accounts & Authentication (Prabhashi Peiris)
- **Directory**: `modules/M1_accounts_auth/`
- **Primary Files**:
  - `modules/M1_accounts_auth/routes.py`: Flask Blueprint `auth_bp` (`/auth/register`, `/auth/login`, `/auth/logout`).
  - `modules/M1_accounts_auth/service.py`: Authentication business logic, user credential verification, password hashing, and safe URL validation.
  - `modules/M1_accounts_auth/decorators.py`: RBAC decorators (`@staff_required`, `@student_required`).
  - `modules/M1_accounts_auth/templates/auth/`: HTML templates for `login.html` and `register.html`.
  - `modules/M1_accounts_auth/tests/test_auth.py`: Pytest test cases for registration, login, logout, and role access security.

### Module M2 – Equipment Catalogue (Shashinika Rathnayaka)
- **Directory**: `modules/M2_equipment_catalogue/`
- **Primary Files**:
  - `modules/M2_equipment_catalogue/routes.py`: Flask Blueprint `equipment_bp` (`/equipment`, `/equipment/<id>`, `/equipment/api/check-availability`).
  - `modules/M2_equipment_catalogue/service.py`: Equipment search and category filter queries, item detail lookup, equipment CRUD operations (`add_equipment`, `update_equipment`, `delete_equipment`), and slot availability verification.
  - `modules/M2_equipment_catalogue/templates/equipment/`: HTML templates for `catalogue.html` and `detail.html`.
  - `modules/M2_equipment_catalogue/tests/test_equipment.py`: Pytest test cases for catalogue rendering, search, category filters, and equipment CRUD actions.

### Module M3 – Booking Form & Model (Imasha Chandralal)
- **Directory**: `modules/M3_booking_form_model/`
- **Primary Files**:
  - `modules/M3_booking_form_model/models.py`: Database models for `User`, `Equipment`, and `Booking`, defining columns, relationships, and model methods (`approve()`, `reject()`, `cancel()`, `can_be_deleted()`).
  - `modules/M3_booking_form_model/routes.py`: Flask Blueprint `bookings_bp` (`/student/dashboard`, `/student/my-bookings`, `/student/book`, `/student/bookings/<id>/cancel`).
  - `modules/M3_booking_form_model/service.py`: Student booking submission service (integrating M4 validation), student history query, and booking cancellation.
  - `modules/M3_booking_form_model/templates/student/`: HTML templates for `create_booking.html`, `my_bookings.html`, and `dashboard.html`.
  - `modules/M3_booking_form_model/tests/test_booking.py` and `test_models.py`: Tests for booking request creation, Pending state initialization, and ORM model integrity.

### Module M4 – Booking Validation & QA (Hashini Wickramasinghe)
- **Directory**: `modules/M4_booking_validation/`
- **Primary Files**:
  - `modules/M4_booking_validation/validation.py`: Pure validation algorithms for date parsing (`parse_date`), time parsing (`parse_time`), overlap detection (`get_conflicting_approved_bookings`), peak booked capacity calculation (`calculate_peak_booked_quantity`), and rule validation (`validate_booking_request`).
  - `modules/M4_booking_validation/service.py`: High-level validation services consumed by M3 (`validate_booking_submission`), M2 (`check_slot_availability`), and M5 (`validate_approval_capacity`).
  - `modules/M4_booking_validation/tests/test_validation.py`: Pytest test cases covering non-conflicting bookings, overlapping bookings, single/multi-unit capacity, past date/time rejection, and maintenance checks.
  - `docs/TESTING.md`: Comprehensive quality assurance and test documentation.

### Module M5 – Approval & Integration (Pawani Thathsarani Bandara)
- **Directory**: `modules/M5_approval_integration/`
- **Primary Files**:
  - `modules/M5_approval_integration/routes.py`: Flask Blueprint `staff_bp` (`/staff/dashboard`, `/staff/requests/pending`, `/staff/requests/<id>/approve`, `/staff/requests/<id>/reject`, `/staff/bookings/history`, and staff equipment management views calling M2 services).
  - `modules/M5_approval_integration/service.py`: Staff administrative metrics calculation, pending requests queue aggregation, approval action with M4 capacity verification, rejection with reason logging, and booking history archive.
  - `modules/M5_approval_integration/templates/staff/`: HTML templates for `dashboard.html`, `pending_requests.html`, `all_bookings.html`, `manage_equipment.html`, and `equipment_form.html`.
  - `modules/M5_approval_integration/tests/test_approval.py`: Pytest tests for staff approvals, rejections, transition guards, and capacity re-checks.

---

## 3. Shared Infrastructure & Coordination Rules

The following core files are shared across all five modules. **No group member should edit these shared files without prior communication and consensus.**

```
lab-equipment-booking-system/
├── app.py                     # Main application factory & CLI entry point
├── config.py                  # Global configurations (Dev, Test, Prod)
├── pyproject.toml             # Ruff linting & Pytest test runner configuration
├── requirements.txt           # Shared Python package dependencies
├── database/
│   └── database.py            # Central SQLAlchemy db instance & utcnow()
├── templates/
│   ├── base.html              # Master layout, navigation bar, alerts & footer
│   ├── index.html             # Public landing page
│   ├── about.html             # System Overview & Guide
│   └── errors/                # HTTP 403, 404, 500 error templates
├── static/
│   ├── css/style.css          # Shared university branding styles
│   ├── js/script.js           # Shared dynamic JavaScript behaviors
│   └── images/                # Static image assets
└── tests/
    ├── conftest.py            # Global Pytest fixtures (app, client, runner, users)
    ├── test_assets_and_templates.py  # Static asset and CSS/JS linkage tests
    └── test_cli_and_integration.py   # CLI command and end-to-end integration tests
```

### Shared File Policy:
1. **`database/database.py`**: Initialises the central `db = SQLAlchemy()`. Do not re-instantiate `SQLAlchemy()` anywhere else.
2. **`templates/base.html`**: The single navigation bar and master layout. Any changes to the global navigation must be coordinated with the team lead (Pawani).
3. **`static/css/style.css` & `static/js/script.js`**: Shared stylesheet and script. Use module-specific CSS classes or data attributes where necessary to avoid collisions.
4. **`app.py`**: Managed by the Integration Lead (Pawani). Registers all blueprints and configures the template `ChoiceLoader`.

---

## 4. Git Collaboration & Workflow Protocol

To facilitate seamless collaboration on GitHub, our group adheres to standard feature branch and pull request workflows:

### Branch Naming Convention
- `main`: Production-ready, stable codebase. Direct commits to `main` are restricted.
- Feature branches must follow the naming pattern:
  - `feature/M1-auth-improvements`
  - `feature/M2-catalogue-filters`
  - `feature/M3-booking-date-picker`
  - `feature/M4-validation-edge-cases`
  - `feature/M5-staff-bulk-approval`
  - `fix/M2-equipment-code-check`

### Development Workflow
1. **Pull Latest Changes**: Always branch from an updated `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/M1-your-task
   ```
2. **Work Locally Within Assigned Module**: Restrict your file modifications to your assigned `modules/M*/` directory.
3. **Run Code Quality Checks Locally**:
   ```bash
   # 1. Run Ruff linter
   python -m ruff check .

   # 2. Run the test suite
   python -m pytest

   # 3. Or run only your module's tests
   python -m pytest modules/M1_accounts_auth/tests/
   ```
4. **Commit & Push**:
   ```bash
   git add modules/M1_accounts_auth/
   git commit -m "M1: Implement secure password hashing validation"
   git push origin feature/M1-your-task
   ```
5. **Open a Pull Request (PR)**:
   - Provide a clear PR title and description summarizing your changes.
   - Reference the requirement (e.g., `Resolves FR-00`).
   - GitHub Actions CI will automatically run Ruff linting and the 53-test Pytest suite.
   - At least one code review and CI passing status are required before merging into `main`.
