import customtkinter as ctk
import database
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

class HomeView(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.conn = database.get_connection()
        self.cursor = self.conn.cursor()

        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="Analytics Dashboard", font=("Arial", 28, "bold")).pack(anchor="w", padx=10, pady=(10, 20))

        # =========================
        # 1. STAT CARDS (Now 3 Cards)
        # =========================
        card_frame = ctk.CTkFrame(self, fg_color="transparent")
        card_frame.pack(fill="x", padx=10)

        # Card 1: Total Students
        self.total_students_card = ctk.CTkFrame(card_frame, height=110, corner_radius=15, fg_color="#1f6aa5")
        self.total_students_card.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(self.total_students_card, text="Total Students", font=("Arial", 16, "bold"), text_color="white").pack(pady=(15, 0))
        self.total_label = ctk.CTkLabel(self.total_students_card, text="0", font=("Arial", 36, "bold"), text_color="white")
        self.total_label.pack(pady=(5, 15))

        # Card 2: Average Marks
        self.avg_marks_card = ctk.CTkFrame(card_frame, height=110, corner_radius=15, fg_color="#28c76f")
        self.avg_marks_card.pack(side="left", fill="x", expand=True, padx=(5, 5))
        ctk.CTkLabel(self.avg_marks_card, text="Avg. Raw Marks", font=("Arial", 16, "bold"), text_color="white").pack(pady=(15, 0))
        self.avg_label = ctk.CTkLabel(self.avg_marks_card, text="0", font=("Arial", 36, "bold"), text_color="white")
        self.avg_label.pack(pady=(5, 15))
        
        # Card 3: Overall Attendance
        self.avg_att_card = ctk.CTkFrame(card_frame, height=110, corner_radius=15, fg_color="#ea5455")
        self.avg_att_card.pack(side="left", fill="x", expand=True, padx=(10, 0))
        ctk.CTkLabel(self.avg_att_card, text="Overall Attendance", font=("Arial", 16, "bold"), text_color="white").pack(pady=(15, 0))
        self.att_label = ctk.CTkLabel(self.avg_att_card, text="0%", font=("Arial", 36, "bold"), text_color="white")
        self.att_label.pack(pady=(5, 15))

        self.update_stats()

        # =========================
        # 2. CHARTS GRID
        # =========================
        self.charts_container = ctk.CTkFrame(self, fg_color="transparent")
        self.charts_container.pack(fill="both", expand=True, pady=20, padx=10)
        
        # Configure Grid Layout (2x2)
        self.charts_container.columnconfigure(0, weight=1)
        self.charts_container.columnconfigure(1, weight=1)
        
        self.draw_all_charts()

    def update_stats(self):
        # Total
        self.cursor.execute("SELECT COUNT(*) FROM students")
        total = self.cursor.fetchone()[0]
        self.total_label.configure(text=str(total))
        
        # Avg Marks
        self.cursor.execute("SELECT AVG(obtained_marks) FROM students WHERE obtained_marks IS NOT NULL")
        res_marks = self.cursor.fetchone()
        avg_marks = res_marks[0] if res_marks and res_marks[0] is not None else 0
        self.avg_label.configure(text=f"{avg_marks:.1f}")
        
        # Avg Attendance
        self.cursor.execute("SELECT AVG(attendance) FROM students WHERE attendance IS NOT NULL")
        res_att = self.cursor.fetchone()
        avg_att = res_att[0] if res_att and res_att[0] is not None else 0
        self.att_label.configure(text=f"{avg_att:.1f}%")

    def _get_theme_colors(self):
        current_mode = ctk.get_appearance_mode()
        text_color = "white" if current_mode == "Dark" else "black"
        bg_color = "#2b2b2b" if current_mode == "Dark" else "#f2f2f2"
        return text_color, bg_color

    def draw_all_charts(self):
        # Clear existing charts if refreshing
        for w in self.charts_container.winfo_children():
            w.destroy()

        text_color, bg_color = self._get_theme_colors()
        chart_colors = ['#FF9F43', '#00CFE8', '#28C76F', '#EA5455', '#7367F0', '#FFCE56', '#FF6384']

        # --- CHART 1: Average Marks by Department (Bar) ---
        frame1 = ctk.CTkFrame(self.charts_container, corner_radius=10)
        frame1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.cursor.execute("SELECT department, AVG(obtained_marks) FROM students WHERE department != '' AND obtained_marks IS NOT NULL GROUP BY department")
        data1 = self.cursor.fetchall()
        
        fig1 = Figure(figsize=(5, 4), dpi=100)
        fig1.patch.set_facecolor(bg_color)
        ax1 = fig1.add_subplot(111)
        ax1.set_facecolor(bg_color)
        
        if data1:
            depts = [row[0] for row in data1]
            marks = [row[1] for row in data1]
            bars = ax1.bar(depts, marks, color=chart_colors[:len(depts)])
            ax1.set_title("Avg Marks by Department", color=text_color, pad=15)
            ax1.tick_params(colors=text_color)
            for spine in ax1.spines.values(): spine.set_color(text_color)
            
            # Add values on top of bars
            for bar in bars:
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f"{bar.get_height():.0f}", ha='center', color=text_color, fontsize=9)
        else:
            ax1.text(0.5, 0.5, "No Data Available", ha='center', va='center', color=text_color)

        canvas1 = FigureCanvasTkAgg(fig1, master=frame1)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)


        # --- CHART 2: Attendance by Department (Line/Area) ---
        frame2 = ctk.CTkFrame(self.charts_container, corner_radius=10)
        frame2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.cursor.execute("SELECT department, AVG(attendance) FROM students WHERE department != '' AND attendance IS NOT NULL GROUP BY department")
        data2 = self.cursor.fetchall()
        
        fig2 = Figure(figsize=(5, 4), dpi=100)
        fig2.patch.set_facecolor(bg_color)
        ax2 = fig2.add_subplot(111)
        ax2.set_facecolor(bg_color)
        
        if data2:
            depts = [row[0] for row in data2]
            atts = [row[1] for row in data2]
            ax2.plot(depts, atts, marker='o', color='#00CFE8', linewidth=3, markersize=8)
            ax2.fill_between(depts, atts, color='#00CFE8', alpha=0.2)
            ax2.set_title("Avg Attendance (%) by Department", color=text_color, pad=15)
            ax2.tick_params(colors=text_color)
            ax2.set_ylim(0, 105)
            for spine in ax2.spines.values(): spine.set_color(text_color)
        else:
            ax2.text(0.5, 0.5, "No Data Available", ha='center', va='center', color=text_color)

        canvas2 = FigureCanvasTkAgg(fig2, master=frame2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)


        # --- CHART 3: School Grade Distribution (Pie) ---
        frame3 = ctk.CTkFrame(self.charts_container, corner_radius=10)
        frame3.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.cursor.execute("SELECT obtained_marks, total_marks FROM students WHERE obtained_marks IS NOT NULL AND total_marks > 0")
        data3 = self.cursor.fetchall()
        
        fig3 = Figure(figsize=(5, 4), dpi=100)
        fig3.patch.set_facecolor(bg_color)
        ax3 = fig3.add_subplot(111)
        ax3.set_facecolor(bg_color)
        
        if data3:
            grades = {'A+ (90+)': 0, 'A (80+)': 0, 'B (70+)': 0, 'C (60+)': 0, 'D (50+)': 0, 'Fail': 0}
            for ob, tot in data3:
                pct = (ob / tot) * 100
                if pct >= 90: grades['A+ (90+)'] += 1
                elif pct >= 80: grades['A (80+)'] += 1
                elif pct >= 70: grades['B (70+)'] += 1
                elif pct >= 60: grades['C (60+)'] += 1
                elif pct >= 50: grades['D (50+)'] += 1
                else: grades['Fail'] += 1
                
            labels = [k for k, v in grades.items() if v > 0]
            sizes = [v for v in grades.values() if v > 0]
            
            # Matplotlib pie styling
            wedges, texts, autotexts = ax3.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=chart_colors)
            for t in texts: t.set_color(text_color)
            for at in autotexts: at.set_color("black"), at.set_weight("bold")
            
            ax3.set_title("Overall Grade Distribution", color=text_color, pad=15)
        else:
            ax3.text(0.5, 0.5, "Add complete marks to view grades", ha='center', va='center', color=text_color)

        canvas3 = FigureCanvasTkAgg(fig3, master=frame3)
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)


        # --- CHART 4: Top Performing Subjects (Horizontal Bar) ---
        frame4 = ctk.CTkFrame(self.charts_container, corner_radius=10)
        frame4.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # Calculate subject averages as a percentage
        self.cursor.execute("""
            SELECT subject_name, AVG(obtained_marks * 100.0 / max_marks) 
            FROM academic_records 
            WHERE max_marks > 0 
            GROUP BY subject_name 
            ORDER BY AVG(obtained_marks * 100.0 / max_marks) DESC 
            LIMIT 5
        """)
        data4 = self.cursor.fetchall()
        
        fig4 = Figure(figsize=(5, 4), dpi=100)
        fig4.patch.set_facecolor(bg_color)
        ax4 = fig4.add_subplot(111)
        ax4.set_facecolor(bg_color)
        
        if data4:
            subjects = [row[0] for row in data4]
            # Reverse lists so the highest score is at the top of the horizontal bar chart
            subjects.reverse() 
            scores = [row[1] for row in data4]
            scores.reverse()
            
            ax4.barh(subjects, scores, color='#7367F0')
            ax4.set_title("Top 5 Performing Subjects (%)", color=text_color, pad=15)
            ax4.tick_params(colors=text_color)
            ax4.set_xlim(0, 105)
            for spine in ax4.spines.values(): spine.set_color(text_color)
        else:
            ax4.text(0.5, 0.5, "Add subject records in 'Marks' tab", ha='center', va='center', color=text_color)

        canvas4 = FigureCanvasTkAgg(fig4, master=frame4)
        canvas4.draw()
        canvas4.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)