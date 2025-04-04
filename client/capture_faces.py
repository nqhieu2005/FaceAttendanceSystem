import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
from pymongo import MongoClient
import datetime
import numpy as np

class AttendanceWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Điểm Danh Sinh Viên")
        self.root.geometry("1000x800")

        # Kết nối MongoDB
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['face_attendance']
        self.students_col = self.db['students']
        self.attendance_col = self.db['attendance']

        # Khởi tạo các biến
        self.cap = None
        self.attendance_marked = False
        self.haar_cascade = cv2.CascadeClassifier(
            "E:/NCKH2024_2025/FaceAttendanceSystem/client/haarcascade_frontalface_default.xml"
        )

        self.create_widgets()

    def create_widgets(self):
        # Frame cho camera
        self.camera_frame = ttk.LabelFrame(self.root, text="Camera", padding=20)
        self.camera_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.camera_label = ttk.Label(self.camera_frame)
        self.camera_label.pack()

        # Frame cho thông tin
        self.info_frame = ttk.LabelFrame(self.root, text="Thông tin sinh viên", padding=20)
        self.info_frame.pack(fill='x', padx=20, pady=10)

        self.info_label = ttk.Label(self.info_frame, text="Chưa phát hiện khuôn mặt")
        self.info_label.pack()

        # Button điều khiển
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(pady=20)

        self.start_btn = ttk.Button(
            self.control_frame,
            text="Bắt đầu điểm danh",
            command=self.start_camera
        )
        self.start_btn.pack(side='left', padx=5)

        self.stop_btn = ttk.Button(
            self.control_frame,
            text="Dừng",
            command=self.stop_camera,
            state='disabled'
        )
        self.stop_btn.pack(side='left', padx=5)

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.start_btn.configure(state='disabled')
        self.stop_btn.configure(state='normal')
        self.update_camera()

    def stop_camera(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.start_btn.configure(state='normal')
        self.stop_btn.configure(state='disabled')
        self.camera_label.configure(image='')
        self.info_label.configure(text="Chưa phát hiện khuôn mặt")

    def update_camera(self):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                # Nhận diện khuôn mặt
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.haar_cascade.detectMultiScale(gray, 1.3, 4)

                if len(faces) > 0:
                    # Xử lý khi phát hiện khuôn mặt
                    student = self.students_col.find_one()
                    if student:
                        name = student.get('name', 'N/A')
                        student_id = student.get('student_id', 'N/A')
                        class_ = student.get('class', 'N/A')

                        info_text = f"Họ và tên: {name}\nMã sinh viên: {student_id}\nLớp: {class_}"
                        self.info_label.configure(text=info_text)

                        # Xử lý điểm danh
                        if not self.attendance_marked:
                            self.mark_attendance(student)

                    # Vẽ khung xung quanh khuôn mặt
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                else:
                    self.info_label.configure(text="Chưa phát hiện khuôn mặt")
                    self.attendance_marked = False

                # Hiển thị frame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (640, 480))
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)
                self.root.after(10, self.update_camera)

    def mark_attendance(self, student):
        existing_record = self.attendance_col.find_one({
            "student_id": student['student_id'],
            "timestamp": {
                "$gte": datetime.datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            }
        })

        if not existing_record:
            attendance_record = {
                "student_id": student['student_id'],
                "name": student['name'],
                "class": student['class'],
                "timestamp": datetime.datetime.now(),
                "status": "Có mặt",
                "method": "Nhận diện khuôn mặt"
            }
            self.attendance_col.insert_one(attendance_record)
            PopupWindow(self.root, student)
            self.attendance_marked = True
        else:
            self.info_label.configure(
                text=self.info_label.cget("text") + "\n\nĐã điểm danh hôm nay!"
            )
            self.attendance_marked = True

    def run(self):
        self.root.mainloop()

class PopupWindow:
    def __init__(self, parent, student_info):
        self.popup = tk.Toplevel(parent)
        self.popup.title("Điểm Danh Thành Công")
        self.popup.geometry("400x500")
        
        # Đảm bảo popup luôn hiển thị trên cùng và grab focus
        self.popup.attributes('-topmost', True)
        self.popup.grab_set()
        self.popup.focus_force()
        
        # Đặt cửa sổ ở giữa màn hình
        window_width = 400
        window_height = 500
        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.popup.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Thiết lập style với màu sắc nổi bật hơn
        style = ttk.Style()
        style.configure("Success.TLabel", foreground="#00b300", font=('Arial', 50, 'bold'))
        style.configure("Title.TLabel", font=('Arial', 18, 'bold'), foreground='#000000')
        style.configure("Info.TLabel", font=('Arial', 12))
        style.configure("Custom.TButton", font=('Arial', 12))

        # Container chính với nền màu để dễ nhìn
        main_frame = ttk.Frame(self.popup, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        success_label = ttk.Label(main_frame, text="✓", style="Success.TLabel")
        success_label.pack(pady=(20, 10))
        
        # Tiêu đề
        title_label = ttk.Label(
            main_frame,
            text="ĐIỂM DANH THÀNH CÔNG",
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 20))
        
        # Khung thông tin
        info_frame = ttk.LabelFrame(
            main_frame,
            text="Thông tin sinh viên",
            padding=15
        )
        info_frame.pack(fill='x', padx=10)
        
        # Thông tin chi tiết
        info_list = [
            ("Họ và tên", student_info['name']),
            ("Mã số SV", student_info['student_id']),
            ("Lớp", student_info['class']),
            ("Thời gian", datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y'))
        ]
        
        for label, value in info_list:
            info_container = ttk.Frame(info_frame)
            info_container.pack(fill='x', pady=5)
            
            ttk.Label(
                info_container,
                text=f"{label}:",
                style="Info.TLabel",
                width=10
            ).pack(side='left')
            
            ttk.Label(
                info_container,
                text=value,
                style="Info.TLabel"
            ).pack(side='left', padx=(10, 0))
        
        # Nút đóng
        close_btn = ttk.Button(
            main_frame,
            text="Đóng",
            command=self.popup.destroy,
            style="Custom.TButton",
            width=20
        )
        close_btn.pack(pady=30)
        
        # Tự động đóng sau 5 giây nhưng không có fade effect
        self.popup.after(5000, self.popup.destroy)

if __name__ == "__main__":
    app = AttendanceWindow()
    app.run()