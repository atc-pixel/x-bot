import os
import tweepy


def build_twitter_client() -> tweepy.Client:
    api_key = os.getenv("X_API_KEY")
    api_secret = os.getenv("X_API_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_secret = os.getenv("X_ACCESS_SECRET")

    if not all([api_key, api_secret, access_token, access_secret]):
        raise RuntimeError("X API credentials missing in environment.")

    return tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret,
    )


def post_tweet(client: tweepy.Client, text: str, in_reply_to_tweet_id: str | None = None):
    if in_reply_to_tweet_id:
        resp = client.create_tweet(text=text, in_reply_to_tweet_id=in_reply_to_tweet_id)
    else:
        resp = client.create_tweet(text=text)
    tweet_id = resp.data.get("id") if resp and resp.data else "unknown"
    print(f"[INFO] Tweet sent. ID: {tweet_id}")
