import os
import asyncio
import random
from twikit import Client

def build_twitter_client():
    # Tweepy yerine Twikit kullandığımız için boş dönüyoruz
    return None

async def _post_tweet_async(text: str, reply_to: str = None):
    client = Client(
        language='en-US',
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    
    cookies_path = 'cookies.json'

    # Scrapper'ın oluşturduğu çerezleri kullan
    if os.path.exists(cookies_path):
        try:
            client.load_cookies(cookies_path)
        except Exception as e:
            print(f"[ERROR] Failed to load cookies for posting: {e}")
            return
    else:
        print("[ERROR] cookies.json not found! Please check .env and run scrapper first.")
        return

    try:
        print("[INFO] Preparing to post tweet via Twikit...")
        
        # İNSAN TAKLİDİ: Tweeti yazıyormuş gibi rastgele bekle
        wait_time = random.uniform(5.0, 12.0)
        print(f"[DEBUG] Waiting {wait_time:.1f} seconds to mimic human typing...")
        await asyncio.sleep(wait_time)

        # Reply ise ID ver, değilse normal tweet at
        await client.create_tweet(text=text, reply_to=reply_to)
        print("[INFO] Tweet successfully posted!")
        
    except Exception as e:
        print(f"[ERROR] Twikit post failed: {e}")
        # Eğer 226 hatası alırsan cookie'leri silme, çünkü okuma (fetch) hala çalışıyor olabilir.
        # Sadece 401/403 durumunda silmek daha mantıklı.

def post_tweet(client, text: str, in_reply_to_tweet_id: str = None, quote_tweet_id: str = None):
    """
    Twikit kullanarak tweet atar.
    """
    asyncio.run(_post_tweet_async(text, in_reply_to_tweet_id))