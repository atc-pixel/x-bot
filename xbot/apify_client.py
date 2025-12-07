import os
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple

import requests

from .models import BotConfig

APIFY_BASE = "https://api.apify.com/v2/acts"
STYLE_CACHE_PATH = Path("style_cache.json")


def _get_apify_token() -> str:
    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        raise RuntimeError("APIFY_API_TOKEN missing in environment.")
    return token


def _run_actor_sync(actor_id: str, payload: Dict) -> List[Dict]:
    token = _get_apify_token()
    url = f"{APIFY_BASE}/{actor_id}/run-sync-get-dataset-items?token={token}"
    resp = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload), timeout=120)
    resp.raise_for_status()
    try:
        data = resp.json()
        if isinstance(data, list):
            return data
        # bazen dataset tek obje dönebiliyor, normalize edelim
        return [data]
    except Exception:
        return []


# ---------- Stil örnekleri (tweet dili) ----------

def _load_style_cache(max_age_seconds: int) -> List[Dict]:
    if not STYLE_CACHE_PATH.exists():
        return []
    age = time.time() - STYLE_CACHE_PATH.stat().st_mtime
    if age > max_age_seconds:
        return []
    try:
        with STYLE_CACHE_PATH.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj.get("examples", [])
    except Exception:
        return []


def _save_style_cache(examples: List[Dict]):
    STYLE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STYLE_CACHE_PATH.open("w", encoding="utf-8") as f:
        json.dump(
            {"generated_at": time.time(), "examples": examples},
            f,
            ensure_ascii=False,
            indent=2,
        )


def fetch_style_examples(config: BotConfig) -> List[Dict]:
    """
    Stil referansı verilen hesaplardan, Apify tweet scraper ile
    periyodik olarak tweet örnekleri alır ve cache'ler.
    """
    if not config.apify.enabled or not config.apify.tweet_actor:
        return []

    ttl = config.style.cache_ttl_hours * 3600
    cached = _load_style_cache(ttl)
    if cached:
        print("[INFO] Using cached style examples.")
        return cached

    handles = config.style.handles
    if not handles:
        return []

    print("[INFO] Refreshing style examples via Apify...")
    actor_id = config.apify.tweet_actor.replace("/", "~")  # store format -> acts/owner~name
    all_examples: List[Dict] = []

    for handle in handles:
        # timeline benzeri: from:username search
        search_url = f"https://twitter.com/search?q=from%3A{handle}&src=typed_query&f=live"
        payload = {
            "maxItems": config.apify.max_tweets_per_handle,
            "startUrls": [search_url],
        }
        items = _run_actor_sync(actor_id, payload)
        for it in items:
            text = (
                it.get("full_text")
                or it.get("text")
                or it.get("tweet_text")
                or ""
            ).strip()
            tweet_id = (
                it.get("id_str")
                or it.get("tweetId")
                or it.get("id")
                or ""
            )
            if not text:
                continue
            if len(text) > 240:
                text = text[:240] + "..."
            all_examples.append(
                {"handle": handle, "tweet_id": tweet_id, "text": text}
            )

    if not all_examples:
        return []

    _save_style_cache(all_examples)
    return all_examples


# ---------- Dinamik mention hedefleri (isteğe bağlı) ----------

def fetch_dynamic_mention_handles(config: BotConfig) -> List[str]:
    """
    Seed hesapların followings listesini alıp, mention için potansiyel hedefler döndürür.
    """
    if not config.apify.enabled or not config.apify.follower_actor:
        return []

    seeds = config.mentions.dynamic_seed_handles
    if not seeds:
        return []

    actor_id = config.apify.follower_actor.replace("/", "~")
    max_per_seed = config.apify.max_followings_per_seed
    seen: set[str] = set()

    for seed in seeds:
        payload = {
            "user_names": [seed],
            "user_ids": [],
            "maxFollowers": 0,
            "maxFollowings": max_per_seed,
            "getFollowers": False,
            "getFollowing": True,
        }
        items = _run_actor_sync(actor_id, payload)
        for it in items:
            # field ismi tam net değil; yaygın varyantları deneyelim
            uname = (
                it.get("username")
                or it.get("user_name")
                or it.get("screen_name")
            )
            if not uname:
                continue
            uname = uname.strip()
            if uname and uname not in seen:
                seen.add(uname)
                if len(seen) >= config.mentions.dynamic_max_size:
                    break
        if len(seen) >= config.mentions.dynamic_max_size:
            break

    return list(seen)
