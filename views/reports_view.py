import customtkinter as ctk
from tkinter import messagebox, filedialog
import database
import csv

class ReportsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.conn = database.get_connection()
        self.cursor = self.conn.cursor()

        self.setup_ui()
        self.after(100, lambda: self.winfo_toplevel().focus_set())

    def setup_ui(self):
        ctk.CTkLabel(self, text="Data Management & Reports", font=("Arial", 28, "bold")).pack(anchor="w", pady=(0, 20))
        
        # ==========================================
        # EXPORT DATA CARD
        # ==========================================
        export_card = ctk.CTkFrame(self, corner_radius=15)
        export_card.pack(fill="x", pady=10, padx=10, ipady=15)
        
        ctk.CTkLabel(export_card, text="Export Student Data", font=("Arial", 20, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        
        export_desc = (
            "Download a complete backup of all student records in CSV format.\n"
            "This file can be opened directly in Microsoft Excel or Google Sheets."
        )
        ctk.CTkLabel(export_card, text=export_desc, text_color="gray", justify="left").pack(anchor="w", padx=20, pady=(0, 15))
        
        ctk.CTkButton(export_card, text="Export to CSV / Excel", font=("Arial", 14, "bold"), height=40, command=self.export_to_csv, width=220).pack(anchor="w", padx=20, pady=(0, 15))

        # ==========================================
        # IMPORT DATA CARD 
        # ==========================================
        import_card = ctk.CTkFrame(self, corner_radius=15)
        import_card.pack(fill="x", pady=10, padx=10, ipady=15)
        
        ctk.CTkLabel(import_card, text="Import Student Data", font=("Arial", 20, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        
        import_desc = (
            "Upload an existing CSV spreadsheet of students directly into the database.\n"
            "The importer is SMART: It reads your headers to find the data automatically."
        )
        ctk.CTkLabel(import_card, text=import_desc, text_color="gray", justify="left").pack(anchor="w", padx=20, pady=(0, 15))
        
        ctk.CTkButton(
            import_card, 
            text="Import CSV File", 
            font=("Arial", 14, "bold"), 
            height=40, 
            command=self.import_from_csv, 
            fg_color="#28a745", 
            hover_color="#218838", 
            width=220
        ).pack(anchor="w", padx=20, pady=(0, 15))

    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Student Data"
        )
        if not file_path: return 

        try:
            self.cursor.execute("SELECT id, roll, name, department, phone, email, obtained_marks, total_marks, attendance FROM students")
            rows = self.cursor.fetchall()
            column_names = ["ID", "Roll Number", "Name", "Department", "Phone", "Email", "Obtained Marks", "Total Marks", "Attendance %"]
            
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(column_names)
                writer.writerows(rows)
                
            messagebox.showinfo("Success", f"Data successfully exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data:\n{str(e)}")

    def import_from_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Select Student CSV File"
        )
        if not file_path: return

        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader, None)
                
                if not header:
                    messagebox.showwarning("Warning", "The selected file is empty.")
                    return

                # Convert headers to lowercase for flexible matching
                headers = [str(h).strip().lower() for h in header]
                
                # 🌟 SMART MATCHING: Finds column numbers based on header text!
                def get_idx(*possible_names):
                    for name in possible_names:
                        for i, h in enumerate(headers):
                            if name in h: return i
                    return -1

                idx_roll = get_idx('roll')
                idx_name = get_idx('name', 'student')
                idx_dept = get_idx('dept', 'department')
                idx_phone = get_idx('phone', 'contact')
                idx_email = get_idx('email')
                
                idx_ob = get_idx('obtained')
                idx_tot = get_idx('total')
                idx_marks = get_idx('marks')
                idx_att = get_idx('attendance', 'att')

                if idx_roll == -1 or idx_name == -1:
                    messagebox.showerror("Import Error", "Your CSV file must have column headers for at least 'Roll' and 'Name'.")
                    return

                inserted_count = 0
                for row in reader:
                    if not row: continue
                    
                    while len(row) < len(headers): row.append("")
                    
                    roll = row[idx_roll].strip() if idx_roll != -1 else ""
                    name = row[idx_name].strip() if idx_name != -1 else ""
                    dept = row[idx_dept].strip() if idx_dept != -1 else ""
                    phone = row[idx_phone].strip() if idx_phone != -1 else ""
                    email = row[idx_email].strip() if idx_email != -1 else ""
                    
                    if not roll or not name: continue

                    # Parse Marks Safely
                    ob, tot = None, None
                    if idx_ob != -1 and idx_tot != -1:
                        try: ob = float(row[idx_ob].strip())
                        except: pass
                        try: tot = float(row[idx_tot].strip())
                        except: pass
                    elif idx_marks != -1:
                        m_str = row[idx_marks].strip()
                        if "/" in m_str:
                            try:
                                parts = m_str.split("/")
                                ob, tot = float(parts[0]), float(parts[1])
                            except: pass

                    # Parse Attendance Safely
                    att = None
                    if idx_att != -1:
                        att_str = row[idx_att].strip().replace('%', '')
                        try: att = float(att_str)
                        except: pass
                        
                        # Added a safety cap to ensure attendance can't exceed 100%
                        if att is not None and att > 100:
                            att = 100.0

                    self.cursor.execute("""
                        INSERT INTO students (roll, name, department, phone, email, obtained_marks, total_marks, attendance, profile_pic)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL)
                    """, (roll, name, dept, phone, email, ob, tot, att))
                    inserted_count += 1

                self.conn.commit()
                messagebox.showinfo("Success", f"Successfully imported {inserted_count} student records!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import data:\n{str(e)}")