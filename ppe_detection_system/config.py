# Ortam ve PPE seçenekleri tanımlanır
# config.py

from typing import List
from pathlib import Path
import json

# Türkçe PPE seçim listesi
PPE_CHOICES = [
    "Gözlük", "Tıbbi Maske", "Yüz Koruyucu", "Kulak Koruyucu",
    "Eldiven", "Ayakkabı", "Güvenlik Yeleği", "İş Aletleri",
    "Baret", "Tıbbi Koruyucu Tulum", "İş Güvenliği Tulum"
]

# Yapılandırma dosyası
CONFIG_FILE = Path("config.json")

def load_config() -> dict:
    """
    Kaydedilen PPE seçimlerini döndür. Yoksa boş liste döner.
    """
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "required_items": []
    }

def save_config(required_items: List[str]) -> None:
    """
    Seçilen PPE listesini kaydeder.
    """
    data = {
        "required_items": required_items
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
