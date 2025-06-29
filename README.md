# 📸 Face Attendance System (Flask-based)

This project is a **QR-enabled face recognition attendance system** with support for:

✅ User registration (photo + details)
✅ QR code generation for easy mobile/desktop attendance
✅ Face recognition model training with OpenCV + face_recognition
✅ Attendance logs in SQLite and Excel
✅ Web interface for registration and attendance (mobile/desktop camera support)

---

## 🚀 Features

- User Registration with photo upload
- Face encoding extraction and model training
- Attendance via QR code
- Mobile and desktop camera support
- Excel attendance logs with timestamps
- Simple admin gallery to manage QR codes
- Light/dark theme switch on web forms

---

## ⚙️ Tech Stack

- **Backend:** Python, Flask
- **Face Recognition:** face_recognition, OpenCV
- **Database:** SQLite (users and attendance)
- **Frontend:** HTML, CSS, JavaScript
- **QR Codes:** qrcode
- **Excel Logging:** pandas, openpyxl

---

## 🗂️ Project Structure

project/

│

├── server.py                # Flask app

├── recognizer.py            # Face encoding and prediction

├── database.py              # DB logic

├── attendance_log.xlsx      # (created automatically)

│

├── static/

│   ├── register.html

│   ├── attendance_form.html

│   ├── desktop_attendance.html

│   ├── qrs/

│   ├── register_qrs/

│   ├── css/

│   │   ├── register.css

│   │   └── attendance.css

│   └── js/

│       ├── register.js

│       └── attendance.js

│

└── users/                    # Saved user images

## 🧩 Setup Instructions

1️⃣ Clone the repo:

```bash
git clone https://github.com/RadheKrishna-RadheRadhe/Attendance-System.git
cd Attendance-System
```
