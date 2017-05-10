from typing import List

import discord
from discord import Member
from discord.ext import commands
from discord.ext.commands import Bot, Context, cooldown, BucketType
from peewee import CharField, DoubleField

from cogs.utils import checks
from cogs.utils.database import BaseModel, db
from cogs.utils.table import make_table


class User(BaseModel):
    user_id = CharField()
    balance = DoubleField(default=1000)
    # credit_debit = ForeignKeyField(CreditDebit, related_name='credit_debit')


# class CreditDebit(BaseModel):
#     timestamp = TimestampField()
#     creditor = ForeignKeyField(User, to_field='user_id', related_name='creditor')
#     debitor = ForeignKeyField(User, to_field='user_id', related_name='debitor')
#     owed = DoubleField(constraints=[Check('owed > 0')])
#     paid = DoubleField(constraints=[Check('0 <= paid <= owed')])
#     interest = DoubleField(constraints=[Check('interest >= 0')], default=0)
#
#     @property
#     def paid_off(self):
#         return self.owed == self.paid
#
#     def pay(self, amount):
#         if self.paid + amount > self.owed:
#             left_over = amount - (self.paid - self.owed)
#             self.paid = self.owed
#             self.save()
#             return left_over
#         else:
#             self.paid += amount
#             return 0


class Economy:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot.add_listener(self._create_accounts, 'on_server_join')
        self.bot.add_listener(self._create_account, 'on_member_join')

        User.create_table(fail_silently=True)

    async def _create_accounts(self, server: discord.Server):
        """Creates accounts for everyone on the server."""
        accounts = [{'user_id': member.id} for member in server.members]
        with db.atomic():
            for i in range(0, len(accounts), 100):
                User.insert_many(accounts[i:i + 100]).execute()

    async def _create_account(self, user: discord.User):
        with db.atomic():
            User.insert(user_id=user.id).execute()

    @commands.command(
        hidden=True,
        pass_context=True
    )
    @checks.is_owner()
    async def init_server(self, ctx: Context):
        await self._create_accounts(ctx.message.author.server)
        await self.bot.say('\N{OK HAND SIGN}')

    @commands.command(
        hidden=True
    )
    @checks.is_owner()
    async def init_user(self, user: discord.User):
        await self._create_account(user)
        await self.bot.say('\N{OK HAND SIGN}')

    @commands.command(
        pass_context=True
    )
    async def balance(self, ctx: Context):
        try:
            user = User.get(User.user_id == ctx.message.author.id)
        except User.DoesNotExist:
            # TODO: make sure ctx.message.author resolves to a string.
            await self.bot.say('Account not found for {0}.'.format(ctx.message.author))
            return

        await self.bot.say('Your balance is ${0:.2f}'.format(user.balance))

    @commands.command(
        aliases=['lb']
    )
    async def leaderboard(self, page=1):
        def from_user_id(user_ids: List[str]):
            for user_id in user_ids:
                for server in self.bot.servers:
                    for member in server.members:
                        if user_id == member.id:
                            yield member.name
                            break
                    else:
                        continue
                    break

        users = User.select().order_by(User.balance.desc()).paginate(page, 10)

        members = list(from_user_id([user.user_id for user in users]))
        balances = ['${0:.2f}'.format(user.balance) for user in users]

        leaderboard = make_table(members, balances)

        message = \
            'Leaderboard **Page {page}**:\n' \
            '```\n' \
            '{leaderboard}\n' \
            '```'
        await self.bot.say(message.format(leaderboard=leaderboard, page=page))

    @commands.command(
        pass_context=True,
        aliases=['pay', 'loan']
    )
    # async def give(self, ctx: Context, who: discord.User, amount: float, interest: float = 0):
    async def give(self, ctx: Context, who: discord.User, amount: float):
        if ctx.message.author.id == who.id:
            await self.bot.say('You cannot give yourself money!')
            return
        if amount <= 0:
            await self.bot.say('You must {0} greater than $0.'.format(ctx.invoked_with))
            return
        try:
            giver = User.get(User.user_id == ctx.message.author.id)
        except User.DoesNotExist:
            await self.bot.say('You do not have an account.')
            return

        try:
            recipient = User.get(User.user_id == who.id)
        except User.DoesNotExist:
            await self.bot.say('Recipient does not have an account.')
            return

        if giver.balance - amount < 0:
            await self.bot.say('Insufficient funds.')
            return

        giver.balance -= amount
        recipient.balance += amount

        giver.save()
        recipient.save()

        await self.bot.say('Transferred ${0:.2f} from **{1}** to **{2}**.'
                           .format(amount, ctx.message.author.nick, who.nick))

    @commands.command(
        pass_context=True
    )
    @cooldown(rate=1, per=60 * 60 * 12, type=BucketType.user)
    async def wage(self, ctx: Context):
        try:
            user = User.get(User.user_id == ctx.message.author.id)
        except User.DoesNotExist:
            await self.bot.say('You do not have an account.')
            return

        user.balance += 250
        user.save()

        await self.bot.say('Added $250 to **{0}**.'.format(ctx.message.author.nick))


def setup(bot):
    bot.add_cog(Economy(bot))


def teardown(bot):
    pass
