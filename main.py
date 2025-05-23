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
        self.root.title("Hệ thống nhận diện khuôn mặt")
        self.root.geometry("1366x768")
        
        # Modern Color Palette
        self.colors = {
            'primary': "#00923F",       # Material Blue
            'secondary': '#1976D2',     # Darker Blue
            'gradient1': '#1A237E',     # Indigo
            'gradient2': '#0D47A1',     # Deep Blue
            'background': '#E3F2FD',    # Light Blue Background
            'card_bg': '#FFFFFF',       # Pure White
            'text_dark': '#212121',     # Almost Black
            'text_light': '#FFFFFF',    # White
            'accent': '#03A9F4',        # Light Blue
            'success': '#4CAF50',       # Green
            'warning': '#FFC107',       # Amber
            'error': '#F44336',          # Red
            'card_bg': "#ffffff",
            'hover_bg': "#85f2b4",  # Màu khi hover
            'accent': "#00aaff",    # Màu border khi hover
            # 'primary': "#dddddd"  # Màu chính
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

        self.create_main_interface()

    def create_main_interface(self):
        # Header Frame
        header_frame = ctk.CTkFrame(
            self.root,
            height=80,
            fg_color=self.colors['primary'],
            corner_radius=0
        )
        header_frame.pack(fill="x", pady=0)
        header_frame.pack_propagate(False)

        # Header Content
        header_content = ctk.CTkFrame(
            header_frame,
            fg_color="transparent"
        )
        header_content.pack(expand=True, fill="both")

        logo_image = Image.open("logo.png")
        logo_image = logo_image.resize((60, 60))  # Adjust size as needed
        self.logo_photo = ImageTk.PhotoImage(logo_image)  # Keep a reference to avoid garbage collection

        logo_label = tk.Label(
            header_content,
            image=self.logo_photo,
            bg=self.colors['primary']
        )
        logo_label.pack(side="left", padx=20)

        # Title
        title_label = ctk.CTkLabel(
            header_content,
            text="Hệ thống nhận diện khuôn mặt",
            font=("Roboto", 28, "bold"),
            text_color=self.colors['text_light']
        )
        title_label.pack(expand=True)

        # Main Content Frame with background image effect
        self.main_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors['background'],
            corner_radius=0
        )
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=40)

        # Create function cards grid
        self.create_function_cards()

    def create_function_cards(self):
        # Cards Container
        cards_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        cards_frame.pack(expand=True, fill="both")

        # Function cards data (only functions that exist in the code)
        functions = [
            {
                "title": "Sinh viên",
                "icon": "👤",
                "command": self.open_add_student,
                "description": "Thêm sinh viên mới"
            },
            {
                "title": "Nhận diện", 
                "icon": "📷",
                "command": self.open_attendance,
                "description": "Điểm danh khuôn mặt"
            },
            {
                "title": "Điểm danh",
                "icon": "📝",
                "command": self.show_attendance_dashboard,
                "description": "Xem bảng điểm danh"
            },
            {
                "title": "Thống kê",
                "icon": "📊", 
                "command": self.show_statistics,
                "description": "Thống kê điểm danh"
            }
        ]

        # Create cards in 2x2 grid
        for i, func in enumerate(functions):
            row = i // 2
            col = i % 2
            
            # Card Frame
            card = ctk.CTkFrame(
                cards_frame,
                width=300,
                height=200,
                fg_color=self.colors['card_bg'],
                corner_radius=20,
                border_width=2,
                border_color=self.colors['primary']
            )
            card.grid(row=row, column=col, padx=30, pady=30, sticky="nsew")
            card.grid_propagate(False)

            # Card Content Frame
            content_frame = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )
            content_frame.pack(expand=True, fill="both")

            # Icon
            icon_label = ctk.CTkLabel(
                content_frame,
                text=func['icon'],
                font=("Segoe UI Emoji", 48),
                text_color=self.colors['primary']
            )
            icon_label.pack(pady=(30, 10))

            # Title
            title_label = ctk.CTkLabel(
                content_frame,
                text=func['title'],
                font=("Roboto", 20, "bold"),
                text_color=self.colors['text_dark']
            )
            title_label.pack(pady=(0, 5))

            # Description
            desc_label = ctk.CTkLabel(
                content_frame,
                text=func['description'],
                font=("Roboto", 12),
                text_color=self.colors['text_dark'],
                fg_color="transparent"
            )
            desc_label.pack(pady=(0, 20))

            # Make card clickable
            self.make_card_clickable(card, func['command'])
            self.make_card_clickable(content_frame, func['command'])
            self.make_card_clickable(icon_label, func['command'])
            self.make_card_clickable(title_label, func['command'])
            self.make_card_clickable(desc_label, func['command'])

        # Configure grid weights
        cards_frame.grid_columnconfigure((0, 1), weight=1)
        cards_frame.grid_rowconfigure((0, 1), weight=1)

    def make_card_clickable(self, widget, command):
        """Make widget clickable with border highlight and hover effect"""

        def is_default_fg(widget, default_color):
            fg = widget.cget("fg_color")
            if isinstance(fg, (list, tuple)):
                return default_color in fg
            return fg == default_color

        def on_enter(event):
            try:
                if isinstance(widget, ctk.CTkFrame):
                    if is_default_fg(widget, self.colors['card_bg']):
                        widget.configure(
                            border_color=self.colors['accent'],
                            fg_color=self.colors['hover_bg']
                        )
            except Exception as e:
                print(f"Error in on_enter: {e}")

        def on_leave(event):
            try:
                if isinstance(widget, ctk.CTkFrame):
                    widget.configure(
                        border_color=self.colors['primary'],
                        fg_color=self.colors['card_bg']
                    )
            except Exception as e:
                print(f"Error in on_leave: {e}")

        def on_click(event):
            try:
                command()
            except Exception as e:
                print(f"Error in on_click: {e}")

        if isinstance(widget, ctk.CTkFrame):
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

            if not widget.cget("border_width"):
                widget.configure(border_width=2)




    def show_attendance_dashboard(self):
        """Show attendance dashboard in new window"""
        dashboard_window = ctk.CTkToplevel(self.root)
        dashboard_window.title("Bảng điểm danh")
        dashboard_window.geometry("1200x800")
        dashboard_window.configure(fg_color=self.colors['background'])
        
        # Make window appear on top and grab focus
        dashboard_window.transient(self.root)
        dashboard_window.grab_set()
        dashboard_window.focus_set()
        dashboard_window.lift()
        dashboard_window.attributes('-topmost', True)
        dashboard_window.after(100, lambda: dashboard_window.attributes('-topmost', False))

        # Header
        header = ctk.CTkFrame(
            dashboard_window,
            height=60,
            fg_color=self.colors['primary'],
            corner_radius=0
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Bảng điểm danh hôm nay",
            font=("Roboto", 24, "bold"),
            text_color=self.colors['text_light']
        ).pack(expand=True)

        # Class selection frame
        class_frame = ctk.CTkFrame(
            dashboard_window,
            fg_color=self.colors['card_bg'],
            corner_radius=15,
            height=60
        )
        class_frame.pack(fill="x", padx=20, pady=20)

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

        self.class_var = tk.StringVar()
        class_selector = ctk.CTkComboBox(
            controls_frame,
            values=self.get_class_list(),
            variable=self.class_var,
            width=200,
            font=("Roboto", 14)
        )
        class_selector.pack(side="left", padx=10)
        class_selector.set("Tất cả các lớp")

        refresh_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Làm mới",
            command=lambda: self.populate_dashboard_table(tree, self.class_var.get()),
            font=("Roboto", 14),
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary'],
            width=120
        )
        refresh_btn.pack(side="left", padx=10)

        # Table frame
        table_frame = ctk.CTkFrame(
            dashboard_window,
            fg_color=self.colors['card_bg'],
            corner_radius=15
        )
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Create treeview
        columns = ("Họ Tên", "Mã Sinh Viên", "Lớp", "Thời gian", "Trạng Thái")
        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            style='Custom.Treeview'
        )

        # Style treeview
        style = ttk.Style()
        style.configure(
            'Custom.Treeview',
            background=self.colors['card_bg'],
            foreground=self.colors['text_dark'],
            rowheight=35,
            font=("Roboto", 12),
            fieldbackground=self.colors['card_bg']
        )

        for col in columns:
            tree.heading(col, text=col, anchor='center')
            tree.column(col, anchor='center', width=150)

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(
            table_frame,
            orientation='vertical',
            command=tree.yview
        )
        tree.configure(yscroll=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        scrollbar.pack(side='right', fill='y', padx=(0, 20), pady=20)

        # Populate table
        self.populate_dashboard_table(tree, "Tất cả các lớp")

        # Bind class change
        self.class_var.trace('w', lambda *args: self.populate_dashboard_table(tree, self.class_var.get()))

    def show_statistics(self):
        """Show statistics window"""
        stats_window = ctk.CTkToplevel(self.root)
        stats_window.title("Thống kê điểm danh")
        stats_window.geometry("800x600")
        stats_window.configure(fg_color=self.colors['background'])
        
        # Make window appear on top and grab focus
        stats_window.transient(self.root)
        stats_window.grab_set()
        stats_window.focus_set()
        stats_window.lift()
        stats_window.attributes('-topmost', True)
        stats_window.after(100, lambda: stats_window.attributes('-topmost', False))

        # Header
        header = ctk.CTkFrame(
            stats_window,
            height=60,
            fg_color=self.colors['primary'],
            corner_radius=0
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Thống kê điểm danh",
            font=("Roboto", 24, "bold"),
            text_color=self.colors['text_light']
        ).pack(expand=True)

        # Stats container
        stats_container = ctk.CTkFrame(
            stats_window,
            fg_color="transparent"
        )
        stats_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Get statistics
        stats = self.get_statistics()
        
        # Create stat cards
        stats_data = [
            {
                "title": "Tổng sinh viên",
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
                stats_container,
                fg_color=self.colors['card_bg'],
                corner_radius=15,
                border_width=2,
                border_color=data['color']
            )
            card.grid(row=i//2, column=i%2, padx=20, pady=20, sticky="nsew")

            # Icon
            ctk.CTkLabel(
                card,
                text=data['icon'],
                font=("Segoe UI Emoji", 48),
                text_color=data['color']
            ).pack(pady=(30, 10))

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
            ).pack(pady=(5, 30))

        stats_container.grid_columnconfigure((0, 1), weight=1)
        stats_container.grid_rowconfigure((0, 1, 2), weight=1)

    def get_class_list(self):
        """Get unique class names from students collection"""
        try:
            classes = self.db['students'].distinct('class')
            return ["Tất cả các lớp"] + sorted(classes)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách lớp: {str(e)}")
            return ["Tất cả các lớp"]

    def get_statistics(self, selected_class="Tất cả các lớp"):
        try:
            student_query = {}
            attendance_query = {
                'timestamp': {
                    '$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                    '$lt': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                }
            }

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

    def populate_dashboard_table(self, tree, selected_class="Tất cả các lớp"):
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
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
                    tree.insert('', 'end', values=(
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

        threading.Thread(target=run_script, daemon=True).start()

    def open_attendance(self):
        def run_script():
            try:
                os.system('python client/capture_faces.py')
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở cửa sổ điểm danh: {str(e)}")

        threading.Thread(target=run_script, daemon=True).start()

    def __del__(self):
        if hasattr(self, 'client'):
            self.client.close()

def main():
    root = ctk.CTk()
    app = FaceAttendanceSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()