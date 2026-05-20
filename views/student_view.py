import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import database
import os
from PIL import Image

class StudentView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True)
        
        self.conn = database.get_connection()
        self.cursor = self.conn.cursor()

        os.makedirs("profile_pics", exist_ok=True)
        
        self.current_pic_path = None
        self.current_ctk_img = None 

        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        # =========================
        # SEARCH SECTION
        # =========================
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill='x', padx=15, pady=(15, 0))

        ctk.CTkLabel(search_frame, text="Search Keywords:", font=("Arial", 15, "bold")).pack(side='left', padx=(0, 10))
        self.search_entry = ctk.CTkEntry(search_frame, width=350, height=35, font=("Arial", 14))
        self.search_entry.pack(side='left', padx=(0, 10))
        self.search_entry.bind("<Return>", lambda event: self.search_data())

        ctk.CTkButton(search_frame, text="Search", command=self.search_data, width=110, height=35, font=("Arial", 14)).pack(side='left', padx=5)
        ctk.CTkButton(search_frame, text="Clear / Back", command=self.refresh_table, width=110, height=35, font=("Arial", 14)).pack(side='left', padx=5)

        # =========================
        # FORM SECTION W/ PROFILE PIC
        # =========================
        form_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        form_wrapper.pack(fill='x', padx=15, pady=15)

        pic_frame = ctk.CTkFrame(form_wrapper, corner_radius=10)
        pic_frame.pack(side='left', fill='y', padx=(0, 15))

        self.pic_label = ctk.CTkLabel(pic_frame, text="No Photo", width=140, height=140, fg_color="#333333", corner_radius=10)
        self.pic_label.pack(pady=(15, 10), padx=15)
        ctk.CTkButton(pic_frame, text="📸 Upload Photo", command=self.upload_picture, width=140, font=("Arial", 12, "bold")).pack(pady=(0, 15), padx=15)

        form_frame = ctk.CTkFrame(form_wrapper)
        form_frame.pack(side='left', fill='x', expand=True)

        label_font = ("Arial", 13, "bold")
        entry_font = ("Arial", 14)
        entry_kwargs = {"width": 170, "height": 35, "font": entry_font}

        ctk.CTkLabel(form_frame, text="Roll Number", font=label_font, text_color="gray").grid(row=0, column=0, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(form_frame, text="Student Name", font=label_font, text_color="gray").grid(row=0, column=1, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(form_frame, text="Department", font=label_font, text_color="gray").grid(row=0, column=2, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(form_frame, text="Phone Number", font=label_font, text_color="gray").grid(row=0, column=3, padx=15, pady=(15, 0), sticky="w")

        self.roll_entry = ctk.CTkEntry(form_frame, **entry_kwargs)
        self.roll_entry.grid(row=1, column=0, padx=15, pady=(0, 15))
        self.name_entry = ctk.CTkEntry(form_frame, **entry_kwargs)
        self.name_entry.grid(row=1, column=1, padx=15, pady=(0, 15))
        self.dept_entry = ctk.CTkEntry(form_frame, **entry_kwargs)
        self.dept_entry.grid(row=1, column=2, padx=15, pady=(0, 15))
        self.phone_entry = ctk.CTkEntry(form_frame, **entry_kwargs)
        self.phone_entry.grid(row=1, column=3, padx=15, pady=(0, 15))

        ctk.CTkLabel(form_frame, text="Email Address", font=label_font, text_color="gray").grid(row=2, column=0, padx=15, pady=(5, 0), sticky="w")
        ctk.CTkLabel(form_frame, text="Marks (Obtained/Total)", font=label_font, text_color="gray").grid(row=2, column=1, padx=15, pady=(5, 0), sticky="w")
        ctk.CTkLabel(form_frame, text="Attendance (%)", font=label_font, text_color="gray").grid(row=2, column=2, padx=15, pady=(5, 0), sticky="w")

        self.email_entry = ctk.CTkEntry(form_frame, **entry_kwargs)
        self.email_entry.grid(row=3, column=0, padx=15, pady=(0, 15))
        self.marks_entry = ctk.CTkEntry(form_frame, **entry_kwargs)
        self.marks_entry.grid(row=3, column=1, padx=15, pady=(0, 15))
        self.attendance_entry = ctk.CTkEntry(form_frame, **entry_kwargs)
        self.attendance_entry.grid(row=3, column=2, padx=15, pady=(0, 15))

        self.attendance_entry.bind("<Return>", lambda event: self.add_student())

        # =========================
        # BUTTONS
        # =========================
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill='x', padx=15)
        
        btn_font = ("Arial", 14, "bold")
        ctk.CTkButton(btn_frame, text="Add Student", command=self.add_student, width=120, height=35, font=btn_font).pack(side='left', padx=5)
        ctk.CTkButton(btn_frame, text="Update Student", command=self.update_student, width=130, height=35, font=btn_font).pack(side='left', padx=5)
        ctk.CTkButton(btn_frame, text="Add Extra Info ➕", command=self.open_extra_info, fg_color="#28a745", hover_color="#218838", width=140, height=35, font=btn_font).pack(side='left', padx=15)
        
        ctk.CTkButton(btn_frame, text="Clear", fg_color="gray", hover_color="#555555", command=self.clear_fields, width=90, height=35, font=btn_font).pack(side='right', padx=5)
        ctk.CTkButton(btn_frame, text="Delete Student", fg_color="#d32f2f", hover_color="#b71c1c", command=self.delete_student, width=130, height=35, font=btn_font).pack(side='right', padx=5)
        
        # =========================
        # TABLE WITH SCROLLBAR
        # =========================
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"))

        columns = ("ID", "Roll", "Name", "Department", "Phone", "Email", "Marks", "Attendance")
        self.student_table = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.student_table.yview)
        self.student_table.configure(yscrollcommand=scrollbar.set)
        
        for col in columns:
            self.student_table.heading(col, text=col)
            self.student_table.column(col, width=60 if col == "ID" else 130)
            
        scrollbar.pack(side='right', fill='y')
        self.student_table.pack(side='left', fill='both', expand=True)
        self.student_table.bind("<<TreeviewSelect>>", self.on_select)

    # =========================
    # IMAGE LOGIC
    # =========================
    def load_profile_picture(self, path):
        if not path or not os.path.exists(path):
            blank_image = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
            self.current_ctk_img = ctk.CTkImage(light_image=blank_image, dark_image=blank_image, size=(140, 140))
            self.pic_label.configure(image=self.current_ctk_img, text="No Photo")
            return
        try:
            img = Image.open(path)
            self.current_ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(140, 140))
            self.pic_label.configure(image=self.current_ctk_img, text="")
        except Exception:
            self.pic_label.configure(text="Image Error")

    def upload_picture(self):
        roll = self.roll_entry.get().strip()
        if not roll:
            messagebox.showwarning("Warning", "Please enter a Roll Number first.")
            return
        file_path = filedialog.askopenfilename(title="Select Profile Picture", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if not file_path: return
        try:
            img = Image.open(file_path)
            min_dim = min(img.size)
            left = (img.width - min_dim) / 2
            top = (img.height - min_dim) / 2
            img = img.crop((left, top, left + min_dim, top + min_dim))
            img = img.resize((300, 300)) 
            save_path = f"profile_pics/{roll}.png"
            img.save(save_path, format="PNG")
            self.current_pic_path = save_path
            self.load_profile_picture(save_path)
            messagebox.showinfo("Success", "Profile picture uploaded! Make sure to click 'Update' or 'Add Student' to save it.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image:\n{e}")

    # =========================
    # EXTRA INFO MODAL
    # =========================
    def open_extra_info(self):
        selected = self.student_table.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a student from the table first.")
            return
        student_id = self.student_table.item(selected, 'values')[0]
        student_name = self.student_table.item(selected, 'values')[2]

        modal = ctk.CTkToplevel(self)
        modal.title(f"Extra Information - {student_name}")
        modal.geometry("550x550")
        modal.attributes("-topmost", True)
        modal.grab_set()

        ctk.CTkLabel(modal, text=f"Custom Profile Details: {student_name}", font=("Arial", 18, "bold")).pack(pady=20)

        input_frame = ctk.CTkFrame(modal, fg_color="transparent")
        input_frame.pack(fill='x', padx=20)
        ctk.CTkLabel(input_frame, text="Field Name:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=5)
        ctk.CTkLabel(input_frame, text="Value:", font=("Arial", 12, "bold")).grid(row=0, column=1, sticky="w", padx=5)
        
        field_entry = ctk.CTkEntry(input_frame, width=180, font=("Arial", 14))
        field_entry.grid(row=1, column=0, padx=5, pady=5)
        val_entry = ctk.CTkEntry(input_frame, width=180, font=("Arial", 14))
        val_entry.grid(row=1, column=1, padx=5, pady=5)

        info_cols = ("ID", "Field Name", "Value")
        info_table = ttk.Treeview(modal, columns=info_cols, show='headings', height=8)
        for col in info_cols:
            info_table.heading(col, text=col)
            info_table.column(col, width=50 if col == "ID" else 200)
        info_table.pack(fill='both', expand=True, padx=20, pady=15)

        def refresh_modal_table():
            for row in info_table.get_children(): info_table.delete(row)
            self.cursor.execute("SELECT id, field_name, field_value FROM student_extra_info WHERE student_id=?", (student_id,))
            for row in self.cursor.fetchall(): info_table.insert('', 'end', values=row)

        def save_custom_field():
            field, val = field_entry.get().strip(), val_entry.get().strip()
            if not field or not val: return
            self.cursor.execute("INSERT INTO student_extra_info (student_id, field_name, field_value) VALUES (?, ?, ?)", (student_id, field, val))
            self.conn.commit()
            field_entry.delete(0, 'end')
            val_entry.delete(0, 'end')
            refresh_modal_table()
            field_entry.focus_set()

        def delete_custom_field():
            sel = info_table.focus()
            if not sel: return
            rec_id = info_table.item(sel, 'values')[0]
            self.cursor.execute("DELETE FROM student_extra_info WHERE id=?", (rec_id,))
            self.conn.commit()
            refresh_modal_table()

        val_entry.bind("<Return>", lambda e: save_custom_field())

        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))
        ctk.CTkButton(btn_frame, text="Save Field", command=save_custom_field, font=("Arial", 14, "bold")).pack(side='left', padx=5)
        ctk.CTkButton(btn_frame, text="Delete Selected", fg_color="#d32f2f", hover_color="#b71c1c", command=delete_custom_field, font=("Arial", 14, "bold")).pack(side='right', padx=5)
        refresh_modal_table()

    # =========================
    # CORE LOGIC
    # =========================
    def parse_marks(self, marks_str):
        marks_str = marks_str.strip()
        if not marks_str: return None, None
        if "/" in marks_str:
            try:
                parts = marks_str.split("/")
                ob, tot = float(parts[0]), float(parts[1])
                if tot <= 0: raise ValueError
                return ob, tot
            except ValueError: raise ValueError("Marks entry must match format: Obtained/Total")
        else: raise ValueError("Fraction slash symbol '/' is required for Marks format")

    def _format_marks(self, ob, tot):
        """🌟 FIX: Smart helper prevents missing columns by displaying whatever marks data exists safely."""
        if ob is None and tot is None: return ""
        def clean(v):
            if v is None: return ""
            try: return str(int(v)) if float(v).is_integer() else str(v)
            except: return str(v)
        if ob is not None and tot is not None:
            return f"{clean(ob)}/{clean(tot)}"
        elif ob is not None:
            return clean(ob)
        return clean(tot)

    def search_data(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.refresh_table()
            return
        for row in self.student_table.get_children(): self.student_table.delete(row)
        self.cursor.execute("SELECT id, roll, name, department, phone, email, obtained_marks, total_marks, attendance FROM students WHERE name LIKE ? OR roll LIKE ? OR department LIKE ?", (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        for row in self.cursor.fetchall():
            marks_display = self._format_marks(row[6], row[7])
            sanitized_row = [row[0], row[1], row[2], row[3] or "", row[4] or "", row[5] or "", marks_display, f"{row[8]}%" if row[8] is not None else ""]
            self.student_table.insert('', 'end', values=sanitized_row)

    def add_student(self):
        roll, name = self.roll_entry.get(), self.name_entry.get()
        dept, phone = self.dept_entry.get(), self.phone_entry.get()
        email, attendance = self.email_entry.get(), self.attendance_entry.get()
        if not name or not roll:
            messagebox.showerror("Error", "Roll and Name are required")
            return
        if self.marks_entry.get():
            try: ob_val, tot_val = self.parse_marks(self.marks_entry.get())
            except ValueError as e:
                messagebox.showerror("Validation Error", str(e))
                return
        else: ob_val, tot_val = None, None
            
        self.cursor.execute("INSERT INTO students (roll, name, department, phone, email, obtained_marks, total_marks, attendance, profile_pic) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (roll, name, dept, phone, email, ob_val, tot_val, attendance if attendance else None, self.current_pic_path))
        self.conn.commit()
        self.clear_fields(bypass_confirm=True)
        self.refresh_table()
        self.roll_entry.focus_set()

    def update_student(self):
        selected = self.student_table.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a student.")
            return
        student_id = self.student_table.item(selected, 'values')[0]
        roll, name = self.roll_entry.get(), self.name_entry.get()
        dept, phone = self.dept_entry.get(), self.phone_entry.get()
        email, attendance = self.email_entry.get(), self.attendance_entry.get()
        if not name or not roll:
            messagebox.showerror("Error", "Roll and Name are required")
            return
        if self.marks_entry.get():
            try: ob_val, tot_val = self.parse_marks(self.marks_entry.get())
            except ValueError as e:
                messagebox.showerror("Validation Error", str(e))
                return
        else: ob_val, tot_val = None, None

        self.cursor.execute("UPDATE students SET roll=?, name=?, department=?, phone=?, email=?, obtained_marks=?, total_marks=?, attendance=?, profile_pic=? WHERE id=?", (roll, name, dept, phone, email, ob_val, tot_val, attendance if attendance else None, self.current_pic_path, student_id))
        self.conn.commit()
        self.refresh_table()
        messagebox.showinfo("Success", "Student Updated Successfully")

    def delete_student(self):
        selected = self.student_table.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a student.")
            return
        if messagebox.askyesno("Confirm Delete", "Are you sure?"):
            student_id = self.student_table.item(selected, 'values')[0]
            roll_number = self.student_table.item(selected, 'values')[1]
            
            self.cursor.execute("SELECT profile_pic FROM students WHERE id=?", (student_id,))
            pic_res = self.cursor.fetchone()
            pic_path = pic_res[0] if pic_res else None

            self.cursor.execute("DELETE FROM student_extra_info WHERE student_id=?", (student_id,))
            self.cursor.execute("DELETE FROM academic_records WHERE student_id=?", (student_id,))
            self.cursor.execute("DELETE FROM attendance_records WHERE student_id=?", (student_id,))
            self.cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
            self.conn.commit()
            
            if pic_path and os.path.exists(pic_path):
                try: os.remove(pic_path)
                except Exception: pass
            
            self.clear_fields(bypass_confirm=True)
            self.refresh_table()

    def clear_fields(self, bypass_confirm=False, keep_table_selection=False):
        if not bypass_confirm and (self.roll_entry.get() or self.name_entry.get()):
            if not messagebox.askyesno("Confirm Clear", "Clear all fields?"): return
        self.roll_entry.delete(0, 'end')
        self.name_entry.delete(0, 'end')
        self.dept_entry.delete(0, 'end')
        self.phone_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')
        self.marks_entry.delete(0, 'end')
        self.attendance_entry.delete(0, 'end')
        
        self.current_pic_path = None
        self.load_profile_picture(None)
        
        if not keep_table_selection:
            for item in self.student_table.selection(): self.student_table.selection_remove(item)

    def on_select(self, event):
        selected = self.student_table.focus()
        if not selected: return
        values = self.student_table.item(selected, 'values')
        self.clear_fields(bypass_confirm=True, keep_table_selection=True)
        
        def safe_insert(entry, val):
            if val is not None and str(val).strip() != "" and str(val).strip() != "None": entry.insert(0, val)
        safe_insert(self.roll_entry, values[1])
        safe_insert(self.name_entry, values[2])
        safe_insert(self.dept_entry, values[3])
        safe_insert(self.phone_entry, values[4])
        safe_insert(self.email_entry, values[5])
        safe_insert(self.marks_entry, values[6])
        safe_insert(self.attendance_entry, values[7].replace("%","") if values[7] else "")
        
        student_id = values[0]
        self.cursor.execute("SELECT profile_pic FROM students WHERE id=?", (student_id,))
        res = self.cursor.fetchone()
        self.current_pic_path = res[0] if res else None
        self.load_profile_picture(self.current_pic_path)

    def refresh_table(self):
        if hasattr(self, 'search_entry'): self.search_entry.delete(0, 'end')
        for row in self.student_table.get_children(): self.student_table.delete(row)
        self.cursor.execute("SELECT id, roll, name, department, phone, email, obtained_marks, total_marks, attendance FROM students")
        for row in self.cursor.fetchall():
            marks_display = self._format_marks(row[6], row[7])
            sanitized_row = [row[0], row[1], row[2], row[3] or "", row[4] or "", row[5] or "", marks_display, f"{row[8]}%" if row[8] is not None else ""]
            self.student_table.insert('', 'end', values=sanitized_row)