import os
import asyncio
from twikit import Client
from typing import Optional, Dict

# Twikit, asenkron (async) çalışır, ama biz senkron koda entegre edeceğiz.
# Bu yüzden wrapper fonksiyonlar kullanacağız.

async def _fetch_latest_tweet_async(username: str, auth_info: dict) -> Optional[Dict]:
    client = Client('en-US')
    
    # 1. Giriş Yap (Web arayüzü gibi davranır)
    # cookies.json varsa oradan yükle, yoksa sıfırdan gir ve kaydet
    try:
        client.load_cookies('cookies.json')
    except:
        print("[INFO] Cookies not found, logging in with credentials...")
        await client.login(
            auth_info_1=auth_info['username'],
            auth_info_2=auth_info['email'],
            password=auth_info['password']
        )
        client.save_cookies('cookies.json')

    try:
        # 2. Kullanıcıyı bul
        user = await client.get_user_by_screen_name(username)
        
        # 3. Son tweetlerini çek (Replies hariç)
        # 'Tweets' sekmesindeki son tweetleri alır
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
        return None

def fetch_latest_tweet_scrapper(username: str) -> Optional[Dict]:
    """
    Twikit kullanarak ücretsiz şekilde son tweeti çeker.
    """
    # .env'den bilgileri al
    auth_info = {
        'username': os.getenv("TWITTER_USERNAME"), # Botun kullanıcı adı (örn: jon_oldman_bot)
        'email': os.getenv("TWITTER_EMAIL"),       # Botun bağlı olduğu email
        'password': os.getenv("TWITTER_PASSWORD")  # Botun şifresi
    }

    if not all(auth_info.values()):
        print("[ERROR] .env dosyasında TWITTER_USERNAME, EMAIL ve PASSWORD eksik!")
        return None

    # Async fonksiyonu senkron içinde çalıştır
    return asyncio.run(_fetch_latest_tweet_async(username, auth_info))