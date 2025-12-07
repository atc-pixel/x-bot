from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional


@dataclass
class PersonaConfig:
    name: str
    bio: str
    traits: str
    interests: List[str]
    language: str


@dataclass
class ActionRanges:
    mention: Tuple[int, int]
    tweet: Tuple[int, int]
    no_action: Tuple[int, int]
    random_min: int
    random_max: int


@dataclass
class MentionConfig:
    static_targets: List[str]
    dynamic_targets_enabled: bool
    dynamic_seed_handles: List[str]
    dynamic_max_size: int


@dataclass
class StyleConfig:
    handles: List[str]
    cache_ttl_hours: int


@dataclass
class ApifyConfig:
    enabled: bool
    tweet_actor: str
    follower_actor: str
    max_tweets_per_handle: int
    max_followings_per_seed: int


@dataclass
class BotConfig:
    persona: PersonaConfig
    actions: ActionRanges
    mentions: MentionConfig
    topics: Dict
    style: StyleConfig
    apify: ApifyConfig
