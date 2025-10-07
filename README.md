# Hospital Desktop – Backend (Python + MySQL)

Restructured backend data layer for a local Tkinter app.
This module provides read-only queries over the Patient, Doctor, Medical_Record, and Billing tables.

Requirements
- Python 3.10+
- MySQL 8.x (running locally or reachable)
- Install packages:
    pip install mysql-connector-python python-dotenv

Setup
1) Place db.py at the project root.
2) Create a .env next to updated_db.py:

		DB_HOST=127.0.0.1
		DB_PORT=3306
		DB_USER=appuser
		DB_PASS=app_pass
		DB_NAME=hospital_db

Quick Test
    python updated_db.py

Expected:

		DB reachable: True
		[patients rows...]
		[doctors rows...]
		[medical records rows...]
		[billing rows...]

What the module exposes (all return list[dict] except _count functions)
- ping_db()
- find_patients(...)
- total_patients_count(...)
- find_doctors(...)
- total_doctors_count(...)
- find_medical_records(...)
- total_medrecs_count(...)
- find_billing(...)
- total_billing_count(...)

Schema assumptions
- Patient: MRN (PK), First_Name, Last_Name, Birthdate
- Doctor: Employee_ID (PK), First_Name, Last_Name, Specialty
- Medical_Record: Record_ID (PK), Patient_MRN (FK), Doctor_ID (FK), Admission_Date, Diagnosis
- Billing: Bill_ID (PK), Patient_MRN (FK), Insurance_Provider, Amount_Due, Amount_Paid

Troubleshooting
- Cannot connect: check MySQL and .env.
- Auth errors: create appuser/app_pass:

    CREATE USER 'appuser'@'127.0.0.1' IDENTIFIED BY 'app_pass';
    GRANT ALL PRIVILEGES ON hospital_db.* TO 'appuser'@'127.0.0.1';
    FLUSH PRIVILEGES;

- No data: run 01_schema.sql then 02_seed.sql.
