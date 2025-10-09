import os
from contextlib import contextmanager
from typing import Any, Iterable, Optional, List, Dict
import datetime
from decimal import Decimal

import mysql.connector as mc
from mysql.connector import pooling, Error, cursor
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
    with conn.cursor(cursor_class=cursor.MySQLCursorDict) as cur:
        cur.execute(sql, tuple(params) if params is not None else None)
        return list(cur.fetchall())
    
def _fetchone(conn, sql: str, params: Optional[Iterable[Any]] = None) -> Dict[str, Any]:
    with conn.cursor(cursor_class=cursor.MySQLCursorDict) as cur:
        cur.execute(sql, tuple(params) if params is not None else None)
        result = cur.fetchone()
        return dict(result) if result else {}
    
def execute_dml(conn, sql: str, params: Optional[Iterable[Any]] = None) -> int:
    with conn.cursor() as cur:
        cur.execute(sql, tuple(params) if params is not None else None)
        return cur.rowcount

# ---------- Connectivity Test ----------

def ping_db() -> bool:
    try:
        with get_conn() as conn:
            return conn.is_connected()
    except Error:
        return False
    

# ----------------------------------------------------------------------
#                           Read Operations
# ----------------------------------------------------------------------


# --- Patient ---

def find_patients(
    input: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    sql = """
        SELECT 
            p.MRN AS MRN, 
            p.First_Name AS First_Name,
            p.Last_Name AS Last_Name,
            p.Birthdate AS Birthdate, 
            m.Diagnosis AS Diagnosis, 
            CONCAT(d.First_Name, ' ', d.Last_Name) AS Doctor_Name, 
            d.Employee_ID AS Doctor_ID
        FROM Patient p
        LEFT JOIN Medical_Record m ON p.MRN = m.Patient_MRN
        LEFT JOIN Doctor d ON m.Doctor_ID = d.Employee_ID
        WHERE p.MRN = %s OR p.First_Name LIKE %s OR p.Last_Name LIKE %s
        LIMIT %s OFFSET %s;
    """
    search_term_like = f'%{input}%' if input else '%'

    input = str(input)

    if input and input.isdigit():
        params = [int(input), search_term_like, search_term_like, int(limit), int(offset)]
    else:
        params = [0, search_term_like, search_term_like, int(limit), int(offset)]
        
    with get_conn() as conn:
        results_dicts = _fetchall(conn, sql, params)
        
        column_keys = ["MRN", "First_Name", "Last_Name", "Birthdate", "Diagnosis", "Doctor_Name", "Doctor_ID"]
        
        results_list = []
        for row_dict in results_dicts:
            row_list = [str(row_dict.get(key, '')) for key in column_keys]
            results_list.append(row_list)
            
        return results_list

def total_patient_count(
    input: Optional[str] = None,
) -> int:
    sql = """
        SELECT COUNT(*) AS cnt
        FROM Patient p
        WHERE p.MRN = %s OR p.First_Name LIKE %s OR p.Last_Name LIKE %s;
    """
    search_term_like = f'%{input}%' if input else '%'
    
    input = str(input)

    if input and input.isdigit():
        params = [int(input), search_term_like, search_term_like]
    else:
        params = [0, search_term_like, search_term_like]
        
    with get_conn() as conn:
        result = _fetchone(conn, sql, params)
    return int(result.get("cnt", 0))

# --- Doctor ---

def find_doctors(
    input: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    sql = """
        SELECT 
            d.Employee_ID AS Employee_ID, 
            d.First_Name AS First_Name,
            d.Last_Name AS Last_Name,
            d.Specialty AS Specialty,
            GROUP_CONCAT(CONCAT(p.First_Name,' ',p.Last_Name,' (',p.MRN,')') SEPARATOR ', ') AS Patients
        FROM Doctor d
        LEFT JOIN Medical_Record m ON d.Employee_ID = m.Doctor_ID
        LEFT JOIN Patient p ON m.Patient_MRN = p.MRN
        WHERE d.Employee_ID = %s OR d.First_Name LIKE %s OR d.Last_Name LIKE %s
        GROUP BY d.Employee_ID
        LIMIT %s OFFSET %s
    """
    search_term_like = f'%{input}%' if input else '%'
    
    input = str(input)

    if input and input.isdigit():
        params = [int(input), search_term_like, search_term_like, int(limit), int(offset)]
    else:
        params = [0, search_term_like, search_term_like, int(limit), int(offset)]
        
    with get_conn() as conn:
        results_dicts = _fetchall(conn, sql, params)
        
        column_keys = ["Employee_ID", "First_Name", "Last_Name", "Specialty", "Patients"]
        
        results_list = []
        for row_dict in results_dicts:
            row_list = [str(row_dict.get(key, '')) for key in column_keys]
            results_list.append(row_list)
            
        return results_list

def total_doctor_count(
    input: Optional[str] = None,
) -> int:
    sql = """
        SELECT COUNT(*) AS cnt
        FROM Doctor d
        WHERE d.Employee_ID = %s OR d.First_Name LIKE %s OR d.Last_Name LIKE %s
    """
    search_term_like = f'%{input}%' if input else '%'

    input = str(input)
    
    if input and input.isdigit():
        params = [int(input), search_term_like, search_term_like]
    else:
        params = [0, search_term_like, search_term_like]
        
    with get_conn() as conn:
        result = _fetchone(conn, sql, params)
    return int(result.get("cnt", 0))

# --- Medical Record ---

def find_medical_records(
    input: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    sql = """
        SELECT Record_ID, Patient_MRN, Doctor_ID, Admission_Date, Diagnosis 
        FROM Medical_Record 
        WHERE Record_ID = %s OR Patient_MRN = %s 
        LIMIT %s OFFSET %s;
    """
    
    input_val = int(input) if input is not None else 0
    params = [input_val, input_val, int(limit), int(offset)]
    with get_conn() as conn:
        results_dicts = _fetchall(conn, sql, params)
        
        column_keys = ["Record_ID", "Patient_MRN", "Doctor_ID", "Admission_Date", "Diagnosis"]
        
        results_list = []
        for row_dict in results_dicts:
            row_list = [str(row_dict.get(key, '')) for key in column_keys]
            results_list.append(row_list)
            
        return results_list

def total_medrec_count(
    input: Optional[int] = None
) -> int:
    sql = """
        SELECT COUNT(*) AS cnt
        FROM Medical_Record mr
        WHERE Record_ID = %s OR Patient_MRN = %s;
    """
    input_val = int(input) if input is not None else 0
    params = [input_val, input_val]
    with get_conn() as conn:
        result = _fetchone(conn, sql, params)
    return int(result.get("cnt", 0))

# --- Billing ---

def find_billing(
    input: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    sql = """
        SELECT Bill_ID, Patient_MRN, Insurance_Provider, Amount_Due, Amount_Paid 
        FROM Billing 
        WHERE Bill_ID = %s OR Patient_MRN = %s 
        LIMIT %s OFFSET %s;
    """
    
    input_val = int(input) if input is not None else 0
    params = [input_val, input_val, int(limit), int(offset)]
    with get_conn() as conn:
        results_dicts = _fetchall(conn, sql, params)
        
        column_keys = ["Bill_ID", "Patient_MRN", "Insurance_Provider", "Amount_Due", "Amount_Paid"]
        
        results_list = []
        for row_dict in results_dicts:
            row_list = [str(row_dict.get(key, '')) for key in column_keys]
            results_list.append(row_list)
            
        return results_list

def total_bill_count(
    input: Optional[int] = None
) -> int:
    sql = """
        SELECT COUNT(*) AS cnt
        FROM Billing
        WHERE Bill_ID = %s OR Patient_MRN = %s;
    """
    input_val = int(input) if input is not None else 0
    params = [input_val, input_val]
    with get_conn() as conn:
        rows = _fetchall(conn, sql, params)
        return int(rows[0]["cnt"]) if rows and rows[0] else 0
    

# ----------------------------------------------------------------------
#                           Write Operations
# ----------------------------------------------------------------------


# --- Patient ---

def add_new_patient(mrn: int, first_name: str, last_name: str, birthdate: str) -> int:
    sql = """
        INSERT INTO Patient (MRN, First_Name, Last_Name, Birthdate)
        VALUES (%s, %s, %s, %s);
        """
    params = [mrn, first_name, last_name, birthdate]
    with get_conn() as conn:
        try:
            row_count = execute_dml(conn, sql, params)
            conn.commit()
            return row_count
        except Error as e:
            conn.rollback()
            raise ValueError(f"Failed to add new patient (MRN: {mrn}): {e}")

def update_patient(
    mrn: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    birthdate: Optional[str] = None,
) -> int:
    updates = {}
    if first_name is not None:
        updates["First_Name"] = first_name
    if last_name is not None:
        updates["Last_Name"] = last_name
    if birthdate is not None:
        updates["Birthdate"] = birthdate

    if not updates:
        return 0

    set_clauses = [f"{col} = %s" for col in updates.keys()]
    params = list(updates.values())
    params.append(mrn)

    sql = f"""
        UPDATE Patient
        SET {', '.join(set_clauses)}
        WHERE MRN = %s;
        """
    with get_conn() as conn:
        try:
            row_count = execute_dml(conn, sql, params)
            conn.commit()
            return row_count
        except Error as e:
            conn.rollback()
            raise ValueError(f"Failed to update patient {mrn}: {e}")

def delete_patient(mrn: int) -> int:
    sql = """
        DELETE FROM Patient
        WHERE MRN = %s;
        """
    params = [mrn]
    with get_conn() as conn:
        try:
            row_count = execute_dml(conn, sql, params)
            conn.commit()
            return row_count
        except Error as e:
            conn.rollback()
            raise ValueError(f"Failed to delete patient {mrn}: {e}")

# --- Doctor ---

def add_new_doctor(employee_id: int, first_name: str, last_name: str, specialty: str) -> int:
    sql = """
        INSERT INTO Doctor (Employee_ID, First_Name, Last_Name, Specialty)
        VALUES (%s, %s, %s, %s);
        """
    params = [employee_id, first_name, last_name, specialty]
    with get_conn() as conn:
        try:
            row_count = execute_dml(conn, sql, params)
            conn.commit()
            return row_count
        except Error as e:
            conn.rollback()
            raise ValueError(f"Failed to add new doctor (ID: {employee_id}): {e}")

def update_doctor(
    employee_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    specialty: Optional[str] = None,
) -> int:
    updates = {}
    if first_name is not None:
        updates["First_Name"] = first_name
    if last_name is not None:
        updates["Last_Name"] = last_name
    if specialty is not None:
        updates["Specialty"] = specialty

    if not updates:
        return 0

    set_clauses = [f"{col} = %s" for col in updates.keys()]
    params = list(updates.values())
    params.append(employee_id)

    sql = f"""
        UPDATE Doctor
        SET {', '.join(set_clauses)}
        WHERE Employee_ID = %s;
        """
    with get_conn() as conn:
        try:
            row_count = execute_dml(conn, sql, params)
            conn.commit()
            return row_count
        except Error as e:
            conn.rollback()
            raise ValueError(f"Failed to update doctor {employee_id}: {e}")

def delete_doctor(employee_id: int) -> int:
    sql = """
        DELETE FROM Doctor
        WHERE Employee_ID = %s;
        """
    params = [employee_id]
    with get_conn() as conn:
        try:
            row_count = execute_dml(conn, sql, params)
            conn.commit()
            return row_count
        except Error as e:
            conn.rollback()
            raise ValueError(f"Failed to delete doctor {employee_id}: {e}")

# --- Medical Record ---

def add_new_medical_record(record_id: int, patient_mrn: int, doctor_id: Optional[int], admission_date: str, diagnosis: str) -> int:
    sql = """
        INSERT INTO Medical_Record (Record_ID, Patient_MRN, Doctor_ID, Admission_Date, Diagnosis)
        VALUES (%s, %s, %s, %s, %s);
        """
    params = [record_id, patient_mrn, doctor_id, admission_date, diagnosis]
    with get_conn() as conn:
        try:
            row_count = execute_dml(conn, sql, params)
            conn.commit()
            return row_count
        except Error as e:
            conn.rollback()
            raise ValueError(f"Failed to add new medical record (ID: {record_id}): {e}")

def update_medical_record(
    record_id: int,
    admission_date: Optional[str] = None,
    diagnosis: Optional[str] = None,
) -> int:
    updates = {}
    if admission_date is not None:
        updates["Admission_Date"] = admission_date
    if diagnosis is not None:
        updates["Diagnosis"] = diagnosis

    if not updates:
        return 0

    set_clauses = [f"{col} = %s" for col in updates.keys()]
    params = list(updates.values())
    params.append(record_id)

    sql = f"""
        UPDATE Medical_Record
        SET {', '.join(set_clauses)}
        WHERE Record_ID = %s;
        """
    with get_conn() as conn:
        try:
            row_count = execute_dml(conn, sql, params)
            conn.commit()
            return row_count
        except Error as e:
            conn.rollback()
            raise ValueError(f"Failed to update medical record {record_id}: {e}")

def delete_medical_record(record_id: int) -> int:
    sql = """
        DELETE FROM Medical_Record
        WHERE Record_ID = %s;
    """
    params = [record_id]
    with get_conn() as conn:
        try:
            row_count = execute_dml(conn, sql, params)
            conn.commit()
            return row_count
        except Error as e:
            conn.rollback()
            raise ValueError(f"Failed to delete medical record {record_id}: {e}")

# --- Billing ---

def add_new_bill(bill_id: int, patient_mrn: int, insurance_name: str, amount_due: Decimal, amount_paid: Decimal) -> int:
    sql = """
        INSERT INTO Billing (Bill_ID, Patient_MRN, Insurance_Provider, Amount_Due, Amount_Paid)
        VALUES (%s, %s, %s, %s, %s);
        """
    params = [bill_id, patient_mrn, insurance_name, amount_due, amount_paid]
    with get_conn() as conn:
        try:
            row_count = execute_dml(conn, sql, params)
            conn.commit()
            return row_count
        except Error as e:
            conn.rollback()
            raise ValueError(f"Failed to add new bill (ID: {bill_id}): {e}")

def update_billing(
    bill_id: int,
    insurance_provider: Optional[str] = None,
    amount_due: Optional[Decimal] = None,
    amount_paid: Optional[Decimal] = None,
) -> int:
    updates = {}
    if insurance_provider is not None:
        updates["Insurance_Provider"] = insurance_provider
    if amount_due is not None:
        updates["Amount_Due"] = amount_due
    if amount_paid is not None:
        updates["Amount_Paid"] = amount_paid

    if not updates:
        return 0

    set_clauses = [f"{col} = %s" for col in updates.keys()]
    params = list(updates.values())
    params.append(bill_id)

    sql = f"""
        UPDATE Billing
        SET {', '.join(set_clauses)}
        WHERE Bill_ID = %s;
        """
    with get_conn() as conn:
        try:
            row_count = execute_dml(conn, sql, params)
            conn.commit()
            return row_count
        except Error as e:
            conn.rollback()
            raise ValueError(f"Failed to update bill {bill_id}: {e}")

def delete_billing(bill_id: int) -> int:
    sql = """
        DELETE FROM Billing
        WHERE Bill_ID = %s;
        """
    params = [bill_id]
    with get_conn() as conn:
        try:
            row_count = execute_dml(conn, sql, params)
            conn.commit()
            return row_count
        except Error as e:
            conn.rollback()
            raise ValueError(f"Failed to delete bill {bill_id}: {e}")

# ---------- sanity run ----------


if __name__ == "__main__":
    from pprint import pprint
    print("DB reachable:", ping_db())
    pprint(find_patients(input="Ja", limit=10)) 
    pprint(find_doctors(input="Ja", limit=10)) 
    pprint(find_medical_records(input=1001)) 
    pprint(find_billing(input=1001)) 
