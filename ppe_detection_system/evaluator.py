# Kurallara uyulup uyulmadığı burada değerlendirilir
# evaluator.py

from typing import List, Dict
from schemas import Detection, EvaluationResult

# Her nesne hangi bölgeyle eşleştirilmeli
REGION_RULES = {
    "Helmet": "head",
    "Glasses": "face",
    "Face-mask-medical": "face",
    "Face-guard": "face",
    "Earmuffs": "head",
    "Gloves": "hands",
    "Safety-vest": "person",
    "Medical-suit": "person",
    "Safety-suit": "person",
    "Shoes": "feet",
    "Tools": "hands"
}


def evaluate_person(face_id: int, person_box: Dict, detections: List[Detection], required_items: List[str]) -> EvaluationResult:
    """
    Belirli bir kişiye (face_id) ait tespit sonuçlarını kurallara göre değerlendir.
    """
    missing = []

    # Hangi bölgelerde hangi nesneler var
    region_items = {
        "head": [],
        "face": [],
        "hands": [],
        "person": [],
        "feet": []
    }

    # İlgili kutuların içinde olanları sınıflandır
    for det in detections:
        for region, box in person_box.items():
            if region in region_items and iou(det.bbox, box) > 0.3:
                region_items[region].append(det.label)

    # Kurala göre eksikleri kontrol et
    for item in required_items:
        region = REGION_RULES.get(item)
        if region and item not in region_items[region]:
            missing.append(item)

    return EvaluationResult(
        face_id=face_id,
        is_compliant=len(missing) == 0,
        missing_items=missing
    )


def iou(boxA, boxB) -> float:
    """
    Intersection over Union hesaplama
    """
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    if interArea == 0:
        return 0.0

    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    return interArea / float(boxAArea + boxBArea - interArea)
