import customtkinter as ctk
from views.home_view import HomeView
from views.student_view import StudentView
from views.attendance_view import AttendanceView
from views.reports_view import ReportsView
from views.settings_view import SettingsView
from views.marks_view import MarksView

class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, on_logout):
        super().__init__(master)
        self.on_logout = on_logout
        self.pack(fill="both", expand=True)

        self.setup_sidebar()
        
        # Create a main content area
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(side='right', fill='both', expand=True)
        
        # Initialize an empty dictionary for Lazy Loading
        self.views = {}
        self.current_view_name = None
        
        # Load the default view
        self.switch_view("Dashboard")

    def setup_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.pack(side='left', fill='y')
        ctk.CTkLabel(sidebar, text="Student Manager", font=("Arial", 20, "bold")).pack(pady=30)
        
        menu_items = ["Dashboard", "Students", "Attendance", "Marks", "Reports", "Settings"]
        for item in menu_items:
            ctk.CTkButton(sidebar, text=item, height=45, command=lambda view=item: self.switch_view(view)).pack(fill='x', padx=15, pady=8)
        
        # Logout Button
        ctk.CTkButton(sidebar, text="Logout", height=45, fg_color="#d32f2f", hover_color="#b71c1c", command=self.logout).pack(side='bottom', fill='x', padx=15, pady=20)

    def switch_view(self, view_name):
        # 1. Hide the current view if one exists
        if self.current_view_name and self.current_view_name in self.views:
            self.views[self.current_view_name].pack_forget()
            
        # 2. LAZY LOADING: Create the view frame ONLY when it is first clicked
        if view_name not in self.views:
            if view_name == "Dashboard":
                self.views[view_name] = HomeView(self.main_content)
            elif view_name == "Students":
                self.views[view_name] = StudentView(self.main_content)
            elif view_name == "Attendance":
                self.views[view_name] = AttendanceView(self.main_content)
            elif view_name == "Marks":
                self.views[view_name] = MarksView(self.main_content)
            elif view_name == "Reports":
                self.views[view_name] = ReportsView(self.main_content)
            elif view_name == "Settings":
                self.views[view_name] = SettingsView(self.main_content)

        # 3. Show the newly requested view
        if view_name in self.views:
            self.views[view_name].pack(fill="both", expand=True)
            self.current_view_name = view_name
            
            # 4. Trigger data updates/refreshes
            if hasattr(self.views[view_name], 'refresh_table'):
                self.views[view_name].refresh_table()
            if hasattr(self.views[view_name], 'update_stats'):
                self.views[view_name].update_stats()
                
            # 5. Clear global widget focus so placeholders render perfectly immediately
            self.after(50, lambda: self.winfo_toplevel().focus_set())

    def logout(self):
        self.pack_forget()
        self.destroy()
        self.on_logout()