import customtkinter as ctk
import traceback
from database import setup_db
from screens.login_screen import LoginScreen
from screens.dashboard import DashboardScreen

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Student Management System")
        self.geometry("1400x750")
        
        # Apply themes from MVP
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Ensure database and tables exist
        setup_db()

        
        # Launch the first screen
        self.show_login()

    
    def show_login(self):
        self.login_screen = LoginScreen(self, on_login_success=self.show_dashboard)

    def show_dashboard(self):
        self.dashboard_screen = DashboardScreen(self, on_logout=self.show_login)

if __name__ == "__main__":
    app = App()
    app.mainloop()