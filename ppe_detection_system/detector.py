# YOLO ile nesne tespiti yapılır
# detector.py

import cv2
import torch
from ultralytics import YOLO
from typing import List, Dict, Any


class YoloDetector:
    def __init__(self, model_path: str, conf_threshold: float = 0.6):
        self.model = YOLO(model_path)
        self.model.fuse()
        self.conf_threshold = conf_threshold
        self.class_names = self.model.names  # Sınıf ID -> İsim

    def infer(self, frame) -> List[Dict[str, Any]]:
        """
        Her bir tespit için:
        {
            'cls_name': sinif ismi,
            'conf': 0.87 gibi güven skoru,
            'box': (x1, y1, x2, y2)
        }
        """
        detections = []
        try:
            results = self.model.predict(frame, conf=self.conf_threshold, verbose=False)

            if not results or len(results) == 0 or results[0] is None:
                return detections

            r = results[0]
            boxes = getattr(r, 'boxes', None)
            if boxes is None:
                return detections

            for b in boxes:
                conf = float(b.conf)
                if conf < self.conf_threshold:
                    continue
                cls_id = int(b.cls)
                x1, y1, x2, y2 = map(int, b.xyxy[0].tolist())
                cls_name = self.class_names.get(cls_id, str(cls_id))

                detections.append({
                    'cls_name': cls_name,
                    'conf': conf,
                    'box': (x1, y1, x2, y2)
                })
        except Exception as e:
            print(f"[YOLO Hata] {e}")

        return detections
