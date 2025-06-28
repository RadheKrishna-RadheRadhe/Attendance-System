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

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Trick: connect to external IP (no data sent) to discover local IP
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


# -----------------------------------------
# Flask setup
# -----------------------------------------
app = Flask(__name__, static_folder='static')
CORS(app)

# -----------------------------------------
# Logging setup
# -----------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------
# Ensure folders exist
# -----------------------------------------
recognizer.ensure_dirs()
database.init_db()
qrs_folder = os.path.join(app.static_folder, 'qrs')
os.makedirs(qrs_folder, exist_ok=True)

# -----------------------------------------
# Home page
# -----------------------------------------
@app.route('/')
def home():
    logger.info("Serving home page")
    return send_from_directory(app.static_folder, 'index.html')

# -----------------------------------------
# Static file serving
# -----------------------------------------
@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

# -----------------------------------------
# User Registration
# -----------------------------------------
@app.route('/api/register', methods=['POST'])
def register():
    try:
        name = request.form.get('name')
        image = request.files.get('image')

        if not name or not image:
            return jsonify({'status': 'fail', 'message': 'Name and image are required'}), 400

        user_id = database.add_user(name)
        user_folder = os.path.join('users', str(user_id))
        os.makedirs(user_folder, exist_ok=True)

        img_count = len(os.listdir(user_folder)) + 1
        img_path = os.path.join(user_folder, f"{img_count}.jpg")
        with open(img_path, 'wb') as f:
            f.write(image.read())

        if not recognizer.train_model('users', 'model/lbph_model.xml'):
            logger.warning(f"Registration failed: no faces found for {name}")
            return jsonify({'status': 'fail', 'message': 'Failed to retrain model - no faces found'}), 400

        logger.info(f"User registered: {name} (ID {user_id})")
        return jsonify({'status': 'success', 'message': f'User \"{name}\" registered and model retrained'})

    except Exception as e:
        logger.exception("Error in /api/register")
        return jsonify({'status': 'fail', 'message': str(e)}), 500

# -----------------------------------------
# Webcam Attendance
# -----------------------------------------
@app.route('/attendance/camera')
def attendance_camera_page():
    logger.info("Serving camera attendance page")
    return send_from_directory(app.static_folder, 'attendance_camera.html')


# -----------------------------------------
# Direct Attendance Upload
# -----------------------------------------
@app.route('/api/attendance', methods=['POST'])
def attendance():
    try:
        image = request.files.get('image')
        if not image:
            return jsonify({'status': 'fail', 'message': 'Image is required'}), 400

        label, confidence = recognizer.predict_user(image.read())
        if label is None or confidence > 80:
            logger.info("Unrecognized face attempt")
            return jsonify({'status': 'fail', 'message': 'Face not recognized. Please try again.'}), 400

        name = database.get_user_name(label)
        if not name:
            logger.warning(f"DB lookup failed for label {label}")
            return jsonify({'status': 'fail', 'message': 'User not found in DB'}), 400

        database.log_attendance(label)
        logger.info(f"Attendance marked for {name} (Confidence: {confidence:.2f})")
        return jsonify({'status': 'success', 'name': name, 'confidence': confidence})

    except Exception as e:
        logger.exception("Error in /api/attendance")
        return jsonify({'status': 'fail', 'message': str(e)}), 500

# -----------------------------------------
# QR Code Generation
# -----------------------------------------
@app.route('/api/generate_qr')
def generate_qr():
    try:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        unique_code = str(uuid.uuid4())
        qr_filename = f"{now}_{unique_code}.png"

        # Use local Wi-Fi IP address instead of localhost
        local_ip = get_local_ip()
        server_port = 5000  # Change if you run Flask on another port
        server_url = f"http://{local_ip}:{server_port}"

        attendance_link = f"{server_url}/attendance/{unique_code}"
        logger.info(f"Generating QR for link: {attendance_link}")

        # Create and save QR image
        img = qrcode.make(attendance_link)
        qr_path = os.path.join(qrs_folder, qr_filename)
        img.save(qr_path)

        logger.info(f"QR saved at {qr_path}")

        return jsonify({
            'status': 'success',
            'qr_image_url': url_for('static_files', path=f'qrs/{qr_filename}'),
            'link': attendance_link
        })

    except Exception as e:
        logger.exception("Error in /api/generate_qr")
        return jsonify({'status': 'fail', 'message': str(e)}), 500

# -----------------------------------------
# Attendance Capture Page (Mobile)
# -----------------------------------------
@app.route('/attendance/<code>')
def attendance_page(code):
    try:
        logger.info(f"Serving attendance page for code: {code}")
        return send_from_directory(app.static_folder, 'attendance_form.html')
    except Exception as e:
        logger.exception("Error serving attendance page")
        return "Error serving page", 500

# -----------------------------------------
# Attendance Upload (from Mobile)
# -----------------------------------------
@app.route('/api/attendance_upload', methods=['POST'])
def attendance_upload():
    try:
        image = request.files.get('image')
        if not image:
            return jsonify({'status': 'fail', 'message': 'Image is required'}), 400

        label, confidence = recognizer.predict_user(image.read())
        if label is None or confidence > 80:
            logger.info("Unrecognized face upload attempt")
            return jsonify({'status': 'fail', 'message': 'Face not recognized. Please try again.'}), 400

        name = database.get_user_name(label)
        if not name:
            logger.warning(f"DB lookup failed for label {label}")
            return jsonify({'status': 'fail', 'message': 'User not found in DB'}), 400

        database.log_attendance(label)
        logger.info(f"Attendance uploaded for {name} (Confidence: {confidence:.2f})")
        return jsonify({'status': 'success', 'message': f'Welcome {name}! (Confidence: {confidence:.2f})'})

    except Exception as e:
        logger.exception("Error in /api/attendance_upload")
        return jsonify({'status': 'fail', 'message': str(e)}), 500

# -----------------------------------------
# QR Code Gallery Page
# -----------------------------------------
@app.route('/qrs')
def qrs_gallery_page():
    logger.info("Serving QR gallery page")
    return send_from_directory(app.static_folder, 'qrs_gallery.html')

# -----------------------------------------
# QR Code List API
# -----------------------------------------
@app.route('/api/list_qrs')
def list_qrs_api():
    try:
        files_info = []
        for f in sorted(os.listdir(qrs_folder)):
            if f.lower().endswith('.png'):
                # Parse date from filename
                parts = f.split('_')
                if len(parts) > 1:
                    date_str = parts[0]
                else:
                    date_str = 'Unknown Date'
                files_info.append({
                    'url': f"/static/qrs/{f}",
                    'date': date_str
                })

        logger.info(f"Listing {len(files_info)} QR codes")
        return jsonify({'status': 'success', 'files': files_info})

    except Exception as e:
        logger.exception("Error listing QR codes")
        return jsonify({'status': 'fail', 'message': str(e)}), 500
    
# -----------------------------------------
# Delete QR Code API
# -----------------------------------------
@app.route('/api/delete_qr', methods=['POST'])
def delete_qr():
    try:
        data = request.get_json()
        filename = data.get('filename')
        if not filename:
            return jsonify({'status': 'fail', 'message': 'Filename is required'}), 400

        # Extract basename to prevent path traversal
        filename = os.path.basename(filename)
        file_path = os.path.join(qrs_folder, filename)

        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted QR: {file_path}")
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

