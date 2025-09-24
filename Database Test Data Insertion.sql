USE hospital_db;

INSERT INTO Patient (MRN, First_Name, Last_Name, Birthdate) VALUES
(1001,'John','Doe','1985-04-12'),
(1002,'Jane','Smith','1992-07-21'),
(1003,'Peter','Jones','2010-11-05'),
(1004,'Emily','Brown','1975-02-28'),
(1005,'Michael','Johnson','1968-09-10'),
(1006,'Sarah','Williams','2001-03-17'),
(1007,'Chris','Miller','1995-12-01'),
(1008,'Anna','Garcia','1989-06-25'),
(1009,'Daniel','Davis','1980-08-14'),
(1010,'Olivia','Wilson','1998-05-30');

INSERT INTO Doctor (Employee_ID, First_Name, Last_Name, Specialty) VALUES
(101,'Susan','Chen','Cardiology'),
(102,'James','Rodriguez','Neurology'),
(103,'Maria','Garcia','Pediatrics'),
(104,'David','Lee','Oncology'),
(105,'Samantha','Jones','Dermatology'),
(106,'Robert','Miller','Orthopedics'),
(107,'Laura','Wilson','Gastroenterology'),
(108,'Mark','Davis','Endocrinology'),
(109,'Jessica','Taylor','Rheumatology'),
(110,'Kevin','Brown','Anesthesiology');

INSERT INTO Medical_Record (Record_ID, Patient_MRN, Doctor_ID, Admission_Date, Diagnosis) VALUES
(1,1001,101,'2023-01-15','Hypertension'),
(2,1002,102,'2023-02-20','Migraine'),
(3,1003,103,'2023-03-10','Common Cold'),
(4,1001,102,'2023-05-22','Post-concussion syndrome'),
(5,1004,104,'2023-04-01','Breast Cancer'),
(6,1005,106,'2023-06-12','Osteoarthritis'),
(7,1006,105,'2023-07-07','Acne Vulgaris'),
(8,1007,107,'2023-08-19','Gastroesophageal Reflux Disease'),
(9,1008,108,'2023-09-02','Diabetes Type 2'),
(10,1009,109,'2023-10-25','Rheumatoid Arthritis'),
(11,1010,110,'2023-11-18','Anesthesia for Surgery');

INSERT INTO Billing (Bill_ID, Patient_MRN, Insurance_Name, Amount_Due, Amount_Paid) VALUES
(201,1001,'Blue Cross Blue Shield',550.00,550.00),
(202,1002,'Aetna',125.50,0.00),
(203,1003,'Cigna',30.00,30.00),
(204,1004,'United Healthcare',1500.00,1000.00),
(205,1005,'Medicare',250.00,250.00),
(206,1006,'Cigna',75.00,0.00),
(207,1007,'Aetna',200.00,200.00),
(208,1008,'Blue Cross Blue Shield',400.00,350.00),
(209,1009,'United Healthcare',600.00,0.00),
(210,1010,'Medicare',800.00,800.00);
