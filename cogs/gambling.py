import discord
from discord.ext import commands
from numpy import random


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def coinflip(self):
        return random.choice(['Heads', 'Tails'])

def setup(bot):
    bot.add_cog(Gambling(bot))