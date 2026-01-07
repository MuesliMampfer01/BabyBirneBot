import discord
from discord.ext import commands
import aiohttp
import os

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ollama_url = os.getenv("OLAMA_URL", "http://ollama:11434")

async def setup(bot):
    await bot.add_cog(AI(bot))