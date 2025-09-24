import db

def test_ping():
    assert db.ping_db()

def test_patients_search():
    rows = db.find_patients(first="Ja")
    assert any(r["full_name"] == "Jane Smith" for r in rows)

def test_doctors_search():
    rows = db.find_doctors(employee_id=102)
    assert rows and rows[0]["Employee_ID"] == 102

def test_medical_records():
    rows = db.find_medical_records(patient_mrn=1001)
    assert rows and all(r["Patient_MRN"] == 1001 for r in rows)

def test_billing():
    rows = db.find_billing(patient_mrn=1001)
    assert rows and all(r["Patient_MRN"] == 1001 for r in rows)
