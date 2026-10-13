# Testing Documentation

## Test Design & Summary
This document records the automated tests implemented using `pytest` and `pytest-cov` for the Lab Equipment Booking System, focusing particularly on Module M4 (Booking Validation - FR-03)[cite: 10, 12, 16].

## Test Cases Table

| Test ID | Test Requirement Condition | Expected Result | Technique | Result |
| :--- | :--- | :--- | :--- | :--- |
| T01 | FR-03: End time before start time | Reject | Boundary / Logic | Pass[cite: 17] |
| T02 | FR-03: Duration = 29 minutes | Reject | Boundary Value | Pass[cite: 17] |
| T03 | FR-03: Duration = 30 minutes | Accept | Boundary Value | Pass[cite: 17] |
| T04 | FR-03: Duration = 4 hours | Accept | Boundary Value | Pass[cite: 17] |
| T05 | FR-03: Duration = 4 hours 1 minute | Reject | Boundary Value | Pass[cite: 17] |
| T06 | FR-03: Past booking start time | Reject | Validation Rule | Pass |
| T07 | FR-03: Equipment Out of service | Reject | Status Check | Pass |
| T08 | FR-03: Overlapping booking times | Reject | Overlap Logic | Pass |
