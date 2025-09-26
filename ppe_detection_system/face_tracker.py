# Yüz takibi ve ID ataması yapılır

# face_tracker.py

import cv2
import numpy as np
from collections import defaultdict

class FaceTracker:
    def __init__(self, max_distance=50):
        self.next_id = 0
        self.tracked_faces = {}  # face_id -> bbox
        self.max_distance = max_distance

    def update(self, faces):
        """
        Yüzleri güncelle ve her biri için ID ata.

        Args:
            faces: List of face bounding boxes [(x1, y1, x2, y2), ...]

        Returns:
            List of dicts: [{'id': int, 'box': (x1, y1, x2, y2)}]
        """
        updated_faces = []
        assigned_ids = set()

        for box in faces:
            x1, y1, x2, y2 = box
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            matched_id = None
            for face_id, old_box in self.tracked_faces.items():
                ox1, oy1, ox2, oy2 = old_box
                ocx, ocy = (ox1 + ox2) // 2, (oy1 + oy2) // 2
                dist = np.hypot(cx - ocx, cy - ocy)
                if dist < self.max_distance and face_id not in assigned_ids:
                    matched_id = face_id
                    break

            if matched_id is None:
                matched_id = self.next_id
                self.next_id += 1

            self.tracked_faces[matched_id] = box
            assigned_ids.add(matched_id)
            updated_faces.append({'id': matched_id, 'box': box})

        # Opsiyonel: unutulan yüzleri temizle (çok gerekmez)
        # self._cleanup()

        return updated_faces
