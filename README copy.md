# Project22 - Laboratory Order Intake and Input Validation Service

## Overview

This project implements a small laboratory order intake and validation service.

The service accepts one laboratory order as a JSON string, validates the input, and returns either:

- `Accepted` with the validated order
- `Rejected` with all validation errors

The implementation is kept simple and focused on the requirements of the assessment.

> Note: This version is implemented in Python for practice and learning.
> The assessment submission requires the equivalent implementation in C#.

---

## Project Structure

```text
Project22/
│
├── order_intake.py
│
├── tests/
│   └── test_order_intake.py
│
├── README.md
#use this command
python test -v
