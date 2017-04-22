import sys

import random
from discord.ext import commands
from discord.ext.commands import Bot, Context


class RNG:
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(
        aliases=['dice', 'random', 'rng', 'rand'],
        description='Roll the dice.',
        pass_context=True
    )
    async def roll(self, ctx: Context, num1: float = None, num2: float = None):

        if num1 is not None and num2 is None:
            num2 = num1
            num1 = 1
        elif num1 is None and num2 is None:
            num1 = num1 or 1
            num2 = num2 or 6

        await self.bot.say('{0} rolls {1} ({2} - {3}).'.format(
            ctx.message.author.mention,
            random.randint(num1, num2),
            num1, num2))

    @commands.command(
        aliases=['decide'],
        description='Decide between two or more choices.'
    )
    async def choose(self, choice1, choice2, *other_choices):
        choices = [choice1, choice2, *other_choices]

        decision = random.choice(choices)

        await self.bot.say('The decision is: `{0}`.'.format(decision))

    @commands.command(
        description='Flip a coin.',
    )
    async def flip(self):
        result = random.choice(('heads', 'tails'))

        await self.bot.say('Flipped a coin. It landed `{0}`.'.format(result))

    @commands.command(
        description='Shuffle a list.'
    )
    async def shuffle(self, item1, item2, *other_items):
        items = [item1, item2, *other_items]

        random.shuffle(items)

        response = ', '.join(items)

        await self.bot.say('The shuffled list:\n{0}'.format(response))


def setup(bot):
    bot.add_cog(RNG(bot))
