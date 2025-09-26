# Yardımcı fonksiyonlar burada
# utils.py

import cv2
import os
import uuid
from typing import Tuple
import numpy as np


# Her sınıf için renk ata
def get_color_for(label: str) -> Tuple[int, int, int]:
    np.random.seed(hash(label) % 2**32)
    return tuple(int(x) for x in np.random.randint(60, 255, size=3))

# Bounding box çiz
def draw_box(frame, box: Tuple[int, int, int, int], color, thickness=2):
    x1, y1, x2, y2 = box
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)


# Etiket yaz
def put_label(frame, text: str, box: Tuple[int, int, int, int], color):
    x1, y1, _, _ = box
    cv2.putText(frame, text, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, lineType=cv2.LINE_AA)


# Yüz görüntüsünü kırp ve kaydet
def save_violation_face(frame, face_box: Tuple[int, int, int, int], reason: str, face_id: int, output_dir="violations"):
    os.makedirs(output_dir, exist_ok=True)
    x1, y1, x2, y2 = face_box
    cropped = frame[y1:y2, x1:x2]
    
    filename = f"{face_id}_{uuid.uuid4().hex[:6]}.jpg"
    save_path = os.path.join(output_dir, filename)

    if cropped.size > 0:
        cv2.imwrite(save_path, cropped)

        # Açıklama altına yazı ekle
        cv2.putText(cropped, reason, (5, cropped.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, lineType=cv2.LINE_AA)
        cv2.imwrite(save_path, cropped)

    return save_path

