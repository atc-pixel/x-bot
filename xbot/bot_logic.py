import random
from typing import List, Optional

from .models import BotConfig
from .openai_client import generate_text
from .twitter_client import post_tweet


# -----------------------------------------------------------
#   STYLE BLOCK — LLM’in %80 dikkatini buraya çeker
# -----------------------------------------------------------

def _build_style_block(style_examples: List[dict]) -> str:
    """Modelin yazım tarzını doğrudan taklit etmesi için stil örneklerini düzenler."""

    if not style_examples:
        return ""

    # max 8 örnek alıyoruz
    samples = random.sample(style_examples, k=min(len(style_examples), 8))

    lines = []
    for i, ex in enumerate(samples, 1):
        text = ex.get("text") or ""
        text = text.replace("\n", " ").strip()
        if not text:
            continue
        if len(text) > 200:
            text = text[:200] + "..."
        lines.append(f"ÖRNEK {i}: {text}")

    if not lines:
        return ""

    return (
        "Aşağıdaki tweet örnekleri, birebir KOPYALAMAMAN gereken ama TARZINI taklit edeceğin stil örnekleridir.\n"
        "Bu örneklerden şunları taklit et:\n"
        "- cümle uzunluğu\n"
        "- ritim\n"
        "- ironik/alayıcı ton\n"
        "- kısa ve timeline uyumlu yapı\n"
        "Ama hiçbir cümleyi doğrudan kopyalama, sadece 'tavır ve ritmi' al.\n\n"
        + "\n".join(lines)
        + "\n"
    )


# -----------------------------------------------------------
#   BUILD TWEET PROMPT
# -----------------------------------------------------------

def build_tweet_prompt(config: BotConfig, style_examples: List[dict]) -> str:
    persona = config.persona
    interests = ", ".join(persona.interests)
    style_block = _build_style_block(style_examples)

    return f"""
AŞAĞIDAKİ GÖREVİ BİR X KULLANICISI GİBİ YERİNE GETİR.

ÖNCELİK SIRAN:
1) Stil örneklerindeki yazım tarzı
2) Türkçe'nin doğal akışı
3) Karakter kişiliği

KARAKTER:
- Ton: {persona.traits}
- İlgi alanları: {interests}
- Dil: {persona.language}

STİL (EN BÜYÜK ÖNCELİK):
{style_block}

GÖREV:
- Yukarıdaki ilgi alanlarından birine dair tek bir tweet yaz.
- 240 karakteri geçme.
- Kısa, doğal, tok, timeline üslubunda.
- Açıklama yapma. Makale yazma.
- Tek çıktı: Tweet metni.
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
AŞAĞIDAKİ TWEET'E GERÇEK BİR X KULLANICISI GİBİ CEVAP VER.

ÖNCELİK:
1) Stil örnekleri
2) Doğal Türkçe
3) Karakter tonu

HEDEF TWEET:
@{handle}: "{target_tweet_text}"

STİL:
{style_block}

KURALLAR:
- 1–2 cümlelik doğal bir mention yaz.
- Hafif iğneleyici olabilir ama kavga çıkarmayan.
- Tweet uzunluğu: en fazla 240 karakter.
- Sadece mention metnini döndür.
"""


# -----------------------------------------------------------
#   PICK MENTION TARGET
# -----------------------------------------------------------

def _pick_mention_target(config: BotConfig, dynamic_handles: Optional[List[str]]) -> Optional[str]:
    """Mention atılacak kişiyi seçer."""
    static = config.mention_targets.static_handles
    use_dynamic = config.mention_targets.use_dynamic

    if use_dynamic and dynamic_handles:
        pool = static + dynamic_handles
    else:
        pool = static

    if not pool:
        return None

    return random.choice(pool)


# -----------------------------------------------------------
#   RUN ONCE — MAIN BOT LOGIC
# -----------------------------------------------------------

def run_once(config: BotConfig, openai_client, twitter_client):
    """Bot'un bir çalıştırmada ne yapacağını belirler."""

    # Action dağılımı
    r = random.randint(
        config.actions.random_min,
        config.actions.random_max
    )
    # Decide action
    if config.actions.mention_range[0] <= r <= config.actions.mention_range[1]:
        decided = "mention"
    elif config.actions.tweet_range[0] <= r <= config.actions.tweet_range[1]:
        decided = "tweet"
    else:
        decided = "no_action"

    print(f"[INFO] Random value: {r}, decided action: {decided}")


    mention_lo, mention_hi = config.actions.mention_range
    tweet_lo, tweet_hi = config.actions.tweet_range

    dynamic_handles = []  # ileride dinamik handle desteği buraya takılır

    # -----------------------------------------------------------
    #  NO ACTION
    # -----------------------------------------------------------
    if r < mention_lo or r > tweet_hi:
        print("[INFO] No action this run.")
        return

    # -----------------------------------------------------------
    #  TWEET ACTION
    # -----------------------------------------------------------
    if mention_hi < r <= tweet_hi:
        prompt = build_tweet_prompt(config, config.style_examples)
        text = generate_text(openai_client, prompt)

        if not text or not text.strip():
            print("[WARN] Empty tweet generated; skipping.")
            return

        print(f"[DEBUG] Generated tweet: {text}")
        post_tweet(twitter_client, text)
        return

    # -----------------------------------------------------------
    #  MENTION ACTION
    # -----------------------------------------------------------
    if mention_lo <= r <= mention_hi:

        handle = _pick_mention_target(config, dynamic_handles)
        if not handle:
            print("[WARN] No mention target. Skipping.")
            return

        # Stil cache'inde bu handle’a ait örnek arıyoruz
        candidate = next(
            (ex for ex in config.style_examples if ex["handle"] == handle),
            None
        )

        if not candidate:
            print(f"[WARN] No style example found for @{handle}. Skipping mention.")
            return

        target_text = candidate.get("text") or ""
        target_tweet_id = candidate.get("tweet_id") or None

        if not target_text.strip():
            print(f"[WARN] target_text is empty for @{handle}; skipping.")
            return

        prompt = build_mention_prompt(config, handle, target_text, config.style_examples)
        reply_text = generate_text(openai_client, prompt)

        if not reply_text.strip():
            print(f"[WARN] Empty reply for @{handle}; skipping.")
            return

        reply_text = f"@{handle} {reply_text}"

        print(f"[DEBUG] Generated mention reply: {reply_text}")

        post_tweet(twitter_client, reply_text, in_reply_to_tweet_id=target_tweet_id)
        return
