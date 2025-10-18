from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from PIL import Image
import uvicorn
import asyncio
import cv2
import json
import numpy as np
from pathlib import Path

from detector import YoloDetector
from face_tracker import FaceTracker
from evaluator import evaluate_person
from face_recognizer import enroll_person, img_to_embedding_pil, recognize_face
from temporal_tracker import TemporalTracker
from violation_manager import ViolationManager

# ===============================
# 🔧 Uygulama Başlatma
# ===============================
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

detector = YoloDetector("models/yolo9e.pt")
tracker = FaceTracker()

# ✅ Yeni temporal tracker ve violation manager
temporal_tracker = TemporalTracker(
    max_distance=100,
    max_missing_frames=30,
    grace_frames=2,
    confidence_threshold=0.2
)
violation_manager = ViolationManager(
    factory_area_name="Ana Üretim Alanı",
    camera_name="Kamera 1",
    min_consecutive_frames=5,
    violation_timeout=5.0,
    cleanup_interval=30.0,
    violations_dir="violations/images"
)

# ✅ Yüz ID ↔ isim eşlemesi (bellek içi)
recognized_map = {}  # face_id -> person_id
frame_count = 0

# ===============================
# 💬 Etiket Haritaları
# ===============================
label_map = {
    "tr": {
        "Person": "Kişi", "Head": "Kafa", "Face": "Yüz", "Glasses": "Gözlük",
        "Face-mask": "Maske", "Face-guard": "Yüz Koruyucu", "Ear": "Kulak", "Ear-mufs": "Kulak Koruyucu",
        "Hands": "Eller", "Gloves": "Eldiven", "Foot": "Ayak", "Shoes": "Ayakkabı",
        "Safety-vest": "Güvenlik Yeleği", "Tools": "Alet", "Helmet": "Baret",
        "Medical-suit": "Tıbbi Tulum", "Safety-suit": "İş Tulumu"
    }
}

CONFIG_PATH = Path("config.json")

def get_color_for(key: str) -> tuple:
    np.random.seed(hash(key) % 2**32)
    return tuple(int(x) for x in np.random.randint(60, 255, size=3))

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"required_items": [], "workspace": ""}

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

# ===============================
# 🌐 ROUTES
# ===============================
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index2.html", {"request": request})

@app.get("/config")
def get_config():
    return load_config()

@app.post("/config")
async def update_config(req: Request):
    cfg = await req.json()
    save_config(cfg)
    
    # Update violation manager with required PPE
    required_items = cfg.get("required_items", [])
    if required_items:
        violation_manager.set_required_ppe(required_items)
    
    return JSONResponse({"ok": True})

# ===============================
# 📡 WEBSOCKET STREAM
# ===============================
@app.websocket("/ws")
async def get_stream(websocket: WebSocket):
    await websocket.accept()
    global frame_count
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break

            frame_count += 1
            detections = detector.infer(frame)
            config = load_config()
            required_items = [item.strip().lower() for item in config.get("required_items", [])]
            
            # Update violation manager with required items
            violation_manager.set_required_ppe(required_items)

            # 1️⃣ Update temporal tracker with all detections
            recognitions = {}
            
            # Extract face detections for recognition
            face_detections = [det for det in detections if det["cls_name"].lower() == "face"]
            
            for face_det in face_detections:
                x1, y1, x2, y2 = face_det["box"]
                face_img = frame[y1:y2, x1:x2]
                
                if face_img.size > 0:
                    # Embedding çıkar
                    face_pil = Image.fromarray(cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB))
                    emb = img_to_embedding_pil(face_pil)
                    
                    if emb is not None:
                        match_id, score = recognize_face(emb)
                        
                        # Find corresponding person in tracker (will be assigned after update)
                        # For now, we'll update recognitions after tracking
                        if match_id and score is not None:
                            # Store temporarily with face box for matching
                            face_center = ((x1 + x2) // 2, (y1 + y2) // 2)
                            recognitions[face_center] = (match_id, 1.0 - score)  # Convert distance to confidence
            
            # Update temporal tracker
            tracked_persons = temporal_tracker.update_frame(detections)
            
            # Match recognitions to tracked persons
            for person in tracked_persons:
                px1, py1, px2, py2 = person.box
                person_center = ((px1 + px2) // 2, (py1 + py2) // 2)
                
                # Find closest face recognition
                best_match = None
                best_distance = float('inf')
                
                for face_center, (name, conf) in recognitions.items():
                    dist = np.hypot(person_center[0] - face_center[0], 
                                  person_center[1] - face_center[1])
                    if dist < best_distance and dist < 100:  # 100 pixel threshold
                        best_distance = dist
                        best_match = (name, conf)
                
                if best_match:
                    person.update_recognition(best_match[0], best_match[1], 
                                            frame_count, confidence_threshold=0.2)

            # 2️⃣ Check for violations with temporal consistency
            violations_to_report = violation_manager.check_violations(
                tracked_persons, frame, frame_count
            )
            
            # Log any new violations
            if violations_to_report:
                for violation in violations_to_report:
                    print(f"[VIOLATION] {violation['employee_name']}: {violation['violation_type']} "
                          f"({violation['duration_frames']} frames)")

            # 3️⃣ Draw tracked persons with stable recognition
            for person in tracked_persons:
                x1, y1, x2, y2 = person.box
                color = get_color_for(f"person_{person.person_id}")
                
                # Stabil isim gösterimi
                name_label = person.recognized_name or f"Unknown ({person.person_id})"
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, name_label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Show PPE status
                y_offset = y1 - 30
                for ppe_type in required_items:
                    has_ppe = person.get_stable_ppe_status(ppe_type, frame_count, grace_frames=2)
                    status_text = f"{ppe_type}: {'✓' if has_ppe else '✗'}"
                    status_color = (0, 255, 0) if has_ppe else (0, 0, 255)
                    
                    cv2.putText(frame, status_text, (x1, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, status_color, 1)
                    y_offset -= 15

            # 4️⃣ Diğer tespitleri çiz (PPE ekipmanları)
            for det in detections:
                if det["conf"] >= 0.6:
                    x1, y1, x2, y2 = det["box"]
                    label = det["cls_name"]
                    label_lower = label.lower()
                    
                    # Skip person/face (already drawn above)
                    if label_lower in ['person', 'face']:
                        continue
                    
                    color = get_color_for(label)
                    label_text = label_map["tr"].get(label, label)
                    thickness = 4 if label_lower in required_items else 1

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                    cv2.putText(frame, f"{label_text} ({det['conf']:.0%})", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            # 5️⃣ Frame gönder
            _, buffer = cv2.imencode(".jpg", frame)
            await websocket.send_bytes(buffer.tobytes())
            await asyncio.sleep(0.02)
            
            # Periodic cleanup
            if frame_count % 300 == 0:  # Every 10 seconds at 30 FPS
                temporal_tracker.cleanup_old_persons(max_age_seconds=30.0)

    except (WebSocketDisconnect, Exception) as e:
        print("[!] WS Disconnect:", e)

# ===============================
# 🧍 Kayıt Sayfası
# ===============================
@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/enroll")
async def enroll_person_api(
    request: Request,
    person_id: str = Form(...),
    full_name: str = Form(""),
    files: list[UploadFile] = Form(...)
):
    from io import BytesIO

    images = []
    for file in files:
        content = await file.read()
        img = Image.open(BytesIO(content)).convert("RGB")
        images.append(img)

    try:
        enrolled_id = enroll_person(person_id, images, full_name)
        return templates.TemplateResponse("success.html", {"request": request, "person_id": enrolled_id})
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "message": str(e)})

# ===============================
# 🚀 Uygulama Başlat
# ===============================
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
