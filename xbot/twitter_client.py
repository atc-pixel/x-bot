import os
import asyncio
import random
from twikit import Client
from typing import Optional, Dict

async def _fetch_latest_tweet_async(username: str, auth_info: dict) -> Optional[Dict]:
    # Cloudflare'i aşmak için gerçek bir tarayıcı User-Agent'ı kullanıyoruz
    client = Client(
        language='en-US',
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    
    # Cookies dosyasının yolu
    cookies_path = 'cookies.json'

    # 1. Giriş Yap (Web arayüzü gibi davranır)
    try:
        if os.path.exists(cookies_path):
            client.load_cookies(cookies_path)
            # Cookie yükledikten sonra kısa bir bekleme (insan gibi)
            await asyncio.sleep(random.uniform(1.0, 3.0))
        else:
            print("[INFO] Cookies not found, logging in with credentials...")
            await client.login(
                auth_info_1=auth_info['username'],
                auth_info_2=auth_info['email'],
                password=auth_info['password']
            )
            client.save_cookies(cookies_path)
            print("[INFO] Logged in and cookies saved.")

        # 2. Kullanıcıyı bul
        user = await client.get_user_by_screen_name(username)
        await asyncio.sleep(random.uniform(1.5, 3.5)) # İnsan taklidi
        
        # 3. Son tweetlerini çek
        tweets = await user.get_tweets('Tweets', count=1)
        
        if not tweets:
            return None
            
        latest_tweet = tweets[0]
        
        return {
            "id": latest_tweet.id,
            "text": latest_tweet.text,
            "author": username
        }

    except Exception as e:
        print(f"[ERROR] Twikit fetch error for @{username}: {e}")
        # Eğer cookie hatası varsa dosyayı silip tekrar denemesi için
        if "403" in str(e) or "401" in str(e):
             print("[WARN] Authentication failed. Deleting cookies.json to retry next time.")
             if os.path.exists(cookies_path):
                 os.remove(cookies_path)
        return None

def fetch_latest_tweet_scrapper(username: str) -> Optional[Dict]:
    """
    Twikit kullanarak ücretsiz şekilde son tweeti çeker.
    """
    auth_info = {
        'username': os.getenv("TWITTER_USERNAME"),
        'email': os.getenv("TWITTER_EMAIL"),
        'password': os.getenv("TWITTER_PASSWORD")
    }

    if not all(auth_info.values()):
        print("[ERROR] .env dosyasında TWITTER_USERNAME, EMAIL ve PASSWORD eksik!")
        return None

    try:
        return asyncio.run(_fetch_latest_tweet_async(username, auth_info))
    except Exception as e:
        print(f"[ERROR] Async run failed: {e}")
        return None