import random
from discord.ext import commands
from discord.ext.commands import Bot, Context

from cogs.economy import User


class Casino:
    slot_reel = [
        '\N{GREEN APPLE}',
        '\N{RED APPLE}',
        '\N{PEAR}',
        '\N{TANGERINE}',
        '\N{LEMON}',
        '\N{BANANA}',
        '\N{WATERMELON}',
        '\N{MELON}',
        '\N{GRAPES}',
        '\N{STRAWBERRY}',
        '\N{PEACH}',
        '\N{PINEAPPLE}',
        '\N{TOMATO}',
        '\N{HOT PEPPER}',
        '\N{EAR OF MAIZE}',
        '\N{CHERRIES}',
        '\N{BELL}',
        '\N{REGIONAL INDICATOR SYMBOL LETTER L}\N{REGIONAL INDICATOR SYMBOL LETTER V}',
        '\N{DIGIT SEVEN}\N{COMBINING ENCLOSING KEYCAP}',
    ]

    weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 3.5, 3, 2.5]
    multipliers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 5, 10, 50]

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

        try:
            better = User.get(User.user_id == ctx.message.author.id)
        except User.DoesNotExist:
            await self.bot.say('You do not have an account!')
            return

        if better.balance < amount:
            await self.bot.say('Insufficient funds.')
            return

        better.balance -= amount

        reel_1 = random.choices(self.slot_reel, weights=self.weights, k=3)
        reel_2 = random.choices(self.slot_reel, weights=self.weights, k=3)
        reel_3 = random.choices(self.slot_reel, weights=self.weights, k=3)
        reel = [reel_1[1], reel_2[1], reel_3[1]]
        counts = [reel.count(emoji) for emoji in self.slot_reel]
        rewards = [amount * count * multiplier if count >= 2 or emoji == '\N{CHERRIES}' else 0
                   for count, multiplier, emoji in zip(counts, self.multipliers, self.slot_reel)]
        reward = sum(rewards)

        slots_message = \
            '__**     S  L  O  T  S     **__\n' \
            '|| {0[0]} {1[0]} {2[0]} ||\n' \
            '> {0[1]} {1[1]} {2[1]} <\n' \
            '|| {0[2]} {1[2]} {2[2]} ||\n\n'
        reward_message = \
            '**{0}** bet **${1:.2f}** and won **${2:.2f}**.\n'
        reward_info = \
            '{0} x{1}: **${2:.2f}**'
        lost_message = \
            '**{0}** bet **${1:.2f}** and lost all of it.'

        message = slots_message.format(reel_1, reel_2, reel_3)
        if reward == 0:
            message += lost_message.format(ctx.message.author, amount)
        else:
            message += reward_message.format(ctx.message.author, amount, reward)
            message += '\n'.join([reward_info.format(emoji, count, count * amount * multiplier)
                                  for emoji, count, multiplier in zip(self.slot_reel, counts, self.multipliers)
                                  if (emoji == '\N{CHERRIES}' and count >= 1) or count >= 2])
        await self.bot.say(message)

        better.balance += reward
        better.save()


def setup(bot: Bot):
    if 'cogs.economy' not in bot.extensions:
        raise ImportError('Economy cog must be loaded first.')
    else:
        bot.add_cog(Casino(bot))
