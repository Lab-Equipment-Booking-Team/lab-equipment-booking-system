# Project Retrospective — Lab Equipment Booking System

## 1. Project Context & Objectives

- **Project Title:** Lab Equipment Booking System
- **Academic Context:** University Software Engineering Coursework
- **Date of Review:** 25 October 2026
- **Team Leader:** Pawani
- **Participants:** Pawani, Prabhashi, Shashinika, Imasha, Hashini

---

## 2. Module Deliverables & Implementation Status

| Module | Scope / Feature | Lead | Status | Team Notes |
|---|---|---|---|---|
| **M1 (FR-00)** | Accounts, Authentication, RBAC, Password Hashing | Prabhashi | Complete | Authentication, registration, access control, and login-related scenarios are covered by automated tests. |
| **M2 (FR-01)** | Equipment Catalogue, Search, Filters, Staff CRUD | Shashinika | Complete | Equipment catalogue functionality, search, filtering, and staff equipment management are covered by automated tests. |
| **M3 (FR-02)** | Booking Form, DB Schema, Student Reservation History | Imasha | Complete | Booking requests, date and time validation, cancellation rules, and database model operations are tested. |
| **M4 (FR-03)** | Overlapping Logic, Capacity Validation, Pytest Suite | Hashini | Complete | Booking conflict detection, capacity allocation, and booking time restrictions are covered by six passing validation tests. |
| **M5 (FR-04)** | Approval Queue, Integration, Dashboards, GitHub Actions | Pawani | Complete | Approval and rejection workflows, status transitions, access restrictions, and integration-related functionality are covered by automated tests. |

**Overall Testing Result:** All 53 collected automated tests passed using pytest. This confirms that the collected tests passed, although it does not independently establish complete requirement coverage.

---

## 3. What Went Well (Successes)

### 1. Architecture & Modularity

The modular architecture helped the team divide the application into five functional modules. This made it easier to assign responsibilities, develop individual features, and organize the project code. Separating authentication, equipment management, booking requests, validation, and approval functionality improved the maintainability of the application.

### 2. Quality & Test Coverage

The team used pytest to automate functional and business-rule testing. The tests covered important scenarios such as invalid booking dates, overlapping reservations, equipment capacity, authentication, and staff approval. All 53 collected tests passed during the final local test run. This helped us verify the expected behaviour of the tested functionality.

### 3. Collaboration & Version Control

GitHub provided a shared repository for managing the project code. Branches and commits helped organize changes, while the team gained practical experience with version control, code integration, and resolving Git-related problems. The development process also highlighted the importance of reviewing changes before merging them into the main branch.

### 4. User Experience

The web application brought equipment browsing, booking requests, and staff approval functionality together in one system. Organizing the application into separate student and staff workflows helped make the main functions easier to understand. Form validation and user feedback also helped communicate the results of user actions.

---

## 4. Challenges & Roadblocks Encountered

### 1. Technical Challenges

Implementing booking validation required careful consideration of date and time conditions, overlapping reservations, and equipment capacity. Different booking scenarios needed separate test cases to verify that valid requests were accepted and invalid requests were handled correctly.

### 2. Database & Schema Challenges

The application needed to maintain consistent relationships between equipment, users, and booking records. Equipment deletion also required consideration of existing reservations and referential integrity. These requirements highlighted the importance of defining appropriate database relationships and testing operations that affect related records.

### 3. Integration Challenges

Combining the five modules required attention to shared functionality, authentication state, role-based access control, database operations, and application routes. Git branch switching, merge conflicts, and repository configuration issues also created additional work during development. These experiences demonstrated the need for consistent interfaces between modules and careful integration practices.

### 4. Time & Schedule Management

Dividing the work among five team members required coordination to ensure that the individual modules worked together. Debugging, integrating changes, and verifying the complete application added to the workload. Earlier integration and more regular progress checks would help identify problems sooner in future projects.

---

## 5. Key Engineering Lessons Learned

- **Lesson 1 — Importance of Automated Testing:** Testing different booking scenarios helped identify and verify important business rules, including overlapping time slots and equipment capacity restrictions.

- **Lesson 2 — Security Must Be Enforced on the Server:** Role-based access restrictions must be checked by the backend, not only by hiding buttons or pages in the user interface.

- **Lesson 3 — Importance of Isolated Test Environments:** Using a separate test database helps prevent automated tests from modifying real development data and makes test results more consistent.

- **Lesson 4 — Benefits of Continuous Integration:** Automated test execution and code-quality checks can identify problems earlier and reduce the risk of introducing errors during integration.

- **Lesson 5 — Effective Version Control and Communication:** Clear branch naming, meaningful commits, regular communication, and reviewing changes before integration help teams collaborate more effectively.

---

## 6. Actionable Improvements for Future Iterations

If the project were continued into a future release, the following improvements would be considered:

- [ ] **Email or SMS notifications:** Notify students when booking requests are approved or rejected.
- [ ] **Calendar-based scheduling:** Provide a visual calendar to help users identify equipment availability and existing reservations.
- [ ] **Reservation report exports:** Allow authorized staff to export booking records to CSV or PDF for laboratory administration and auditing.
- [ ] **Maintenance scheduling calendar:** Allow staff to block equipment availability during planned maintenance periods.
- [ ] **QR code check-in and check-out:** Support equipment collection and return tracking through QR codes.
- [ ] **Improved CI and code quality checks:** Ensure that automated tests and linting checks run consistently through GitHub Actions.
- [ ] **Improved integration planning:** Integrate modules earlier, agree on shared interfaces, and review changes regularly to reduce merge conflicts.

---

## 7. Final Reflection

The Lab Equipment Booking System project provided practical experience in modular application development, database management, booking validation, authentication, automated testing, and version control. Working on separate modules helped the team understand the importance of clear responsibilities and integration between components.

Running the complete local test suite resulted in 53 passing tests, providing evidence that the tested functionality behaved as expected in those scenarios. The project also highlighted areas for improvement, particularly early integration, systematic peer review, and consistent automation of quality checks.

Overall, the project strengthened our understanding of software engineering principles and demonstrated the value of teamwork, testing, documentation, and continuous improvement throughout the development process.
