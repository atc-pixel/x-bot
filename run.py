import sys
from dotenv import load_dotenv

from xbot.config_loader import load_config
from xbot.openai_client import build_openai_client
from xbot.twitter_client import build_twitter_client
from xbot.bot_logic import run_once
from xbot.apify_client import fetch_style_examples  # EKLENDİ


def main():
    print("[DEBUG] run.py started...")
    
    # .env dosyasındaki şifreleri yükle
    load_dotenv()

    try:
        # 1. Konfigürasyonu yükle
        config = load_config()
        print(f"[INFO] Config loaded for persona: {config.persona.name}")

        # 2. Stil örneklerini Apify'dan (veya cache'ten) çek
        #    Bu adım, botun "nasıl konuşacağını" öğrendiği yerdir.
        print("[INFO] Fetching style examples...")
        examples = fetch_style_examples(config)
        
        # models.py içinde 'style_examples' alanı eklediğimiz için burası çalışacak
        config.style_examples = examples
        print(f"[INFO] Loaded {len(config.style_examples)} style examples.")

        # 3. İstemcileri (Clients) hazırla
        openai_client = build_openai_client()
        twitter_client = build_twitter_client()
        
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}", file=sys.stderr)
        sys.exit(1)

    # 4. Bot mantığını tek seferlik çalıştır
    print("[INFO] Running bot logic...")
    run_once(config, openai_client, twitter_client)
    print("[INFO] Run complete.")


if __name__ == "__main__":
    main()