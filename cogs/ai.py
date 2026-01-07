from asyncio import timeout
import discord
from discord.ext import commands
import aiohttp
import os

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")

    @commands.command(name="chat", aliases=["ask"], help="Frage Ollama3.2 was mit !chat [Frage]")
    async def chat(self, ctx, *, frage: str = None):
        if not frage:
            await ctx.send("Bitte gebe eine Frage ein. Bsp: !chat [Frage]")
            return

        async with ctx.typing():
            try:

                payload = {
                    "model": "llama3.2",
                    "prompt": frage,
                    "stream": False
                }

                full_url = f"{self.ollama_url}/api/generate"

                async with aiohttp.ClientSession() as session:

                    timeout = aiohttp.ClientTimeout(total=120)

                    async with session.post(full_url, json=payload, timeout=timeout) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            antwort = data.get("response", "")

                            if len(antwort) > 1900:
                                antwort = antwort[:1900] + "...\n*(Antwort war zu lang und wurde gekürzt)*"

                            await ctx.reply(antwort)

                        else:
                            await ctx.send(f"Ollama hat Schwierigkeiten. Status Code: {resp.status}")

            except Exception as e:
                await ctx.send(f"Verbindung verloren. Fehler {e}")

async def setup(bot):
    await bot.add_cog(AI(bot))