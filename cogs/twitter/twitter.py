import logging

import tweepy
from discord.ext import commands
from discord.ext.commands import Bot, Context
from peewee import IntegrityError
from tweepy import Status

from cogs.twitter.listener import TwitterStreamListener
from cogs.twitter.models import TwitterEcho
from cogs.utils.database import Server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Twitter:
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot
        config = self.bot.config['twitter']

        TwitterEcho.create_table(fail_silently=True)

        logger.info('Connecting to Twitter...')
        auth = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
        auth.set_access_token(config['access_token_key'], config['access_token_secret'])
        self.api = tweepy.API(auth)
        listener = TwitterStreamListener(self)
        self.stream = tweepy.Stream(auth=self.api.auth, listener=listener)
        self._update_stream_filter()

    def _update_stream_filter(self):
        if self.stream.running:
            self.stream.disconnect()
        self.stream.filter(follow=[str(user.user_id) for user in TwitterEcho.select()], async=True)

    async def echo_tweet(self, status: Status):
        # print(status)
        author = status.author
        echo = TwitterEcho.get(TwitterEcho.user_id == author.id)
        channel = self.bot.get_channel(echo.channel)
        await self.send_tweet(channel, status)

    async def send_tweet(self, channel, status):
        if status.author:
            author = status.author
        await self.bot.send_message(
            channel,
            'https://twitter.com/{0.author.screen_name}/status/{0.id_str}'
                .format(status))

    @commands.group(
        aliases=['tw'],
        invoke_without_command=True
    )
    async def twitter(self):
        """
        List the Twitter users the bot is currently following.
        """
        following = ', '.join(['@' + user.screen_name for user in TwitterEcho.select()])

        await self.bot.say('Currently following:\n{0}'.format(following))

    @twitter.command(
        aliases=['f'],
        pass_context=True
    )
    async def follow(self, ctx: Context, user):
        """
        Add a user to the bot's follow list.
        Bot will post user's tweets to this channel. 
        Args:
            user: The @handle of the user to follow.
        """
        user = self.api.get_user(user)

        echo = TwitterEcho(server=Server.get_server(ctx.message.server.id), user_id=user.id,
                           screen_name=user.screen_name, channel=ctx.message.channel.id)

        try:
            saved = echo.save()
            self._update_stream_filter()
        except IntegrityError as e:
            await self.bot.say('Already following @{0.screen_name}.'.format(user))
            return

        await self.bot.say('Now following @{0.screen_name}.'.format(user))

    @twitter.command(
        aliases=['uf'],
        pass_context=True
    )
    async def unfollow(self, ctx, user):
        """
        Remove a user from the bot's follow list.
        Args:
            user: The user to unfollow.
        """
        user = self.api.get_user(user)

        try:
            echo = TwitterEcho.get(TwitterEcho.server == ctx.message.server.id, TwitterEcho.user_id == user.id)
        except TwitterEcho.DoesNotExist:
            await self.bot.say('Was not following @{0.screen_name}.'.format(user))
            return

        echo.delete_instance()
        self._update_stream_filter()

        await self.bot.say('Unfollowed @{0.screen_name}.'.format(user))

    @twitter.command(
        aliases=['l']
    )
    async def latest(self, user):
        """
        Get the latest tweet from a specified user.
        Args:
            user: The user to get. 
        """
        # TODO: Fix this
        user = self.api.get_user(user)
        # await self.bot.say(
        #     'Latest tweet from @{0.screen_name}:\n'
        #     'https://twitter.com/{0.screen_name}/status/{0.status.id_str}'
        #         .format(user))
        status = self.api.get_status(user.status.id)
        await self.echo_tweet(status)


def setup(bot):
    bot.add_cog(Twitter(bot))

def teardown(bot):
    # this is ghetto af.
    # TODO: make this not ghetto af
    del TwitterEcho.server.rel_model._meta.reverse_rel['{0}_set'.format(TwitterEcho.__name__)]