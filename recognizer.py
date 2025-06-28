import cv2
import os
import numpy as np

# Paths
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
MODEL_PATH = "model/lbph_model.xml"

def ensure_dirs():
    os.makedirs('users', exist_ok=True)
    os.makedirs('model', exist_ok=True)

def detect_face(gray_img):
    faces = FACE_CASCADE.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return None
    (x, y, w, h) = faces[0]
    return gray_img[y:y+h, x:x+w]

def prepare_training_data(data_folder):
    faces = []
    labels = []

    for label in os.listdir(data_folder):
        label_id = int(label)
        user_folder = os.path.join(data_folder, label)

        for img_name in os.listdir(user_folder):
            img_path = os.path.join(user_folder, img_name)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue

            face = detect_face(img)
            if face is not None:
                faces.append(face)
                labels.append(label_id)

    return faces, labels

def train_model(data_folder, model_save_path):
    faces, labels = prepare_training_data(data_folder)
    if not faces:
        return False

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))
    recognizer.save(model_save_path)
    return True

def predict_user(img_bytes):
    if not os.path.exists(MODEL_PATH):
        return None, 999

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_PATH)

    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None, 999

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face = detect_face(gray)
    if face is None:
        return None, 999

    label, confidence = recognizer.predict(face)
    return label, confidence
