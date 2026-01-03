import discord
from discord.ext import commands
import random


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coinflip",aliases=["cf", "münze"], help="mache einen Coinflip")
    async def coinflip(self,ctx):
        seiten =["Kopf", "Zahl"]
        ergebnis = random.choice(seiten)
        await ctx.send(f"{ctx.author.mention} hat eine Münze geworfen... \nDas Ergebnis ist {ergebnis}")

async def setup(bot):
    await bot.add_cog(Gambling(bot))