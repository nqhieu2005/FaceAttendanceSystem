import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from pymongo import MongoClient
from datetime import datetime, timedelta
import os
import threading
from PIL import Image, ImageTk
import random

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class FaceAttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Điểm danh thông minh")
        self.root.geometry("1366x768")
        
        # Modern Color Palette
        self.colors = {
            'primary': '#2196F3',       # Material Blue
            'secondary': '#1976D2',     # Darker Blue
            'gradient1': '#1A237E',     # Indigo
            'gradient2': '#0D47A1',     # Deep Blue
            'background': '#FAFAFA',    # Almost White
            'card_bg': '#FFFFFF',       # Pure White
            'text_dark': '#212121',     # Almost Black
            'text_light': '#FFFFFF',    # White
            'accent': '#03A9F4',        # Light Blue
            'success': '#4CAF50',       # Green
            'warning': '#FFC107',       # Amber
            'error': '#F44336'          # Red
        }

        self.root.configure(bg=self.colors['background'])
        
        # MongoDB Connection
        try:
            self.client = MongoClient('mongodb://localhost:27017/')
            self.db = self.client['face_attendance']
            self.attendance_col = self.db['attendance']
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not connect to MongoDB: {str(e)}")
            self.root.quit()

        self.create_sidebar()
        self.create_main_content()
        
        # Add animation effects
        self.animate_cards()

    def create_sidebar(self):
        # Gradient Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(
            master=self.root,
            width=300,
            corner_radius=0,
            fg_color=self.colors['gradient1']
        )
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # Logo Frame
        logo_frame = ctk.CTkFrame(
            self.sidebar_frame,
            fg_color="transparent"
        )
        logo_frame.pack(pady=(40, 30))

        
        try:
            logo_img = Image.open("assets/logo.png")  
            logo_img = logo_img.resize((80, 80))
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(
                logo_frame,
                image=logo_photo,
                bg=self.colors['gradient1']
            )
            logo_label.image = logo_photo
            logo_label.pack()
        except:
            pass

        # App Title
        title_label = ctk.CTkLabel(
            logo_frame,
            text="Nhận diện khuôn mặt",
            font=("Roboto", 28, "bold"),
            text_color=self.colors['text_light']
        )
        title_label.pack(pady=(10, 0))

        # Sidebar Menu Buttons with Icons
        menu_items = [
            ("📊 Bảng điều khiển", self.show_dashboard),
            ("👥 Thêm sinh viên", self.open_add_student),
            ("📸 Điểm danh", self.open_attendance),
            # ("📋 Lịch sử điểm danh", self.show_attendance_list),
            # ("⚙️ Settings", self.open_settings),
            ("❌ Thoát", self.root.quit)
        ]

        for text, command in menu_items:
            button = ctk.CTkButton(
                master=self.sidebar_frame,
                text=text,
                command=command,
                fg_color="transparent",
                hover_color=self.colors['gradient2'],
                anchor="w",
                font=("Roboto", 16),
                height=50,
                corner_radius=0
            )
            button.pack(fill="x", pady=2)

    def get_class_list(self):
        """Get unique class names from students collection"""
        try:
            classes = self.db['students'].distinct('class')
            return ["Tất cả các lớp"] + sorted(classes)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách lớp: {str(e)}")
            return ["Tất cả các lớp"]       

    def create_main_content(self):
        # Main Content Area
        self.main_frame = ctk.CTkFrame(
            master=self.root,
            fg_color=self.colors['background'],
            corner_radius=0
        )
        self.main_frame.pack(side="right", fill="both", expand=True)

        # Header with welcome message
        header_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors['card_bg'],
            height=100,
            corner_radius=15
        )
        header_frame.pack(fill="x", padx=20, pady=20)

        self.time_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=("Roboto", 24, "bold"),
            text_color=self.colors['text_dark']
        )
        self.time_label.pack(pady=30)
        self.update_time()

        
        header_frame.pack(fill="x", padx=20, pady=20)

        # Add Class Selection Frame
        class_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors['card_bg'],
            corner_radius=15,
            height=60
        )
        class_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Class Selection Controls
        controls_frame = ctk.CTkFrame(
            class_frame,
            fg_color="transparent"
        )
        controls_frame.pack(expand=True, pady=10)

        ctk.CTkLabel(
            controls_frame,
            text="Lớp:",
            font=("Roboto", 16, "bold"),
            text_color=self.colors['text_dark']
        ).pack(side="left", padx=(20, 10))

        # Class Selection Combobox
        self.class_var = tk.StringVar()
        self.class_selector = ctk.CTkComboBox(
            controls_frame,
            values=self.get_class_list(),
            variable=self.class_var,
            width=200,
            font=("Roboto", 14),
            button_color=self.colors['primary'],
            button_hover_color=self.colors['secondary'],
            border_color=self.colors['primary'],
            dropdown_hover_color=self.colors['secondary']
        )
        self.class_selector.pack(side="left", padx=10)
        self.class_selector.set("Tất cả các lớp")

        # Bind class change event
        self.class_var.trace('w', lambda *args: self.refresh_dashboard())

        # Refresh Button
        ctk.CTkButton(
            controls_frame,
            text="🔄 Làm mới",
            command=self.refresh_dashboard,
            font=("Roboto", 14),
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary'],
            width=120
        ).pack(side="left", padx=10)
        

        # Statistics Cards with Animation
        self.stats_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.stats_frame.pack(fill="x", padx=20, pady=20)

        stats = self.get_statistics()
        self.create_stat_cards(stats)

        # Create modern attendance table
        self.create_attendance_table()

    def update_time(self):
        current_time = datetime.now().strftime('%B %d, %Y %H:%M:%S')
        self.time_label.configure(text=f"Today is {current_time}")
        self.root.after(1000, self.update_time) 

    def refresh_dashboard(self):
        """Refresh dashboard data based on selected class"""
        selected_class = self.class_var.get()
        stats = self.get_statistics(selected_class)
        self.create_stat_cards(stats)
        self.populate_attendance_table(selected_class)

    def create_stat_cards(self, stats):
        stats_data = [
            {
                "title": "Tổng",
                "value": stats["Total Students"],
                "icon": "👥",
                "color": self.colors['primary']
            },
            {
                "title": "Có mặt hôm nay",
                "value": stats["Today's Attendance"],
                "icon": "✅",
                "color": self.colors['success']
            },
            {
                "title": "Vắng mặt hôm nay",
                "value": stats["Absent Today"],
                "icon": "❌",
                "color": self.colors['error']
            }
        ]

        for i, data in enumerate(stats_data):
            card = ctk.CTkFrame(
                self.stats_frame,
                fg_color=self.colors['card_bg'],
                corner_radius=15,
                border_width=2,
                border_color=data['color']
            )
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

            # Icon
            ctk.CTkLabel(
                card,
                text=data['icon'],
                font=("Segoe UI Emoji", 48),
                text_color=data['color']
            ).pack(pady=(20, 5))

            # Value
            ctk.CTkLabel(
                card,
                text=data['value'],
                font=("Roboto", 36, "bold"),
                text_color=data['color']
            ).pack(pady=5)

            # Title
            ctk.CTkLabel(
                card,
                text=data['title'],
                font=("Roboto", 16),
                text_color=self.colors['text_dark']
            ).pack(pady=(5, 20))

        # Configure grid
        self.stats_frame.grid_columnconfigure((0,1,2), weight=1)

    def animate_cards(self):
        def update_colors():
            for card in self.stats_frame.winfo_children():
                current_color = card.cget("border_color")
                # Add subtle color animation
                r = random.randint(-10, 10)
                g = random.randint(-10, 10)
                b = random.randint(-10, 10)
                # Ensure color values stay within valid range
                new_color = f"#{min(255, max(0, int(current_color[1:3], 16) + r)):02x}" \
                           f"{min(255, max(0, int(current_color[3:5], 16) + g)):02x}" \
                           f"{min(255, max(0, int(current_color[5:7], 16) + b)):02x}"
                card.configure(border_color=new_color)
            self.root.after(1000, update_colors)
        
        self.root.after(0, update_colors)

    def create_attendance_table(self):
        # Table Frame
        table_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color='transparent'
        )
        table_frame.pack(fill='both', expand=True, pady=20, padx=20)  

        # Table Title
        ctk.CTkLabel(
            table_frame, 
            text="Điểm danh hôm nay",
            font=("Helvetica", 22, "bold"),  
            text_color=self.colors['text_dark']
        ).pack(anchor='w', pady=(0, 20), padx=30)  

        # Treeview
        columns = ("Họ Tên", "Mã Sinh Viên", "Lớp", "Thời gian", "Trạng Thái")
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
            rowheight=40,  
            font=("Helvetica", 12),  
            fieldbackground=self.colors['text_light'],
            bordercolor=self.colors['primary']  
        )
        style.map(
            'Custom.Treeview', 
            background=[('selected', self.colors['primary'])],
            bordercolor=[('selected', self.colors['accent'])]  
        )

        # Column setup
        for col in columns:
            self.tree.heading(col, text=col, anchor='center')  
            self.tree.column(col, anchor='center', width=130)  

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(
            table_frame, 
            orientation='vertical', 
            command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)

        # Pack Table and Scrollbar
        self.tree.pack(side='left', fill='both', expand=True, padx=(30, 0), pady=(0, 30))  
        scrollbar.pack(side='right', fill='y', padx=(0, 30), pady=(0, 30)) 

        # Populate Table (sample data)
        self.populate_attendance_table()

    def show_dashboard(self):
        # Refresh statistics and table
        selected_class = self.class_var.get()
        stats = self.get_statistics(selected_class)
        self.create_stat_cards(stats)
        self.populate_attendance_table(selected_class)

    # def open_settings(self):
        
    #     pass

    def get_statistics(self, selected_class="Tất cả các lớp"):
        try:
            # Base queries
            student_query = {}
            attendance_query = {
                'timestamp': {
                    '$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                    '$lt': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                }
            }

            # Add class filter if specific class is selected
            if selected_class != "Tất cả các lớp":
                student_query['class'] = selected_class
                attendance_query['class'] = selected_class

            total_students = self.db['students'].count_documents(student_query)
            present_students = self.attendance_col.count_documents({
                **attendance_query,
                'status': 'Có mặt'
            })
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

    def populate_attendance_table(self, selected_class="Tất cả các lớp"):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        def fetch_and_populate():
            try:
                query = {
                    'timestamp': {
                        '$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                        '$lt': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                    }
                }

                if selected_class != "Tất cả các lớp":
                    query['class'] = selected_class

                records = self.attendance_col.find(query).sort("timestamp", -1)

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

        threading.Thread(target=fetch_and_populate, daemon=True).start()

    def open_add_student(self):
        def run_script():
            try:
                os.system('python client/recognize_face.py')
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở cửa sổ thêm sinh viên: {str(e)}")

        threading.Thread(target=run_script, daemon=True).start()  # Run in a separate thread

    def open_attendance(self):
        def run_script():
            try:
                os.system('python client/capture_faces.py')
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở cửa sổ điểm danh: {str(e)}")

        threading.Thread(target=run_script, daemon=True).start()  # Run in a separate thread

    def show_attendance_list(self):
        # print("Loading attendance list...")
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