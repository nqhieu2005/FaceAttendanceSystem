import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import os
from pymongo import MongoClient
from datetime import datetime
from ttkthemes import ThemedStyle

class FaceAttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống Điểm danh Khuôn mặt")
        self.root.geometry("1200x800")
        
        # Set theme and styles
        self.style = ThemedStyle(self.root)
        self.style.set_theme("arc")
        
        # Define color scheme
        self.colors = {
            'bg': '#f0f0f0',
            'button': '#2196f3',
            'button_hover': '#1976d2',
            'header': '#1565c0',
            'text': '#333333'
        }
        
        self.root.configure(bg=self.colors['bg'])

        # MongoDB connection
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['face_attendance']
        self.attendance_col = self.db['attendance']

        # Create main container
        self.create_main_container()
        self.create_header()
        self.create_navigation()
        self.create_attendance_table()
        self.create_status_bar()

    def create_main_container(self):
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Configure styles
        self.style.configure(
            'Header.TLabel',
            font=('Helvetica', 28, 'bold'),
            foreground=self.colors['header'],
            background=self.colors['bg']
        )
        
        self.style.configure(
            'Navigation.TButton',
            font=('Helvetica', 12),
            padding=15
        )

    def create_header(self):
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill='x', pady=(0, 20))
        
        title = ttk.Label(
            header_frame,
            text="HỆ THỐNG ĐIỂM DANH KHUÔN MẶT",
            style='Header.TLabel'
        )
        title.pack()

    def create_navigation(self):
        nav_frame = ttk.Frame(self.main_container)
        nav_frame.pack(fill='x', pady=(0, 20))
        
        # Create modern buttons using customtkinter
        button_style = {
            'font': ('Helvetica', 12),
            'corner_radius': 10,
            'height': 40,
            'width': 200,
            'fg_color': self.colors['button'],
            'hover_color': self.colors['button_hover']
        }
        
        self.add_student_btn = ctk.CTkButton(
            nav_frame,
            text="Thêm Sinh Viên",
            command=self.open_add_student,
            **button_style
        )
        self.add_student_btn.pack(side='left', padx=10)
        
        self.attendance_btn = ctk.CTkButton(
            nav_frame,
            text="Điểm Danh",
            command=self.open_attendance,
            **button_style
        )
        self.attendance_btn.pack(side='left', padx=10)
        
        self.view_attendance_btn = ctk.CTkButton(
            nav_frame,
            text="Xem Danh Sách Điểm Danh",
            command=self.show_attendance_list,
            **button_style
        )
        self.view_attendance_btn.pack(side='left', padx=10)

    def create_attendance_table(self):
        self.attendance_frame = ttk.Frame(self.main_container)
        self.attendance_frame.pack(fill='both', expand=True, pady=10)
        
        # Configure Treeview style
        self.style.configure(
            'Treeview',
            background='white',
            foreground=self.colors['text'],
            rowheight=30,
            fieldbackground='white',
            font=('Helvetica', 10)
        )
        
        self.style.configure(
            'Treeview.Heading',
            font=('Helvetica', 11, 'bold')
        )
        
        # Create Treeview
        self.tree = ttk.Treeview(self.attendance_frame)
        self.tree["columns"] = ("name", "student_id", "class", "time", "status")
        
        # Configure columns
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("name", width=250, anchor=tk.W)
        self.tree.column("student_id", width=150, anchor=tk.W)
        self.tree.column("class", width=150, anchor=tk.W)
        self.tree.column("time", width=200, anchor=tk.W)
        self.tree.column("status", width=150, anchor=tk.W)
        
        # Configure headings
        self.tree.heading("#0", text="")
        self.tree.heading("name", text="Họ và tên", anchor=tk.W)
        self.tree.heading("student_id", text="Mã sinh viên", anchor=tk.W)
        self.tree.heading("class", text="Lớp", anchor=tk.W)
        self.tree.heading("time", text="Thời gian", anchor=tk.W)
        self.tree.heading("status", text="Trạng thái", anchor=tk.W)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.attendance_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack elements
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Hide initially
        self.attendance_frame.pack_forget()

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(10, 5)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Sẵn sàng")

    def open_add_student(self):
        import client.recognize_face as recognize_face
        self.status_var.set("Đang mở cửa sổ thêm sinh viên...")
        try:
            os.system('python client/recognize_face.py')
            self.status_var.set("Đã mở cửa sổ thêm sinh viên")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở cửa sổ thêm sinh viên: {str(e)}")
            self.status_var.set("Lỗi khi mở cửa sổ thêm sinh viên")

    def open_attendance(self):
        import client.capture_faces as capture_faces
        self.status_var.set("Đang mở cửa sổ điểm danh...")
        try:
            os.system('python client/capture_faces.py')
            self.status_var.set("Đã mở cửa sổ điểm danh")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở cửa sổ điểm danh: {str(e)}")
            self.status_var.set("Lỗi khi mở cửa sổ điểm danh")

    def show_attendance_list(self):
        self.attendance_frame.pack(fill='both', expand=True)
        self.status_var.set("Đang tải danh sách điểm danh...")
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            attendance_records = self.attendance_col.find({}).sort("timestamp", -1)
            
            for record in attendance_records:
                time_str = record.get('timestamp', datetime.now()).strftime("%d-%m-%Y %H:%M:%S")
                
                self.tree.insert("", "end", values=(
                    record.get('name', 'N/A'),
                    record.get('student_id', 'N/A'),
                    record.get('class', 'N/A'),
                    time_str,
                    record.get('status', 'N/A')
                ))
            
            self.status_var.set(f"Đã tải {self.tree.get_children().__len__()} bản ghi")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách điểm danh: {str(e)}")
            self.status_var.set("Lỗi khi tải danh sách điểm danh")

    def __del__(self):
        if hasattr(self, 'client'):
            self.client.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceAttendanceSystem(root)
    root.mainloop()