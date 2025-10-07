"""Internal facenet embedding implementation (fallback).
Used if app.ppe.embedding is not importable inside the container.
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
    _AVAILABLE = True
except Exception as e:  # pragma: no cover
    logging.warning(f"[EmbeddingFallback] facenet stack unavailable: {e}")
    _AVAILABLE = False

def facenet_available() -> bool:
    return _AVAILABLE

def _normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    if n == 0:
        return v
    return v / n

@lru_cache(maxsize=1)
def _models():
    if not _AVAILABLE:
        return None, None, 'cpu'
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    mtcnn = MTCNN(image_size=160, margin=10, device=device)
    model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
    logging.info(f"[EmbeddingFallback] Models initialized on {device}")
    return mtcnn, model, device

def img_to_embedding_pil(pil_img):  # type: ignore
    if not _AVAILABLE:
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
