import re
from datetime import datetime

import discord
import praw
from discord.ext import commands
from discord.ext.commands import Bot, Converter, Context
from praw.models import Submission, Comment, Subreddit, Front, Redditor, ListingGenerator

__all__ = ['Reddit', 'RedditConverter']

r_client: praw.Reddit = None


class RedditConverter(Converter):
    prog = re.compile(r'\s*/?(u|r)/([\w_]+)\s*')

    async def convert(self):
        match = self.prog.search(self.argument)
        if match:
            if match.group(1) == 'r':
                return r_client.subreddit(match.group(2))
            elif match.group(1) == 'u':
                return r_client.redditor(match.group(2))

        return None


class Reddit:
    def __init__(self, bot: Bot):
        self.bot = bot
        config = bot.config['reddit']
        global r_client
        r_client = praw.Reddit(client_id=config['client_id'],
                               client_secret=config['client_secret'],
                               username=config['username'],
                               password=config['password'],
                               user_agent=config['user_agent'])
        self.reddit.read_only = True
        self._last_result = None
        self._last_embed = None

    async def send_posts(self, destination, *posts: Submission):
        pass

    async def send_detailed_post(self, destination, post: Submission):
        tmp = {
            'title': post.title,
            'color': discord.Color(0xff5700),
            'url': 'https://www.reddit.com{0}'.format(post.permalink),
            'description': post.selftext if post.selftext != '' else None,
            'timestamp': datetime.fromtimestamp(post.created),
        }

        embed = discord.Embed(**tmp)
        del tmp

        embed.set_footer(text=str(post.score))
        embed.set_thumbnail(url=post.thumbnail)
        embed.set_author(name='/u/{0.name}'.format(post.author),
                         url='https://www.reddit.com/u/{0.name}'.format(post.author))

        await self.bot.send_message(destination, embed=embed)

    async def send_comments(self, destination, *comments: Comment):
        pass

    async def send_detailed_comment(self, destination, comment: Comment):
        pass

    @commands.command(
        aliases='r',
        pass_context=True
    )
    async def reddit(self, ctx: Context, link: RedditConverter = None, sort='hot', time='day', count=3):
        """
        Pull stuff from reddit.
        Args:
            link:
                Optional.
                The user/subreddit to pull from.
                Valid options:
                    /u/<user>
                    u/<user>
                    /r/<subreddit>
                    r/<subreddit>
                Defaults to the default front page.
            sort:
                Optional.
                How to sort the results. Can use [a]bbreviation.
                Valid options:
                    [h]ot, [n]ew, [r]ising, [c]ontroversial, [t]op, [g]ilded
                Defaults to hot.
            time:
                Optional.
                Time period to pull from. Can use [a]bbreviation.
                Valid options:
                    [d]ay, [w]eek, [m]onth, [y]ear, [a]ll
                Defaults to day.
                Ignored for hot, new, rising, and gilded.
            Count:
                Optional.
                The number of posts/comments to pull.
                Defaults to 3.
        """
        await self.bot.type()

        if link is None:
            link = r_client.front
        if time not in ('day', 'week', 'month', 'year', 'all',
                        'd', 'w', 'm', 'y', 'a'):
            await self.bot.say('Invalid time: {0}.'.format(time), delete_after=30)
            return

        if link is not None:
            if sort == 'hot' or sort == 'h':
                result = link.hot()
            elif sort == 'new' or sort == 'n':
                result = link.new()
            elif sort == 'rising' or sort == 'r':
                result = link.rising()
            elif sort == 'controversial' or sort == 'c':
                result = link.controversial(time_filter=time)
            elif sort == 'top' or sort == 't':
                result = link.top(time_filter=time)
            elif sort == 'gilded' or sort == 'g':
                result = link.gilded()
            else:
                await self.bot.say('Invalid sort: {0}.'.format(sort), delete_after=30)
                return

            if isinstance(link, Subreddit):
                title = '/r/{0}'.format(link.display_name)
                url = 'https://www.reddit.com/r/{0}'.format(link.display_name)
            elif isinstance(link, Redditor):
                title = '/u/'.format(link.name)
                url = 'https://www.reddit.com/u/{0}'.format(link.name)
            else:
                raise ValueError

            tmp = {
                'title': title,
                'color': discord.Color(0xff5700),
                'url': url,
                'description': '{0} posts from the past {1} from {2}'.format(sort, time, title)
            }

            embed = discord.Embed(**tmp)
            del tmp

            for _, sub in zip(range(count), result):
                if isinstance(sub, Submission):
                    value = '{0.shortlink}'.format(sub)
                    if sub.selftext != '':
                        value += '\n{0.selftext}'.format(sub)
                    else:
                        value += '\n{0.url}'.format(sub)
                    embed.add_field(name=sub.title, value=value)
                elif isinstance(sub, Comment):
                    value = '{0.submission.shortlink}\n{0.body}'.format(sub)
                    embed.add_field(name=sub.submission.title, value=value)

            await self.bot.say(embed=embed)

            self._last_result = result
            self._last_embed = embed
        else:
            await self.bot.say('Something terribly wrong has happened.')

    @commands.command()
    async def next(self, count=3):
        """
        Get the next three posts/comments from the last query.
        Args:
            count:
                Optional.
                The number of posts/comments to pull.
                Defaults to 3.
        """
        if self._last_result is None:
            await self.bot.say('No previous query.', delete_after=30)
            return
        else:
            result = self._last_result
            embed = self._last_embed
            for i, sub in zip(range(count), result):
                if isinstance(sub, Submission):
                    value = '{0.shortlink}'.format(sub)
                    if sub.selftext != '':
                        value += '\n{0.selftext}'.format(sub)
                    else:
                        value += '\n{0.url}'.format(sub)
                    embed.set_field_at(i, name=sub.title, value=value)
                elif isinstance(sub, Comment):
                    value = '{0.submission.shortlink}\n{0.body}'.format(sub)
                    embed.set_field_at(i, name=sub.submission.title, value=value)

            await self.bot.say(embed=embed)


def setup(bot):
    bot.add_cog(Reddit(bot))
