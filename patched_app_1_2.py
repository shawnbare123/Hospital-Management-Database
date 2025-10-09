import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from decimal import Decimal
import updated_db_1_2

class MainApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Hospital Database System - Read/Write Separation")
        self.geometry("1400x850")
        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        try:
            if not updated_db_1_2.ping_db():
                self.show_error("Database Connection Error", "Failed to connect to the database. Please check your configuration.")
                self.destroy()
                return
        except Exception as e:
            self.show_error("Database Initialization Error", f"An error occurred during DB connection check: {e}")
            self.destroy()
            return

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        tabControl = ttk.Notebook(main_frame)
        tabControl.pack(expand=1, fill="both")

        patient_tab = ttk.Frame(tabControl)
        tabControl.add(patient_tab, text='Patient Management')
        self.create_patient_tab_content(patient_tab)

        doctor_tab = ttk.Frame(tabControl)
        tabControl.add(doctor_tab, text='Doctor Management')
        self.create_doctor_tab_content(doctor_tab)

        medrec_tab = ttk.Frame(tabControl)
        tabControl.add(medrec_tab, text='Medical Records')
        self.create_medical_record_tab_content(medrec_tab)

        billing_tab = ttk.Frame(tabControl)
        tabControl.add(billing_tab, text='Billing')
        self.create_billing_tab_content(billing_tab)

    # ------------------- Patient Tab Content -------------------

    def create_patient_tab_content(self, tab):
        self.create_patient_read_ui(tab)
        self.create_patient_write_ui(tab)

    def create_patient_read_ui(self, tab):
        read_frame = ttk.LabelFrame(tab, text="Patient Search & Results", padding="10")
        read_frame.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        search_input_frame = ttk.Frame(read_frame)
        search_input_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(search_input_frame, text="Search by MRN, First Name, or Last Name:").pack(side=tk.LEFT, padx=5)
        self.patient_search_entry = ttk.Entry(search_input_frame, width=30)
        self.patient_search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(search_input_frame, text="Search", command=self.run_patient_search).pack(side=tk.LEFT, padx=5)
        
        self.patient_results_text = tk.Text(read_frame, height=3, state=tk.DISABLED, bg='light yellow')
        self.patient_results_text.pack(fill=tk.X, pady=(0, 5))

        cols = ("MRN", "First Name", "Last Name", "Birthdate (YYYY-MM-DD)")
        self.patient_tree = ttk.Treeview(read_frame, columns=cols, show='headings')
        for col in cols:
            self.patient_tree.heading(col, text=col)
            self.patient_tree.column(col, width=120, anchor=tk.CENTER)
        self.patient_tree.pack(fill=tk.BOTH, expand=True)

    def create_patient_write_ui(self, tab):
        write_frame = ttk.LabelFrame(tab, text="Patient Data Modification", padding="10")
        write_frame.pack(fill=tk.X, padx=5, pady=10)

        patient_fields = ["MRN", "First Name", "Last Name", "Birthdate (YYYY-MM-DD)"]
        self.patient_entries = {}
        for i, field in enumerate(patient_fields):
            row, col = divmod(i, 4)
            ttk.Label(write_frame, text=field + ":").grid(row=row, column=col*2, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(write_frame, width=20)
            entry.grid(row=row, column=col*2 + 1, padx=5, pady=5, sticky=tk.W)
            self.patient_entries[field] = entry

        btn_frame = ttk.Frame(write_frame)
        btn_frame.grid(row=1, column=0, columnspan=8, pady=10)
        
        ttk.Button(btn_frame, text="Add New Patient", command=lambda: self.handle_patient_crud('add')).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Update Patient", command=lambda: self.handle_patient_crud('update')).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Delete Patient", command=lambda: self.handle_patient_crud('delete')).pack(side=tk.LEFT, padx=10)

    def run_patient_search(self):
        input = str(self.patient_search_entry.get().strip())
        self._reset_results(self.patient_results_text, self.patient_tree)

        if not input:
            self._display_message(self.patient_results_text, "Please enter an MRN (number) or Patient Name (text).\n\n")
            return

        try:
            if input.isdigit():
                input = int(input)

            total_count = updated_db_1_2.total_patient_count(input)
            self._display_message(self.patient_results_text, f"Found {total_count} matching patients.\n\n")

            if total_count > 0:
                results = updated_db_1_2.find_patients(input)
                for row in results:
                    tree_values = list(row)
                    self.patient_tree.insert("", tk.END, values=tree_values)

        except Exception as e:
            self._reset_results(self.patient_results_text, self.patient_tree)
            self.show_error("Database Error", f"An error occurred while searching patients: {e}")
        finally:
            self.patient_results_text.config(state=tk.DISABLED)

    def handle_patient_crud(self, operation: str):
        mrn_str = str(self.patient_entries["MRN"].get().strip())
        first_name = self.patient_entries["First Name"].get().strip()
        last_name = self.patient_entries["Last Name"].get().strip()
        birthdate = self.patient_entries["Birthdate (YYYY-MM-DD)"].get().strip()
        
        if not mrn_str or not mrn_str.isdigit():
            self.show_error("Input Error", "MRN must be a valid number.")
            return

        mrn = int(mrn_str)
        
        try:
            if operation == 'add':
                if not first_name or not last_name or not birthdate:
                    self.show_error("Input Error", "First Name, Last Name, and Birthdate are required for ADD.")
                    return
                rows = updated_db_1_2.add_new_patient(mrn, first_name, last_name, birthdate)
                messagebox.showinfo("Success", f"Patient {mrn} added successfully ({rows} row(s) affected).")

            elif operation == 'update':
                fn = first_name or None
                ln = last_name or None
                bd = birthdate or None
                
                if not (fn or ln or bd):
                    self.show_error("Input Error", "At least one field (First Name, Last Name, or Birthdate) must be provided for UPDATE.")
                    return

                rows = updated_db_1_2.update_patient(mrn, fn, ln, bd)
                messagebox.showinfo("Success", f"Patient {mrn} updated successfully.")

            elif operation == 'delete':
                if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Patient {mrn}?"):
                    return
                rows = updated_db_1_2.delete_patient(mrn)
                messagebox.showinfo("Success", f"Patient {mrn} deleted successfully.")
            
            self.run_patient_search() 
            for entry in self.patient_entries.values():
                entry.delete(0, tk.END)

        except ValueError as e:
            self.show_error("Database Error", f"Operation failed (Check data types/formats): {e}")
        except Exception as e:
            self.show_error("Database Error", f"Operation failed: {e}")

    # ------------------- Doctor Tab Content -------------------

    def create_doctor_tab_content(self, tab):
        self.create_doctor_read_ui(tab)
        self.create_doctor_write_ui(tab)

    def create_doctor_read_ui(self, tab):
        read_frame = ttk.LabelFrame(tab, text="Doctor Search & Results", padding="10")
        read_frame.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        search_input_frame = ttk.Frame(read_frame)
        search_input_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(search_input_frame, text="Search by ID, Name, or Specialty:").pack(side=tk.LEFT, padx=5)
        self.doctor_search_entry = ttk.Entry(search_input_frame, width=30)
        self.doctor_search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(search_input_frame, text="Search", command=self.run_doctor_search).pack(side=tk.LEFT, padx=5)

        self.doctor_results_text = tk.Text(read_frame, height=3, state=tk.DISABLED, bg='light yellow')
        self.doctor_results_text.pack(fill=tk.X, pady=(0, 5))

        cols = ("Employee ID", "First Name", "Last Name", "Specialty")
        self.doctor_tree = ttk.Treeview(read_frame, columns=cols, show='headings')
        for col in cols:
            self.doctor_tree.heading(col, text=col)
            self.doctor_tree.column(col, width=120, anchor=tk.CENTER)
        self.doctor_tree.pack(fill=tk.BOTH, expand=True)

    def create_doctor_write_ui(self, tab):
        write_frame = ttk.LabelFrame(tab, text="Doctor Data Modification", padding="10")
        write_frame.pack(fill=tk.X, padx=5, pady=10)

        doctor_fields = ["Employee ID", "First Name", "Last Name", "Specialty"]
        self.doctor_entries = {}
        for i, field in enumerate(doctor_fields):
            row, col = divmod(i, 4)
            ttk.Label(write_frame, text=field + ":").grid(row=row, column=col*2, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(write_frame, width=20)
            entry.grid(row=row, column=col*2 + 1, padx=5, pady=5, sticky=tk.W)
            self.doctor_entries[field] = entry

        btn_frame = ttk.Frame(write_frame)
        btn_frame.grid(row=1, column=0, columnspan=8, pady=10)
        
        ttk.Button(btn_frame, text="Add New Doctor", command=lambda: self.handle_doctor_crud('add')).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Update Doctor", command=lambda: self.handle_doctor_crud('update')).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Delete Doctor", command=lambda: self.handle_doctor_crud('delete')).pack(side=tk.LEFT, padx=10)

    def run_doctor_search(self):
        input = str(self.doctor_search_entry.get().strip())
        self._reset_results(self.doctor_results_text, self.doctor_tree)

        if not input:
            self._display_message(self.doctor_results_text, "Please enter an Employee ID (number), Name, or Specialty (text).\n\n")
            return

        try:
            if input.isdigit():
                input = int(input)

            total_count = updated_db_1_2.total_doctor_count(input)
            self._display_message(self.doctor_results_text, f"Found {total_count} matching doctors.\n\n")

            if total_count > 0:
                results = updated_db_1_2.find_doctors(input)
                for row in results:
                    tree_values = list(row)
                    self.doctor_tree.insert("", tk.END, values=tree_values)

        except Exception as e:
            self._reset_results(self.doctor_results_text, self.doctor_tree)
            self.show_error("Database Error", f"An error occurred while searching doctors: {e}")
        finally:
            self.doctor_results_text.config(state=tk.DISABLED)

    def handle_doctor_crud(self, operation: str):
        id_str = str(self.doctor_entries["Employee ID"].get().strip())
        first_name = self.doctor_entries["First Name"].get().strip()
        last_name = self.doctor_entries["Last Name"].get().strip()
        specialty = self.doctor_entries["Specialty"].get().strip()

        if not id_str or not id_str.isdigit():
            self.show_error("Input Error", "Employee ID must be a valid number.")
            return

        employee_id = int(id_str)
        
        try:
            if operation == 'add':
                if not first_name or not last_name or not specialty:
                    self.show_error("Input Error", "First Name, Last Name, and Specialty are required for ADD.")
                    return
                rows = updated_db_1_2.add_new_doctor(employee_id, first_name, last_name, specialty)
                messagebox.showinfo("Success", f"Doctor {employee_id} added successfully ({rows} row(s) affected).")

            elif operation == 'update':
                fn = first_name or None
                ln = last_name or None
                spec = specialty or None
                
                if not (fn or ln or spec):
                    self.show_error("Input Error", "At least one field must be provided for UPDATE.")
                    return

                rows = updated_db_1_2.update_doctor(employee_id, fn, ln, spec)
                messagebox.showinfo("Success", f"Doctor {employee_id} updated successfully.")

            elif operation == 'delete':
                if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Doctor {employee_id}?"):
                    return
                rows = updated_db_1_2.delete_doctor(employee_id)
                messagebox.showinfo("Success", f"Doctor {employee_id} deleted successfully.")
            
            self.run_doctor_search()
            for entry in self.doctor_entries.values():
                entry.delete(0, tk.END)

        except ValueError as e:
            self.show_error("Database Error", f"Operation failed (Check data types/formats): {e}")
        except Exception as e:
            self.show_error("Database Error", f"Operation failed: {e}")

    # ------------------- Medical Record Tab Content -------------------

    def create_medical_record_tab_content(self, tab):
        self.create_medical_record_read_ui(tab)
        self.create_medical_record_write_ui(tab)

    def create_medical_record_read_ui(self, tab):
        read_frame = ttk.LabelFrame(tab, text="Medical Record Search & Results", padding="10")
        read_frame.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        search_input_frame = ttk.Frame(read_frame)
        search_input_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(search_input_frame, text="Search by Record ID or Patient MRN:").pack(side=tk.LEFT, padx=5)
        self.medrec_search_entry = ttk.Entry(search_input_frame, width=30)
        self.medrec_search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(search_input_frame, text="Search", command=self.run_medical_record_search).pack(side=tk.LEFT, padx=5)

        self.medrec_results_text = tk.Text(read_frame, height=3, state=tk.DISABLED, bg='light yellow')
        self.medrec_results_text.pack(fill=tk.X, pady=(0, 5))

        cols = ("Record ID", "Patient MRN", "Doctor ID (Optional)", "Admission Date (YYYY-MM-DD)", "Diagnosis")
        self.medrec_tree = ttk.Treeview(read_frame, columns=cols, show='headings')
        for col in cols:
            self.medrec_tree.heading(col, text=col)
            self.medrec_tree.column(col, width=120, anchor=tk.CENTER)
        self.medrec_tree.pack(fill=tk.BOTH, expand=True)

    def create_medical_record_write_ui(self, tab):
        write_frame = ttk.LabelFrame(tab, text="Medical Record Data Modification", padding="10")
        write_frame.pack(fill=tk.X, padx=5, pady=10)

        medrec_fields = ["Record ID", "Patient MRN", "Doctor ID (Optional)", "Admission Date (YYYY-MM-DD)", "Diagnosis"]
        self.medrec_entries = {}
        for i, field in enumerate(medrec_fields):
            row, col = divmod(i, 5)
            ttk.Label(write_frame, text=field + ":").grid(row=row, column=col*2, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(write_frame, width=20)
            entry.grid(row=row, column=col*2 + 1, padx=5, pady=5, sticky=tk.W)
            self.medrec_entries[field] = entry

        btn_frame = ttk.Frame(write_frame)
        btn_frame.grid(row=1, column=0, columnspan=10, pady=10)
        
        ttk.Button(btn_frame, text="Add New Record", command=lambda: self.handle_medical_record_crud('add')).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Update Record", command=lambda: self.handle_medical_record_crud('update')).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Delete Record", command=lambda: self.handle_medical_record_crud('delete')).pack(side=tk.LEFT, padx=10)

    def run_medical_record_search(self):
        input = str(self.medrec_search_entry.get().strip())
        self._reset_results(self.medrec_results_text, self.medrec_tree)

        if not input:
            self._display_message(self.medrec_results_text, "Please enter a Record ID or Patient MRN.\n\n")
            return

        try:
            if not input.isdigit():
                self._display_message(self.medrec_results_text, "Invalid input. Please enter a valid number (ID or MRN).")
                return

            input_int = int(input)
            total_count = updated_db_1_2.total_medrec_count(input=input_int)
            self._display_message(self.medrec_results_text, f"Found {total_count} matching records.\n\n")

            if total_count > 0:
                results = updated_db_1_2.find_medical_records(input=input_int)
                for row in results:
                    self.medrec_tree.insert("", tk.END, values=row)

        except Exception as e:
            self._reset_results(self.medrec_results_text, self.medrec_tree)
            self.show_error("Database Error", f"An error occurred while searching medical records: {e}")
        finally:
            self.medrec_results_text.config(state=tk.DISABLED)

    def handle_medical_record_crud(self, operation: str):
        record_id_str = str(self.medrec_entries["Record ID"].get().strip())
        patient_mrn_str = str(self.medrec_entries["Patient MRN"].get().strip())
        doctor_id_str = str(self.medrec_entries["Doctor ID (Optional)"].get().strip())
        admission_date = self.medrec_entries["Admission Date (YYYY-MM-DD)"].get().strip()
        diagnosis = self.medrec_entries["Diagnosis"].get().strip()
        
        if not record_id_str or not record_id_str.isdigit():
            self.show_error("Input Error", "Record ID must be a valid number.")
            return

        record_id = int(record_id_str)

        try:
            if operation == 'add':
                if not patient_mrn_str or not patient_mrn_str.isdigit() or not admission_date or not diagnosis:
                    self.show_error("Input Error", "Record ID, Patient MRN, Admission Date, and Diagnosis are required for ADD.")
                    return
                
                patient_mrn = int(patient_mrn_str)
                doctor_id = int(doctor_id_str) if doctor_id_str.isdigit() else None

                rows = updated_db_1_2.add_new_medical_record(record_id, patient_mrn, doctor_id, admission_date, diagnosis)
                messagebox.showinfo("Success", f"Medical Record {record_id} added successfully ({rows} row(s) affected).")

            elif operation == 'update':
                adm_date = admission_date or None
                diag = diagnosis or None
                
                if not (adm_date or diag):
                    self.show_error("Input Error", "At least one updatable field (Admission Date or Diagnosis) must be provided for UPDATE.")
                    return

                rows = updated_db_1_2.update_medical_record(record_id, adm_date, diag)
                messagebox.showinfo("Success", f"Medical Record {record_id} updated successfully.")

            elif operation == 'delete':
                if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Medical Record {record_id}?"):
                    return
                rows = updated_db_1_2.delete_medical_record(record_id)
                messagebox.showinfo("Success", f"Medical Record {record_id} deleted successfully.")
            
            self.run_medical_record_search()
            for entry in self.medrec_entries.values():
                entry.delete(0, tk.END)

        except ValueError as e:
            self.show_error("Database Error", f"Operation failed (Check data types/formats or FK existence): {e}")
        except Exception as e:
            self.show_error("Database Error", f"Operation failed: {e}")

    # ------------------- Billing Tab Content -------------------

    def create_billing_tab_content(self, tab):
        self.create_billing_read_ui(tab)
        self.create_billing_write_ui(tab)

    def create_billing_read_ui(self, tab):
        read_frame = ttk.LabelFrame(tab, text="Billing Record Search & Results", padding="10")
        read_frame.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        search_input_frame = ttk.Frame(read_frame)
        search_input_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(search_input_frame, text="Search by Bill ID or Patient MRN:").pack(side=tk.LEFT, padx=5)
        self.bill_search_entry = ttk.Entry(search_input_frame, width=30)
        self.bill_search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(search_input_frame, text="Search", command=self.run_billing_search).pack(side=tk.LEFT, padx=5)

        self.bill_results_text = tk.Text(read_frame, height=3, state=tk.DISABLED, bg='light yellow')
        self.bill_results_text.pack(fill=tk.X, pady=(0, 5))

        cols = ("Bill ID", "Patient MRN", "Insurance Provider", "Amount Due", "Amount Paid")
        self.billing_tree = ttk.Treeview(read_frame, columns=cols, show='headings')
        for col in cols:
            self.billing_tree.heading(col, text=col)
            self.billing_tree.column(col, width=120, anchor=tk.CENTER)
        self.billing_tree.pack(fill=tk.BOTH, expand=True)

    def create_billing_write_ui(self, tab):
        write_frame = ttk.LabelFrame(tab, text="Billing Data Modification", padding="10")
        write_frame.pack(fill=tk.X, padx=5, pady=10)

        billing_fields = ["Bill ID", "Patient MRN", "Insurance Provider", "Amount Due (Decimal)", "Amount Paid (Decimal)"]
        self.billing_entries = {}
        for i, field in enumerate(billing_fields):
            row, col = divmod(i, 5)
            ttk.Label(write_frame, text=field + ":").grid(row=row, column=col*2, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(write_frame, width=20)
            entry.grid(row=row, column=col*2 + 1, padx=5, pady=5, sticky=tk.W)
            self.billing_entries[field] = entry

        btn_frame = ttk.Frame(write_frame)
        btn_frame.grid(row=1, column=0, columnspan=10, pady=10)
        
        ttk.Button(btn_frame, text="Add New Bill", command=lambda: self.handle_billing_crud('add')).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Update Bill", command=lambda: self.handle_billing_crud('update')).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Delete Bill", command=lambda: self.handle_billing_crud('delete')).pack(side=tk.LEFT, padx=10)

    def run_billing_search(self):
        input = str(self.bill_search_entry.get().strip())
        self._reset_results(self.bill_results_text, self.billing_tree)

        if not input:
            self._display_message(self.bill_results_text, "Please enter a Bill ID or Patient MRN.\n\n")
            return

        try:
            if not input.isdigit():
                self._display_message(self.bill_results_text, "Invalid input. Please enter a valid number (ID or MRN).")
                return

            input_int = int(input)
            total_count = updated_db_1_2.total_bill_count(input=input_int)
            self._display_message(self.bill_results_text, f"Found {total_count} matching bills.\n\n")

            if total_count > 0:
                results = updated_db_1_2.find_billing(input=input_int)
                for row in results:
                    self.billing_tree.insert("", tk.END, values=row)

        except Exception as e:
            self._reset_results(self.bill_results_text, self.billing_tree)
            self.show_error("Database Error", f"An error occurred while searching billing: {e}")
        finally:
            self.bill_results_text.config(state=tk.DISABLED)

    def handle_billing_crud(self, operation: str):
        bill_id_str = str(self.billing_entries["Bill ID"].get().strip())
        patient_mrn_str = str(self.billing_entries["Patient MRN"].get().strip())
        insurance_provider = self.billing_entries["Insurance Provider"].get().strip()
        amount_due_str = str(self.billing_entries["Amount Due (Decimal)"].get().strip())
        amount_paid_str = str(self.billing_entries["Amount Paid (Decimal)"].get().strip())
        
        if not bill_id_str or not bill_id_str.isdigit():
            self.show_error("Input Error", "Bill ID must be a valid number.")
            return

        bill_id = int(bill_id_str)

        try:
            def safe_decimal(s):
                if not s: return None
                try: return Decimal(s)
                except: raise ValueError(f"Invalid decimal value: '{s}'")

            if operation == 'add':
                if not patient_mrn_str or not patient_mrn_str.isdigit() or not insurance_provider or not amount_due_str or not amount_paid_str:
                    self.show_error("Input Error", "All fields are required for ADD.")
                    return
                
                patient_mrn = int(patient_mrn_str)
                amount_due = safe_decimal(amount_due_str)
                amount_paid = safe_decimal(amount_paid_str)
                
                rows = updated_db_1_2.add_new_bill(bill_id, patient_mrn, insurance_provider, amount_due, amount_paid)
                messagebox.showinfo("Success", f"Bill {bill_id} added successfully ({rows} row(s) affected).")

            elif operation == 'update':
                ins = insurance_provider or None
                due = safe_decimal(amount_due_str)
                paid = safe_decimal(amount_paid_str)
                
                if not (ins or due or paid):
                    self.show_error("Input Error", "At least one updatable field must be provided for UPDATE.")
                    return

                rows = updated_db_1_2.update_billing(bill_id, ins, due, paid)
                messagebox.showinfo("Success", f"Bill {bill_id} updated successfully")

            elif operation == 'delete':
                if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Bill {bill_id}?"):
                    return
                rows = updated_db_1_2.delete_billing(bill_id)
                messagebox.showinfo("Success", f"Bill {bill_id} deleted successfully.")
            
            self.run_billing_search()
            for entry in self.billing_entries.values():
                entry.delete(0, tk.END)

        except ValueError as e:
            self.show_error("Input Error", f"Operation failed (Check numeric/date/decimal formats): {e}")
        except Exception as e:
            self.show_error("Database Error", f"Operation failed: {e}")


    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def _display_message(self, text_widget, message):
        text_widget.insert(tk.END, message)
    
    def _reset_results(self, text_widget, tree_widget):
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        tree_widget.delete(*tree_widget.get_children())

if __name__ == "__main__":
    app = MainApp()
    if not app.winfo_exists():
        exit() 
    app.mainloop()
