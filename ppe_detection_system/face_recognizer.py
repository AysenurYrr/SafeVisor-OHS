import os
import json
import numpy as np
from PIL import Image
import torch
import cv2
from torchvision import transforms
from facenet_pytorch import MTCNN, InceptionResnetV1

REGISTRY_PATH = "face_registry.json"
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Modeller
mtcnn = MTCNN(image_size=160, margin=10, device=device)
model = InceptionResnetV1(pretrained='vggface2').eval().to(device)

def _normalize(v):
    return v / np.linalg.norm(v)

# ✅ PIL img üzerinden embedding (Kayıt için)
def img_to_embedding_pil(pil_img):
    face = mtcnn(pil_img)
    if face is None:
        return None
    with torch.no_grad():
        emb = model(face.unsqueeze(0).to(device)).cpu().numpy()[0]
    return _normalize(emb)

# ✅ NumPy img (gerçek zamanlı stream için)
def img_to_embedding_np(np_img):
    try:
        img = cv2.resize(np_img, (160, 160))
    except:
        return None
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5])
    ])
    tensor = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        emb = model(tensor).cpu().numpy()[0]
    return _normalize(emb)

# 🔄 JSON kayıtlarını oku
def load_registry():
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

# 💾 JSON kayıtlarını kaydet
def save_registry(reg):
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)

# 🧍‍♂️ Yeni kişi kaydı
def enroll_person(person_id, pil_images, full_name=""):
    embs = [img_to_embedding_pil(im) for im in pil_images if img_to_embedding_pil(im) is not None]
    if not embs:
        raise ValueError("Yüz bulunamadı.")
    mean_emb = _normalize(np.mean(embs, axis=0))
    reg = load_registry()
    reg[person_id] = {
        "name": full_name or person_id,
        "embedding": mean_emb.tolist()
    }
    save_registry(reg)
    return person_id

# 🔍 Yüz tanıma
def recognize_face(embedding, threshold=0.7):
    registry = load_registry()
    if not registry:
        return None, None

    best_match = None
    best_score = float("inf")

    for person_id, entry in registry.items():
        reg_emb = np.array(entry["embedding"])
        dist = np.linalg.norm(embedding - reg_emb)
        if dist < best_score:
            best_score = dist
            best_match = entry["name"]

    if best_score < threshold:
        return best_match, best_score
    return None, best_score
