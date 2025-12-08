import json
import random
from pathlib import Path
from typing import List, Dict

from .models import BotConfig

# Manuel oluşturduğumuz stil dosyası
STYLE_FILE_PATH = Path("style_examples.json")

def fetch_style_examples(config: BotConfig) -> List[Dict]:
    """
    Apify yerine yerel 'style_examples.json' dosyasından rastgele tweet seçer.
    """
    print(f"[INFO] Loading style examples from {STYLE_FILE_PATH}...")

    if not STYLE_FILE_PATH.exists():
        print(f"[ERROR] {STYLE_FILE_PATH} not found! Please create it manually.")
        return []

    try:
        with STYLE_FILE_PATH.open("r", encoding="utf-8") as f:
            all_examples = json.load(f)
        
        if not all_examples:
            print("[WARN] Style file is empty.")
            return []

        # Listeden rastgele 30 tane (veya daha azsa hepsini) seç
        count = min(len(all_examples), 30)
        selected_examples = random.sample(all_examples, count)
        
        print(f"[INFO] Successfully loaded {len(all_examples)} tweets, selected {count} random examples.")
        
        # Format kontrolü ve temizlik
        cleaned_examples = []
        for ex in selected_examples:
            text = ex.get("text", "").strip()
            handle = ex.get("handle", "unknown")
            if text:
                cleaned_examples.append({"handle": handle, "text": text})
                
        return cleaned_examples

    except json.JSONDecodeError:
        print(f"[ERROR] {STYLE_FILE_PATH} is not a valid JSON file!")
        return []
    except Exception as e:
        print(f"[ERROR] Failed to load style examples: {e}")
        return []

# Bu fonksiyonlar artık kullanılmıyor ama hata vermemesi için boş bırakıyoruz
def fetch_dynamic_mention_handles(config: BotConfig) -> List[str]:
    return []