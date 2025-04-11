import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import pymongo
import gridfs
import os
import numpy as np
import face_recognition
from tkinter import messagebox

class AddStudentWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Thêm Sinh Viên Mới")
        self.root.geometry("800x600")
        
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
        self.face_encodings = []  # Lưu trữ face encodings

    def create_widgets(self):
        # Frame cho thông tin sinh viên
        info_frame = ttk.LabelFrame(self.root, text="Thông tin sinh viên", padding=20)
        info_frame.pack(fill='x', padx=20, pady=10)

        # Labels và Entries
        ttk.Label(info_frame, text="Họ và tên:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(info_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(info_frame, text="Mã sinh viên:").grid(row=1, column=0, padx=5, pady=5)
        self.id_entry = ttk.Entry(info_frame, width=30)
        self.id_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(info_frame, text="Lớp:").grid(row=2, column=0, padx=5, pady=5)
        self.class_entry = ttk.Entry(info_frame, width=30)
        self.class_entry.grid(row=2, column=1, padx=5, pady=5)

        # Frame cho camera
        self.camera_frame = ttk.LabelFrame(self.root, text="Chụp ảnh", padding=20)
        self.camera_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.camera_label = ttk.Label(self.camera_frame)
        self.camera_label.pack()

        # Frame cho buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)

        self.start_camera_btn = ttk.Button(
            button_frame, 
            text="Bắt đầu chụp ảnh", 
            command=self.start_camera
        )
        self.start_camera_btn.pack(side='left', padx=5)

        self.capture_btn = ttk.Button(
            button_frame, 
            text="Chụp (C)", 
            command=self.capture_photo,
            state='disabled'
        )
        self.capture_btn.pack(side='left', padx=5)

        self.save_btn = ttk.Button(
            button_frame, 
            text="Lưu thông tin", 
            command=self.save_student,
            state='disabled'
        )
        self.save_btn.pack(side='left', padx=5)

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.capture_btn.configure(state='normal')
        self.update_camera()

    def update_camera(self):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (640, 480))
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)
                self.root.after(10, self.update_camera)

    def capture_photo(self):
        if self.cap is not None and self.photo_count < 5:
            ret, frame = self.cap.read()
            if ret:
                # Tạo thư mục dataset nếu chưa có
                student_id = self.id_entry.get()
                dataset_dir = os.path.join("e:/NCKH2024_2025/FaceAttendanceSystem/dataset", student_id)
                os.makedirs(dataset_dir, exist_ok=True)

                # Lưu ảnh
                photo_filename = os.path.join(dataset_dir, f"{student_id}_{self.photo_count}.jpg")
                cv2.imwrite(photo_filename, frame)

                # Lưu vào MongoDB
                with open(photo_filename, "rb") as image_file:
                    image_id = self.fs.put(image_file, filename=photo_filename)
                    self.image_ids.append(image_id)

                # Tính toán face encoding
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_encodings = face_recognition.face_encodings(rgb_frame)
                if face_encodings:
                    # Lưu face encoding đầu tiên (nếu có khuôn mặt)
                    self.face_encodings.append(face_encodings[0])
                    self.photo_count += 1
                else:
                    messagebox.showwarning("Cảnh báo", "Không phát hiện khuôn mặt trong ảnh này. Vui lòng thử lại.")

                if self.photo_count >= 5:
                    self.capture_btn.configure(state='disabled')
                    self.save_btn.configure(state='normal')
                    self.cap.release()
                    self.cap = None

    def save_student(self):
        try:
            # Kiểm tra thông tin đầu vào
            if not self.name_entry.get() or not self.id_entry.get() or not self.class_entry.get():
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin sinh viên")
                return

            # Kiểm tra trùng lặp student_id
            if self.students_col.find_one({"student_id": self.id_entry.get()}):
                messagebox.showerror("Lỗi", "Mã sinh viên đã tồn tại. Vui lòng nhập mã khác.")
                return

            if len(self.image_ids) < 5:
                messagebox.showerror("Lỗi", "Vui lòng chụp đủ 5 tấm ảnh")
                return

            if len(self.face_encodings) < 5:
                messagebox.showerror("Lỗi", "Không phải tất cả ảnh đều chứa khuôn mặt. Vui lòng chụp lại.")
                return

            # Tính trung bình face encodings
            mean_face_encoding = np.mean(self.face_encodings, axis=0).tolist()

            # Tạo bản ghi sinh viên
            student_record = {
                'name': self.name_entry.get(),
                'student_id': self.id_entry.get(),
                'class': self.class_entry.get(),
                'images': self.image_ids,
                'face_encoding': mean_face_encoding  # Lưu face encoding
            }

            # Lưu vào cơ sở dữ liệu
            self.students_col.insert_one(student_record)

            # Hiển thị thông báo thành công
            messagebox.showinfo(
                "Thành công", 
                f"Đã lưu thông tin sinh viên:\nHọ tên: {student_record['name']}\nMSSV: {student_record['student_id']}\nLớp: {student_record['class']}"
            )
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu thông tin sinh viên: {str(e)}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AddStudentWindow()
    app.run()