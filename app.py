import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from pprint import pprint
import db

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Database Search")
        self.geometry("800x600")
        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        # Check for database connection at startup
        if not db.ping_db():
            self.show_error("Database Connection Error", "Failed to connect to the database. Please check your configuration.")
            self.destroy()
            return
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Creates the tabbed interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Creates and adds the tabs
        self.patient_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.patient_tab, text="Patient Search")
        self.create_patient_search_tab(self.patient_tab)

        self.doctor_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.doctor_tab, text="Doctor Search")
        self.create_doctor_search_tab(self.doctor_tab)

        self.records_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.records_tab, text="Medical Records")
        self.create_records_tab(self.records_tab)

        self.doc_patients_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.doc_patients_tab, text="Patient for Doctor")
        self.create_doc_patients_tab(self.doc_patients_tab)

    def create_patient_search_tab(self, parent_frame):
        # Creates input fields for patient search
        ttk.Label(parent_frame, text="Search for Patients", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(parent_frame, text="MRN:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.patient_mrn_entry = ttk.Entry(parent_frame)
        self.patient_mrn_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(parent_frame, text="First Name:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.patient_first_entry = ttk.Entry(parent_frame)
        self.patient_first_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(parent_frame, text="Last Name:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.patient_last_entry = ttk.Entry(parent_frame)
        self.patient_last_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        # Search button
        ttk.Button(parent_frame, text="Search", command=self.search_patients).grid(row=4, column=0, columnspan=2, pady=10)

        # Results field
        self.patient_results_text = tk.Text(parent_frame, wrap=tk.WORD, height=20, width=70, state=tk.DISABLED)
        self.patient_results_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Grid configuration
        parent_frame.grid_columnconfigure(1, weight=1)
        parent_frame.grid_rowconfigure(5, weight=1)

    def search_patients(self):
        self.patient_results_text.delete(1.0, tk.END)
        mrn = self.patient_mrn_entry.get() or None
        first = self.patient_first_entry.get() or None
        last = self.patient_last_entry.get() or None

        if mrn is not None:
            try:
                mrn = int(mrn)
            except ValueError:
                self.patient_results_text.insert(tk.END, "Invalid MRN. Please enter a number.")
                return
        try:
            total_count = db.total_patients_count(mrn=mrn, first=first, last=last)
            self.patient_results_text.insert(tk.END, f"Found {total_count} matching patients.\n\n")

            results = db.find_patients(mrn=mrn, first=first, last=last)
            self.patient_results_text.insert(tk.END, "Results:\n")
            self.patient_results_text.insert(tk.END, pprint.pformat(results))

        except Exception as e:
            self.show_error("Database Error", f"An error occurred: {e}")

    def create_doctor_search_tab(self, parent_frame):
        # Creates input fields for doctor search
        ttk.Label(parent_frame, text="Search for Doctors", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(parent_frame, text="Employee ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.doctor_id_entry = ttk.Entry(parent_frame)
        self.doctor_id_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(parent_frame, text="First Name:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.doctor_first_entry = ttk.Entry(parent_frame)
        self.doctor_first_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(parent_frame, text="Last Name:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.doctor_last_entry = ttk.Entry(parent_frame)
        self.doctor_last_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        # Search button
        ttk.Button(parent_frame, text="Search", command=self.search_doctors).grid(row=4, column=0, columnspan=2, pady=10)

        # Results field
        self.doctor_results_text = tk.Text(parent_frame, wrap=tk.WORD, height=20, width=70, state=tk.DISABLED)
        self.doctor_results_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Grid configuration
        parent_frame.grid_columnconfigure(1, weight=1)
        parent_frame.grid_rowconfigure(5, weight=1)

    def search_doctors(self):
        self.doctor_results_text.delete(1.0, tk.END)
        employee_id = self.doctor_id_entry.get() or None
        first = self.doctor_first_entry.get() or None
        last = self.doctor_last_entry.get() or None

        if employee_id is not None:
            try:
                employee_id = int(employee_id)
            except ValueError:
                self.doctor_results_text.insert(tk.END, "Invalid Employee ID. Please enter a number.")
                return

        try:
            total_count = db.total_doctors_count(employee_id=employee_id, first=first, last=last)
            self.doctor_results_text.insert(tk.END, f"Found {total_count} matching doctors.\n\n")

            results = db.find_doctors(employee_id=employee_id, first=first, last=last, limit=50)
            self.doctor_results_text.insert(tk.END, "Results:\n")
            self.doctor_results_text.insert(tk.END, pprint.pformat(results))
        
        except Exception as e:
            self.show_error("Database Error", f"An error occurred: {e}")

    def create_records_tab(self, parent_frame):
        # Creates fields for medical record search
        ttk.Label(parent_frame, text="Get Medical Records for a Patient", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(parent_frame, text="Patient MRN:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.records_mrn_entry = ttk.Entry(parent_frame)
        self.records_mrn_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Search button
        ttk.Button(parent_frame, text="Search", command=self.get_patient_records).grid(row=2, column=0, columnspan=2, pady=10)

        # Results field
        self.records_results_text = tk.Text(parent_frame, wrap=tk.WORD, height=20, width=70, state=tk.DISABLED)
        self.records_results_text.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # Grid configuration
        parent_frame.grid_columnconfigure(1, weight=1)
        parent_frame.grid_rowconfigure(3, weight=1)

    def get_patient_records(self):
        self.records_results_text.delete(1.0, tk.END)
        mrn_str = self.records_mrn_entry.get()
        
        if not mrn_str:
            self.records_results_text.insert(tk.END, "Please enter a Patient MRN.")
            return
            
        try:
            mrn = int(mrn_str)
            records = db.medical_records_for_patient(mrn)
            if records:
                self.records_results_text.insert(tk.END, pprint.pformat(records))
            else:
                self.records_results_text.insert(tk.END, f"No medical records found for patient MRN: {mrn}")
        except ValueError:
            self.records_results_text.insert(tk.END, "Invalid MRN. Please enter a valid number.")
        except Exception as e:
            self.show_error("Database Error", f"An error occurred: {e}")

    def create_doc_patients_tab(self, parent_frame):
        # Creates fields for patients of doctor search
        ttk.Label(parent_frame, text="Get Patients of a Doctor", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(parent_frame, text="Doctor Employee ID:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.doc_patients_id_entry = ttk.Entry(parent_frame)
        self.doc_patients_id_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Search button
        ttk.Button(parent_frame, text="Search", command=self.get_doctors_patients).grid(row=2, column=0, columnspan=2, pady=10)

        # Results field
        self.doc_patients_results_text = tk.Text(parent_frame, wrap=tk.WORD, height=20, width=70, state=tk.DISABLED)
        self.doc_patients_results_text.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # Grid configuration
        parent_frame.grid_columnconfigure(1, weight=1)
        parent_frame.grid_rowconfigure(3, weight=1)

    def get_doctors_patients(self):
        self.doc_patients_results_text.delete(1.0, tk.END)
        employee_id_str = self.doc_patients_id_entry.get()

        if not employee_id_str:
            self.doc_patients_results_text.insert(tk.END, "Please enter a Doctor Employee ID.")
            return

        try:
            employee_id = int(employee_id_str)
            patients = db.patients_for_doctor(employee_id)
            if patients:
                self.doc_patients_results_text.insert(tk.END, pprint.pformat(patients))
            else:
                self.doc_patients_results_text.insert(tk.END, f"No patients found for doctor with Employee ID: {employee_id}")
        except ValueError:
            self.doc_patients_results_text.insert(tk.END, "Invalid Employee ID. Please enter a valid number.")
        except Exception as e:
            self.show_error("Database Error", f"An error occurred: {e}")

    def show_error(self, title, message):
        # Creates and displays an error message pop-up
        messagebox.showerror(title, message)

if __name__ == "__main__":
    app = MainApp()
    if app.winfo_exists():
        app.mainloop()