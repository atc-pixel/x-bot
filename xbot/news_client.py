import feedparser
import random
import ssl

# SSL hatası almamak için (bazen localde sertifika sorunu olabiliyor)
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# Google News Türkiye RSS Linkleri
RSS_URLS = [
    "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr",  # Genel Manşetler
    "https://news.google.com/rss/headlines/section/topic/NATION.tr?hl=tr&gl=TR&ceid=TR:tr", # Türkiye
    "https://news.google.com/rss/headlines/section/topic/BUSINESS.tr?hl=tr&gl=TR&ceid=TR:tr", # Ekonomi
]

def get_random_news_item() -> dict:
    """
    RSS kaynaklarından rastgele bir haber başlığı ve linki çeker.
    """
    selected_rss = random.choice(RSS_URLS)
    
    try:
        feed = feedparser.parse(selected_rss)
        if not feed.entries:
            return None
        
        # İlk 10 haberden birini seçelim (en günceller)
        entry = random.choice(feed.entries[:10])
        
        return {
            "title": entry.title,
            "link": entry.link,
            "source": entry.source.get("title", "Bilinmiyor")
        }
    except Exception as e:
        print(f"[WARN] News fetch failed: {e}")
        return None