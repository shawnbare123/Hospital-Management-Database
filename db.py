# db.py
import os
from contextlib import contextmanager
from typing import Any, Iterable, Optional, List, Dict

import mysql.connector as mc
from mysql.connector import pooling, Error
from dotenv import load_dotenv

load_dotenv()

def _make_pool() -> pooling.MySQLConnectionPool:
    return pooling.MySQLConnectionPool(
        pool_name="clinic_pool",
        pool_size=5,
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        database=os.getenv("DB_NAME", "hospital_db"),
        autocommit=False,
    )

_pool = _make_pool()

@contextmanager
def get_conn():
    conn = _pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()

def _fetchall(conn, sql: str, params: Optional[Iterable[Any]] = None) -> List[Dict[str, Any]]:
    with conn.cursor(dictionary=True) as cur:
        cur.execute(sql, tuple(params) if params is not None else None)
        return list(cur.fetchall())

# ---------- health ----------
def ping_db() -> bool:
    try:
        with get_conn() as conn:
            return conn.is_connected()
    except Error:
        return False

# ---------- patients ----------
def find_patients(
    mrn: Optional[int] = None,
    first: Optional[str] = None,
    last: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    sql = """
    WITH ranked AS (
      SELECT
        mr.*,
        ROW_NUMBER() OVER (
          PARTITION BY mr.Patient_MRN
          ORDER BY mr.Admission_Date DESC, mr.Record_ID DESC
        ) AS rn
      FROM Medical_Record mr
    )
    SELECT
      p.MRN,
      CONCAT(p.First_Name,' ',p.Last_Name) AS full_name,
      p.Birthdate,
      r.Diagnosis AS latest_dx,
      CONCAT(d.First_Name,' ',d.Last_Name) AS doctor_name,
      d.Employee_ID
    FROM Patient p
    LEFT JOIN ranked r ON r.Patient_MRN = p.MRN AND r.rn = 1
    LEFT JOIN Doctor d ON d.Employee_ID = r.Doctor_ID
    WHERE (%s IS NULL OR p.MRN = %s)
      AND (%s IS NULL OR p.First_Name LIKE CONCAT('%%', %s, '%%'))
      AND (%s IS NULL OR p.Last_Name  LIKE CONCAT('%%', %s, '%%'))
    ORDER BY p.MRN
    LIMIT %s OFFSET %s;
    """
    params = [mrn, mrn, first, first, last, last, int(limit), int(offset)]
    with get_conn() as conn:
        return _fetchall(conn, sql, params)

def total_patients_count(
    mrn: Optional[int] = None,
    first: Optional[str] = None,
    last: Optional[str] = None,
) -> int:
    sql = """
    SELECT COUNT(*) AS cnt
    FROM Patient p
    WHERE (%s IS NULL OR p.MRN = %s)
      AND (%s IS NULL OR p.First_Name LIKE CONCAT('%%', %s, '%%'))
      AND (%s IS NULL OR p.Last_Name  LIKE CONCAT('%%', %s, '%%'));
    """
    params = [mrn, mrn, first, first, last, last]
    with get_conn() as conn:
        rows = _fetchall(conn, sql, params)
        return int(rows[0]["cnt"]) if rows else 0

def medical_records_for_patient(mrn: int) -> List[Dict[str, Any]]:
    sql = """
    SELECT mr.Record_ID, mr.Admission_Date, mr.Diagnosis,
           mr.Doctor_ID, CONCAT(d.First_Name,' ',d.Last_Name) AS DoctorName
    FROM Medical_Record mr
    LEFT JOIN Doctor d ON d.Employee_ID = mr.Doctor_ID
    WHERE mr.Patient_MRN = %s
    ORDER BY mr.Admission_Date DESC, mr.Record_ID DESC;
    """
    with get_conn() as conn:
        return _fetchall(conn, sql, (mrn,))

def billing_for_patient(mrn: int) -> List[Dict[str, Any]]:
    sql = """
    SELECT Bill_ID, Insurance_Name, Amount_Due, Amount_Paid
    FROM Billing
    WHERE Patient_MRN = %s
    ORDER BY Bill_ID DESC;
    """
    with get_conn() as conn:
        return _fetchall(conn, sql, (mrn,))

# ---------- doctors ----------
def find_doctors(
    employee_id: Optional[int] = None,
    first: Optional[str] = None,
    last: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    sql = """
    SELECT d.Employee_ID,
           CONCAT(d.First_Name,' ',d.Last_Name) AS full_name,
           d.Specialty
    FROM Doctor d
    WHERE (%s IS NULL OR d.Employee_ID = %s)
      AND (%s IS NULL OR d.First_Name LIKE CONCAT('%%', %s, '%%'))
      AND (%s IS NULL OR d.Last_Name  LIKE CONCAT('%%', %s, '%%'))
    ORDER BY d.Employee_ID
    LIMIT %s OFFSET %s;
    """
    params = [employee_id, employee_id, first, first, last, last, int(limit), int(offset)]
    with get_conn() as conn:
        return _fetchall(conn, sql, params)

def total_doctors_count(employee_id=None, first=None, last=None) -> int:
    sql = """
    SELECT COUNT(*) AS cnt
    FROM Doctor d
    WHERE (%s IS NULL OR d.Employee_ID = %s)
      AND (%s IS NULL OR d.First_Name LIKE CONCAT('%%', %s, '%%'))
      AND (%s IS NULL OR d.Last_Name  LIKE CONCAT('%%', %s, '%%'));
    """
    params = [employee_id, employee_id, first, first, last, last]
    with get_conn() as conn:
        rows = _fetchall(conn, sql, params)
        return int(rows[0]["cnt"]) if rows else 0

def patients_for_doctor(employee_id: int) -> List[Dict[str, Any]]:
    sql = """
    SELECT DISTINCT p.MRN,
           CONCAT(p.First_Name,' ',p.Last_Name) AS full_name
    FROM Medical_Record mr
    JOIN Patient p ON p.MRN = mr.Patient_MRN
    WHERE mr.Doctor_ID = %s
    ORDER BY p.MRN;
    """
    with get_conn() as conn:
        return _fetchall(conn, sql, (employee_id,))

# ---------- medical records search ----------
def find_medical_records(
    record_id: Optional[int] = None,
    patient_mrn: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    sql = """
    SELECT mr.Record_ID, mr.Patient_MRN, mr.Doctor_ID,
           CONCAT(d.First_Name,' ',d.Last_Name) AS DoctorName,
           mr.Admission_Date, mr.Diagnosis
    FROM Medical_Record mr
    LEFT JOIN Doctor d ON d.Employee_ID = mr.Doctor_ID
    WHERE (%s IS NULL OR mr.Record_ID = %s)
      AND (%s IS NULL OR mr.Patient_MRN = %s)
    ORDER BY mr.Admission_Date DESC, mr.Record_ID DESC
    LIMIT %s OFFSET %s;
    """
    params = [record_id, record_id, patient_mrn, patient_mrn, int(limit), int(offset)]
    with get_conn() as conn:
        return _fetchall(conn, sql, params)

def total_medrecs_count(record_id=None, patient_mrn=None) -> int:
    sql = """
    SELECT COUNT(*) AS cnt
    FROM Medical_Record mr
    WHERE (%s IS NULL OR mr.Record_ID = %s)
      AND (%s IS NULL OR mr.Patient_MRN = %s);
    """
    params = [record_id, record_id, patient_mrn, patient_mrn]
    with get_conn() as conn:
        rows = _fetchall(conn, sql, params)
        return int(rows[0]["cnt"]) if rows else 0

# ---------- billing search ----------
def find_billing(
    bill_id: Optional[int] = None,
    patient_mrn: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    sql = """
    SELECT Bill_ID, Patient_MRN, Insurance_Name, Amount_Due, Amount_Paid
    FROM Billing
    WHERE (%s IS NULL OR Bill_ID = %s)
      AND (%s IS NULL OR Patient_MRN = %s)
    ORDER BY Bill_ID DESC
    LIMIT %s OFFSET %s;
    """
    params = [bill_id, bill_id, patient_mrn, patient_mrn, int(limit), int(offset)]
    with get_conn() as conn:
        return _fetchall(conn, sql, params)

def total_billing_count(bill_id=None, patient_mrn=None) -> int:
    sql = """
    SELECT COUNT(*) AS cnt
    FROM Billing
    WHERE (%s IS NULL OR Bill_ID = %s)
      AND (%s IS NULL OR Patient_MRN = %s);
    """
    params = [bill_id, bill_id, patient_mrn, patient_mrn]
    with get_conn() as conn:
        rows = _fetchall(conn, sql, params)
        return int(rows[0]["cnt"]) if rows else 0

# ---------- sanity run ----------
if __name__ == "__main__":
    from pprint import pprint
    print("DB reachable:", ping_db())
    pprint(find_patients(first="Ja", limit=10))
    pprint(find_doctors(first="Ja", limit=10))
    pprint(find_medical_records(patient_mrn=1001))
    pprint(find_billing(patient_mrn=1001))
