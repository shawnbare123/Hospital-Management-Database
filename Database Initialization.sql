
CREATE DATABASE IF NOT EXISTS hospital_db;
USE hospital_db;


DROP TABLE IF EXISTS Billing;
DROP TABLE IF EXISTS Medical_Record;
DROP TABLE IF EXISTS Patient;
DROP TABLE IF EXISTS Doctor;

CREATE TABLE Patient (
  MRN         SMALLINT UNSIGNED PRIMARY KEY,
  First_Name  VARCHAR(20) NOT NULL,
  Last_Name   VARCHAR(20) NOT NULL,
  Birthdate   DATE
) ENGINE=InnoDB;

CREATE TABLE Doctor (
  Employee_ID SMALLINT UNSIGNED PRIMARY KEY,
  First_Name  VARCHAR(20) NOT NULL,
  Last_Name   VARCHAR(20) NOT NULL,
  Specialty   VARCHAR(30)
) ENGINE=InnoDB;

CREATE TABLE Medical_Record (
  Record_ID      SMALLINT UNSIGNED PRIMARY KEY,
  Patient_MRN    SMALLINT UNSIGNED NOT NULL,
  Doctor_ID      SMALLINT UNSIGNED,
  Admission_Date DATE,
  Diagnosis      VARCHAR(100),
  CONSTRAINT fk_medrec_patient
    FOREIGN KEY (Patient_MRN) REFERENCES Patient(MRN)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_medrec_doctor
    FOREIGN KEY (Doctor_ID) REFERENCES Doctor(Employee_ID)
    ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX idx_medrec_patient (Patient_MRN),
  INDEX idx_medrec_doctor  (Doctor_ID),
  INDEX idx_medrec_admdate (Admission_Date)
) ENGINE=InnoDB;

CREATE TABLE Billing (
  Bill_ID        SMALLINT UNSIGNED PRIMARY KEY,
  Patient_MRN    SMALLINT UNSIGNED NOT NULL,
  Insurance_Name VARCHAR(50),
  Amount_Due     DECIMAL(10,2) UNSIGNED DEFAULT 0.00,
  Amount_Paid    DECIMAL(10,2) UNSIGNED DEFAULT 0.00,
  CONSTRAINT fk_bill_patient
    FOREIGN KEY (Patient_MRN) REFERENCES Patient(MRN)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_bill_patient (Patient_MRN)
) ENGINE=InnoDB;

SHOW TABLES;
