import sys
from dotenv import load_dotenv

from xbot.config_loader import load_config
from xbot.openai_client import build_openai_client
from xbot.twitter_client import build_twitter_client
from xbot.bot_logic import run_once
# YENİ IMPORT:
from xbot.apify_client import fetch_style_examples


def main():
    print("[DEBUG] main() started")
    load_dotenv()

    try:
        config = load_config()
        
        # DÜZELTME: Bot mantığı çalışmadan önce stil örneklerini çekip config'e ekliyoruz
        print("[INFO] Fetching style examples...")
        examples = fetch_style_examples(config)
        config.style_examples = examples
        print(f"[INFO] Loaded {len(config.style_examples)} style examples.")

        openai_client = build_openai_client()
        twitter_client = build_twitter_client()
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}", file=sys.stderr)
        sys.exit(1)

    run_once(config, openai_client, twitter_client)


if __name__ == "__main__":
    print("[DEBUG] __main__ block entered")
    main()