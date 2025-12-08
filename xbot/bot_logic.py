import random
from typing import List, Optional

from .models import BotConfig
from .openai_client import generate_text
from .twitter_client import post_tweet
from .news_client import get_random_news_item  
from .scrapper_client import fetch_latest_tweet_scrapper

# -----------------------------------------------------------
#   STYLE BLOCK
# -----------------------------------------------------------

def _build_style_block(style_examples: List[dict]) -> str:
    """Modelin yazım tarzını kopyalaması için örnekleri hazırlar."""
    if not style_examples:
        return "Stil örneği yok. Kısa, öz ve hafif agresif yaz."

    # SENİN GÜNCELLEMEN: Örnek sayısını artırdık.
    # Ancak token limitini patlatmamak için çok uzun tweetleri filtreleyelim.
    valid_examples = [ex for ex in style_examples if ex.get("text") and len(ex["text"]) < 280]
    samples = random.sample(valid_examples, k=min(len(valid_examples), 20))

    lines = []
    for ex in samples:
        text = ex["text"].replace("\n", " ").strip()
        lines.append(f">>> {text}")

    return (
        "AŞAĞIDAKİ TWEETLER, SENİN TAKLİT ETMEN GEREKEN 'RUH HALİ', 'ARGO' VE 'ÜSLUP' ÖRNEKLERİDİR.\n"
        "BU ÖRNEKLERİ ANALİZ ET VE ŞUNLARI KOPYALA:\n"
        "1. Cümle yapısı (küçük harfle başlama, nokta koymama vb.)\n"
        "2. Küfür/Argo kullanımı (aq, amk, lan vb. varsa sen de kullan)\n"
        "3. Agresiflik veya boş vermişlik seviyesi.\n"
        "4. Asla 'robot' gibi düzgün cümle kurma.\n"
        "--------------------------------------------------\n"
        + "\n".join(lines) + "\n"
        "--------------------------------------------------\n"
    )


# -----------------------------------------------------------
#   BUILD TWEET PROMPT (HABER YORUMLAMA)
# -----------------------------------------------------------

def build_news_tweet_prompt(config: BotConfig, news_item: dict, style_examples: List[dict]) -> str:
    persona = config.persona
    style_block = _build_style_block(style_examples)
    
    news_context = f"HABER BAŞLIĞI: {news_item['title']}\nKAYNAK: {news_item['source']}"

    return f"""
GÖREV: Aşağıdaki haberi gören bir 'Twitter Fenomeni' gibi bu haberi yorumla (Tweet at).

KİMLİK (PERSONA):
İsim: {persona.name}
Özellikler: {persona.traits}
Dil: {persona.language} (Sokak ağzı, Twitter jargonu)

REFERANS STİL (BUNU TAKLİT ET - KUTSAL KİTABIN BU):
{style_block}

HEDEF HABER:
{news_context}

🛑 KESİN KURALLAR (AŞARSAN FİŞİNİ ÇEKERİM):
1. 🚫 ASLA EMOJI KULLANMA.
2. 🚫 ASLA HASHTAG (#) KULLANMA.
3. 🚫 Haber başlığını olduğu gibi yazma. Habere tepki ver.
4. 🚫 "İnanılmaz", "Şok oldum" gibi yapay tepkiler verme.
5. ✅ Stil örneklerinde küfür/argo (aq, amk, s**t) varsa, ÇEKİNMEDEN KULLAN. Sansürleme.
6. ✅ İmla kurallarını boşver. Örneklerdeki gibi küçük harfle başla, nokta koyma.
7. ✅ Alaycı, sarkastik, iğneleyici ol. Taraf tut.
8. Tweet 240 karakteri geçmesin.

ÇIKTI (SADECE TWEET):
"""

# -----------------------------------------------------------
#   BUILD MENTION PROMPT
# -----------------------------------------------------------

def build_mention_prompt(
    config: BotConfig,
    handle: str,
    target_tweet_text: str,
    style_examples: List[dict],
) -> str:
    persona = config.persona
    style_block = _build_style_block(style_examples)

    return f"""
GÖREV: Aşağıdaki tweete mention atarak cevap ver.

HEDEF TWEET (@{handle}):
"{target_tweet_text}"

REFERANS STİL (BUNU TAKLİT ET):
{style_block}

🛑 KESİN KURALLAR:
1. 🚫 EMOJI VE HASHTAG YASAK.
2. 🚫 Resmiyetten uzak dur. "Merhaba", "Sayın" YOK.
3. ✅ Gerekirse sert çıkış, gerekirse dalga geç.
4. ✅ "aq", "amk", "lan" gibi kalıplar stil örneklerinde varsa kullan.
5. Sadece cevap metnini yaz.

CEVAP:
"""
# -----------------------------------------------------------
#   BUILD QUOTE PROMPT
# -----------------------------------------------------------

def build_quote_prompt(config: BotConfig, target_handle: str, target_text: str, style_examples: List[dict]) -> str:
    persona = config.persona
    style_block = _build_style_block(style_examples)

    return f"""
GÖREV: Aşağıdaki tweeti, sanki timeline'ında görüp takipçilerine gösteriyormuş gibi ALINTILA (Quote Tweet).

HEDEF TWEET (@{target_handle}):
"{target_text}"

SENİN KİMLİĞİN:
{persona.traits}
Dil: {persona.language} (Sokak ağzı, sarkastik)

STİL REHBERİ:
{style_block}

KURALLAR:
1. 🚫 EMOJI VE HASHTAG YASAK.
2. 🚫 "Bakın ne demiş" gibi sıkıcı girişler yapma.
3. Hedef tweetin içeriğiyle ilgili sarkastik, iğneleyici bir yorum yap.
4. 240 karakteri geçme.

ÇIKTI:
"""

# -----------------------------------------------------------
#   PICK MENTION TARGET
# -----------------------------------------------------------

def _pick_mention_target(config: BotConfig, dynamic_handles: Optional[List[str]]) -> Optional[str]:
    static = getattr(config.mentions, 'static_targets', [])
    use_dynamic = getattr(config.mentions, 'dynamic_targets_enabled', False)

    pool = (static + dynamic_handles) if (use_dynamic and dynamic_handles) else static
    
    if not pool:
        return None
    return random.choice(pool)


# -----------------------------------------------------------
#   RUN ONCE — MAIN BOT LOGIC
# -----------------------------------------------------------

def run_once(config: BotConfig, openai_client, twitter_client):
    r = random.randint(config.actions.random_min, config.actions.random_max)
    
    # Eylem aralıklarını kontrol et
    if config.actions.mention[0] <= r <= config.actions.mention[1]:
        decided = "mention"
    elif config.actions.quote[0] <= r <= config.actions.quote[1]:
        decided = "quote"
    elif config.actions.tweet[0] <= r <= config.actions.tweet[1]:
        decided = "tweet"
    else:
        decided = "no_action"
    
    print(f"[INFO] Random: {r}, Action: {decided}")

    if decided == "no_action":
        return

    # -----------------------------------------------------------
    #  TWEET ACTION (HABER YORUMLAMA)
    # -----------------------------------------------------------
    if decided == "tweet":
        styles = getattr(config, 'style_examples', [])
        
        # 1. Haberi çek
        print("[INFO] Fetching a random news item...")
        news_item = get_random_news_item()
        
        if not news_item:
            print("[WARN] Could not fetch news. Falling back to generic prompt isn't implemented. Skipping.")
            return

        print(f"[INFO] Selected News: {news_item['title']}")

        # 2. Prompt oluştur
        prompt = build_news_tweet_prompt(config, news_item, styles)
        
        # 3. Yazdır
        text = generate_text(openai_client, prompt)

        if not text or not text.strip():
            print("[WARN] Empty tweet generated; skipping.")
            return

        # 4. (Opsiyonel) Haberin linkini de ekleyelim mi?
        # Genelde 'alıntı' (quote tweet) mantığı daha iyidir ama link atmak etkileşimi düşürebilir.
        # Şimdilik sadece metin atıyoruz, "haberden bahsediyor" gibi.
        
        print(f"[DEBUG] Generated tweet: {text}")
        post_tweet(twitter_client, text)
        return

    # -----------------------------------------------------------
    #  MENTION ACTION
    # -----------------------------------------------------------
    if decided == "mention":
        handle = _pick_mention_target(config, [])
        if not handle:
            return

        all_styles = getattr(config, 'style_examples', [])
        candidate = next((ex for ex in all_styles if ex["handle"] == handle), None)

        if not candidate:
            print(f"[WARN] No cached tweet found for @{handle}. Skipping.")
            return

        target_text = candidate.get("text") or ""
        target_tweet_id = candidate.get("tweet_id") or None

        prompt = build_mention_prompt(config, handle, target_text, all_styles)
        reply_text = generate_text(openai_client, prompt)

        if not reply_text.strip():
            return

        reply_text = f"@{handle} {reply_text}"
        print(f"[DEBUG] Generated mention: {reply_text}")

        post_tweet(twitter_client, reply_text, in_reply_to_tweet_id=target_tweet_id)
        return
        
    # -----------------------------------------------------------
    #  QUOTE ACTION (Twikit ile Ücretsiz)
    # -----------------------------------------------------------
    if decided == "quote":
        targets = getattr(config, "quote_targets", [])
        if not targets:
            print("[WARN] No quote targets defined.")
            return

        target_handle = random.choice(targets)
        print(f"[INFO] Fetching latest tweet for quote: @{target_handle} (via Twikit)")
        
        # Ücretsiz Scraper ile çek
        tweet_data = fetch_latest_tweet_scrapper(target_handle)
        
        if not tweet_data:
            print(f"[WARN] Could not fetch tweet for @{target_handle}. Skipping.")
            return

        styles = getattr(config, 'style_examples', [])
        # Stil örnekleri hala style_examples.json'dan (veya config'den) geliyor, bu değişmedi.
        
        prompt = build_quote_prompt(config, target_handle, tweet_data["text"], styles)
        
        text = generate_text(openai_client, prompt)
        if not text: return

        print(f"[DEBUG] Generated Quote Text: {text}")
        post_tweet(twitter_client, text, quote_tweet_id=tweet_data["id"])
        return