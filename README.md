# Project22
Assessment Repo
Please accept my apologies for the late submission. I experienced a delay while uploading the project because the 6-minute explanation video was approximately 184 MB, which exceeded GitHub’s 100 MB file-size limit. I therefore uploaded the required project files separately and excluded the large video file.

Thank you for your understanding.
Drive link for video-https://drive.google.com/file/d/1Ii5EE3MtWBTH8HPYq-j3m_lgWYz0XnMA/view?usp=sharing

# Project22 - Laboratory Order Intake and Input Validation Service

## Overview

This project implements a small laboratory order intake and validation service.

The service accepts one laboratory order as a JSON string, validates the input, and returns either:

- `Accepted` with the validated order
- `Rejected` with all validation errors

The implementation is kept simple and focused on the requirements of the assessment.



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
