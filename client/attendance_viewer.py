# import tkinter as tk
# from tkinter import ttk
# from datetime import datetime
# from pymongo import MongoClient

# class AttendanceViewer(tk.Toplevel):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.title("Chi tiết điểm danh")
#         self.geometry("800x600")
        
#         # Connect to MongoDB
#         self.client = MongoClient('mongodb://localhost:27017/')
#         self.db = self.client['face_attendance']
#         self.attendance_col = self.db['attendance']
        
#         self.create_widgets()
#         self.load_attendance()

#     def create_widgets(self):
#         # Create filters
#         filter_frame = ttk.LabelFrame(self, text="Bộ lọc")
#         filter_frame.pack(fill='x', padx=10, pady=5)
        
#         ttk.Label(filter_frame, text="Lớp:").pack(side='left', padx=5)
#         self.class_var = tk.StringVar()
#         self.class_combo = ttk.Combobox(filter_frame, textvariable=self.class_var)
#         self.class_combo.pack(side='left', padx=5)
        
#         ttk.Label(filter_frame, text="Ngày:").pack(side='left', padx=5)
#         self.date_var = tk.StringVar()
#         self.date_entry = ttk.Entry(filter_frame, textvariable=self.date_var)
#         self.date_entry.pack(side='left', padx=5)
        
#         ttk.Button(filter_frame, text="Lọc", command=self.filter_records).pack(side='left', padx=5)
        
#         # Create table
#         self.tree = ttk.Treeview(self)
#         self.tree["columns"] = ("name", "student_id", "class", "time", "status")
        
#         # Configure columns
#         self.tree.column("#0", width=0, stretch=tk.NO)
#         self.tree.column("name", width=200)
#         self.tree.column("student_id", width=100)
#         self.tree.column("class", width=100)
#         self.tree.column("time", width=150)
#         self.tree.column("status", width=100)
        
#         # Configure headings
#         self.tree.heading("#0", text="")
#         self.tree.heading("name", text="Họ và tên")
#         self.tree.heading("student_id", text="Mã SV")
#         self.tree.heading("class", text="Lớp")
#         self.tree.heading("time", text="Thời gian")
#         self.tree.heading("status", text="Trạng thái")
        
#         # Add scrollbar
#         scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
#         self.tree.configure(yscrollcommand=scrollbar.set)
        
#         # Pack elements
#         self.tree.pack(side="left", fill="both", expand=True)
#         scrollbar.pack(side="right", fill="y")

#     def load_attendance(self):
#         for item in self.tree.get_children():
#             self.tree.delete(item)
            
#         records = self.attendance_col.find({}).sort("timestamp", -1)
        
#         for record in records:
#             time_str = record.get('timestamp', datetime.now()).strftime("%d-%m-%Y %H:%M:%S")
            
#             self.tree.insert("", "end", values=(
#                 record.get('name', 'N/A'),
#                 record.get('student_id', 'N/A'),
#                 record.get('class', 'N/A'),
#                 time_str,
#                 record.get('status', 'N/A')
#             ))

#     def filter_records(self):
#         class_filter = self.class_var.get()
#         date_filter = self.date_var.get()
        
#         query = {}
#         if class_filter:
#             query['class'] = class_filter
#         if date_filter:
#             try:
#                 date = datetime.strptime(date_filter, "%d-%m-%Y")
#                 query['timestamp'] = {
#                     '$gte': date.replace(hour=0, minute=0, second=0),
#                     '$lt': date.replace(hour=23, minute=59, second=59)
#                 }
#             except:
#                 pass
                
#         self.load_attendance()