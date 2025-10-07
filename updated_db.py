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
    
def _fetchone(conn, sql: str, params: Optional[Iterable[Any]] = None) -> Dict[str, Any]:
    with conn.cursor(dictionary=True) as cur:
        cur.execute(sql, tuple(params) if params is not None else None)
        result = cur.fetchone()
        return dict(result) if result else {}

# ---------- health ----------

def ping_db() -> bool:
    try:
        with get_conn() as conn:
            return conn.is_connected()
    except Error:
        return False

# ---------- patients ----------

def find_patients(
    input: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    sql = """
        SELECT 
            p.MRN AS MRN, 
            CONCAT(p.First_Name, ' ', p.Last_Name) AS Full_Name, 
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
    
    if input and input.isdigit():
        params = [int(input), search_term_like, search_term_like, int(limit), int(offset)]
    else:
        params = [0, search_term_like, search_term_like, int(limit), int(offset)]
        
    with get_conn() as conn:
        results_dicts = _fetchall(conn, sql, params)
        
        column_keys = ["MRN", "Full_Name", "Birthdate", "Diagnosis", "Doctor_Name", "Doctor_ID"]
        
        results_list = []
        for row_dict in results_dicts:
            row_list = [str(row_dict.get(key, '')) for key in column_keys]
            results_list.append(row_list)
            
        return results_list

def total_patients_count(
    input: Optional[str] = None,
) -> int:
    sql = """
        SELECT COUNT(*) AS cnt
        FROM Patient p
        WHERE p.MRN = %s OR p.First_Name LIKE %s OR p.Last_Name LIKE %s;
    """
    search_term_like = f'%{input}%' if input else '%'
    
    if input and input.isdigit():
        params = [int(input), search_term_like, search_term_like]
    else:
        params = [0, search_term_like, search_term_like]
        
    with get_conn() as conn:
        result = _fetchone(conn, sql, params)
    return int(result.get("cnt", 0))

# ---------- doctors ----------

def find_doctors(
    input: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    sql = """
        SELECT 
            d.Employee_ID AS Employee_ID, 
            CONCAT(d.First_Name,' ',d.Last_Name) AS Full_Name, 
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
    
    if input and input.isdigit():
        params = [int(input), search_term_like, search_term_like, int(limit), int(offset)]
    else:
        params = [0, search_term_like, search_term_like, int(limit), int(offset)]
        
    with get_conn() as conn:
        results_dicts = _fetchall(conn, sql, params)
        
        column_keys = ["Employee_ID", "Full_Name", "Specialty", "Patients"]
        
        results_list = []
        for row_dict in results_dicts:
            row_list = [str(row_dict.get(key, '')) for key in column_keys]
            results_list.append(row_list)
            
        return results_list


def total_doctors_count(
    input: Optional[str] = None,
) -> int:
    sql = """
        SELECT COUNT(*) AS cnt
        FROM Doctor d
        WHERE d.Employee_ID = %s OR d.First_Name LIKE %s OR d.Last_Name LIKE %s
    """
    search_term_like = f'%{input}%' if input else '%'
    
    if input and input.isdigit():
        params = [int(input), search_term_like, search_term_like]
    else:
        params = [0, search_term_like, search_term_like]
        
    with get_conn() as conn:
        result = _fetchone(conn, sql, params)
    return int(result.get("cnt", 0))

# ---------- medical records search ----------

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


def total_medrecs_count(
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

# ---------- billing search ----------

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

def total_billing_count(
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

# ---------- sanity run ----------

if __name__ == "__main__":
    from pprint import pprint
    print("DB reachable:", ping_db())
    pprint(find_patients(input="Ja", limit=10)) 
    pprint(find_doctors(input="Ja", limit=10)) 
    pprint(find_medical_records(input=1001)) 
    pprint(find_billing(input=1001)) 
