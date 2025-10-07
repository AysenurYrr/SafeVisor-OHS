import logging
import os
from typing import List, Optional

import numpy as np
from PIL import Image

LOGGER = logging.getLogger("app.face_embedding")

try:  # Attempt internal ppe module (expected path)
    from app.ppe.embedding import img_to_embedding_pil, facenet_available  # type: ignore
except Exception as e:  # pragma: no cover
    LOGGER.warning(f"[FaceEmbedding] Primary embedding module unavailable: {e}")
    # Final fallback: define inert stubs
    def facenet_available():  # type: ignore
        return False
    def img_to_embedding_pil(_img):  # type: ignore
        return None

def _load_image_pil(path: str) -> Optional[Image.Image]:
    try:
        if not os.path.exists(path):
            LOGGER.warning("Image path does not exist: %s", path)
            return None
        return Image.open(path).convert("RGB")
    except Exception as e:  # pragma: no cover
        LOGGER.warning("Failed loading image %s: %s", path, e)
        return None


def _encode_face_pil(pil_img: Image.Image) -> Optional[np.ndarray]:
    if not facenet_available():
        return None
    try:
        emb = img_to_embedding_pil(pil_img)
        return emb
    except Exception as e:  # pragma: no cover
        LOGGER.warning("Face embedding failed: %s", e)
        return None


def generate_employee_embedding(employee_id: int, photo_paths: List[str]) -> Optional[List[float]]:
    """Generate averaged embedding from multiple photos using internal facenet pipeline.

    - Skips missing/unusable photos
    - Returns None if no embeddings produced
    """
    if not facenet_available():
        LOGGER.warning("Facenet stack unavailable; cannot generate embedding for employee_id=%s", employee_id)
        return None
    vectors = []
    for p in photo_paths:
        if not p:
            continue
        pil_img = _load_image_pil(p)
        if pil_img is None:
            continue
        vec = _encode_face_pil(pil_img)
        if vec is not None:
            vectors.append(vec)
    if not vectors:
        LOGGER.warning("No face embeddings generated for employee_id=%s", employee_id)
        return None
    mean_vec = np.mean(vectors, axis=0)
    return mean_vec.astype(float).tolist()
