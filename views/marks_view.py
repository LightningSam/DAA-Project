import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import database
import os
from fpdf import FPDF

class MarksView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=20, pady=20)

        self.conn = database.get_connection()
        self.cursor = self.conn.cursor()

        self.selected_student_id = None
        self.selected_student_name = ""

        self.setup_ui()
        self.refresh_student_table()
        
        self.after(100, lambda: self.winfo_toplevel().focus_set())

    def setup_ui(self):
        # =========================
        # TOP PANEL: STUDENT SELECTOR
        # =========================
        top_frame = ctk.CTkFrame(self, corner_radius=10)
        top_frame.pack(fill='x', pady=(0, 15))
        
        search_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        search_frame.pack(fill='x', padx=15, pady=10)
        ctk.CTkLabel(search_frame, text="1. Select Student:", font=("Arial", 16, "bold")).pack(side='left', padx=(0, 10))
        self.search_entry = ctk.CTkEntry(search_frame, width=250, placeholder_text="Search Roll or Name")
        self.search_entry.pack(side='left', padx=(0, 10))
        self.search_entry.bind("<Return>", lambda event: self.refresh_student_table())
        ctk.CTkButton(search_frame, text="Search", command=self.refresh_student_table, width=100).pack(side='left', padx=5)

        columns = ("ID", "Roll Number", "Student Name", "Department")
        self.student_table = ttk.Treeview(top_frame, columns=columns, show='headings', height=4)
        for col in columns:
            self.student_table.heading(col, text=col)
            self.student_table.column(col, width=100 if col == "ID" else 200)
        self.student_table.pack(fill='x', padx=15, pady=(0, 15))
        self.student_table.bind("<<TreeviewSelect>>", self.on_student_select)

        # =========================
        # BOTTOM PANEL: ACADEMIC DASHBOARD
        # =========================
        self.dashboard_frame = ctk.CTkFrame(self, corner_radius=10)
        self.dashboard_frame.pack(fill='both', expand=True)

        header_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        header_frame.pack(fill='x', padx=20, pady=15)
        
        self.student_name_label = ctk.CTkLabel(header_frame, text="No Student Selected", font=("Arial", 20, "bold"), text_color="#1f6aa5")
        self.student_name_label.pack(side='left')

        # NEW: PDF Export Button
        ctk.CTkButton(header_frame, text="📄 Export PDF Report", command=self.generate_pdf, fg_color="#ff9800", hover_color="#f57c00", text_color="black", font=("Arial", 14, "bold")).pack(side='left', padx=20)

        sem_control_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        sem_control_frame.pack(side='right')
        
        ctk.CTkLabel(sem_control_frame, text="Current Semester:", font=("Arial", 14, "bold")).pack(side='left', padx=10)
        self.semester_var = ctk.StringVar(value="Semester 1")
        self.sem_dropdown = ctk.CTkOptionMenu(sem_control_frame, variable=self.semester_var, 
                                              values=[f"Semester {i}" for i in range(1, 9)],
                                              command=self.on_semester_change)
        self.sem_dropdown.pack(side='left', padx=5)
        ctk.CTkButton(sem_control_frame, text="Next Semester ➡", command=self.go_next_semester, fg_color="#28a745", hover_color="#218838").pack(side='left', padx=10)

        form_frame = ctk.CTkFrame(self.dashboard_frame)
        form_frame.pack(fill='x', padx=20, pady=5)
        
        ctk.CTkLabel(form_frame, text="Subject Name", font=("Arial", 12, "bold"), text_color="gray").grid(row=0, column=0, padx=10, pady=(10,0), sticky="w")
        ctk.CTkLabel(form_frame, text="Marks Obtained", font=("Arial", 12, "bold"), text_color="gray").grid(row=0, column=1, padx=10, pady=(10,0), sticky="w")
        ctk.CTkLabel(form_frame, text="Maximum Marks", font=("Arial", 12, "bold"), text_color="gray").grid(row=0, column=2, padx=10, pady=(10,0), sticky="w")
        
        self.subject_entry = ctk.CTkEntry(form_frame, width=250, font=("Arial", 14))
        self.subject_entry.grid(row=1, column=0, padx=10, pady=(0, 15))
        
        self.obtained_entry = ctk.CTkEntry(form_frame, width=120, font=("Arial", 14))
        self.obtained_entry.grid(row=1, column=1, padx=10, pady=(0, 15))
        
        self.max_entry = ctk.CTkEntry(form_frame, width=120, font=("Arial", 14))
        self.max_entry.insert(0, "100") 
        self.max_entry.grid(row=1, column=2, padx=10, pady=(0, 15))
        
        self.obtained_entry.bind("<Return>", lambda e: self.add_subject_mark())
        
        ctk.CTkButton(form_frame, text="Add Subject", font=("Arial", 14, "bold"), command=self.add_subject_mark).grid(row=1, column=3, padx=15, pady=(0, 15))
        ctk.CTkButton(form_frame, text="Delete Selected", fg_color="#d32f2f", hover_color="#b71c1c", command=self.delete_subject).grid(row=1, column=4, padx=5, pady=(0, 15))

        subj_cols = ("Record ID", "Subject", "Obtained", "Total", "Percentage")
        self.subject_table = ttk.Treeview(self.dashboard_frame, columns=subj_cols, show='headings', height=6)
        for col in subj_cols:
            self.subject_table.heading(col, text=col)
            self.subject_table.column(col, width=80 if col == "Record ID" else 150)
        self.subject_table.pack(fill='both', expand=True, padx=20, pady=10)

        summary_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="#1f6aa5", corner_radius=5)
        summary_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.summary_label = ctk.CTkLabel(summary_frame, text="Semester Totals: 0 / 0  |  Percentage: 0.00%  |  Grade: N/A", font=("Arial", 16, "bold"), text_color="white")
        self.summary_label.pack(pady=10)
        
        self.disable_dashboard()

    # =========================
    # LOGIC & DB METHODS
    # =========================
    def calculate_grade(self, percentage):
        if percentage >= 90: return "A+"
        elif percentage >= 80: return "A"
        elif percentage >= 70: return "B"
        elif percentage >= 60: return "C"
        elif percentage >= 50: return "D"
        else: return "F"

    def refresh_student_table(self):
        keyword = self.search_entry.get().strip()
        for row in self.student_table.get_children():
            self.student_table.delete(row)
            
        self.cursor.execute("SELECT id, roll, name, department FROM students WHERE name LIKE ? OR roll LIKE ?", (f'%{keyword}%', f'%{keyword}%'))
        for row in self.cursor.fetchall():
            self.student_table.insert('', 'end', values=row)

    def on_student_select(self, event):
        selected = self.student_table.focus()
        if not selected: return
        
        values = self.student_table.item(selected, 'values')
        self.selected_student_id = values[0]
        self.selected_student_name = values[2]
        
        self.student_name_label.configure(text=f"Managing Grades for: {self.selected_student_name}")
        self.enable_dashboard()
        self.refresh_subject_table()

    def on_semester_change(self, choice):
        self.refresh_subject_table()

    def go_next_semester(self):
        current_val = self.semester_var.get()
        current_num = int(current_val.split(" ")[1])
        if current_num < 8:
            next_sem = f"Semester {current_num + 1}"
            self.semester_var.set(next_sem)
            self.refresh_subject_table()

    def add_subject_mark(self):
        if not self.selected_student_id: return
        
        subject = self.subject_entry.get().strip()
        try:
            ob = float(self.obtained_entry.get())
            tot = float(self.max_entry.get())
            if tot <= 0 or ob < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Marks must be valid positive numbers.")
            return
            
        if not subject:
            messagebox.showerror("Error", "Subject Name is required.")
            return

        sem_num = int(self.semester_var.get().split(" ")[1])
        
        self.cursor.execute("INSERT INTO academic_records (student_id, semester, subject_name, obtained_marks, max_marks) VALUES (?, ?, ?, ?, ?)", (self.selected_student_id, sem_num, subject, ob, tot))
        self.conn.commit()
        
        self.sync_cumulative_marks()
        
        self.subject_entry.delete(0, 'end')
        self.obtained_entry.delete(0, 'end')
        self.subject_entry.focus_set()
        self.refresh_subject_table()

    def delete_subject(self):
        selected = self.subject_table.focus()
        if not selected: return
        
        record_id = self.subject_table.item(selected, 'values')[0]
        self.cursor.execute("DELETE FROM academic_records WHERE id=?", (record_id,))
        self.conn.commit()
        
        self.sync_cumulative_marks()
        self.refresh_subject_table()

    def refresh_subject_table(self):
        if not self.selected_student_id: return
        
        for row in self.subject_table.get_children():
            self.subject_table.delete(row)
            
        sem_num = int(self.semester_var.get().split(" ")[1])
        self.cursor.execute("SELECT id, subject_name, obtained_marks, max_marks FROM academic_records WHERE student_id=? AND semester=?", (self.selected_student_id, sem_num))
        
        total_ob = 0
        total_max = 0
        
        for row in self.cursor.fetchall():
            pct = (row[2] / row[3]) * 100 if row[3] > 0 else 0
            self.subject_table.insert('', 'end', values=(row[0], row[1], row[2], row[3], f"{pct:.1f}%"))
            total_ob += row[2]
            total_max += row[3]

        if total_max > 0:
            overall_pct = (total_ob / total_max) * 100
            grade = self.calculate_grade(overall_pct)
            summary_txt = f"Semester {sem_num} Totals: {total_ob:g} / {total_max:g}  |  Percentage: {overall_pct:.2f}%  |  Grade: {grade}"
        else:
            summary_txt = f"Semester {sem_num} Totals: 0 / 0  |  Percentage: 0.00%  |  Grade: N/A"
            
        self.summary_label.configure(text=summary_txt)

    def sync_cumulative_marks(self):
        self.cursor.execute("SELECT SUM(obtained_marks), SUM(max_marks) FROM academic_records WHERE student_id=?", (self.selected_student_id,))
        res = self.cursor.fetchone()
        ob_tot = res[0] if res[0] is not None else None
        max_tot = res[1] if res[1] is not None else None
        
        self.cursor.execute("UPDATE students SET obtained_marks=?, total_marks=? WHERE id=?", (ob_tot, max_tot, self.selected_student_id))
        self.conn.commit()

    # =========================
    # NEW: PDF GENERATION ENGINE
    # =========================
    def generate_pdf(self):
        if not self.selected_student_id:
            messagebox.showwarning("Warning", "Please select a student to generate a report.")
            return

        # Fetch Student Details
        self.cursor.execute("SELECT roll, name, department, attendance, obtained_marks, total_marks FROM students WHERE id=?", (self.selected_student_id,))
        student = self.cursor.fetchone()
        if not student: return
        roll, name, dept, attendance, total_ob, total_max = student

        # Ask user where to save the PDF
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"ReportCard_{roll}_{name}.pdf".replace(" ", "_"),
            filetypes=[("PDF Files", "*.pdf")],
            title="Save Report Card"
        )
        if not file_path: return

        try:
            pdf = FPDF()
            pdf.add_page()
            
            # --- Header ---
            pdf.set_font("Arial", 'B', 24)
            pdf.cell(200, 15, txt="Official Academic Report Card", ln=True, align='C')
            pdf.ln(10)

            # --- Student Information ---
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(40, 10, txt="Student Name: ")
            pdf.set_font("Arial", '', 12)
            pdf.cell(100, 10, txt=str(name))
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(30, 10, txt="Roll No: ")
            pdf.set_font("Arial", '', 12)
            pdf.cell(30, 10, txt=str(roll), ln=True)

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(40, 10, txt="Department: ")
            pdf.set_font("Arial", '', 12)
            pdf.cell(100, 10, txt=str(dept))
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(30, 10, txt="Attendance: ")
            pdf.set_font("Arial", '', 12)
            pdf.cell(30, 10, txt=f"{attendance}%" if attendance else "N/A", ln=True)
            pdf.ln(10)

            # --- Subject Marks Table ---
            self.cursor.execute("SELECT semester, subject_name, obtained_marks, max_marks FROM academic_records WHERE student_id=? ORDER BY semester", (self.selected_student_id,))
            records = self.cursor.fetchall()

            if records:
                # Table Header
                pdf.set_font("Arial", 'B', 11)
                pdf.set_fill_color(200, 220, 255)
                pdf.cell(30, 10, "Semester", border=1, fill=True, align='C')
                pdf.cell(80, 10, "Subject", border=1, fill=True, align='C')
                pdf.cell(30, 10, "Obtained", border=1, fill=True, align='C')
                pdf.cell(30, 10, "Max Marks", border=1, fill=True, align='C')
                pdf.cell(20, 10, "Grade", border=1, fill=True, align='C', ln=True)

                # Table Data
                pdf.set_font("Arial", '', 11)
                for rec in records:
                    sem, subj, ob, mx = rec
                    pct = (ob / mx) * 100 if mx > 0 else 0
                    grade = self.calculate_grade(pct)
                    
                    pdf.cell(30, 10, f"Sem {sem}", border=1, align='C')
                    pdf.cell(80, 10, str(subj), border=1)
                    pdf.cell(30, 10, str(ob), border=1, align='C')
                    pdf.cell(30, 10, str(mx), border=1, align='C')
                    pdf.cell(20, 10, str(grade), border=1, align='C', ln=True)
            else:
                pdf.set_font("Arial", 'I', 12)
                pdf.cell(200, 10, txt="No subject records found for this student.", ln=True, align='C')

            # --- Final Summary Footer ---
            pdf.ln(10)
            if total_ob is not None and total_max is not None and total_max > 0:
                final_pct = (total_ob / total_max) * 100
                final_grade = self.calculate_grade(final_pct)
                
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, txt=f"Cumulative Performance", ln=True)
                pdf.set_font("Arial", '', 12)
                pdf.cell(200, 10, txt=f"Total Score: {total_ob:g} / {total_max:g}", ln=True)
                pdf.cell(200, 10, txt=f"Final Percentage: {final_pct:.2f}%", ln=True)
                pdf.cell(200, 10, txt=f"Final Grade: {final_grade}", ln=True)

            pdf.output(file_path)
            messagebox.showinfo("Success", f"Report card saved successfully to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to generate PDF:\n{str(e)}")

    def disable_dashboard(self):
        self.subject_entry.configure(state="disabled")
        self.obtained_entry.configure(state="disabled")
        self.max_entry.configure(state="disabled")
        self.sem_dropdown.configure(state="disabled")

    def enable_dashboard(self):
        self.subject_entry.configure(state="normal")
        self.obtained_entry.configure(state="normal")
        self.max_entry.configure(state="normal")
        self.sem_dropdown.configure(state="normal")