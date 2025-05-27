import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import pymongo
import gridfs
import os
import numpy as np
import face_recognition
from tkinter import messagebox

class ModernStyle:
    # Màu sắc chủ đề
    PRIMARY = "#00923F"
    SECONDARY = "#764ba2"
    ACCENT = "#f093fb"
    SUCCESS = "#78c680"
    WARNING = "#f093fb"
    DANGER = "#ff6b6b"
    DARK = "#354453"
    LIGHT = "#ecf0f1"
    WHITE = "#ffffff"
    GRAY = "#95a5a6"
    
    # Fonts
    TITLE_FONT = ("Segoe UI", 20, "bold")
    HEADER_FONT = ("Segoe UI", 14, "bold")
    NORMAL_FONT = ("Segoe UI", 11)
    SMALL_FONT = ("Segoe UI", 9)

class AddStudentWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎓 Đăng ký sinh viên")
        self.root.geometry("1000x700")
        self.root.configure(bg=ModernStyle.LIGHT)
        
        # Cấu hình style
        self.setup_styles()
        
        # Kết nối MongoDB
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["face_attendance"]
        self.students_col = self.db["students"]
        self.fs = gridfs.GridFS(self.db)

        # Tạo giao diện
        self.create_widgets()
        
        # Khởi tạo camera
        self.cap = None
        self.photo_count = 0
        self.image_ids = []
        self.face_encodings = []
        
        # Bind events
        self.root.bind('<Key-c>', lambda e: self.capture_photo())
        self.root.focus_set()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Style cho các frame
        style.configure("Title.TFrame", background=ModernStyle.PRIMARY)
        style.configure("Card.TFrame", background=ModernStyle.WHITE, relief="raised")
        style.configure("Camera.TFrame", background=ModernStyle.DARK, relief="sunken")
        
        # Style cho labels
        style.configure("Title.TLabel", 
                       background=ModernStyle.PRIMARY, 
                       foreground=ModernStyle.WHITE,
                       font=ModernStyle.TITLE_FONT)
        style.configure("Header.TLabel", 
                       background=ModernStyle.WHITE,
                       foreground=ModernStyle.DARK, 
                       font=ModernStyle.HEADER_FONT)
        style.configure("Info.TLabel", 
                       background=ModernStyle.WHITE,
                       foreground=ModernStyle.GRAY, 
                       font=ModernStyle.NORMAL_FONT)
        style.configure("Status.TLabel", 
                       background=ModernStyle.DARK,
                       foreground=ModernStyle.SUCCESS, 
                       font=ModernStyle.SMALL_FONT)
        
        # Style cho buttons
        style.configure("Primary.TButton",
                       background=ModernStyle.PRIMARY,
                       foreground=ModernStyle.WHITE,
                       font=ModernStyle.NORMAL_FONT,
                       focuscolor="none")
        style.configure("Success.TButton",
                       background=ModernStyle.SUCCESS,
                       foreground=ModernStyle.WHITE,
                       font=ModernStyle.NORMAL_FONT,
                       focuscolor="none")
        style.configure("Warning.TButton",
                       background=ModernStyle.WARNING,
                       foreground=ModernStyle.WHITE,
                       font=ModernStyle.NORMAL_FONT,
                       focuscolor="none")
        
        # Style cho entries
        style.configure("Modern.TEntry",
                       fieldbackground=ModernStyle.WHITE,
                       borderwidth=2,
                       relief="solid",
                       font=ModernStyle.NORMAL_FONT)

    def create_widgets(self):
        # Header với title
        self.create_header()
        
        # Main container
        main_container = tk.Frame(self.root, bg=ModernStyle.LIGHT)
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel - Thông tin sinh viên
        self.create_info_panel(main_container)
        
        # Right panel - Camera
        self.create_camera_panel(main_container)
        
        # Bottom panel - Status và buttons
        self.create_bottom_panel()

    def create_header(self):
        header_frame = tk.Frame(self.root, bg=ModernStyle.PRIMARY, height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Title với icon
        title_container = tk.Frame(header_frame, bg=ModernStyle.PRIMARY)
        title_container.pack(expand=True)
        
        title_label = tk.Label(
            title_container,
            text="🎓 Đăng ký sinh viên",
            font=ModernStyle.TITLE_FONT,
            bg=ModernStyle.PRIMARY,
            fg=ModernStyle.WHITE
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            title_container,
            text="Thêm sinh viên mới vào hệ thống",
            font=ModernStyle.SMALL_FONT,
            bg=ModernStyle.PRIMARY,
            fg=ModernStyle.LIGHT
        )
        subtitle_label.pack()

    def create_info_panel(self, parent):
        # Left panel frame
        left_panel = tk.Frame(parent, bg=ModernStyle.LIGHT)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Student info card
        info_card = tk.Frame(left_panel, bg=ModernStyle.WHITE, relief='raised', bd=2)
        info_card.pack(fill='x', pady=10)
        
        # Card header
        card_header = tk.Frame(info_card, bg=ModernStyle.WHITE)
        card_header.pack(fill='x', padx=20, pady=(20, 10))
        
        header_label = tk.Label(
            card_header,
            text="📝 Thông tin sinh viên",
            font=ModernStyle.HEADER_FONT,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.DARK
        )
        header_label.pack(anchor='w')
        
        # Form fields
        form_frame = tk.Frame(info_card, bg=ModernStyle.WHITE)
        form_frame.pack(fill='x', padx=20, pady=20)
        
        # Name field
        self.create_form_field(form_frame, "👤 Họ tên:", 0)
        self.name_entry = tk.Entry(
            form_frame, 
            font=ModernStyle.NORMAL_FONT,
            bg=ModernStyle.WHITE,
            relief='solid',
            bd=2,
            width=30
        )
        self.name_entry.grid(row=0, column=1, padx=(10, 0), pady=10, sticky='ew')
        
        # Student ID field
        self.create_form_field(form_frame, "🎫 MSV:", 1)
        self.id_entry = tk.Entry(
            form_frame,
            font=ModernStyle.NORMAL_FONT,
            bg=ModernStyle.WHITE,
            relief='solid',
            bd=2,
            width=30
        )
        self.id_entry.grid(row=1, column=1, padx=(10, 0), pady=10, sticky='ew')
        
        # Class field
        self.create_form_field(form_frame, "🏫 Lớp:", 2)
        self.class_entry = tk.Entry(
            form_frame,
            font=ModernStyle.NORMAL_FONT,
            bg=ModernStyle.WHITE,
            relief='solid',
            bd=2,
            width=30
        )
        self.class_entry.grid(row=2, column=1, padx=(10, 0), pady=10, sticky='ew')
        
        form_frame.columnconfigure(1, weight=1)
        
        # Progress indicator
        self.create_progress_indicator(info_card)

    def create_form_field(self, parent, text, row):
        label = tk.Label(
            parent,
            text=text,
            font=ModernStyle.NORMAL_FONT,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.DARK,
            anchor='w'
        )
        label.grid(row=row, column=0, padx=(0, 10), pady=10, sticky='w')

    def create_progress_indicator(self, parent):
        progress_frame = tk.Frame(parent, bg=ModernStyle.WHITE)
        progress_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        progress_label = tk.Label(
            progress_frame,
            text="📸 Tiến trình:",
            font=ModernStyle.NORMAL_FONT,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.DARK
        )
        progress_label.pack(anchor='w')
        
        # Progress indicators
        self.progress_indicators = tk.Frame(progress_frame, bg=ModernStyle.WHITE)
        self.progress_indicators.pack(anchor='w', pady=(5, 0))
        
        self.photo_indicators = []
        for i in range(5):
            indicator = tk.Label(
                self.progress_indicators,
                text="○",
                font=("Segoe UI", 16),
                bg=ModernStyle.WHITE,
                fg=ModernStyle.GRAY
            )
            indicator.pack(side='left', padx=2)
            self.photo_indicators.append(indicator)

    def create_camera_panel(self, parent):
        # Right panel frame
        right_panel = tk.Frame(parent, bg=ModernStyle.LIGHT)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Camera card
        camera_card = tk.Frame(right_panel, bg=ModernStyle.DARK, relief='raised', bd=2)
        camera_card.pack(fill='both', expand=True, pady=10)
        
        # Camera header
        camera_header = tk.Frame(camera_card, bg=ModernStyle.DARK)
        camera_header.pack(fill='x', padx=20, pady=(20, 10))
        
        camera_title = tk.Label(
            camera_header,
            text="📷 Camera Preview",
            font=ModernStyle.HEADER_FONT,
            bg=ModernStyle.DARK,
            fg=ModernStyle.WHITE
        )
        camera_title.pack(anchor='w')
        
        # Camera display container
        camera_container = tk.Frame(camera_card, bg=ModernStyle.DARK)
        camera_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.camera_label = tk.Label(
            camera_container,
            text="📹\nCamera chưa khởi động\nẤn 'Start Camera' để bắt đầu",
            font=ModernStyle.NORMAL_FONT,
            bg=ModernStyle.DARK,
            fg=ModernStyle.GRAY,
            justify='center'
        )
        self.camera_label.pack(fill='both', expand=True)
        
        # Camera status
        self.camera_status = tk.Label(
            camera_card,
            text="Status: Ready",
            font=ModernStyle.SMALL_FONT,
            bg=ModernStyle.DARK,
            fg=ModernStyle.SUCCESS
        )
        self.camera_status.pack(pady=10)

    def create_bottom_panel(self):
        bottom_panel = tk.Frame(self.root, bg=ModernStyle.LIGHT, height=100)
        bottom_panel.pack(fill='x', padx=20, pady=20)
        bottom_panel.pack_propagate(False)
        
        # Button container
        button_container = tk.Frame(bottom_panel, bg=ModernStyle.LIGHT)
        button_container.pack(expand=True, fill='both')
        
        # Create a centered frame for buttons
        centered_frame = tk.Frame(button_container, bg=ModernStyle.LIGHT)
        centered_frame.pack(expand=True)
        
        # Start camera button
        self.start_camera_btn = tk.Button(
            centered_frame,
            text="🎥 Start Camera",
            font=ModernStyle.NORMAL_FONT,
            bg=ModernStyle.PRIMARY,
            fg=ModernStyle.WHITE,
            relief='flat',
            padx=25,
            pady=12,
            command=self.start_camera,
            cursor='hand2'
        )
        self.start_camera_btn.pack(side='left', padx=8, pady=5)
        
        # Capture button
        self.capture_btn = tk.Button(
            centered_frame,
            text="📸 Chụp ảnh (C)",
            font=ModernStyle.NORMAL_FONT,
            bg=ModernStyle.WARNING,
            fg=ModernStyle.WHITE,
            relief='flat',
            padx=25,
            pady=12,
            command=self.capture_photo,
            state='disabled',
            cursor='hand2'
        )
        self.capture_btn.pack(side='left', padx=8, pady=5)
        
        # Save button
        self.save_btn = tk.Button(
            centered_frame,
            text="💾 Lưu",
            font=ModernStyle.NORMAL_FONT,
            bg=ModernStyle.SUCCESS,
            fg=ModernStyle.WHITE,
            relief='flat',
            padx=25,
            pady=12,
            command=self.save_student,
            state='disabled',
            cursor='hand2'
        )
        self.save_btn.pack(side='left', padx=8, pady=5)
        
        # Instructions
        instructions = tk.Label(
            button_container,
            text="💡 Hướng dẫn: Điền thông tin sinh viên → Start camera → Chụp 5 ảnh → Lưu",
            font=ModernStyle.SMALL_FONT,
            bg=ModernStyle.LIGHT,
            fg=ModernStyle.GRAY
        )
        instructions.pack(side='bottom', pady=(5, 0))

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if self.cap.isOpened():
            self.capture_btn.configure(state='normal', bg=ModernStyle.SUCCESS)
            self.camera_status.configure(text="Status: Camera Active", fg=ModernStyle.SUCCESS)
            self.start_camera_btn.configure(state='disabled', text="🎥 Camera Started")
            self.update_camera()
        else:
            messagebox.showerror("Lỗi", "Không thể mở camera!")

    def update_camera(self):
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Get camera container size and scale frame accordingly
                self.root.update_idletasks()
                container_width = self.camera_label.winfo_width()
                container_height = self.camera_label.winfo_height()
                
                # Use a good default size that scales well
                target_width = 640
                target_height = 480
                
                # If container is properly sized, scale to fit
                if container_width > 100 and container_height > 100:
                    # Calculate aspect ratio preserving resize
                    original_height, original_width = frame.shape[:2]
                    aspect_ratio = original_width / original_height
                    
                    # Add some margin
                    available_width = container_width - 40
                    available_height = container_height - 40
                    
                    if available_width / available_height > aspect_ratio:
                        # Container is wider, fit to height
                        target_height = min(available_height, 480)
                        target_width = int(target_height * aspect_ratio)
                    else:
                        # Container is taller, fit to width  
                        target_width = min(available_width, 640)
                        target_height = int(target_width / aspect_ratio)
                
                frame = cv2.resize(frame, (target_width, target_height))
                
                # Create rounded corners effect
                img = Image.fromarray(frame)
                img = self.add_rounded_corners(img, 15)
                
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)
                self.root.after(30, self.update_camera)

    def add_rounded_corners(self, img, radius):
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0) + img.size, radius=radius, fill=255)
        
        result = Image.new('RGBA', img.size, (0, 0, 0, 0))
        result.paste(img, (0, 0))
        result.putalpha(mask)
        return result

    def capture_photo(self):
        if self.cap is not None and self.photo_count < 5:
            ret, frame = self.cap.read()
            if ret:
                # Flip frame for consistency
                frame = cv2.flip(frame, 1)
                
                # Tạo thư mục dataset nếu chưa có
                student_id = self.id_entry.get()
                if not student_id:
                    messagebox.showwarning("Cảnh báo", "Nhập mã sinh viên trước khi chụp ảnh!")
                    return
                    
                dataset_dir = os.path.join("e:/NCKH2024_2025/FaceAttendanceSystem/dataset", student_id)
                os.makedirs(dataset_dir, exist_ok=True)

                # Lưu ảnh
                photo_filename = os.path.join(dataset_dir, f"{student_id}_{self.photo_count}.jpg")
                cv2.imwrite(photo_filename, cv2.flip(frame, 1))

                # Lưu vào MongoDB
                with open(photo_filename, "rb") as image_file:
                    image_id = self.fs.put(image_file, filename=photo_filename)
                    self.image_ids.append(image_id)

                # Tính toán face encoding
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_encodings = face_recognition.face_encodings(rgb_frame)
                if face_encodings:
                    self.face_encodings.append(face_encodings[0])
                    self.photo_count += 1
                    
                    # Update progress indicator
                    self.photo_indicators[self.photo_count - 1].configure(
                        text="●", 
                        fg=ModernStyle.SUCCESS
                    )
                    
                    # Update status
                    self.camera_status.configure(
                        text=f"Status: {self.photo_count}/5 đã chụp",
                        fg=ModernStyle.SUCCESS
                    )
                    
                    # Flash effect
                    self.flash_effect()
                    
                else:
                    messagebox.showwarning("Cảnh báo", "Không phát hiện khuôn mặt. Vui lòng thử lại.")

                if self.photo_count >= 5:
                    self.capture_btn.configure(state='disabled', bg=ModernStyle.GRAY)
                    self.save_btn.configure(state='normal', bg=ModernStyle.SUCCESS)
                    self.camera_status.configure(
                        text="Status: Tất cả ảnh đã chụp! Sẵn sàng để lưu.",
                        fg=ModernStyle.WARNING
                    )
                    if self.cap:
                        self.cap.release()
                        self.cap = None

    def flash_effect(self):
        # Simple flash effect
        original_bg = self.camera_label.cget('bg')
        self.camera_label.configure(bg='white')
        self.root.after(100, lambda: self.camera_label.configure(bg=original_bg))

    def save_student(self):
        try:
            # Kiểm tra thông tin đầu vào
            if not self.name_entry.get() or not self.id_entry.get() or not self.class_entry.get():
                messagebox.showerror("Lỗi", "Hãy điền đầy đủ thông tin!")
                return

            # Kiểm tra trùng lặp student_id
            if self.students_col.find_one({"student_id": self.id_entry.get()}):
                messagebox.showerror("Lỗi", "MSV đã tồn tại!")
                return

            if len(self.image_ids) < 5:
                messagebox.showerror("Lỗi", "Hãy chụp đủ 5 ảnh!")
                return

            if len(self.face_encodings) < 5:
                messagebox.showerror("Lỗi", "Vui lòng chụp lại ảnh")
                return

            # Tính trung bình face encodings
            mean_face_encoding = np.mean(self.face_encodings, axis=0).tolist()

            # Tạo bản ghi sinh viên
            student_record = {
                'name': self.name_entry.get(),
                'student_id': self.id_entry.get(),
                'class': self.class_entry.get(),
                'images': self.image_ids,
                'face_encoding': mean_face_encoding
            }

            # Lưu vào cơ sở dữ liệu
            self.students_col.insert_one(student_record)

            # Success dialog với style đẹp
            success_msg = f"""✅ Đăng ký sinh viên thành công!
            
👤 Name: {student_record['name']}
🎫 Student ID: {student_record['student_id']}
🏫 Class: {student_record['class']}
📸 Photos: 5 images captured
🤖 Face encoding: Generated"""
            
            messagebox.showinfo("Success", success_msg)
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Cannot save student information: {str(e)}")

    def run(self):
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        self.root.mainloop()

if __name__ == "__main__":
    app = AddStudentWindow()
    app.run()