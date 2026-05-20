import customtkinter as ctk
from tkinter import messagebox
import database
from datetime import datetime

class AttendanceView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True)

        self.conn = database.get_connection()
        self.cursor = self.conn.cursor()

        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.checkbox_vars = {} 

        self.setup_ui()
        self.load_students()
        
        self.after(100, lambda: self.winfo_toplevel().focus_set())

    def setup_ui(self):
        # =========================
        # HEADER & DATE
        # =========================
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill='x', padx=20, pady=(20, 5))
        
        ctk.CTkLabel(header_frame, text="Daily Attendance Register", font=("Arial", 28, "bold")).pack(side="left")
        ctk.CTkLabel(header_frame, text=f"Today's Date: {self.current_date}", font=("Arial", 18, "bold"), text_color="#1f6aa5").pack(side="right")

        # =========================
        # 🌟 NEW: SEARCH SECTION
        # =========================
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill='x', padx=20, pady=(5, 10))
        
        ctk.CTkLabel(search_frame, text="Search Student:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 10))
        self.search_entry = ctk.CTkEntry(search_frame, width=300, font=("Arial", 14), placeholder_text="Enter Name or Roll")
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search_students())
        
        ctk.CTkButton(search_frame, text="Search", command=self.search_students, width=100, font=("Arial", 14)).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Clear Search", command=self.clear_search, width=100, fg_color="gray", hover_color="#555555", font=("Arial", 14)).pack(side="left", padx=5)

        # =========================
        # BULK CONTROLS
        # =========================
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(fill='x', padx=20, pady=10)
        
        btn_font = ("Arial", 14, "bold")
        ctk.CTkButton(control_frame, text="Mark All Present", command=self.mark_all, fg_color="#28a745", hover_color="#218838", font=btn_font).pack(side="left", padx=15, pady=15)
        ctk.CTkButton(control_frame, text="Clear All (Absent)", command=self.clear_all, fg_color="#d32f2f", hover_color="#b71c1c", font=btn_font).pack(side="left", padx=5, pady=15)
        
        ctk.CTkButton(control_frame, text="Save Today's Attendance", command=self.save_attendance, font=("Arial", 15, "bold"), height=40).pack(side="right", padx=15, pady=15)

        # =========================
        # TABLE HEADERS
        # =========================
        col_frame = ctk.CTkFrame(self, fg_color="transparent")
        col_frame.pack(fill='x', padx=35, pady=(10, 5))
        
        header_font = ("Arial", 15, "bold")
        ctk.CTkLabel(col_frame, text="Roll Number", font=header_font, width=150, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(col_frame, text="Student Name", font=header_font, width=300, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(col_frame, text="Status (Check = Present)", font=header_font, anchor="w").pack(side="right", padx=45)

        # =========================
        # SCROLLABLE STUDENT LIST
        # =========================
        self.scroll_frame = ctk.CTkScrollableFrame(self, corner_radius=15)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # =========================
    # SEARCH LOGIC
    # =========================
    def search_students(self):
        keyword = self.search_entry.get().strip()
        self.load_students(keyword)

    def clear_search(self):
        self.search_entry.delete(0, 'end')
        self.load_students()

    def load_students(self, keyword=""):
        # 🌟 Memory-Safe Checkbox Logic: Save current UI states into a dictionary before destroying the view
        current_states = {s_id: var.get() for s_id, var in self.checkbox_vars.items()}

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.checkbox_vars.clear()

        # Filter database query based on search keyword
        if keyword:
            self.cursor.execute("SELECT id, roll, name FROM students WHERE name LIKE ? OR roll LIKE ? ORDER BY roll", (f'%{keyword}%', f'%{keyword}%'))
        else:
            self.cursor.execute("SELECT id, roll, name FROM students ORDER BY roll")
            
        students = self.cursor.fetchall()

        if not students:
            ctk.CTkLabel(self.scroll_frame, text="No students found matching your search.", font=("Arial", 16), text_color="gray").pack(pady=50)
            
            # Put invisible states back into memory so we don't lose data if they click Save while searching!
            for s_id, state in current_states.items():
                self.checkbox_vars[s_id] = ctk.StringVar(value=state)
            return

        self.cursor.execute("SELECT student_id, status FROM attendance_records WHERE date=?", (self.current_date,))
        today_records = {row[0]: row[1] for row in self.cursor.fetchall()}

        for idx, student in enumerate(students):
            s_id, roll, name = student
            
            bg_color = "#2b2b2b" if idx % 2 == 0 else "#333333"
            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color=bg_color, corner_radius=5)
            row_frame.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(row_frame, text=roll, font=("Arial", 15), width=150, anchor="w").pack(side="left", padx=10, pady=12)
            ctk.CTkLabel(row_frame, text=name, font=("Arial", 15), width=300, anchor="w").pack(side="left", padx=10, pady=12)
            
            # Determine Checkbox state: 1. Previous unsaved clicks -> 2. Database records -> 3. Default Absent
            if s_id in current_states:
                initial_status = current_states[s_id]
            else:
                initial_status = today_records.get(s_id, "Absent")
                
            var = ctk.StringVar(value=initial_status)
            self.checkbox_vars[s_id] = var
            
            chk = ctk.CTkCheckBox(row_frame, text="Present", variable=var, onvalue="Present", offvalue="Absent", font=("Arial", 15, "bold"))
            chk.pack(side="right", padx=50, pady=12)

        # Final memory-safe check: Re-add any students to the tracker who are currently hidden by the search filter
        for s_id, state in current_states.items():
            if s_id not in self.checkbox_vars:
                self.checkbox_vars[s_id] = ctk.StringVar(value=state)

    # =========================
    # ATTENDANCE LOGIC
    # =========================
    def mark_all(self):
        for var in self.checkbox_vars.values(): var.set("Present")

    def clear_all(self):
        for var in self.checkbox_vars.values(): var.set("Absent")

    def save_attendance(self):
        for s_id, var in self.checkbox_vars.items():
            status = var.get()
            self.cursor.execute("SELECT id FROM attendance_records WHERE student_id=? AND date=?", (s_id, self.current_date))
            record = self.cursor.fetchone()
            
            if record:
                self.cursor.execute("UPDATE attendance_records SET status=? WHERE id=?", (status, record[0]))
            else:
                self.cursor.execute("INSERT INTO attendance_records (student_id, date, status) VALUES (?, ?, ?)", (s_id, self.current_date, status))
        
        self.recalculate_attendance_percentages()
        self.conn.commit()
        messagebox.showinfo("Success", "Daily attendance successfully logged!")

    def recalculate_attendance_percentages(self):
        self.cursor.execute("SELECT DISTINCT student_id FROM attendance_records")
        students_with_records = [row[0] for row in self.cursor.fetchall()]
        
        for s_id in students_with_records:
            self.cursor.execute("SELECT COUNT(*) FROM attendance_records WHERE student_id=?", (s_id,))
            total_days = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM attendance_records WHERE student_id=? AND status='Present'", (s_id,))
            present_days = self.cursor.fetchone()[0]
            
            if total_days > 0:
                percentage = (present_days / total_days) * 100
                self.cursor.execute("UPDATE students SET attendance=? WHERE id=?", (percentage, s_id))