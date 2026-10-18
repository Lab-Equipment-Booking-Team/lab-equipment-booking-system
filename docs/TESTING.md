# Lab Equipment Booking System — Quality Assurance & Testing Guide

Prepared by: **Hashini Wickramasinghe** (Student ID: 6317, GitHub: `Hashini-123`)  
Module: **Module M4 – Booking Validation & QA**  
Integration Lead: **Pawani Thathsarani Bandara** (Student ID: 6251)

---

## 1. Quality Assurance & Testing Strategy

The Lab Equipment Booking System employs a multi-tiered automated testing strategy using **Pytest**, **pytest-cov**, and **Ruff** to guarantee functional correctness, role-based security, business rule enforcement, and template asset integrity.

### Core Testing Pillars:
1. **Isolated In-Memory Test Database**: All automated tests execute against an isolated SQLite test database configured via `TestingConfig`. No operations touch or modify development data.
2. **Pytest Fixtures**: Shared test fixtures (`app`, `client`, `runner`, `student_user`, `staff_user`, `sample_equipment`) are declared in `tests/conftest.py` and exposed globally across all modules via root `conftest.py`.
3. **Module-Scoped Test Suites**: Each assigned module owns its dedicated unit and functional test suite within `modules/M*/tests/`.
4. **End-to-End Integration Tests**: Root-level integration tests (`tests/test_cli_and_integration.py`, `tests/test_assets_and_templates.py`) verify whole-system routing, CLI management commands, and CSS/JS linkage.
5. **Continuous Integration (CI)**: Automated GitHub Actions pipeline runs Ruff linting and the complete 53-test suite on every push and pull request.

---

## 2. Test Suite Breakdown by Module

The test suite contains **53 automated tests** achieving **95% overall code coverage**.

| Module | Test File | Test Count | Key Features & Business Rules Tested |
|---|---|---|---|
| **M1: Accounts & Auth** | `modules/M1_accounts_auth/tests/test_auth.py` | 11 | Student registration, password mismatch rejection, duplicate email/username rejection, public registration role restriction, authorized staff registration key, student/staff login, invalid credentials rejection, logout, unauthenticated redirect, student forbidden from staff routes (403). |
| **M2: Equipment Catalogue** | `modules/M2_equipment_catalogue/tests/test_equipment.py` | 9 | Catalogue public access, search and category filtering, equipment detail view, staff equipment creation, creation validation errors, equipment edit, equipment delete without bookings, deletion prevention with existing bookings, student forbidden from equipment CRUD. |
| **M3: Booking Form & Model** | `modules/M3_booking_form_model/tests/test_booking.py` | 7 | Valid student booking submission, past booking date rejection, start time >= end time rejection, maintenance status rejection, invalid quantity rejection, student pending booking cancellation, approved booking cancellation rejection. |
| **M3: Data Models** | `modules/M3_booking_form_model/tests/test_models.py` | 3 | `User` model password hashing & role checks, `Equipment` model operational check & delete safety, `Booking` model status transitions (`approve()`, `reject()`, `cancel()`) and relationships. |
| **M4: Booking Validation** | `modules/M4_booking_validation/tests/test_validation.py` | 6 | Non-conflicting bookings on different dates, non-conflicting adjacent time slots on same date, single-unit resource overlap conflict, multi-unit partial capacity allocation, pending/rejected bookings not blocking capacity, same-day past start time rejection. |
| **M5: Approval & Integration** | `modules/M5_approval_integration/tests/test_approval.py` | 5 | Staff booking approval and timestamping, staff booking rejection with optional logged reason, invalid status transition prevention (no re-approving), capacity re-verification on approval, student forbidden from approval actions (403). |
| **Shared: Asset & Template Linkage** | `tests/test_assets_and_templates.py` | 5 | Static CSS/JS 200 OK delivery, public pages link `style.css` and `script.js` via `url_for`, student pages link CSS/JS, staff pages link CSS/JS, error pages (403/404) link CSS/JS. |
| **Shared: Integration & CLI** | `tests/test_cli_and_integration.py` | 7 | CLI `init-db` command, CLI `create-staff` command, CLI `seed-data` command, public landing & about pages, role-based dashboard redirection, live API check availability endpoint, staff booking history filtering, custom 404 page. |
| **TOTAL** | **8 Test Modules** | **53 Tests** | **95% Code Coverage (0 Failures)** |

---

## 3. How to Run the Automated Tests

### 3.1 Run the Entire Test Suite
Execute Pytest from the project root directory:
```bash
python -m pytest
```

### 3.2 Run Tests for a Specific Module
Group members can run tests exclusively for their assigned module:
```bash
# Module M1 (Prabhashi Peiris)
python -m pytest modules/M1_accounts_auth/tests/

# Module M2 (Shashinika Rathnayaka)
python -m pytest modules/M2_equipment_catalogue/tests/

# Module M3 (Imasha Chandralal)
python -m pytest modules/M3_booking_form_model/tests/

# Module M4 (Hashini Wickramasinghe)
python -m pytest modules/M4_booking_validation/tests/

# Module M5 (Pawani Thathsarani Bandara)
python -m pytest modules/M5_approval_integration/tests/

# Shared Integration & Template Tests
python -m pytest tests/
```

### 3.3 Run Tests with Coverage Report
Generate a line-by-line coverage analysis:
```bash
python -m pytest --cov=. --cov-report=term-missing
```

To export an XML coverage report for CI or IDE integration:
```bash
python -m pytest --cov=. --cov-report=xml
```

---

## 4. Code Quality & Linting (Ruff)

All Python code must adhere to PEP 8 standards and project styling rules before being merged into `main`.

Run the Ruff linter across the entire project:
```bash
python -m ruff check .
```

To automatically format imports and fix safe lint issues:
```bash
python -m ruff check --fix .
```

---

## 5. Continuous Integration (CI) Pipeline

The repository includes an automated GitHub Actions workflow defined in `.github/workflows/ci.yml`.

### Automated Pipeline Steps:
1. **Environment Setup**: Provisions Ubuntu container with Python 3.11.
2. **Dependency Installation**: Caches and installs dependencies from `requirements.txt`.
3. **Lint Verification**: Executes `ruff check .` to enforce clean formatting and import sorting.
4. **Test Suite Execution**: Runs `pytest --cov=. --cov-report=term-missing --cov-report=xml`.
5. **Quality Gate**: Pull requests cannot be merged if any lint check fails or if any of the 53 tests fail.
