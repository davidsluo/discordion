import random
import sys
from collections import namedtuple

from discord.ext import commands
from discord.ext.commands import Bot, Context

from cogs.economy import User


class Casino:
    Token = namedtuple('Token', ['emoji', 'weight', 'multiplier'])

    cherries = Token('\N{CHERRIES}', 4, 1)
    bell = Token('\N{BELL}', 3.5, 5)
    bar = Token('\N{REGIONAL INDICATOR SYMBOL LETTER L}\N{REGIONAL INDICATOR SYMBOL LETTER V}', 3, 10)
    seven = Token('\N{DIGIT SEVEN}\N{COMBINING ENCLOSING KEYCAP}', 2.5, 50)

    reel = (
        Token('\N{GREEN APPLE}', 1, 0),
        Token('\N{RED APPLE}', 1, 0),
        Token('\N{PEAR}', 1, 0),
        Token('\N{TANGERINE}', 1, 0),
        Token('\N{LEMON}', 1, 0),
        Token('\N{BANANA}', 1, 0),
        Token('\N{WATERMELON}', 1, 0),
        Token('\N{MELON}', 1, 0),
        Token('\N{GRAPES}', 1, 0),
        Token('\N{STRAWBERRY}', 1, 0),
        Token('\N{PEACH}', 1, 0),
        Token('\N{PINEAPPLE}', 1, 0),
        Token('\N{TOMATO}', 1, 0),
        Token('\N{HOT PEPPER}', 1, 0),
        Token('\N{EAR OF MAIZE}', 1, 0),
        cherries,
        bell,
        bar,
        seven
    )

    weights = tuple(r.weight for r in reel)

    reward_message = \
        '**{0}** bet **${1:,.2f}** and won **${2:,.2f}**.\n'
    reward_info = \
        '{0} x{1}: **${2:,.2f}**'
    lost_message = \
        '**{0}** bet **${1:,.2f}** and lost all of it.'

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(
        aliases=['slot'],
        pass_context=True
    )
    async def slots(self, ctx: Context, amount: float = 1):
        if amount <= 0:
            await self.bot.say('You must bet greater than $0.')
            return

        better, _ = User.get_or_create(user_id=ctx.message.author.id)

        if better.balance < amount:
            await self.bot.say('Insufficient funds.')
            return

        better.balance -= amount

        if sys.version_info >= (3, 6):
            reels = [
                random.choices(self.reel, weights=self.weights, k=3),
                random.choices(self.reel, weights=self.weights, k=3),
                random.choices(self.reel, weights=self.weights, k=3)
            ]
        else:
            reel = []
            for token in self.reel:
                for i in range(int(token.weight)):
                    reel.append(token)
            reels = [
                random.sample(reel, k=3),
                random.sample(reel, k=3),
                random.sample(reel, k=3)
            ]
        row = [reel[1] for reel in reels]

        counts = {}
        for token in row:
            if token.multiplier > 0:
                if token in counts:
                    counts[token] += 1
                else:
                    counts[token] = 1

        counts = {token: count for token, count in counts.items() if count >= 2 or token == self.cherries}

        total = sum([token.multiplier * amount * count for token, count in counts.items()])

        slots_message = \
            '__**   S   L   O   T   S   **__\n' \
            '|| {0[0][0][0]} {0[1][0][0]} {0[2][0][0]} ||\n' \
            '> {0[0][1][0]} {0[1][1][0]} {0[2][1][0]} <\n' \
            '|| {0[0][2][0]} {0[1][2][0]} {0[2][2][0]} ||\n\n'

        message = slots_message.format(reels)
        if total == 0:
            message += self.lost_message.format(ctx.message.author, amount)
        else:
            message += self.reward_message.format(ctx.message.author, amount, total)

            message += '\n'.join(
                [self.reward_info.format(token.emoji, count, token.multiplier * count * amount)
                 for token, count in counts.items()]
            )

        await self.bot.say(message)

        better.balance += total
        better.save()

        # @commands.command(
        #     aliases=['multislot'],
        #     pass_context=True
        # )
        # async def multislots(self, ctx: Context, amount: float = 1):
        #     if amount <= 0:
        #         await self.bot.say('You must bet greater than $0.')
        #         return
        #
        #     try:
        #         better, _ = User.get_or_create(user_id = ctx.message.author.id)
        #     except User.DoesNotExist:
        #         await self.bot.say('You do not have an account!')
        #         return
        #
        #     if better.balance < amount:
        #         await self.bot.say('Insufficient funds.')
        #         return
        #
        #     better.balance -= amount
        #
        #     reels = [
        #         random.choices(self.reel, weights=self.weights, k=3),
        #         random.choices(self.reel, weights=self.weights, k=3),
        #         random.choices(self.reel, weights=self.weights, k=3)
        #     ]
        #
        #     counts = []
        #     for reel in reels:
        #         count = {}
        #         for token in reel:
        #             if token.multiplier > 0:
        #                 if token in count:
        #                     count[token] += 1
        #                 else:
        #                     count[token] = 1
        #
        #     counts = [{token: c for token, c in count.items() if count >= 2 or token == self.cherries}
        #               for count in counts]
        #
        #     total = sum([sum([0.5 * token.multiplier * amount * c for token, c in count.items()]) for count in counts])
        #
        #     slots_message = \
        #         '__**   S   L   O   T   S   **__\n' \
        #         '> {0[0][0][0]} {0[1][0][0]} {0[2][0][0]} <\n' \
        #         '> {0[0][1][0]} {0[1][1][0]} {0[2][1][0]} <\n' \
        #         '> {0[0][2][0]} {0[1][2][0]} {0[2][2][0]} <\n\n'
        #
        #     message = slots_message.format(reels)
        #     if total == 0:
        #         message += self.lost_message.format(ctx.message.author, amount)
        #     else:
        #         message += self.reward_message.format(ctx.message.author, amount, total)
        #
        #         message += '\n'.join(
        #             [self.reward_info.format(token.emoji, count, 0.5 * token.multiplier * count * amount)
        #              for token, count in counts.items()]
        #         )
        #
        #     await self.bot.say(message)
        #
        #     better.balance += total
        #     better.save()


def setup(bot: Bot):
    if 'cogs.economy' not in bot.extensions:
        raise ImportError('Economy cog must be loaded first.')
    else:
        bot.add_cog(Casino(bot))
