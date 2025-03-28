import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from pymongo import MongoClient
from datetime import datetime, timedelta  # Added timedelta import
import os
import threading  # Added threading import

# Set the default theme and appearance
ctk.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class FaceAttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Attendance Management System")
        self.root.geometry("1366x768")
        
        # Color Palette
        self.colors = {
            'primary': '#2196F3',
            'secondary': '#1565c0',
            'background': '#f4f6f9',
            'text_dark': '#333333',
            'text_light': '#FFFFFF',
            'accent': '#4CAF50'
        }

        # Configure root window
        self.root.configure(bg=self.colors['background'])
        
        # MongoDB Connection
        try:
            self.client = MongoClient('mongodb://localhost:27017/')
            self.db = self.client['face_attendance']
            self.attendance_col = self.db['attendance']
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not connect to MongoDB: {str(e)}")
            self.root.quit()

        # Create Main Layout
        self.create_sidebar()
        self.create_main_content()

    def create_sidebar(self):
        # Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(
            master=self.root, 
            width=250, 
            corner_radius=0,
            fg_color=self.colors['primary']
        )
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # Logo or Title
        logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Face Attendance",
            font=("Helvetica", 20, "bold"),
            text_color=self.colors['text_light']
        )
        logo_label.pack(pady=(30, 20))

        # Sidebar Buttons
        sidebar_buttons = [
            ("Add Student", self.open_add_student),
            ("Take Attendance", self.open_attendance),
            ("View Attendance", self.show_attendance_list),
            ("Exit", self.root.quit)
        ]

        for text, command in sidebar_buttons:
            button = ctk.CTkButton(
                master=self.sidebar_frame,
                text=text,
                command=command,
                fg_color=self.colors['secondary'],
                hover_color=self.colors['accent'],
                text_color=self.colors['text_light'],
                corner_radius=10,
                width=200,
                height=50
            )
            button.pack(pady=10)

    def get_statistics(self):
        try:
            # Lấy tổng số sinh viên từ collection `students`
            total_students = self.db['students'].count_documents({})

            # Lấy số sinh viên đã điểm danh hôm nay từ collection `attendance`
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)

            present_students = self.attendance_col.count_documents({
                'timestamp': {
                    '$gte': today_start,
                    '$lt': today_end
                },
                'status': 'Có mặt'
            })

            # Tính số sinh viên vắng mặt
            absent_students = total_students - present_students

            return {
                "Total Students": str(total_students),
                "Today's Attendance": str(present_students),
                "Absent Today": str(absent_students)
            }
        except Exception as e:
            messagebox.showwarning("Thống kê", f"Không thể tải số liệu: {str(e)}")
            return {
                "Total Students": "0",
                "Today's Attendance": "0", 
                "Absent Today": "0"
            }

    def populate_attendance_table(self):
        """
        Hiển thị danh sách điểm danh của ngày hôm nay
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        def fetch_and_populate():
            try:
                today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                today_end = today_start + timedelta(days=1)

                records = self.attendance_col.find({
                    'timestamp': {
                        '$gte': today_start,
                        '$lt': today_end
                    }
                }).sort("timestamp", 1)

                for record in records:
                    self.tree.insert('', 'end', values=(
                        record.get('name', 'N/A'),
                        record.get('student_id', 'N/A'),
                        record.get('class', 'N/A'),
                        record.get('timestamp', datetime.now()).strftime("%H:%M"),
                        record.get('status', 'N/A')
                    ))
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tải danh sách điểm danh: {str(e)}")

        # Run the fetch operation in a separate thread to avoid GUI lag
        threading.Thread(target=fetch_and_populate, daemon=True).start()

    def create_main_content(self):
        # Main Content Frame
        self.main_frame = ctk.CTkFrame(
            master=self.root, 
            fg_color=self.colors['background']
        )
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Dashboard Title
        self.dashboard_title = ctk.CTkLabel(
            self.main_frame, 
            text="Bảng điều khiển",
            font=("Helvetica", 24, "bold"),
            text_color=self.colors['text_dark']
        )
        self.dashboard_title.pack(pady=(0, 20), anchor='w')

        # Statistics Cards Frame
        self.stats_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color='transparent'
        )
        self.stats_frame.pack(fill='x', pady=10)

        # Lấy số liệu thực từ database
        stats = self.get_statistics()

        # Create Statistics Cards
        stats_list = [
            ("Tổng số sinh viên", stats["Total Students"]),
            ("Điểm danh hôm nay", stats["Today's Attendance"]),
            ("Vắng mặt hôm nay", stats["Absent Today"])
        ]

        for i, (title, value) in enumerate(stats_list):
            card = ctk.CTkFrame(
                self.stats_frame, 
                fg_color=self.colors['text_light'],
                corner_radius=15
            )
            card.grid(row=0, column=i, padx=10, sticky='ew')

            ctk.CTkLabel(
                card, 
                text=title, 
                font=("Helvetica", 14),
                text_color=self.colors['text_dark']
            ).pack(pady=(10, 5))

            ctk.CTkLabel(
                card, 
                text=value, 
                font=("Helvetica", 24, "bold"),
                text_color=self.colors['primary']
            ).pack(pady=(0, 10))

        self.create_attendance_table()

    def create_attendance_table(self):
        # Table Frame
        table_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color='transparent'
        )
        table_frame.pack(fill='both', expand=True, pady=20)

        # Table Title
        ctk.CTkLabel(
            table_frame, 
            text="Recent Attendance",
            font=("Helvetica", 18, "bold"),
            text_color=self.colors['text_dark']
        ).pack(anchor='w', pady=(0, 10))

        # Treeview
        columns = ("Name", "Student ID", "Class", "Time", "Status")
        self.tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show='headings', 
            style='Custom.Treeview'
        )

        # Style for Treeview
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            'Custom.Treeview', 
            background=self.colors['text_light'],
            foreground=self.colors['text_dark'],
            rowheight=35,
            fieldbackground=self.colors['text_light']
        )
        style.map(
            'Custom.Treeview', 
            background=[('selected', self.colors['primary'])]
        )

        # Column setup
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', width=100)

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(
            table_frame, 
            orientation='vertical', 
            command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)

        # Pack Table and Scrollbar
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y', padx=(0, 10))

        # Populate Table (sample data)
        self.populate_attendance_table()

    def open_add_student(self):
        def run_script():
            try:
                os.system('python client/recognize_face.py')
            except Exception as e:
                messagebox.showerror("Error", f"Could not open student registration: {str(e)}")

        threading.Thread(target=run_script, daemon=True).start()  # Run in a separate thread

    def open_attendance(self):
        def run_script():
            try:
                os.system('python client/capture_faces.py')
            except Exception as e:
                messagebox.showerror("Error", f"Could not open attendance capture: {str(e)}")

        threading.Thread(target=run_script, daemon=True).start()  # Run in a separate thread

    def show_attendance_list(self):
        print("Loading attendance list...")
        # You can add more detailed view or filtering options here
        self.populate_attendance_table()

    def __del__(self):
        if hasattr(self, 'client'):
            self.client.close()

def main():
    root = ctk.CTk()
    app = FaceAttendanceSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()