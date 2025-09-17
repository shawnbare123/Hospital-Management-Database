CREATE DATABASE IF NOT EXISTS hospital_db;
USE hospital_db;

DROP TABLE IF EXISTS Patients;
DROP TABLE IF EXISTS Doctors;
DROP TABLE IF EXISTS Medical_Records;
DROP TABLE IF EXISTS Billing;

CREATE TABLE Patients (
	MRN SMALLINT UNSIGNED PRIMARY KEY,
    First_Name VARCHAR(20),
    Last_Name VARCHAR(20),
    Birthdate DATE
);

CREATE TABLE Doctors (
	Employee_ID SMALLINT UNSIGNED PRIMARY KEY,
    First_Name VARCHAR(20),
    Last_Name VARCHAR(20),
    Specialty VARCHAR(30)
);

CREATE TABLE Medical_Records (
	Record_ID SMALLINT UNSIGNED PRIMARY KEY,
    Patient_MRN SMALLINT UNSIGNED,
    Doctor_ID SMALLINT UNSIGNED,
    Admission_Date DATE,
    Diagnosis VARCHAR(100),
    FOREIGN KEY (Patient_MRN) REFERENCES Patients(MRN),
    FOREIGN KEY (Doctor_ID) REFERENCES Doctors(Employee_ID)
);

CREATE TABLE Billing (
	Bill_ID SMALLINT UNSIGNED PRIMARY KEY,
    Patient_MRN SMALLINT UNSIGNED,
    Insurance_Name VARCHAR(50),
    Amount_Due DECIMAL UNSIGNED,
    Amount_Paid DECIMAL UNSIGNED,
    FOREIGN KEY (Patient_MRN) REFERENCES Patients(MRN)
);

show tables;