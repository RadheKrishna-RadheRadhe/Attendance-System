import os
import cv2
import numpy as np
import face_recognition
import pickle
import logging

logger = logging.getLogger(__name__)

# Load OpenCV's Haar cascade
cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)

def ensure_dirs():
    os.makedirs('users', exist_ok=True)
    os.makedirs('model', exist_ok=True)

def extract_encoding_from_bytes(img_bytes):
    """
    Accepts image bytes, returns 128D face encoding or None.
    """
    try:
        nparr = np.frombuffer(img_bytes, np.uint8)
        img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img_cv is None:
            logger.warning("[DECODING ERROR] Could not decode image bytes.")
            return None

        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

        if len(faces) == 0:
            logger.warning("[DETECTION] No face detected.")
            return None

        x, y, w, h = max(faces, key=lambda rect: rect[2]*rect[3])
        face_img = img_cv[y:y+h, x:x+w]
        face_img_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)

        encodings = face_recognition.face_encodings(face_img_rgb)
        if len(encodings) == 0:
            logger.warning("[ENCODING] No face encodings found.")
            return None

        return encodings[0]

    except Exception as e:
        logger.exception(f"[EXTRACT ERROR] {e}")
        return None

def prepare_training_data(data_folder):
    all_encodings = []
    all_labels = []

    for reg_number in os.listdir(data_folder):
        user_folder = os.path.join(data_folder, reg_number)
        if not os.path.isdir(user_folder):
            continue

        label_id = reg_number
        for img_name in os.listdir(user_folder):
            img_path = os.path.join(user_folder, img_name)
            with open(img_path, 'rb') as f:
                encoding = extract_encoding_from_bytes(f.read())
                if encoding is not None:
                    all_encodings.append(encoding)
                    all_labels.append(label_id)
                else:
                    logger.warning(f"[SKIP] No face in: {img_path}")

    logger.info(f"[TRAINING] Collected {len(all_encodings)} encodings from {len(set(all_labels))} users.")
    return all_encodings, all_labels

def train_model(data_folder, model_save_path=None):
    encodings, labels = prepare_training_data(data_folder)
    if not encodings:
        logger.error("[TRAINING FAILED] No faces found.")
        return False

    os.makedirs('model', exist_ok=True)
    with open('model/encodings_db.pkl', 'wb') as f:
        pickle.dump((encodings, labels), f)
    logger.info(f"[TRAINING SUCCESS] Saved encodings to model/encodings_db.pkl")
    return True

def load_known_encodings():
    path = 'model/encodings_db.pkl'
    if not os.path.exists(path):
        logger.warning("[LOAD] No model found. Returning empty DB.")
        return [], []

    with open(path, 'rb') as f:
        encodings, labels = pickle.load(f)
    return encodings, labels

def predict_user_from_encoding(query_encoding, tolerance=0.5):
    known_encodings, known_labels = load_known_encodings()
    if not known_encodings:
        logger.error("[PREDICT] No known encodings in DB!")
        return None, 999

    distances = face_recognition.face_distance(known_encodings, query_encoding)
    if not len(distances):
        return None, 999

    best_idx = np.argmin(distances)
    best_distance = distances[best_idx]
    logger.info(f"[PREDICT] Best distance: {best_distance:.3f}")

    if best_distance > tolerance:
        return None, best_distance

    return known_labels[best_idx], best_distance
