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

2️⃣ Install requirements:

Go to the requirements folder

Right Click and open Command Prompt in the given folder

```bash
pip install -r requirements.txt
```


3️⃣ Ensure folders exist:

* `users/`
* `model/`
* `static/qrs/`
* `static/register_qrs/`

They’ll usually be auto-created on first run.

▶️ Running the Server

```bash
python app.py
```

Now this will give the Local Server and Local IP Server which Works on your Phone too.

This will be showed in the Output in terminal.



## ⚡ How it works

### ✅ 1. User Registration

* Admin generates a QR code for  **registration page** .
* User scans QR and fills:
  * Name
  * Registration number
  * Uploads 1 face photo
* Server stores the image, updates the face-encoding model, and logs the user in the database.

---

### ✅ 2. Attendance Marking

* Admin generates a QR for  **attendance page** .
* User scans QR or uses desktop camera page:
  * Captures face photo
  * Uploads to server
* Server:
  * Detects face encoding
  * Matches against stored encodings
  * Logs attendance with timestamp in DB and Excel

---

### ✅ 3. QR Code Management

* Admin can list, view, and delete:
  * Registration QR codes
  * Attendance QR codes
* Links are dynamically generated with local IP.

---

### ✅ 4. Attendance Logs

* Each attendance entry is logged in:
  * `attendance.db` (SQLite)
  * `attendance_log.xlsx` (auto-generated Excel file)

Excel Columns:

| User Name | Registration Number | Timestamp            |
| --------- | ------------------- | -------------------- |
| RK        | 23MIA1139           | 2024-01-01T10:00:00Z |

---

## 💻 Requirements

* Python 3.8–3.12 recommended
* OS: Windows / Linux
* Camera (for capture)
* Mobile phone having a good Camera Quality

---

## ❤️ Credits

* [face_recognition](https://github.com/ageitgey/face_recognition)
* OpenCV
* Flask

---

## 📜 License

MIT License
