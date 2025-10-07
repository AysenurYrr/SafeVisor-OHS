"""Facenet-based face embedding utilities.

Lazy-loads MTCNN + InceptionResnetV1.
Exports:
  facenet_available() -> bool
  img_to_embedding_pil(pil_img) -> np.ndarray | None
  img_to_embedding_np(np_img) -> np.ndarray | None  (expects BGR frame crop)
"""
from __future__ import annotations
import logging
from functools import lru_cache
from typing import Optional
import numpy as np

try:
    import torch  # type: ignore
    from PIL import Image  # type: ignore
    from facenet_pytorch import MTCNN, InceptionResnetV1  # type: ignore
    from torchvision import transforms  # type: ignore
    _FACENET_OK = True
except Exception as e:  # pragma: no cover
    logging.warning(f"[Embedding] facenet stack unavailable: {e}")
    _FACENET_OK = False

LOGGER = logging.getLogger("app.ppe.embedding")

def facenet_available() -> bool:
    return _FACENET_OK

def _normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    if n == 0:
        return v
    return v / n

@lru_cache(maxsize=1)
def _models():
    if not _FACENET_OK:
        return None, None, 'cpu'
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    mtcnn = MTCNN(image_size=160, margin=10, device=device)
    model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
    LOGGER.info(f"[Embedding] Facenet models initialized on {device}")
    return mtcnn, model, device

def img_to_embedding_pil(pil_img: 'Image.Image') -> Optional[np.ndarray]:
    if not _FACENET_OK:
        return None
    mtcnn, model, device = _models()
    if mtcnn is None:
        return None
    face = mtcnn(pil_img)
    if face is None:
        return None
    with torch.no_grad():
        emb = model(face.unsqueeze(0).to(device)).cpu().numpy()[0]
    return _normalize(emb)

def img_to_embedding_np(np_img) -> Optional[np.ndarray]:
    if not _FACENET_OK:
        return None
    try:
        import cv2  # type: ignore
        resized = cv2.resize(np_img, (160, 160))
        pil_img = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
    except Exception:
        return None
    return img_to_embedding_pil(pil_img)
