"""
A Twitter bot to post #SummerOfShipping tweets in a Discord channel.
"""

import os

import dotenv
import tweepy

import discord
from discord.ext import tasks

dotenv.load_dotenv()

environment_variables = [
    "TWITTER_API_KEY",
    "TWITTER_API_SECRET_KEY",
    "TWITTER_BEARER_TOKEN" "TWITTER_ACCESS_TOKEN",
    "TWITTER_ACCESS_TOKEN_SECRET",
    "DISCORD_BOT_TOKEN",
    "DISCORD_CHANNEL_ID",
]

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET_KEY = os.getenv("TWITTER_API_SECRET_KEY")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

for var in environment_variables:
    if not os.getenv(var):
        raise ValueError(f"Environment variable {var} is not set.")

LAST_SEEN_ID_FILE = "last_seen_id.txt"

twitter_api = tweepy.Client(TWITTER_BEARER_TOKEN)

# Set up Discord client
intents = discord.Intents.default()
client = discord.Client(intents=intents)


def load_last_seen_id(file_name: str) -> int | None:
    """
    Read in the last seen tweet ID from file.
    """
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return None


def save_last_seen_id(file_name: str, last_seen_id: int) -> None:
    """
    Save the last seen tweet ID to file.
    """
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(str(last_seen_id))


last_seen_tweet_id = load_last_seen_id(LAST_SEEN_ID_FILE)


def search_tweets(last_id):
    """
    Search for tweets with the hashtag #SummerOfShipping.
    """
    if last_id:
        tweets = twitter_api.search_tweets(
            q="#SummerOfShipping", since_id=last_id, result_type="recent", count=10
        )
    else:
        tweets = twitter_api.search_tweets(
            q="#SummerOfShipping", result_type="recent", count=10
        )
    return tweets


@client.event
async def on_ready():
    """
    Event handler for when the bot is ready.
    """
    print(f"Logged in as {client.user}")
    post_tweets.start()


@tasks.loop(minutes=10)
async def post_tweets():
    """
    Post tweets in the Discord channel.
    """
    global last_seen_tweet_id  # pylint: disable=global-statement

    channel = client.get_channel(DISCORD_CHANNEL_ID)
    tweets = search_tweets(last_seen_tweet_id)
    if tweets:
        # loop in reverse to maintain chronological order
        for tweet in reversed(tweets):
            message = f"{tweet.user.name}: {tweet.text}\n{tweet.created_at}\nhttps://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
            await channel.send(message)

        # update last seen tweet ID, and persist it
        last_seen_tweet_id = tweets[0].id
        save_last_seen_id(LAST_SEEN_ID_FILE, last_seen_tweet_id)


# Run the bot
client.run(DISCORD_BOT_TOKEN)
