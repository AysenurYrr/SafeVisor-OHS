import logging
import os
from typing import List, Optional

from PIL import Image
import numpy as np

LOGGER = logging.getLogger("app.face_embedding")

try:
    import face_recognition  # type: ignore
    _FACE_LIB_AVAILABLE = True
except Exception:  # pragma: no cover
    _FACE_LIB_AVAILABLE = False
    LOGGER.warning("face_recognition library not available; embeddings will be skipped.")


def _load_image(path: str) -> Optional[np.ndarray]:
    try:
        if not os.path.exists(path):
            LOGGER.warning("Image path does not exist: %s", path)
            return None
        # face_recognition loads via PIL internally, but we'll convert explicitly
        img = face_recognition.load_image_file(path) if _FACE_LIB_AVAILABLE else np.array(Image.open(path))
        return img
    except Exception as e:  # pragma: no cover
        LOGGER.warning("Failed loading image %s: %s", path, e)
        return None


def _encode_face(img: np.ndarray) -> Optional[np.ndarray]:
    if not _FACE_LIB_AVAILABLE:
        return None
    try:
        encodings = face_recognition.face_encodings(img)
        if not encodings:
            return None
        return np.array(encodings[0])
    except Exception as e:  # pragma: no cover
        LOGGER.warning("Face encoding failed: %s", e)
        return None


def generate_employee_embedding(employee_id: int, photo_paths: List[str]) -> Optional[List[float]]:
    """Generate a single averaged face embedding from provided photo paths.

    - Attempts to extract one face per image
    - Ignores images with no detectable face
    - Returns None if no faces encoded
    """
    valid_vectors = []
    for p in photo_paths:
        if not p:
            continue
        img = _load_image(p)
        if img is None:
            continue
        vec = _encode_face(img)
        if vec is not None:
            valid_vectors.append(vec)
    if not valid_vectors:
        LOGGER.warning("No face encodings generated for employee_id=%s", employee_id)
        return None
    mean_vec = np.mean(valid_vectors, axis=0)
    return mean_vec.astype(float).tolist()
