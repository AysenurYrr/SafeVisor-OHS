"""
Live Camera API endpoints for real-time PPE detection from webcam.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging
import base64
import json
import cv2
import numpy as np

from app.api import deps
from app.models.user import User
from app.services.detector_service import detector_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Available PPE detection classes
AVAILABLE_RULES = [
    "glasses",
    "face-mask", 
    "ear-muffs",
    "hands",
    "gloves",
    "safety-vest",
    "tools",
    "helmet",
    "medical-suit",
    "safety-suit"
]


@router.get("/rules")
def get_available_rules(
    current_user: User = Depends(deps.get_current_active_user),
) -> Dict[str, Any]:
    """
    Get list of available PPE detection rules.
    """
    return {
        "available_rules": AVAILABLE_RULES,
        "description": "Select which safety equipment to detect in the live camera feed"
    }


@router.post("/detect")
async def detect_frame(
    request: Dict[str, Any],
    current_user: User = Depends(deps.get_current_active_user),
) -> Dict[str, Any]:
    """
    Detect PPE in a single frame from the webcam.
    
    Request body:
    {
        "frame": "base64-encoded image data",
        "selected_rules": ["helmet", "safety-vest", ...]
    }
    
    Returns detection results with bounding boxes.
    """
    try:
        # Extract frame and selected rules from request
        frame_data = request.get("frame", "")
        selected_rules = request.get("selected_rules", [])
        
        if not frame_data:
            raise HTTPException(status_code=400, detail="No frame data provided")
        
        # Decode base64 image
        if "," in frame_data:
            # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
            frame_data = frame_data.split(",")[1]
        
        img_bytes = base64.b64decode(frame_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Check if detector service is available
        if not detector_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="PPE detection service is not available. Please check if the AI model is loaded."
            )
        
        # Perform detection
        all_detections = detector_service.detect_ppe(frame)
        
        # Filter detections based on selected rules
        filtered_detections = []
        if selected_rules:
            # Convert selected rules to lowercase for case-insensitive matching
            selected_rules_lower = [rule.lower().replace("-", "").replace("_", "") for rule in selected_rules]
            
            for det in all_detections:
                cls_name = det.get("cls_name", "").lower().replace("-", "").replace("_", "")
                # Check if detection class matches any selected rule
                for rule in selected_rules_lower:
                    if rule in cls_name or cls_name in rule:
                        filtered_detections.append(det)
                        break
        else:
            # If no rules selected, return all detections
            filtered_detections = all_detections
        
        # Format detections for frontend
        results = []
        for det in filtered_detections:
            x1, y1, x2, y2 = det["box"]
            results.append({
                "class_name": det["cls_name"],
                "confidence": float(det["conf"]),
                "box": {
                    "x1": int(x1),
                    "y1": int(y1),
                    "x2": int(x2),
                    "y2": int(y2)
                }
            })
        
        return {
            "success": True,
            "detections": results,
            "total_detections": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing frame: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing frame: {str(e)}")


@router.websocket("/ws")
async def websocket_detection(
    websocket: WebSocket,
    token: Optional[str] = None,
):
    """
    WebSocket endpoint for continuous live camera detection.
    Client sends frames, server responds with detection results.
    """
    await websocket.accept()
    
    try:
        # Authenticate via token (if needed in future)
        # For now, we'll accept connections without auth for simplicity
        
        while True:
            # Receive data from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            command = message.get("command")
            
            if command == "detect":
                # Process frame
                frame_data = message.get("frame", "")
                selected_rules = message.get("selected_rules", [])
                
                if not frame_data:
                    await websocket.send_json({
                        "success": False,
                        "error": "No frame data provided"
                    })
                    continue
                
                try:
                    # Decode base64 image
                    if "," in frame_data:
                        frame_data = frame_data.split(",")[1]
                    
                    img_bytes = base64.b64decode(frame_data)
                    nparr = np.frombuffer(img_bytes, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if frame is None:
                        await websocket.send_json({
                            "success": False,
                            "error": "Invalid image data"
                        })
                        continue
                    
                    # Check if detector service is available
                    if not detector_service.is_available():
                        await websocket.send_json({
                            "success": False,
                            "error": "Detection service not available"
                        })
                        continue
                    
                    # Perform detection
                    all_detections = detector_service.detect_ppe(frame)
                    
                    # Filter detections based on selected rules
                    filtered_detections = []
                    if selected_rules:
                        selected_rules_lower = [rule.lower().replace("-", "").replace("_", "") for rule in selected_rules]
                        
                        for det in all_detections:
                            cls_name = det.get("cls_name", "").lower().replace("-", "").replace("_", "")
                            for rule in selected_rules_lower:
                                if rule in cls_name or cls_name in rule:
                                    filtered_detections.append(det)
                                    break
                    else:
                        filtered_detections = all_detections
                    
                    # Format detections for frontend
                    results = []
                    for det in filtered_detections:
                        x1, y1, x2, y2 = det["box"]
                        results.append({
                            "class_name": det["cls_name"],
                            "confidence": float(det["conf"]),
                            "box": {
                                "x1": int(x1),
                                "y1": int(y1),
                                "x2": int(x2),
                                "y2": int(y2)
                            }
                        })
                    
                    # Send results back to client
                    await websocket.send_json({
                        "success": True,
                        "detections": results,
                        "total_detections": len(results)
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing frame in WebSocket: {e}")
                    await websocket.send_json({
                        "success": False,
                        "error": str(e)
                    })
            
            elif command == "ping":
                # Simple ping/pong for connection health check
                await websocket.send_json({
                    "success": True,
                    "message": "pong"
                })
            
            else:
                await websocket.send_json({
                    "success": False,
                    "error": f"Unknown command: {command}"
                })
    
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass
