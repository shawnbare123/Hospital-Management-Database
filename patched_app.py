import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import updated_db

class MainApp(tk.Tk):


# ------------------- App Setup -------------------


    def __init__(self):
        super().__init__()
        self.title("Hospital Database System")
        self.geometry("1200x700")
        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        # Check for database connection at startup
        if not updated_db.ping_db():
            self.show_error("Database Connection Error", "Failed to connect to the database. Please check your configuration.")
            self.destroy()
            return
        
        self.create_widgets()


# ------------------- GUI Initialization -------------------


    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Creates the tabbed interface
        tabControl = ttk.Notebook(main_frame)
        tabControl.pack(expand=1, fill="both")

        # Creates and adds the tabs
        patient_tab = ttk.Frame(tabControl)
        tabControl.add(patient_tab, text='Search Patients')
        self.create_patient_search_tab(patient_tab)

        doctor_tab = ttk.Frame(tabControl)
        tabControl.add(doctor_tab, text='Search Doctors')
        self.create_doctor_search_tab(doctor_tab)

        records_tab = ttk.Frame(tabControl)
        tabControl.add(records_tab, text='Medical Records')
        self.create_records_tab(records_tab)

        billing_tab = ttk.Frame(tabControl)
        tabControl.add(billing_tab, text='Billing')
        self.create_billing_tab(billing_tab)


    def create_patient_search_tab(self, tab):
        search_frame = ttk.Frame(tab)
        search_frame.pack(fill='x', pady=(10, 5), padx=10)

        # Components are stacked vertically, centered (default for pack without side)
        ttk.Label(search_frame, text="Search (MRN, First Name, Last Name):").pack(pady=(0, 2))
        self.patient_search_var = tk.StringVar()
        # Use fill='x' and padx to stretch the entry box and center it
        ttk.Entry(search_frame, textvariable=self.patient_search_var, width=25).pack(fill='x', padx=500, pady=2)
        ttk.Button(search_frame, text="Search", command=lambda: self.search_patients(self.patient_search_var.get())).pack(pady=(2, 5))

        self.patient_results_text = tk.Text(tab, height=2, state=tk.DISABLED, wrap=tk.WORD)
        self.patient_results_text.pack(pady=5, padx=10, fill='x')

        tree_frame = ttk.Frame(tab)
        tree_frame.pack(expand=True, fill='both', padx=10, pady=5)

        # Treeview
        columns = ("MRN", "Full Name", "Birthdate", "Diagnosis", "Doctor Name", "Doctor ID")
        self.patient_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self.patient_tree.pack(side=tk.LEFT, expand=True, fill='both')

        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.patient_tree.yview)
        vsb.pack(side=tk.RIGHT, fill='y')
        self.patient_tree.configure(yscrollcommand=vsb.set)
        
        # Column formatting
        col_widths = [80, 150, 100, 200, 150, 80]
        for i, col in enumerate(columns):
            self.patient_tree.heading(col, text=col)
            self.patient_tree.column(col, width=col_widths[i], anchor='center')

    def create_doctor_search_tab(self, tab):
        search_frame = ttk.Frame(tab)
        search_frame.pack(fill='x', pady=(10, 5), padx=10)

        # Components are stacked vertically, centered (default for pack without side)
        ttk.Label(search_frame, text="Search (ID, Name):").pack(pady=(0, 2))
        self.doctor_search_var = tk.StringVar()
        # Use fill='x' and padx to stretch the entry box and center it
        ttk.Entry(search_frame, textvariable=self.doctor_search_var, width=25).pack(fill='x', padx=500, pady=2)
        ttk.Button(search_frame, text="Search", command=lambda: self.search_doctors(self.doctor_search_var.get())).pack(pady=(2, 5))

        self.doctor_results_text = tk.Text(tab, height=2, state=tk.DISABLED, wrap=tk.WORD)
        self.doctor_results_text.pack(pady=5, padx=10, fill='x')

        tree_frame = ttk.Frame(tab)
        tree_frame.pack(expand=True, fill='both', padx=10, pady=5)

        # Treeview
        columns = ("Employee ID", "Full Name", "Specialty", "Patients")
        self.doctor_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self.doctor_tree.pack(side=tk.LEFT, expand=True, fill='both')
        
        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.doctor_tree.yview)
        vsb.pack(side=tk.RIGHT, fill='y')
        self.doctor_tree.configure(yscrollcommand=vsb.set)

        # Column formatting
        col_widths = [100, 150, 150, 500]
        for i, col in enumerate(columns):
            self.doctor_tree.heading(col, text=col)
            self.doctor_tree.column(col, width=col_widths[i], anchor='center')

    def create_records_tab(self, tab):
        search_frame = ttk.Frame(tab)
        search_frame.pack(fill='x', pady=(10, 5), padx=10)

        # Components are stacked vertically, centered (default for pack without side)
        ttk.Label(search_frame, text="Search (Record ID, Patient MRN):").pack(pady=(0, 2))
        self.record_search_var = tk.StringVar()
        # Use fill='x' and padx to stretch the entry box and center it
        ttk.Entry(search_frame, textvariable=self.record_search_var, width=25).pack(fill='x', padx=500, pady=2)
        ttk.Button(search_frame, text="Search", command=lambda: self.search_records(self.record_search_var.get())).pack(pady=(2, 5))

        self.record_results_text = tk.Text(tab, height=2, state=tk.DISABLED, wrap=tk.WORD)
        self.record_results_text.pack(pady=5, padx=10, fill='x')

        tree_frame = ttk.Frame(tab)
        tree_frame.pack(expand=True, fill='both', padx=10, pady=5)

        # Treeview
        columns = ("Record ID", "Patient MRN", "Doctor ID", "Admission Date", "Diagnosis")
        self.record_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self.record_tree.pack(side=tk.LEFT, expand=True, fill='both')

        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.record_tree.yview)
        vsb.pack(side=tk.RIGHT, fill='y')
        self.record_tree.configure(yscrollcommand=vsb.set)
        
        # Column formatting
        col_widths = [100, 120, 100, 150, 400]
        for i, col in enumerate(columns):
            self.record_tree.heading(col, text=col)
            self.record_tree.column(col, width=col_widths[i], anchor='center')

    def create_billing_tab(self, tab):
        search_frame = ttk.Frame(tab)
        search_frame.pack(fill='x', pady=(10, 5), padx=10)

        # Components are stacked vertically, centered (default for pack without side)
        ttk.Label(search_frame, text="Search (Bill ID, Patient MRN):").pack(pady=(0, 2))
        self.bill_search_var = tk.StringVar()
        # Use fill='x' and padx to stretch the entry box and center it
        ttk.Entry(search_frame, textvariable=self.bill_search_var, width=25).pack(fill='x', padx=500, pady=2)
        ttk.Button(search_frame, text="Search", command=lambda: self.search_billing(self.bill_search_var.get())).pack(pady=(2, 5))

        self.bill_results_text = tk.Text(tab, height=2, state=tk.DISABLED, wrap=tk.WORD)
        self.bill_results_text.pack(pady=5, padx=10, fill='x')

        tree_frame = ttk.Frame(tab)
        tree_frame.pack(expand=True, fill='both', padx=10, pady=5)

        # Treeview
        columns = ("Bill ID", "Patient MRN", "Insurance Provider", "Amount Due", "Amount Paid")
        self.billing_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self.billing_tree.pack(side=tk.LEFT, expand=True, fill='both')

        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.billing_tree.yview)
        vsb.pack(side=tk.RIGHT, fill='y')
        self.billing_tree.configure(yscrollcommand=vsb.set)
        
        # Column formatting
        col_widths = [100, 120, 200, 100, 100]
        for i, col in enumerate(columns):
            self.billing_tree.heading(col, text=col)
            self.billing_tree.column(col, width=col_widths[i], anchor='center')


# ------------------- Search Functions -------------------


    def search_patients(self, input):
        self.patient_results_text.config(state=tk.NORMAL)
        self.patient_results_text.delete(1.0, tk.END)
        
        try:
            total_count = updated_db.total_patients_count(input=input)
            self.patient_results_text.insert(tk.END, f"Found {total_count} matching patients.\n\n")

            results = updated_db.find_patients(input=input)
            
            self.patient_tree.delete(*self.patient_tree.get_children())
            if results:
                for row in results:
                    self.patient_tree.insert("", tk.END, values=row)
        except Exception as e:
            self.patient_results_text.delete(1.0, tk.END)
            self.show_error("Database Error", f"An error occurred while searching patients: {e}")
        finally:
            self.patient_results_text.config(state=tk.DISABLED)

    def search_doctors(self, input):
        self.doctor_results_text.config(state=tk.NORMAL)
        self.doctor_results_text.delete(1.0, tk.END)
        
        try:
            total_count = updated_db.total_doctors_count(input=input)
            self.doctor_results_text.insert(tk.END, f"Found {total_count} matching doctors.\n\n")

            results = updated_db.find_doctors(input=input)
            
            self.doctor_tree.delete(*self.doctor_tree.get_children())
            if results:
                for row in results:
                    self.doctor_tree.insert("", tk.END, values=row)
        except Exception as e:
            self.doctor_results_text.delete(1.0, tk.END)
            self.show_error("Database Error", f"An error occurred while searching doctors: {e}")
        finally:
            self.doctor_results_text.config(state=tk.DISABLED)


    def search_records(self, input):
        self.record_results_text.config(state=tk.NORMAL)
        self.record_results_text.delete(1.0, tk.END)

        if not input:
            self.record_results_text.insert(tk.END, "Please enter a Record ID or Patient MRN.\n\n")
            self.record_results_text.config(state=tk.DISABLED)
            return

        try:
            total_count = updated_db.total_medrecs_count(input=int(input))
            self.record_results_text.insert(tk.END, f"Found {total_count} matching medical records.\n\n")

            results = updated_db.find_medical_records(input=int(input))
            
            self.record_tree.delete(*self.record_tree.get_children())
            if results:
                for row in results:
                    self.record_tree.insert("", tk.END, values=row)
        except ValueError:
            self.record_results_text.delete(1.0, tk.END)
            self.record_results_text.insert(tk.END, "Invalid input. Please enter a valid number.")
        except Exception as e:
            self.record_results_text.delete(1.0, tk.END)
            self.show_error("Database Error", f"An error occurred while searching records: {e}")
        finally:
            self.record_results_text.config(state=tk.DISABLED)


    def search_billing(self, input):
        self.bill_results_text.config(state=tk.NORMAL)
        self.bill_results_text.delete(1.0, tk.END)
        
        if not input:
            self.bill_results_text.insert(tk.END, "Please enter a Bill ID or Patient MRN.\n\n")
            self.bill_results_text.config(state=tk.DISABLED)
            return

        try:
            total_count = updated_db.total_billing_count(input=int(input))
            self.bill_results_text.insert(tk.END, f"Found {total_count} matching bills.\n\n")

            results = updated_db.find_billing(input=int(input))
            
            self.billing_tree.delete(*self.billing_tree.get_children())
            if results:
                for row in results:
                    self.billing_tree.insert("", tk.END, values=row)
        except ValueError:
            self.bill_results_text.delete(1.0, tk.END)
            self.bill_results_text.insert(tk.END, "Invalid input. Please enter a valid number.")
        except Exception as e:
            self.bill_results_text.delete(1.0, tk.END)
            self.show_error("Database Error", f"An error occurred while searching billing: {e}")
        finally:
            self.bill_results_text.config(state=tk.DISABLED)


# ------------------- Error Handling -------------------


    def show_error(self, title, message):
        messagebox.showerror(title, message)


# ------------------- App Start -------------------


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
