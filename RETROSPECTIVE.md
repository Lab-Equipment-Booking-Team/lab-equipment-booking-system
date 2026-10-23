# Project Retrospective Template (RETROSPECTIVE.md)

*This document serves as a standardized template for the project team to conduct their post-development review and document reflections upon completing the Lab Equipment Booking System assignment.*

---

## 1. Project Context & Objectives

- **Project Title:** Lab Equipment Booking System
- **Academic Context:** University Software Engineering Coursework
- **Date of Review:** [Insert Review Date]
- **Team Leader:** Pawani
- **Participants:** Pawani, Prabhashi, Shashinika, Imasha, Hashini

---

## 2. Module Deliverables & Implementation Status

| Module | Scope / Feature | Lead | Status (Complete / In Progress / Pending) | Team Notes |
|---|---|---|---|---|
| **M1 (FR-00)** | Accounts, Authentication, RBAC, Password Hashing | Prabhashi | [Team to confirm] | |
| **M2 (FR-01)** | Equipment Catalogue, Search, Filters, Staff CRUD | Shashinika | [Team to confirm] | |
| **M3 (FR-02)** | Booking Form, DB Schema, Student Reservation History | Imasha | [Team to confirm] | |
| **M4 (FR-03)** | Overlapping Logic, Capacity Validation, Pytest Suite | Hashini | [Team to confirm] | |
| **M5 (FR-04)** | Approval Queue, Integration, Dashboards, GitHub Actions | Pawani | [Team to confirm] | |

---

## 3. What Went Well (Successes)

*Team members should document technical, procedural, or collaboration successes:*

1. **Architecture & Modularity:**
   - [Document how Flask Blueprints and separation of concerns helped divide work among members]
2. **Quality & Test Coverage:**
   - [Document how writing Pytest tests and running Ruff early helped maintain code quality]
3. **Collaboration & Version Control:**
   - [Document experiences with feature branching, PR reviews, and GitHub Actions CI]
4. **User Experience:**
   - [Document feedback on Bootstrap 5 styling, flash feedback, and responsive layout]

---

## 4. Challenges & Roadblocks Encountered

*Document actual technical hurdles, communication friction, or debugging challenges faced during development:*

1. **Technical Challenges:**
   - *Example topic:* Edge cases in interval overlap mathematics when handling multi-unit equipment and same-day booking validations.
   - [Insert team experience]
2. **Database & Schema Challenges:**
   - *Example topic:* Handling referential integrity when attempting to delete equipment that has historical reservation records.
   - [Insert team experience]
3. **Integration Challenges:**
   - *Example topic:* Harmonizing authentication session state with role-based route decorators across student and staff blueprints.
   - [Insert team experience]
4. **Time & Schedule Management:**
   - [Insert team experience]

---

## 5. Key Engineering Lessons Learned

*What did the team learn from this project that will guide future software engineering work?*

- **Lesson 1:** [e.g., Value of test-driven validation for scheduling intervals]
- **Lesson 2:** [e.g., Importance of server-side role verification rather than relying solely on UI button hiding]
- **Lesson 3:** [e.g., Using in-memory test databases to keep development data clean]
- **Lesson 4:** [e.g., Benefits of continuous automated linting and CI pipelines]

---

## 6. Actionable Improvements for Future Iterations

*If the project were continued into a future release, what features or technical enhancements would be prioritized?*

- [ ] Email or SMS notification integration for instant approval/rejection alerts.
- [ ] Calendar view (e.g. FullCalendar.js) for visual instrument scheduling.
- [ ] Exporting reservation records to CSV/PDF for laboratory audits.
- [ ] Maintenance scheduling block-out calendar for lab technicians.
- [ ] QR code generation for equipment check-in and check-out on site.

---


