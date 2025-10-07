"""
Face Recognition Service for Live Camera
Internal implementation - no external dependencies
"""

import logging
import numpy as np
from sqlalchemy.orm import Session
from typing import Optional, Tuple
import cv2
from PIL import Image

try:
    import torch
    from torchvision import transforms
    from facenet_pytorch import MTCNN, InceptionResnetV1
    FACE_RECOGNIZER_AVAILABLE = True
    
    # Initialize models
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    mtcnn = MTCNN(image_size=160, margin=10, device=device)
    model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
except Exception as e:
    FACE_RECOGNIZER_AVAILABLE = False
    logging.warning(f"Face recognition dependencies not available: {e}")

from app.models.employee import Employee

logger = logging.getLogger(__name__)

# Threshold for face matching (same as ppe_detection_system)
FACE_MATCH_THRESHOLD = 0.7


def _normalize(v):
    """Normalize vector"""
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def img_to_embedding_np(np_img: np.ndarray) -> Optional[np.ndarray]:
    """
    Generate face embedding from numpy image (ported from ppe_detection_system).
    
    Args:
        np_img: Numpy array image (BGR format from OpenCV)
        
    Returns:
        Normalized embedding vector or None if no face detected
    """
    if not FACE_RECOGNIZER_AVAILABLE:
        return None
        
    try:
        # Resize and convert to RGB
        img = cv2.resize(np_img, (160, 160))
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        # Transform to tensor
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5])
        ])
        tensor = transform(img).unsqueeze(0).to(device)
        
        # Generate embedding
        with torch.no_grad():
            emb = model(tensor).cpu().numpy()[0]
        
        return _normalize(emb)
    except Exception as e:
        logger.error(f"[FaceRec] Error generating embedding: {e}")
        return None


def recognize_face_from_frame(face_crop_np: np.ndarray, db: Session) -> Tuple[Optional[str], Optional[str], Optional[float], Optional[float]]:
    """
    Recognize a face from a numpy image crop.
    
    Args:
        face_crop_np: Numpy array of the face crop (BGR format)
        db: Database session
        
    Returns:
        Tuple of (employee_name, employee_id, recognition_distance, recognition_confidence)
        Returns (None, None, None, None) if no match found or if service unavailable
    """
    if not FACE_RECOGNIZER_AVAILABLE:
        logger.warning("[FaceRec] Face recognition service not available")
        return None, None, None, None
    
    try:
        # Generate embedding
        embedding = img_to_embedding_np(face_crop_np)
        
        if embedding is None:
            logger.warning("[FaceRec] Failed to generate embedding from face crop")
            return None, None, None, None
        
        # Get all employees with face embeddings from database
        employees = db.query(Employee).filter(
            Employee.is_active == True,
            Employee.face_embedding.isnot(None)
        ).all()
        
        if not employees:
            logger.warning("[FaceRec] No employees with face embeddings found in database")
            return None, None, None, None
        
        logger.debug(f"[FaceRec] Comparing against {len(employees)} employee embeddings")
        
        # Find best match using the same logic as ppe_detection_system
        best_match_name = None
        best_match_id = None
        best_distance = float("inf")
        
        for emp in employees:
            try:
                # Handle different embedding formats
                if isinstance(emp.face_embedding, list):
                    emp_embedding = np.array(emp.face_embedding)
                elif isinstance(emp.face_embedding, str):
                    import json
                    emp_embedding = np.array(json.loads(emp.face_embedding))
                else:
                    emp_embedding = np.array(emp.face_embedding)
                
                # Calculate distance (same as in ppe_detection_system/face_recognizer.py)
                dist = np.linalg.norm(embedding - emp_embedding)
                
                if dist < best_distance:
                    best_distance = dist
                    best_match_name = f"{emp.first_name} {emp.last_name}"
                    best_match_id = emp.employee_id
                    
            except Exception as e:
                logger.warning(f"[FaceRec] Error comparing with employee {emp.employee_id}: {e}")
                continue
        
        # Apply threshold (same as in ppe_detection_system)
        if best_distance < FACE_MATCH_THRESHOLD:
            # Calculate confidence (inverse of distance, normalized)
            confidence = max(0.0, 1.0 - best_distance)
            logger.info(f"[FaceRec] Face detected, distance={best_distance:.2f} → Match: {best_match_name} (confidence {confidence:.2f})")
            return best_match_name, best_match_id, best_distance, confidence
        else:
            logger.info(f"[FaceRec] Unknown face detected, distance={best_distance:.2f} (threshold={FACE_MATCH_THRESHOLD})")
            return None, None, best_distance, 0.0
            
    except Exception as e:
        logger.error(f"[FaceRec] Error in face recognition: {e}")
        return None, None, None, None


def is_face_recognition_available() -> bool:
    """Check if face recognition service is available"""
    return FACE_RECOGNIZER_AVAILABLE
