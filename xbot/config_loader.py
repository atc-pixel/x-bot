import yaml
from .models import (
    PersonaConfig,
    ActionRanges,
    MentionConfig,
    StyleConfig,
    ApifyConfig,
    BotConfig,
)


def load_config(path: str = "config.yaml") -> BotConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    persona_raw = raw["persona"]
    actions_raw = raw["actions"]
    mentions_raw = raw.get("mentions", {})
    topics_raw = raw.get("topics", {})
    style_raw = raw.get("style_reference", {})
    apify_raw = raw.get("apify", {})

    persona = PersonaConfig(
        name=persona_raw.get("name", "XBot"),
        bio=persona_raw.get("bio", ""),
        traits=persona_raw.get("traits", ""),
        interests=persona_raw.get("interests", []),
        language=persona_raw.get("language", "tr"),
    )

    actions = ActionRanges(
        mention=tuple(actions_raw["mention_range"]),
        tweet=tuple(actions_raw["tweet_range"]),
        no_action=tuple(actions_raw["no_action_range"]),
        random_min=actions_raw.get("random_min", 0),
        random_max=actions_raw.get("random_max", 100),
    )

    mentions = MentionConfig(
        static_targets=mentions_raw.get("static_targets", []),
        dynamic_targets_enabled=mentions_raw.get("dynamic_targets_enabled", False),
        dynamic_seed_handles=mentions_raw.get("dynamic_seed_handles", []),
        dynamic_max_size=mentions_raw.get("dynamic_max_size", 50),
    )

    style = StyleConfig(
        handles=style_raw.get("handles", []),
        cache_ttl_hours=style_raw.get("cache_ttl_hours", 6),
    )

    apify = ApifyConfig(
        enabled=apify_raw.get("enabled", False),
        tweet_actor=apify_raw.get("tweet_actor", ""),
        follower_actor=apify_raw.get("follower_actor", ""),
        max_tweets_per_handle=apify_raw.get("max_tweets_per_handle", 5),
        max_followings_per_seed=apify_raw.get("max_followings_per_seed", 50),
    )

    return BotConfig(
        persona=persona,
        actions=actions,
        mentions=mentions,
        topics=topics_raw,
        style=style,
        apify=apify,
    )
