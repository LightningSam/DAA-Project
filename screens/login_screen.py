import customtkinter as ctk
from tkinter import messagebox
import database

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.pack(fill="both", expand=True)

        # Center frame for the login box
        self.login_box = ctk.CTkFrame(self, width=350, height=400, corner_radius=15)
        self.login_box.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.login_box, text="Admin Login", font=("Arial", 26, "bold")).pack(pady=(40, 30))

        self.username_entry = ctk.CTkEntry(self.login_box, placeholder_text="Username", width=220, height=40)
        self.username_entry.pack(pady=15)

        # Create a mini-frame to hold the password entry and the eye button side-by-side
        pwd_frame = ctk.CTkFrame(self.login_box, fg_color="transparent")
        pwd_frame.pack(pady=15)

        self.password_entry = ctk.CTkEntry(pwd_frame, placeholder_text="Password", show="*", width=180, height=40)
        self.password_entry.pack(side="left", padx=(0, 5))

        self.toggle_btn = ctk.CTkButton(
            pwd_frame, 
            text="👁", 
            width=35, 
            height=40, 
            fg_color="gray", 
            hover_color="#555555", 
            command=self.toggle_password
        )
        self.toggle_btn.pack(side="right")

        ctk.CTkButton(self.login_box, text="Login", command=self.attempt_login, width=220, height=40).pack(pady=30)

        # Bind the 'Enter' key to both input fields
        self.username_entry.bind("<Return>", self.attempt_login)
        self.password_entry.bind("<Return>", self.attempt_login)

    def toggle_password(self):
        # Check current state and swap it
        if self.password_entry.cget("show") == "*":
            self.password_entry.configure(show="")
            self.toggle_btn.configure(text="🙈") # Change icon to hidden
        else:
            self.password_entry.configure(show="*")
            self.toggle_btn.configure(text="👁")  # Change icon to visible

    # Added 'event=None' so it works when called by the Enter key OR the mouse click
    def attempt_login(self, event=None):
        username = self.username_entry.get()
        password = self.password_entry.get()

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.pack_forget()       # Hide the login screen
            self.on_login_success()  # Trigger the dashboard to load
        else:
            messagebox.showerror("Error", "Invalid Username or Password")