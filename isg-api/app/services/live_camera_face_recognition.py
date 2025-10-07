"""
Face Recognition Service for Live Camera
Integrates with existing face_recognizer from ppe_detection_system
"""

import logging
import sys
import os
from typing import Optional, Tuple, Dict, Any
import numpy as np
from sqlalchemy.orm import Session

# Add ppe_detection_system to path to import face_recognizer
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'ppe_detection_system'))

try:
    from face_recognizer import img_to_embedding_np, recognize_face as ppe_recognize_face
    FACE_RECOGNIZER_AVAILABLE = True
except Exception as e:
    FACE_RECOGNIZER_AVAILABLE = False
    logging.warning(f"PPE face_recognizer not available: {e}")

from app.models.employee import Employee

logger = logging.getLogger(__name__)

# Threshold for face matching (same as in ppe_detection_system)
FACE_MATCH_THRESHOLD = 0.7


def recognize_face_from_frame(face_crop_np: np.ndarray, db: Session) -> Tuple[Optional[str], Optional[str], Optional[float]]:
    """
    Recognize a face from a numpy image crop using the ppe_detection_system logic.
    
    Args:
        face_crop_np: Numpy array of the face crop (BGR format)
        db: Database session
        
    Returns:
        Tuple of (employee_name, employee_id, confidence_score)
        Returns (None, None, None) if no match found or if service unavailable
    """
    if not FACE_RECOGNIZER_AVAILABLE:
        return None, None, None
    
    try:
        # Generate embedding using the same function from ppe_detection_system
        embedding = img_to_embedding_np(face_crop_np)
        
        if embedding is None:
            return None, None, None
        
        # Get all employees with face embeddings from database
        employees = db.query(Employee).filter(
            Employee.is_active == True,
            Employee.face_embedding.isnot(None)
        ).all()
        
        if not employees:
            logger.debug("No employees with face embeddings found")
            return None, None, None
        
        # Find best match using the same logic as ppe_detection_system
        best_match_name = None
        best_match_id = None
        best_score = float("inf")
        
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
                
                if dist < best_score:
                    best_score = dist
                    best_match_name = f"{emp.first_name} {emp.last_name}"
                    best_match_id = emp.employee_id
                    
            except Exception as e:
                logger.warning(f"Error comparing with employee {emp.employee_id}: {e}")
                continue
        
        # Apply threshold (same as in ppe_detection_system)
        if best_score < FACE_MATCH_THRESHOLD:
            logger.info(f"Face recognized: {best_match_name} (score: {best_score:.3f})")
            return best_match_name, best_match_id, best_score
        else:
            logger.debug(f"No match found (best score: {best_score:.3f}, threshold: {FACE_MATCH_THRESHOLD})")
            return None, None, best_score
            
    except Exception as e:
        logger.error(f"Error in face recognition: {e}")
        return None, None, None


def is_face_recognition_available() -> bool:
    """Check if face recognition service is available"""
    return FACE_RECOGNIZER_AVAILABLE
