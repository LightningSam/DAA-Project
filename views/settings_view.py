import customtkinter as ctk
from tkinter import messagebox
import database

class SettingsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Connect to database for account updates
        self.conn = database.get_connection()
        self.cursor = self.conn.cursor()

        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="Application Settings", font=("Arial", 28, "bold")).pack(anchor="w", pady=(0, 20))
        
        # =========================
        # APPEARANCE SETTINGS CARD
        # =========================
        appearance_card = ctk.CTkFrame(self, corner_radius=15)
        appearance_card.pack(fill="x", pady=(0, 20), ipady=15)
        
        ctk.CTkLabel(appearance_card, text="Appearance", font=("Arial", 20, "bold")).pack(anchor="w", padx=20, pady=(15, 10))
        
        mode_frame = ctk.CTkFrame(appearance_card, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(mode_frame, text="UI Theme Mode:", font=("Arial", 16)).pack(side="left")
        self.mode_menu = ctk.CTkOptionMenu(mode_frame, values=["System", "Dark", "Light"], command=self.change_appearance_mode)
        self.mode_menu.pack(side="right")
        self.mode_menu.set(ctk.get_appearance_mode())
        
        scale_frame = ctk.CTkFrame(appearance_card, fg_color="transparent")
        scale_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(scale_frame, text="UI Scaling:", font=("Arial", 16)).pack(side="left")
        self.scale_menu = ctk.CTkOptionMenu(scale_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling)
        self.scale_menu.pack(side="right")
        self.scale_menu.set("100%")

        # =========================
        # ACCOUNT SECURITY CARD
        # =========================
        account_card = ctk.CTkFrame(self, corner_radius=15)
        account_card.pack(fill="x", pady=10, ipady=15)

        ctk.CTkLabel(account_card, text="Account Security", font=("Arial", 20, "bold")).pack(anchor="w", padx=20, pady=(15, 10))
        ctk.CTkLabel(account_card, text="Change your admin login credentials.", text_color="gray").pack(anchor="w", padx=20, pady=(0, 15))

        # Username Input
        user_frame = ctk.CTkFrame(account_card, fg_color="transparent")
        user_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(user_frame, text="New Username:", font=("Arial", 16), width=120, anchor="w").pack(side="left")
        self.new_username = ctk.CTkEntry(user_frame, placeholder_text="Enter new username", width=250)
        self.new_username.pack(side="left", padx=20)

        # Password Input
        pass_frame = ctk.CTkFrame(account_card, fg_color="transparent")
        pass_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(pass_frame, text="New Password:", font=("Arial", 16), width=120, anchor="w").pack(side="left")
        self.new_password = ctk.CTkEntry(pass_frame, placeholder_text="Enter new password", show="*", width=250)
        self.new_password.pack(side="left", padx=20)

        # Save Button
        save_btn = ctk.CTkButton(account_card, text="Update Credentials", command=self.update_credentials, width=200, height=40)
        save_btn.pack(anchor="w", padx=20, pady=20)

    # =========================
    # LOGIC FUNCTIONS
    # =========================
    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def update_credentials(self):
        new_user = self.new_username.get().strip()
        new_pass = self.new_password.get().strip()

        # Input validation
        if not new_user or not new_pass:
            messagebox.showerror("Error", "Both Username and Password fields are required.")
            return

        # Update the database (Assuming id=1 is the primary admin account)
        try:
            self.cursor.execute("UPDATE users SET username=?, password=? WHERE id=1", (new_user, new_pass))
            self.conn.commit()
            
            # Clear the entry fields after successful update
            self.new_username.delete(0, 'end')
            self.new_password.delete(0, 'end')
            
            messagebox.showinfo("Success", "Your login credentials have been updated successfully!\nPlease use these next time you log in.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update credentials:\n{str(e)}")