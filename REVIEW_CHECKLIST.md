# Code Review Checklist (REVIEW_CHECKLIST.md)

This checklist outlines the formal code review criteria for all Pull Requests and module deliverables in the **Lab Equipment Booking System** project. Every team member must verify these checkpoints prior to approving pull requests.

---

## 1. Security & Authentication (Led by Prabhashi - M1)

- [ ] **Password Security:** Passwords are never stored in plain text. Salted hashes are generated using Werkzeug's `generate_password_hash` and verified with `check_password_hash`.
- [ ] **Public Registration Role Lock:** Public sign-up strictly defaults to the `Student` role. Users cannot self-assign the `Staff` role without an authorized administrative key.
- [ ] **Administrative Account Creation:** Initial Staff accounts are created through the secure CLI command (`flask create-staff`) or an environment-configured master key.
- [ ] **Server-Side Route Protection:** Sensitive routes are guarded by `@login_required`, `@staff_required`, and `@student_required` decorators, not just frontend conditional rendering.
- [ ] **Redirect Safety:** The `next` parameter in login redirects is checked using `is_safe_url` to prevent open-redirect vulnerabilities.
- [ ] **No Hardcoded Secrets:** Secret keys and environment configurations are loaded via environment variables with safe development defaults.

---

## 2. Equipment Management & Database Integrity (Led by Shashinika - M2 & Imasha - M3)

- [ ] **Referential Integrity on Deletion:** Equipment referenced by existing booking records cannot be deleted (`can_be_deleted() == False`). A user-friendly error message instructs staff to set status to `Decommissioned` instead.
- [ ] **Input Sanitization & Validation:** All equipment form submissions validate code uniqueness, positive inventory numbers, and valid category/status enumerations.
- [ ] **Database Relationships:** Foreign keys (`user_id`, `equipment_id`, `reviewed_by_id`) and SQLAlchemy relationships (`back_populates`) are properly defined with appropriate cascading behavior.
- [ ] **Transactions & Rollback:** Database mutation operations wrap commits in try-except blocks with `db.session.rollback()` on failure.

---

## 3. Booking Rules & Overlap Validation (Led by Hashini - M4)

- [ ] **Chronological Validation:** Start times must be strictly earlier than end times (`start_time < end_time`).
- [ ] **Past Booking Prevention:** Bookings with calendar dates in the past are rejected. Bookings for the current day with past start times are rejected.
- [ ] **Mathematical Overlap Logic:** Overlaps are detected using the interval intersection condition: `existing.start_time < req.end_time and existing.end_time > req.start_time`.
- [ ] **Adjacent Slots Permitted:** Non-overlapping adjacent slots (e.g. 09:00–10:00 and 10:00–11:00) do NOT trigger conflicts.
- [ ] **Multi-Unit Inventory Allocation:** The validation engine checks peak concurrently booked units across overlapping approved bookings, allowing partial reservations up to `quantity_available`.
- [ ] **Operational Status Check:** Non-operational equipment (`Under Maintenance` or `Decommissioned`) cannot be booked.

---

## 4. Approval Workflow & Integration (Led by Pawani - M5)

- [ ] **Pending Queue Authorization:** Only authenticated staff members can access pending approvals.
- [ ] **Approval Capacity Re-Verification:** Approving a booking re-evaluates capacity against other approved bookings to prevent race-condition overbooking.
- [ ] **Rejection Feedback:** Staff can provide a constructive rejection reason that is logged and displayed in the student's reservation history.
- [ ] **State Transition Integrity:** Requests already in `Approved`, `Rejected`, or `Cancelled` states cannot be re-approved or re-rejected.
- [ ] **Flash Messaging:** Clear user notifications accompany every approval, rejection, and cancellation action.

---

## 5. UI, UX & Accessibility Standards

- [ ] **Responsive Design:** Interfaces render correctly across mobile, tablet, and desktop screens using Bootstrap 5 grid classes.
- [ ] **Empty States:** Clear icons and informative messages appear when lists (equipment catalogue, pending queue, booking history) have zero records.
- [ ] **Confirmation Prompts:** Destructive operations (equipment deletion, reservation cancellation, request rejection) prompt for user confirmation before executing.
- [ ] **Accessible Status Badges:** Visual badges clearly distinguish statuses (`Pending`, `Approved`, `Rejected`, `Cancelled`, `Available`, `Under Maintenance`, `Decommissioned`).

---

## 6. Code Cleanliness & CI Pipeline (Led by Imasha - M3 / Hashini - M4)

- [ ] **PEP 8 Compliance:** All code passes `ruff check .` with zero errors.
- [ ] **Automated Testing:** Pytest test suite executes without failures and maintains >= 90% code coverage.
- [ ] **Hermetic Tests:** Automated tests run against an in-memory SQLite database without modifying local development database files.
- [ ] **GitHub Actions:** CI workflow completes successfully on push and pull request events.
