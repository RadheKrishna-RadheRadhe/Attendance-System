import numpy as np
from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_cors import CORS
import os
import recognizer
import database
import logging
import uuid
import qrcode
from datetime import datetime
import socket
import pandas as pd

# -----------------------------------------
# Utilities
# -----------------------------------------
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

EXCEL_FILE = 'attendance_log.xlsx'

def log_attendance_to_excel(name, reg_number, timestamp):
    columns = ['Name', 'Registration Number', 'Timestamp']
    
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
    else:
        df = pd.DataFrame(columns=columns)
    
    new_row = {
        'Name': name,
        'Registration Number': reg_number,
        'Timestamp': timestamp
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)


# -----------------------------------------
# Flask setup
# -----------------------------------------
app = Flask(__name__, static_folder='static')
CORS(app)

attendance_qrs_folder = os.path.join(app.static_folder, 'qrs')
register_qrs_folder = os.path.join(app.static_folder, 'register_qrs')

os.makedirs(attendance_qrs_folder, exist_ok=True)
os.makedirs(register_qrs_folder, exist_ok=True)

# -----------------------------------------
# Logging
# -----------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Attendance QR folder: {attendance_qrs_folder}")
logger.info(f"Register QR folder: {register_qrs_folder}")

# -----------------------------------------
# Ensure dirs and DB
# -----------------------------------------
recognizer.ensure_dirs()
database.init_db()

# -----------------------------------------
# Default Register QR Generator
# -----------------------------------------
def generate_default_register_qr():
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    qr_filename = f"register_{now}_{uuid.uuid4()}_default.png"

    local_ip = get_local_ip()
    server_url = f"http://{local_ip}:5000"
    registration_code = str(uuid.uuid4())
    registration_link = f"{server_url}/register/{registration_code}"

    logger.info(f"Generating DEFAULT REGISTER QR for link: {registration_link}")

    img = qrcode.make(registration_link)
    qr_path = os.path.join(register_qrs_folder, qr_filename)
    img.save(qr_path)
    logger.info(f"Default REGISTER QR saved at {qr_path}")

# -----------------------------------------
# Routes
# -----------------------------------------
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

@app.route('/register/<code>')
def register_page(code):
    return send_from_directory(app.static_folder, 'register.html')

@app.route('/attendance/<code>')
def attendance_page(code):
    return send_from_directory(app.static_folder, 'attendance.html')

# -----------------------------------------
# Registration Upload (Mobile & PC)
# -----------------------------------------
@app.route('/api/register_upload', methods=['POST'])
@app.route('/api/register', methods=['POST'])
def register_upload():
    try:
        name = request.form.get('name', '').strip()
        reg_number = request.form.get('reg_number', '').strip()
        image = request.files.get('image')

        if not name or not reg_number or not image:
            return jsonify({'status': 'fail', 'message': 'Name, registration number, and 1 image are required.'}), 400

        # Store user image
        database.add_user(name, reg_number)
        user_folder = os.path.join('users', reg_number)
        os.makedirs(user_folder, exist_ok=True)
        image.save(os.path.join(user_folder, "1.jpg"))
        logger.info(f"Saved 1 image for {name} in {user_folder}")

        # Retrain model
        if not recognizer.train_model('users'):
            return jsonify({'status': 'fail', 'message': 'Failed to retrain model: no faces detected in images.'}), 400

        return jsonify({'status': 'success', 'message': f'User \"{name}\" registered and model retrained.'}), 201

    except Exception as e:
        logger.exception("[REGISTER_UPLOAD] Error processing request")
        return jsonify({'status': 'fail', 'message': str(e)}), 500

# -----------------------------------------
# Attendance Upload
# -----------------------------------------
@app.route('/api/attendance', methods=['POST'])
@app.route('/api/attendance_upload', methods=['POST'])
def attendance_upload():
    try:
        image = request.files.get('image')
        if not image:
            return jsonify({'status': 'fail', 'message': 'Please upload 1 image.'}), 400

        img_bytes = image.read()
        encoding = recognizer.extract_encoding_from_bytes(img_bytes)
        if encoding is None:
            return jsonify({'status': 'fail', 'message': 'No face detected.'}), 400

        label, distance = recognizer.predict_user_from_encoding(encoding, tolerance=0.5)
        if label is None:
            return jsonify({'status': 'fail', 'message': 'Face not recognized in DB.'}), 400

        try:
            user_id = database.get_user_id_by_reg_number(label)
        except ValueError as e:
            return jsonify({'status': 'fail', 'message': str(e)}), 400

        name = database.get_user_name(user_id)
        if not name:
            return jsonify({'status': 'fail', 'message': 'User not found in DB.'}), 400

        database.log_attendance(user_id)

        # NEW: Also log to Excel
        timestamp = datetime.now().isoformat()
        log_attendance_to_excel(name, label, timestamp)

        return jsonify({
            'status': 'success',
            'name': name,
            'reg_number': label,
            'timestamp': timestamp,
            'confidence': float(distance)
        })

    except Exception as e:
        logger.exception("Error in /api/attendance")
        return jsonify({'status': 'fail', 'message': str(e)}), 500

# -----------------------------------------
# QR Code Generation (Registration)
# -----------------------------------------
@app.route('/api/generate_register_qr')
def generate_register_qr():
    try:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        qr_filename = f"register_{now}_{uuid.uuid4()}.png"

        local_ip = get_local_ip()
        server_url = f"http://{local_ip}:5000"
        registration_code = str(uuid.uuid4())
        registration_link = f"{server_url}/register/{registration_code}"

        logger.info(f"Generating REGISTER QR for link: {registration_link}")

        img = qrcode.make(registration_link)
        qr_path = os.path.join(register_qrs_folder, qr_filename)
        img.save(qr_path)
        logger.info(f"REGISTER QR saved at {qr_path}")

        return jsonify({
            'status': 'success',
            'qr_image_url': url_for('static_files', path=f'register_qrs/{qr_filename}'),
            'link': registration_link
        })

    except Exception as e:
        logger.exception("Error in /api/generate_register_qr")
        return jsonify({'status': 'fail', 'message': str(e)}), 500

@app.route('/api/list_register_qrs')
def list_register_qrs_api():
    try:
        os.makedirs(register_qrs_folder, exist_ok=True)
        files = sorted([f for f in os.listdir(register_qrs_folder) if f.lower().endswith('.png')])

        if not files:
            logger.info("No register QRs found. Generating default one.")
            generate_default_register_qr()
            files = sorted([f for f in os.listdir(register_qrs_folder) if f.lower().endswith('.png')])

        files_info = []
        for f in files:
            parts = f.split('_')
            date_str = parts[0] if len(parts) > 1 else 'Unknown Date'
            files_info.append({
                'url': f"/static/register_qrs/{f}",
                'date': date_str
            })

        logger.info(f"Listing {len(files_info)} REGISTER QR codes")
        return jsonify({'status': 'success', 'files': files_info})

    except Exception as e:
        logger.exception("Error listing REGISTER QR codes")
        return jsonify({'status': 'fail', 'message': str(e)}), 500

# -----------------------------------------
# QR Code Generation (Attendance)
# -----------------------------------------
@app.route('/api/generate_qr')
def generate_qr():
    try:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        qr_filename = f"{now}_{uuid.uuid4()}.png"

        local_ip = get_local_ip()
        server_url = f"http://{local_ip}:5000"
        
        # Fixed attendance link
        attendance_link = f"{server_url}/static/attendance_form.html"

        logger.info(f"Generating Attendance QR for link: {attendance_link}")

        img = qrcode.make(attendance_link)
        qr_path = os.path.join(attendance_qrs_folder, qr_filename)
        img.save(qr_path)
        logger.info(f"Attendance QR saved at {qr_path}")

        return jsonify({
            'status': 'success',
            'qr_image_url': url_for('static_files', path=f'qrs/{qr_filename}'),
            'link': attendance_link
        })

    except Exception as e:
        logger.exception("Error in /api/generate_qr")
        return jsonify({'status': 'fail', 'message': str(e)}), 500

# -----------------------------------------
# QR Galleries
# -----------------------------------------
@app.route('/qrs')
def qrs_gallery_page():
    return send_from_directory(app.static_folder, 'qrs_gallery.html')

@app.route('/api/list_qrs')
def list_qrs_api():
    try:
        os.makedirs(attendance_qrs_folder, exist_ok=True)
        files = sorted([f for f in os.listdir(attendance_qrs_folder) if f.lower().endswith('.png')])

        files_info = []
        for f in files:
            parts = f.split('_')
            date_str = parts[0] if len(parts) > 1 else 'Unknown Date'
            files_info.append({
                'url': f"/static/qrs/{f}",
                'date': date_str
            })

        logger.info(f"Listing {len(files_info)} Attendance QR codes")
        return jsonify({'status': 'success', 'files': files_info})

    except Exception as e:
        logger.exception("Error listing QR codes")
        return jsonify({'status': 'fail', 'message': str(e)}), 500

@app.route('/api/delete_qr', methods=['POST'])
def delete_qr():
    try:
        data = request.get_json()
        filename = data.get('filename')
        if not filename:
            return jsonify({'status': 'fail', 'message': 'Filename is required'}), 400

        filename = os.path.basename(filename)
        file_path_attendance = os.path.join(attendance_qrs_folder, filename)
        file_path_register = os.path.join(register_qrs_folder, filename)

        if os.path.exists(file_path_attendance):
            os.remove(file_path_attendance)
            logger.info(f"Deleted Attendance QR: {file_path_attendance}")
            return jsonify({'status': 'success'})
        elif os.path.exists(file_path_register):
            os.remove(file_path_register)
            logger.info(f"Deleted Register QR: {file_path_register}")
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'fail', 'message': 'File not found'}), 404

    except Exception as e:
        logger.exception("Error in /api/delete_qr")
        return jsonify({'status': 'fail', 'message': str(e)}), 500

# -----------------------------------------
# Main
# -----------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
