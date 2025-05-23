import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
from pymongo import MongoClient
import datetime
import numpy as np
import face_recognition

class AttendanceWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Điểm Danh Sinh Viên")
        self.root.geometry("1200x900")
        self.root.configure(bg='#f0f2f5')
        
        # Icon và cấu hình cửa sổ
        self.root.resizable(True, True)
        self.root.minsize(1000, 700)

        # Kết nối MongoDB
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['face_attendance']
        self.students_col = self.db['students']
        self.attendance_col = self.db['attendance']

        # Khởi tạo các biến
        self.cap = None
        self.attendance_marked = False
        self.current_student_id = None
        self.stats_label = None  # Lưu reference cho stats label để cập nhật
        
        # Cấu hình style
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        """Cấu hình các style cho giao diện"""
        style = ttk.Style()
        
        # Style cho header
        style.configure("Header.TLabel", 
                       font=('Segoe UI', 24, 'bold'),
                       foreground='#27ae60')
        
        # Style cho thông tin
        style.configure("Info.TLabel",
                       font=('Segoe UI', 11),
                       foreground='#2c3e50')
        
        style.configure("InfoTitle.TLabel",
                       font=('Segoe UI', 12, 'bold'),
                       foreground='#27ae60')
        
        # Style cho button
        style.configure("Modern.TButton",
                       font=('Segoe UI', 10),
                       padding=(20, 10))

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#f0f2f5', height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        header_label = ttk.Label(header_frame, 
                                text="🌿 HỆ THỐNG ĐIỂM DANH SINH VIÊN",
                                style="Header.TLabel")
        header_label.pack(expand=True)
        
        # Container chính
        main_container = tk.Frame(self.root, bg='#f0f2f5')
        main_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Left panel - Camera
        left_panel = tk.Frame(main_container, bg='#f0f2f5')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Camera frame với style hiện đại
        self.camera_frame = ttk.LabelFrame(left_panel, 
                                          text="📹 Camera Nhận Diện",
                                          padding=20)
        self.camera_frame.pack(fill='both', expand=True)
        
        # Camera container với border radius effect
        camera_container = tk.Frame(self.camera_frame, bg='#ffffff', relief='solid', bd=2)
        camera_container.pack(expand=True, fill='both')
        
        self.camera_label = tk.Label(camera_container, 
                                    text="📷\n\nCamera sẽ hiển thị tại đây\n\nNhấn 'Bắt đầu' để khởi động",
                                    font=('Segoe UI', 14),
                                    fg='#7f8c8d',
                                    bg='#e8f5e8',
                                    justify='center')
        self.camera_label.pack(expand=True, fill='both')
        
        # Right panel - Thông tin và điều khiển
        right_panel = tk.Frame(main_container, bg='#f0f2f5', width=400)
        right_panel.pack(side='right', fill='y', padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Control panel
        control_frame = ttk.LabelFrame(right_panel, 
                                      text="🎮 Điều Khiển",
                                      padding=20)
        control_frame.pack(fill='x', pady=(0, 20))
        
        # Status indicator
        self.status_frame = tk.Frame(control_frame, bg='#ffffff')
        self.status_frame.pack(fill='x', pady=(0, 15))
        
        self.status_indicator = tk.Label(self.status_frame,
                                        text="●",
                                        font=('Segoe UI', 20),
                                        fg='#e74c3c',
                                        bg='#ffffff')
        self.status_indicator.pack(side='left')
        
        self.status_text = tk.Label(self.status_frame,
                                   text="Camera đang tắt",
                                   font=('Segoe UI', 11, 'bold'),
                                   fg='#e74c3c',
                                   bg='#ffffff')
        self.status_text.pack(side='left', padx=(10, 0))
        
        # Buttons với style hiện đại
        self.start_btn = ttk.Button(control_frame,
                                   text="🚀 Bắt đầu điểm danh",
                                   command=self.start_camera,
                                   style="Modern.TButton")
        self.start_btn.pack(fill='x', pady=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame,
                                  text="⏹️ Dừng điểm danh",
                                  command=self.stop_camera,
                                  style="Modern.TButton",
                                  state='disabled')
        self.stop_btn.pack(fill='x')
        
        # Information panel
        self.info_frame = ttk.LabelFrame(right_panel, 
                                        text="👤 Thông Tin Sinh Viên",
                                        padding=20)
        self.info_frame.pack(fill='both', expand=True)
        
        # Default info display
        self.create_info_display()
        
        # Statistics panel
        stats_frame = ttk.LabelFrame(right_panel, 
                                    text="📊 Thống Kê Hôm Nay",
                                    padding=15)
        stats_frame.pack(fill='x', pady=(20, 0))
        
        self.update_statistics(stats_frame)

    def create_info_display(self):
        """Tạo giao diện hiển thị thông tin sinh viên"""
        # Clear existing widgets
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        # No face detected state
        self.no_face_frame = tk.Frame(self.info_frame, bg='#ffffff')
        self.no_face_frame.pack(expand=True, fill='both')
        
        no_face_icon = tk.Label(self.no_face_frame,
                               text="👤",
                               font=('Segoe UI', 48),
                               fg='#bdc3c7',
                               bg='#ffffff')
        no_face_icon.pack(pady=(20, 10))
        
        self.info_label = tk.Label(self.no_face_frame,
                                  text="Chưa phát hiện khuôn mặt",
                                  font=('Segoe UI', 12),
                                  fg='#7f8c8d',
                                  bg='#ffffff',
                                  justify='center')
        self.info_label.pack()
        
        instruction_label = tk.Label(self.no_face_frame,
                                   text="Đứng trước camera để\ntiến hành điểm danh",
                                   font=('Segoe UI', 10),
                                   fg='#95a5a6',
                                   bg='#ffffff',
                                   justify='center')
        instruction_label.pack(pady=(10, 0))

    def display_student_info(self, student):
        """Hiển thị thông tin chi tiết sinh viên"""
        # Clear existing widgets
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        # Student info container
        info_container = tk.Frame(self.info_frame, bg='#ffffff')
        info_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Avatar placeholder
        avatar_frame = tk.Frame(info_container, bg='#27ae60', width=80, height=80)
        avatar_frame.pack(pady=(0, 15))
        avatar_frame.pack_propagate(False)
        
        avatar_label = tk.Label(avatar_frame,
                               text="👤",
                               font=('Segoe UI', 40),
                               fg='#ffffff',
                               bg='#27ae60')
        avatar_label.pack(expand=True)
        
        # Student details
        details = [
            ("Họ và tên", student.get('name', 'N/A')),
            ("Mã sinh viên", student.get('student_id', 'N/A')),
            ("Lớp", student.get('class', 'N/A')),
            ("Thời gian", datetime.datetime.now().strftime('%H:%M:%S'))
        ]
        
        for label, value in details:
            detail_frame = tk.Frame(info_container, bg='#ffffff')
            detail_frame.pack(fill='x', pady=5)
            
            label_widget = tk.Label(detail_frame,
                                   text=f"{label}:",
                                   font=('Segoe UI', 10, 'bold'),
                                   fg='#34495e',
                                   bg='#ffffff',
                                   anchor='w')
            label_widget.pack(fill='x')
            
            value_widget = tk.Label(detail_frame,
                                   text=value,
                                   font=('Segoe UI', 11),
                                   fg='#2c3e50',
                                   bg='#ffffff',
                                   anchor='w')
            value_widget.pack(fill='x', padx=(10, 0))

    def update_statistics(self, parent):
        """Cập nhật thống kê điểm danh"""
        try:
            today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_count = self.attendance_col.count_documents({
                "timestamp": {"$gte": today}
            })
            
            stats_text = f"✅ Đã điểm danh: {today_count} sinh viên"
            
        except Exception as e:
            stats_text = "❌ Không thể tải thống kê"
        
        # Nếu đã có stats_label thì cập nhật, nếu không thì tạo mới
        if hasattr(self, 'stats_label') and self.stats_label:
            self.stats_label.configure(text=stats_text)
        else:
            self.stats_label = tk.Label(parent,
                                       text=stats_text,
                                       font=('Segoe UI', 11, 'bold'),
                                       fg='#27ae60',
                                       bg='#ffffff')
            self.stats_label.pack()

    def refresh_statistics(self):
        """Làm mới thống kê sau khi điểm danh thành công"""
        if hasattr(self, 'stats_label') and self.stats_label:
            try:
                today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                today_count = self.attendance_col.count_documents({
                    "timestamp": {"$gte": today}
                })
                stats_text = f"✅ Đã điểm danh: {today_count} sinh viên"
                self.stats_label.configure(text=stats_text, fg='#27ae60')
            except Exception as e:
                self.stats_label.configure(text="❌ Không thể tải thống kê", fg='#e74c3c')

    def start_camera(self):
        """Khởi động camera"""
        self.cap = cv2.VideoCapture(0)
        if self.cap.isOpened():
            self.start_btn.configure(state='disabled')
            self.stop_btn.configure(state='normal')
            
            # Update status
            self.status_indicator.configure(fg='#27ae60')
            self.status_text.configure(text="Camera đang hoạt động", fg='#27ae60')
            
            self.update_camera()
        else:
            self.show_error("Không thể khởi động camera")

    def stop_camera(self):
        """Dừng camera"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        self.start_btn.configure(state='normal')
        self.stop_btn.configure(state='disabled')
        
        # Update status
        self.status_indicator.configure(fg='#e74c3c')
        self.status_text.configure(text="Camera đang tắt", fg='#e74c3c')
        
        # Reset camera display
        self.camera_label.configure(image='',
                                   text="📷\n\nCamera đã dừng\n\nNhấn 'Bắt đầu' để khởi động lại",
                                   font=('Segoe UI', 14),
                                   fg='#7f8c8d',
                                   bg='#e8f5e8')
        
        # Reset info display
        self.create_info_display()
        self.attendance_marked = False
        self.current_student_id = None

    def update_camera(self):
        """Cập nhật khung hình camera"""
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                # Flip frame horizontally (mirror effect)
                frame = cv2.flip(frame, 1)
                
                # Chuyển đổi frame sang định dạng RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Nhận diện khuôn mặt
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                # Vẽ khung xung quanh khuôn mặt
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(frame, (left, top), (right, bottom), (39, 174, 96), 3)  # Màu xanh lá

                if face_encodings:
                    # So khớp với dữ liệu trong MongoDB
                    student_found = False
                    for face_encoding in face_encodings:
                        students = self.students_col.find()
                        for student in students:
                            stored_encoding = np.array(student['face_encoding'])
                            match = face_recognition.compare_faces([stored_encoding], face_encoding, tolerance=0.5)
                            if match[0]:
                                student_id = student.get('student_id', 'N/A')
                                if self.current_student_id != student_id:
                                    self.current_student_id = student_id
                                    self.display_student_info(student)
                                    self.mark_attendance(student)
                                student_found = True
                                break
                        if student_found:
                            break
                    
                    if not student_found:
                        self.show_unknown_face()
                else:
                    if not self.attendance_marked:
                        self.create_info_display()
                    self.current_student_id = None

                # Hiển thị frame
                frame = cv2.resize(frame, (640, 480))
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk, text="")
                
                self.root.after(10, self.update_camera)

    def show_unknown_face(self):
        """Hiển thị thông báo khuôn mặt không xác định"""
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        unknown_frame = tk.Frame(self.info_frame, bg='#ffffff')
        unknown_frame.pack(expand=True, fill='both')
        
        unknown_icon = tk.Label(unknown_frame,
                               text="❓",
                               font=('Segoe UI', 48),
                               fg='#f39c12',
                               bg='#ffffff')
        unknown_icon.pack(pady=(20, 10))
        
        unknown_label = tk.Label(unknown_frame,
                                text="Khuôn mặt không xác định",
                                font=('Segoe UI', 12, 'bold'),
                                fg='#f39c12',
                                bg='#ffffff')
        unknown_label.pack()
        
        instruction_label = tk.Label(unknown_frame,
                                   text="Vui lòng đăng ký\nkhuôn mặt trước khi điểm danh",
                                   font=('Segoe UI', 10),
                                   fg='#e67e22',
                                   bg='#ffffff',
                                   justify='center')
        instruction_label.pack(pady=(10, 0))

    def mark_attendance(self, student):
        """Đánh dấu điểm danh"""
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
            ModernPopupWindow(self.root, student)
            self.attendance_marked = True
            # Cập nhật thống kê sau khi điểm danh thành công
            self.refresh_statistics()
        else:
            self.show_already_marked(student)

    def show_already_marked(self, student):
        """Hiển thị thông báo đã điểm danh"""
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        marked_frame = tk.Frame(self.info_frame, bg='#ffffff')
        marked_frame.pack(expand=True, fill='both')
        
        marked_icon = tk.Label(marked_frame,
                              text="✅",
                              font=('Segoe UI', 48),
                              fg='#27ae60',
                              bg='#ffffff')
        marked_icon.pack(pady=(20, 10))
        
        name_label = tk.Label(marked_frame,
                             text=student.get('name', 'N/A'),
                             font=('Segoe UI', 14, 'bold'),
                             fg='#2c3e50',
                             bg='#ffffff')
        name_label.pack()
        
        marked_label = tk.Label(marked_frame,
                               text="Đã điểm danh hôm nay!",
                               font=('Segoe UI', 12),
                               fg='#27ae60',
                               bg='#ffffff')
        marked_label.pack(pady=(5, 0))

    def show_error(self, message):
        """Hiển thị thông báo lỗi"""
        error_popup = tk.Toplevel(self.root)
        error_popup.title("Lỗi")
        error_popup.geometry("300x150")
        error_popup.configure(bg='#ffffff')
        
        error_label = tk.Label(error_popup,
                              text=f"❌ {message}",
                              font=('Segoe UI', 12),
                              fg='#e74c3c',
                              bg='#ffffff')
        error_label.pack(expand=True)
        
        ok_btn = ttk.Button(error_popup,
                           text="OK",
                           command=error_popup.destroy)
        ok_btn.pack(pady=10)

    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()

class ModernPopupWindow:
    def __init__(self, parent, student_info):
        self.popup = tk.Toplevel(parent)
        self.popup.title("Điểm Danh Thành Công")
        self.popup.geometry("450x600")
        self.popup.configure(bg='#ffffff')
        
        # Cấu hình popup
        self.popup.attributes('-topmost', True)
        self.popup.grab_set()
        self.popup.focus_force()
        self.popup.resizable(False, False)
        
        # Center the popup
        self.center_popup()
        
        # Create content
        self.create_popup_content(student_info)
        
        # Auto close after 5 seconds
        self.popup.after(5000, self.popup.destroy)

    def center_popup(self):
        """Căn giữa popup trên màn hình"""
        window_width = 450
        window_height = 600
        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.popup.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def create_popup_content(self, student_info):
        """Tạo nội dung popup"""
        # Header với gradient effect simulation
        header_frame = tk.Frame(self.popup, bg='#27ae60', height=100)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Success icon
        success_icon = tk.Label(header_frame,
                               text="✅",
                               font=('Segoe UI', 48),
                               fg='#ffffff',
                               bg='#27ae60')
        success_icon.pack(expand=True)
        
        # Content frame
        content_frame = tk.Frame(self.popup, bg='#ffffff', padx=40, pady=30)
        content_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(content_frame,
                              text="ĐIỂM DANH THÀNH CÔNG!",
                              font=('Segoe UI', 18, 'bold'),
                              fg='#27ae60',
                              bg='#ffffff')
        title_label.pack(pady=(0, 30))
        
        # Student info card
        info_card = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        info_card.pack(fill='x', pady=(0, 30))
        
        # Card header
        card_header = tk.Frame(info_card, bg='#e9ecef', height=40)
        card_header.pack(fill='x')
        card_header.pack_propagate(False)
        
        card_title = tk.Label(card_header,
                             text="👤 THÔNG TIN SINH VIÊN",
                             font=('Segoe UI', 12, 'bold'),
                             fg='#495057',
                             bg='#e9ecef')
        card_title.pack(expand=True)
        
        # Card content
        card_content = tk.Frame(info_card, bg='#f8f9fa', padx=20, pady=20)
        card_content.pack(fill='x')
        
        # Student details
        details = [
            ("Họ và tên", student_info.get('name', 'N/A')),
            ("Mã số SV", student_info.get('student_id', 'N/A')),
            ("Lớp", student_info.get('class', 'N/A')),
            ("Thời gian", datetime.datetime.now().strftime('%H:%M:%S - %d/%m/%Y'))
        ]
        
        for i, (label, value) in enumerate(details):
            detail_frame = tk.Frame(card_content, bg='#f8f9fa')
            detail_frame.pack(fill='x', pady=8)
            
            label_widget = tk.Label(detail_frame,
                                   text=f"{label}:",
                                   font=('Segoe UI', 11, 'bold'),
                                   fg='#6c757d',
                                   bg='#f8f9fa',
                                   anchor='w')
            label_widget.pack(anchor='w')
            
            value_widget = tk.Label(detail_frame,
                                   text=value,
                                   font=('Segoe UI', 12),
                                   fg='#212529',
                                   bg='#f8f9fa',
                                   anchor='w')
            value_widget.pack(anchor='w', padx=(20, 0))
            
            # Add separator line except for last item
            if i < len(details) - 1:
                separator = tk.Frame(detail_frame, bg='#dee2e6', height=1)
                separator.pack(fill='x', pady=(8, 0))
        
        # Close button
        close_btn = tk.Button(content_frame,
                             text="Đóng",
                             command=self.popup.destroy,
                             font=('Segoe UI', 12, 'bold'),
                             fg='#ffffff',
                             bg='#6c757d',
                             activebackground='#5a6268',
                             activeforeground='#ffffff',
                             relief='flat',
                             padx=30,
                             pady=10,
                             cursor='hand2')
        close_btn.pack()
        
        # Auto-close timer display
        self.timer_label = tk.Label(content_frame,
                                   text="Tự động đóng sau 5 giây",
                                   font=('Segoe UI', 9),
                                   fg='#6c757d',
                                   bg='#ffffff')
        self.timer_label.pack(pady=(10, 0))
        
        # Start countdown
        self.countdown(5)

    def countdown(self, seconds):
        """Đếm ngược thời gian tự động đóng"""
        if seconds > 0:
            self.timer_label.configure(text=f"Tự động đóng sau {seconds} giây")
            self.popup.after(1000, lambda: self.countdown(seconds - 1))
        else:
            self.timer_label.configure(text="Đang đóng...")

if __name__ == "__main__":
    app = AttendanceWindow()
    app.run()