from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["face_attendance"]

students_col = db["students"]
attendance_col = db["attendance"]

def add_student(student_id, name, class_name):
    students_col.insert_one({
        "student_id": student_id,
        "name": name,
        "class": class_name,
        "images": []
    })
