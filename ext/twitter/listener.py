import asyncio

import tweepy


class TwitterStreamListener(tweepy.StreamListener):
    def __init__(self, twitter):
        super().__init__()
        self.twitter = twitter

    def on_status(self, status):
        loop = self.twitter.bot.loop

        # there's some magic in here somewhere
        asyncio.run_coroutine_threadsafe(self.twitter.echo_tweet(status), loop=loop)
