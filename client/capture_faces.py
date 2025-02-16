import cv2
from pymongo import MongoClient
import datetime

# Kết nối MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['face_attendance']
students_col = db['students']
attendance_col = db['attendance']

# Load Haar Cascade
alg = "haarcascade_frontalface_default.xml"
haar_cascade = cv2.CascadeClassifier(alg)
cam = cv2.VideoCapture(0)

attendance_marked = False  # Cờ kiểm tra đã điểm danh chưa

while True:
    _, img = cam.read()
    grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = haar_cascade.detectMultiScale(grayImg, 1.3, 4)

    text_status = "Face not detected"
    attendance_status = ""
    info_lines = []

    # Xử lý khi phát hiện khuôn mặt
    if len(faces) > 0:
        text_status = "Face Detected"

        # Lấy thông tin sinh viên từ MongoDB
        student = students_col.find_one()
        if student:
            name = student.get('name', 'N/A')
            student_id = student.get('student_id', 'N/A')
            class_ = student.get('class', 'N/A')
            info_lines = [
                f"Name: {name}",
                f"ID: {student_id}",
                f"Class: {class_}"
            ]

            # Kiểm tra xem sinh viên đã điểm danh chưa
            if not attendance_marked:
                # Kiểm tra xem sinh viên đã được điểm danh chưa
                existing_record = attendance_col.find_one({"student_id": student_id, "timestamp": {"$gte": datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}})

                if not existing_record:
                    # Ghi nhận điểm danh nếu chưa thực hiện
                    attendance_record = {
                        "student_id": student_id,
                        "name": name,
                        "class": class_,
                        "timestamp": datetime.datetime.now(),
                        "status": "Present",
                        "method": "Face Recognition"
                    }
                    attendance_col.insert_one(attendance_record)
                    attendance_status = "Attendance Successful!"
                    attendance_marked = True

        # Vẽ hình chữ nhật quanh mặt
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    else:
        attendance_marked = False

    # Hiển thị thông tin lên frame
    y_start = 50
    cv2.putText(img, text_status, (50, y_start), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    for idx, line in enumerate(info_lines):
        cv2.putText(img, line, (50, y_start + 30 * (idx + 1)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    if attendance_status:
        cv2.putText(img, attendance_status, (50, y_start + 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Face Detection", img)

    # Thoát bằng phím ESC
    key = cv2.waitKey(10)
    if key == 27:
        break

cam.release()
cv2.destroyAllWindows()