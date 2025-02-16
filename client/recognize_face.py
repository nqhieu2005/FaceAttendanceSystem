import face_recognition
import numpy as np
import pymongo
import gridfs
from io import BytesIO
import cv2
from datetime import datetime

# Kết nối tới MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["face_attendance"]
students_col = db["students"]
attendance_col = db["attendance"]
fs = gridfs.GridFS(db)

# Danh sách chứa đặc trưng khuôn mặt và thông tin sinh viên
known_face_encodings = []
known_face_info = []  # Mỗi phần tử là dict chứa: name, student_id, class

# Load dữ liệu sinh viên từ MongoDB
students = students_col.find()
for student in students:
    if 'images' in student and len(student['images']) > 0:
        file_id = student['images'][0]
        try:
            file_data = fs.get(file_id).read()
            # Debug: in kích thước file
            print(f"[DEBUG] Kích thước file của {student.get('name', 'Unknown')}: {len(file_data)} bytes")
        except Exception as e:
            print(f"Lỗi khi đọc ảnh của {student.get('name', 'Unknown')}: {e}")
            continue

        try:
            # Đọc ảnh từ dữ liệu byte (sử dụng BytesIO)
            image = face_recognition.load_image_file(BytesIO(file_data))
        except Exception as e:
            print(f"Lỗi khi load ảnh của {student.get('name', 'Unknown')}: {e}")
            continue

        # Bắt buộc tạo một bản sao (đảm bảo mảng hoàn toàn mới, contiguous)
        image = np.copy(image)
        if image.ndim != 3 or image.shape[2] not in [1, 3, 4]:
            print(f"Ảnh của {student.get('name', 'Unknown')} có định dạng không hợp lệ: shape {image.shape}")
            continue

        # Nếu ảnh có kênh alpha (RGBA) thì chuyển về RGB
        if image.shape[2] == 4:
            image = image[:, :, :3]

        # Ép image về dạng 8-bit và C-contiguous
        image = np.require(image, np.uint8, 'C')
        print(f"[DEBUG] {student.get('name', 'Unknown')} - image shape: {image.shape}, dtype: {image.dtype}")

        # Debug: lưu ảnh ra file để kiểm tra xem ảnh có hợp lệ không
        cv2.imwrite(f"debug_{student.get('name', 'unknown')}.jpg", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        try:
            # Trích xuất đặc trưng khuôn mặt
            encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(encoding)
            known_face_info.append({
                'name': student.get('name', 'Unknown'),
                'student_id': student.get('student_id', 'Unknown'),
                'class': student.get('class', 'Unknown')
            })
        except IndexError:
            print(f"Không tìm thấy khuôn mặt trong ảnh của {student.get('name', 'Unknown')}")
        except Exception as e:
            print(f"Lỗi khi trích xuất đặc trưng của {student.get('name', 'Unknown')}: {e}")
    else:
        print(f"Sinh viên {student.get('name', 'Unknown')} không có ảnh")

print(f"Đã tải {len(known_face_encodings)} đặc trưng khuôn mặt.")

# Mở camera (webcam mặc định)
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    print("Không thể mở camera!")
    exit()
else:
    print("Camera đã được mở thành công!")

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("Không đọc được frame từ camera.")
        break

    # Chuyển frame từ BGR sang RGB và đảm bảo mảng liên tục
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb_frame = np.require(rgb_frame, np.uint8, 'C')

    try:
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    except Exception as e:
        print("Lỗi khi xử lý frame: ", e)
        continue

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances) if face_distances.size > 0 else None

        name = "Unknown"
        student_id = ""
        student_class = ""
        attendance_message = ""

        if best_match_index is not None and matches[best_match_index]:
            info = known_face_info[best_match_index]
            name = info['name']
            student_id = info['student_id']
            student_class = info['class']
            attendance_message = "Điểm danh thành công"

            attendance_record = {
                'student_id': student_id,
                'name': name,
                'class': student_class,
                'timestamp': datetime.utcnow(),
                'status': 'Present',
                'method': 'Face Recognition'
            }
            attendance_col.update_one(
                {'student_id': student_id},
                {'$set': attendance_record},
                upsert=True
            )
            print(f"Đã điểm danh: {name} - {student_id} - {student_class}")

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        label = f"{name} - {student_id} - {student_class}"
        cv2.rectangle(frame, (left, bottom - 20), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
        if attendance_message:
            cv2.putText(frame, attendance_message, (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 0), 2)

    cv2.imshow("Face Recognition Attendance", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
