# Lab Equipment Booking System

An enterprise-grade, modular web application built for university laboratories to streamline equipment reservation workflows, prevent scheduling conflicts, and manage inventory approvals between students and laboratory staff.

Developed as a university Software Engineering project following modern software development, testing, and continuous integration standards.

---

## 1. Project Overview

In university research and teaching laboratories, high-demand precision instruments (microscopes, spectrophotometers, centrifuges, oscilloscopes) require careful scheduling. This system eliminates manual paperwork and prevents double-booking through:

- **Role-Based Access Control (RBAC):** Distinct interfaces and server-side route protections for **Student** and **Staff** accounts.
- **Dynamic Catalogue & Inventory:** Searchable and filterable instrument directory with status tracking.
- **Intelligent Time-Slot Overlap Prevention:** Server-side mathematical validation ensuring that approved concurrent reservations never exceed available instrument quantities.
- **Staff Approval Workflow:** Queue for staff to inspect project justifications and approve or reject reservations with feedback.
- **Full Traceability:** Preserves historical reservation records by preventing the deletion of active or past-booked equipment.

---

## 2. Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.11+, Flask 3.1, Flask-SQLAlchemy 3.1, Flask-Login 0.6, Werkzeug 3.1 |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons |
| **Database** | SQLite with SQLAlchemy ORM (file-based dev, in-memory test) |
| **Testing** | Pytest 9.1, pytest-cov 7.1 |
| **Code Quality** | Ruff 0.17 |
| **Version Control & CI** | Git, GitHub, GitHub Actions |

---

## 3. Team Members & Module Allocation

| Team Member | Module & Feature Responsibility | Module ID | Coordination Role |
|---|---|---|---|
| **Pawani** | **Approval & Integration:** Staff Approval/Reject Page (FR-04) and System Integration | **M5 (FR-04)** | **Overall Team Leader** |
| **Prabhashi** | **Accounts & Authentication:** Student and Staff Login, Registration (FR-00) | **M1 (FR-00)** | **Review Lead** |
| **Shashinika** | **Equipment Catalogue:** Equipment Listing and Add/Edit/Delete Equipment (FR-01) | **M2 (FR-01)** | **Coordinator** |
| **Imasha** | **Booking Form & Model:** Booking Request Form and Database Schema (FR-02) | **M3 (FR-02)** | **GitHub / CI Lead** |
| **Hashini** | **Booking Validation:** Overlapping Logic and Validation Tests (FR-03) | **M4 (FR-03)** | **QA Lead** |

---

## 4. System Architecture & Features

### Module M1 – Accounts & Authentication (FR-00)
- **Role Distinction:** Students and Staff.
- **Secure Public Registration:** Public registration creates strictly `Student` accounts. Users cannot self-grant Staff privileges.
- **Safe Staff Creation:** Staff accounts are created securely via the documented CLI command (`flask create-staff`) or with a designated staff authorization key.
- **Password Security:** Salted hashes generated and verified via Werkzeug (`generate_password_hash` / `check_password_hash`).
- **Session Protection:** Managed via Flask-Login with custom decorators (`@staff_required`, `@student_required`).

### Module M2 – Equipment Catalogue (FR-01)
- **Catalogue Display:** Responsive card and table layouts showing equipment ID code, name, category, quantity, and status.
- **Search & Filters:** Real-time search by keyword and filtering by category and status (`Available`, `Under Maintenance`, `Decommissioned`).
- **Staff Inventory Control:** Authorized staff can add new instruments and edit specifications.
- **Referential Integrity Protection:** Equipment cannot be deleted if existing booking records reference it, protecting audit trails.

### Module M3 – Booking Form & Model (FR-02)
- **Student Reservation Portal:** Students select equipment, booking date, start time, end time, requested quantity, and purpose.
- **Relational Data Model:** Normalized SQLite tables linking `User`, `Equipment`, and `Booking`.
- **Student Dashboard:** Track personal reservation history with statuses: `Pending`, `Approved`, `Rejected`, `Cancelled`.

### Module M4 – Booking Validation & Capacity Engine (FR-03)
- **Interval Overlap Validation:** Two intervals `[start_1, end_1)` and `[start_2, end_2)` on the same date overlap if and only if `start_1 < end_2 and end_1 > start_2`. Adjacent time slots (e.g. 09:00–10:00 and 10:00–11:00) do not conflict.
- **Capacity Calculations:** Calculates peak concurrently booked quantities across all overlapping approved bookings to ensure available capacity is not exceeded.
- **Past Date/Time Prevention:** Rejects past dates and past times on the current day.
- **Time Inversion Prevention:** Rejects submissions where `start_time >= end_time`.

### Module M5 – Approval Workflow & System Integration (FR-04)
- **Staff Review Dashboard:** Dedicated interface displaying pending student requests, applicant details, and experiment justification.
- **Approval Re-Verification:** Re-evaluates capacity at approval time to guard against concurrent conflicting pending requests.
- **Constructive Rejection:** Allows staff to log feedback reasons viewable by students.
- **State Transition Guard:** Prevents illegal state transitions (e.g., re-approving a rejected request).

---

## 5. Installation & Setup Instructions

### Prerequisites
- Python 3.11 or later
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/<your-username>/lab-equipment-booking-system.git
cd lab-equipment-booking-system
```

### Step 2: Create and Activate Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 6. How to Run the Application

### Step 1: Initialize Database & Seed Demo Data
Initialize the database tables and populate realistic university equipment and demo accounts:
```bash
flask init-db
flask seed-data
```

### Step 2: (Optional) Create a Custom Staff Administrator
To create an administrative Staff account via the secure CLI command:
```bash
flask create-staff --username staff_admin --email admin@university.edu --name "Dr. Sarah Johnson" --staff-id "STF-0101"
```

### Step 3: Start the Development Server
```bash
python app.py
```
Or with Flask CLI:
```bash
flask run --host=127.0.0.1 --port=5000
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

### Pre-Seeded Demo Accounts
| Role | Username | Password | Notes |
|---|---|---|---|
| **Staff** | `staff_admin` | `StaffPass123!` | Full staff inventory and approval access |
| **Student** | `student_alex` | `StudentPass123!` | Student reservation access |
| **Student** | `student_maya` | `StudentPass123!` | Secondary student account for multi-user testing |

---

## 7. How to Run Tests and Code Quality Checks

### Run Automated Pytest Suite
```bash
pytest
```

### Run Tests with Coverage Reporting
```bash
pytest --cov=. --cov-report=term-missing
```

### Run Ruff Linter
```bash
ruff check .
```

---

## 8. GitHub Collaboration Workflow

The development team uses standard GitHub Feature Branching and pull request reviews:

1. **Main Branch Protection:** The `main` branch contains verified, production-ready code. Direct commits are restricted.
2. **Feature Branches:** Each module is developed on a dedicated branch:
   - `feature/m1-accounts-auth` (Prabhashi)
   - `feature/m2-equipment-catalogue` (Shashinika)
   - `feature/m3-booking-model` (Imasha)
   - `feature/m4-validation-tests` (Hashini)
   - `feature/m5-approval-integration` (Pawani)
3. **Continuous Integration:** Every push and pull request triggers the GitHub Actions CI pipeline (`.github/workflows/ci.yml`) to run Ruff lint checks and Pytest with test coverage.
4. **Peer Review:** Pull requests must pass CI and be approved by the designated Review Lead before merging.
