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
from face_recognizer import enroll_person, img_to_embedding_np, recognize_face


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Webcam başlat
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Model ve izleyici
detector = YoloDetector("models/yolo9e.pt")
tracker = FaceTracker()

# 💬 İngilizce sınıf adlarını Türkçeye çeviren eşleme
label_map = {
    "tr": {
        "Person": "Kişi",
        "Head": "Kafa",
        "Face": "Yüz",
        "Glasses": "Gözlük",
        "Face-mask": "Maske",
        "Face-guard": "Yüz Koruyucu",
        "Ear": "Kulak",
        "Ear-mufs": "Kulak Koruyucu",
        "Hands": "Eller",
        "Gloves": "Eldiven",
        "Foot": "Ayak",
        "Shoes": "Ayakkabı",
        "Safety-vest": "Güvenlik Yeleği",
        "Tools": "Alet",
        "Helmet": "Baret",
        "Medical-suit": "Tıbbi Tulum",
        "Safety-suit": "İş Tulumu"
    },
    "en": {
        # İngilizce birebir çeviri, yani olduğu gibi
        "Person": "Person",
        "Head": "Head",
        "Face": "Face",
        "Glasses": "Glasses",
        "Face-mask": "Face-mask",
        "Face-guard": "Face-guard",
        "Ear": "Ear",
        "Ear-mufs": "Earmuffs",
        "Hands": "Hands",
        "Gloves": "Gloves",
        "Foot": "Foot",
        "Shoes": "Shoes",
        "Safety-vest": "Safety-vest",
        "Tools": "Tools",
        "Helmet": "Helmet",
        "Medical-suit": "Medical-suit",
        "Safety-suit": "Safety-suit"
    }
}

CONFIG_PATH = Path("config.json")

# 💡 Renk fonksiyonu
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
    return JSONResponse({"ok": True})

@app.websocket("/ws")
async def get_stream(websocket: WebSocket):
    

    await websocket.accept()
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break

            detections = detector.infer(frame)
            config = load_config()
            required_items = config.get("required_items", [])
            required_items = [item.strip().lower() for item in required_items]

            # 1. Yüzleri filtrele
            face_boxes = [det["box"] for det in detections if det["cls_name"].lower() == "face"]

            # 2. Yüzlere ID ata
            tracked_faces = tracker.update(face_boxes)

            # 3. Yüzleri ID ve isimle çiz
            for face in tracked_faces:
                fid = face["id"]
                x1, y1, x2, y2 = face["box"]
                color = get_color_for(f"face_{fid}")

                # ➕ Yüzü kırp, direkt embedding çıkar
                face_img = frame[y1:y2, x1:x2]
                if face_img.size == 0:
                    continue

                emb = img_to_embedding_np(face_img)  # 🔁 hızlı fonksiyon
                match_id = None

                if emb is not None:
                    match_id, score = recognize_face(emb)

                # Etiket yazısı: sadece ID veya ID + eşleşen kişi
                label = f"ID: {fid}"
                if match_id:
                    label += f" | {match_id}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            # 4. Diğer tespitleri çiz
            for det in detections:
                if det["conf"] >= 0.6:
                    x1, y1, x2, y2 = det["box"]
                    label = det["cls_name"]
                    label_lower = label.lower()
                    color = get_color_for(label)

                    label_text = label_map.get(label, label)
                    thickness = 4 if label_lower in required_items else 1

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                    cv2.putText(
                        frame,
                        f"{label_text} ({det['conf']:.0%})",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        1
                    )

            # 5. Frame gönder
            _, buffer = cv2.imencode(".jpg", frame)
            await websocket.send_bytes(buffer.tobytes())
            await asyncio.sleep(0.02)

    except (WebSocketDisconnect, Exception) as e:
        print("[!] WS Disconnect:", e)


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
    from PIL import Image
    from io import BytesIO

    images = []
    for file in files:
        content = await file.read()
        img = Image.open(BytesIO(content)).convert("RGB")
        images.append(img)

    try:
        enrolled_id = enroll_person(person_id, images)
        return templates.TemplateResponse("success.html", {"request": request, "person_id": enrolled_id})
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "message": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
