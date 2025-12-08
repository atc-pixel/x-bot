import os
import asyncio
import random
import json
import traceback
from twikit import Client
from typing import Optional, Dict

async def _fetch_latest_tweet_async(username: str) -> Optional[Dict]:
    print(f"[DEBUG] Starting fetch process for @{username}...")
    
    # Modern bir User-Agent
    client = Client(
        language='en-US',
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    
    cookies_path = 'cookies.json'

    # 1. Cookie Kontrolü ve Oluşturma
    if not os.path.exists(cookies_path):
        auth_token = os.getenv("TWITTER_AUTH_TOKEN")
        ct0 = os.getenv("TWITTER_CT0")
        
        if auth_token and ct0:
            print("[INFO] Creating cookies.json from env variables...")
            manual_cookies = {
                "auth_token": auth_token,
                "ct0": ct0
            }
            try:
                with open(cookies_path, "w", encoding="utf-8") as f:
                    json.dump(manual_cookies, f)
            except Exception as e:
                print(f"[ERROR] Failed to write cookies.json: {e}")
                return None
        else:
            print("[ERROR] No cookies.json and no TWITTER_AUTH_TOKEN in .env!")
            return None

    # 2. Giriş (Cookie Yükleme)
    try:
        # print("[DEBUG] Loading cookies...")
        client.load_cookies(cookies_path)
    except Exception as e:
        print(f"[ERROR] Failed to load cookies: {e}")
        return None

    # 3. Veri Çekme (YENİ YÖNTEM: ARAMA)
    try:
        await asyncio.sleep(random.uniform(2.0, 4.0))
        
        # Profile gitmek yerine 'from:username' araması yapıyoruz.
        # Bu yöntem bloklanma ihtimalini düşürür.
        print(f"[DEBUG] Searching for latest tweet via query: from:{username}")
        
        results = await client.search_tweet(f'from:{username}', 'Latest', count=1)
        
        if not results:
            print(f"[WARN] Search returned NO results for @{username}.")
            # Fallback: Son çare profile bakmayı dene (ama muhtemelen o da boştur)
            # user = await client.get_user_by_screen_name(username)
            # ...
            return None
            
        latest_tweet = results[0]
        print(f"[DEBUG] Tweet found: {latest_tweet.text[:40]}...")
        
        return {
            "id": latest_tweet.id,
            "text": latest_tweet.text,
            "author": username
        }

    except Exception as e:
        print(f"[ERROR] Twikit fetch error for @{username}: {e}")
        # traceback.print_exc() # Detaylı hata gerekirse açabilirsin
        
        if "401" in str(e) or "403" in str(e):
            print("[WARN] Cookies might be expired/invalid. Please update .env")
            if os.path.exists(cookies_path):
                try:
                    os.remove(cookies_path)
                except:
                    pass
        return None

def fetch_latest_tweet_scrapper(username: str) -> Optional[Dict]:
    try:
        return asyncio.run(_fetch_latest_tweet_async(username))
    except Exception as e:
        print(f"[ERROR] Async run failed: {e}")
        return None