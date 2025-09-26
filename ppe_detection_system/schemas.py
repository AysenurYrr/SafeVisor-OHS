# Veritabanı ve API şemaları
# schemas.py

from typing import List, Tuple
from pydantic import BaseModel


class Detection(BaseModel):
    label: str                 # Örn: "Helmet", "Gloves"
    conf: float                # Güven skoru
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)


class FaceBox(BaseModel):
    head: Tuple[int, int, int, int]
    face: Tuple[int, int, int, int]
    hands: Tuple[int, int, int, int]
    body: Tuple[int, int, int, int]
    feet: Tuple[int, int, int, int]


class EvaluationResult(BaseModel):
    face_id: int
    is_compliant: bool
    missing_items: List[str]  # Eksik malzemeler listesi


class ConfigData(BaseModel):
    required_items: List[str]
    environment: str

