import discord
from discord.ext import commands
import aiohttp
import os
import time

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        self.history = {}
        self.MAX_HISTORY = 8
        self.system_prompt = (
            "Du bist 'BabyBirneBot', ein Discord-Bot. "
            "Verhalte dich gelassen und entspannt. "
            "Fasse dich eher kurz, passend für einen Chat. "
            "Erfinde KEINE Fakten und falls du keine Antwort kennst, sag lieber, dass du keine Antwort dazu hast"
        )

    @commands.command(name="resetbot", help="Löscht Gedächtnis vom Bot")
    async def resetbot(self, ctx):
        context_id = ctx.guild.id if ctx.guild else ctx.author.id

        if context_id in self.history:
            del self.history[context_id]
            await ctx.reply("Mein Gehirn ist jetzt leer...")
        else:
            await ctx.reply("Mein Gehirn ist schon leer...")

    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.command(name="chat", aliases=["ask"], help="Frage Ollama3.2 was mit !chat [Frage]")
    async def chat(self, ctx, *, frage):

        if not frage:
            await ctx.send("Bitte gebe eine Frage ein. Bsp: !chat [Frage]")
            return

        MAX_ZEICHEN = 300

        if len(frage) > MAX_ZEICHEN:
            await ctx.reply(f"Deine Nachricht ist zu lang_ Bitte maximal **{MAX_ZEICHEN} Zeichen** (Du hast {len(frage)} genutzt). ")
            return

        context_id = ctx.guild.id if ctx.guild else ctx.author.id

        if context_id not in self.history:
            self.history[context_id] = []

        self.history[context_id].append({"role": "user", "content": frage})

        start_zeit = time.time()

        async with ctx.typing():
            try:

                messages_payload = [{"role": "system", "content": self.system_prompt}] + self.history[context_id]

                payload = {
                    "model": "llama3.2",
                    "messages": messages_payload,
                    "stream": False,
                    "keep-alive": "2min",
                    "options": {
                        "temperature": 0.6,
                        "num_ctx": 2048,
                        "num_thread": 4
                    }
                }

                full_url = f"{self.ollama_url}/api/chat"

                async with aiohttp.ClientSession() as session:

                    timeout = aiohttp.ClientTimeout(total=60)

                    async with session.post(full_url, json=payload, timeout=timeout) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            msg_obj = data.get("message", {})
                            antwort = msg_obj.get("content", "")

                            dauer = round(time.time() - start_zeit, 1)

                            self.history[context_id].append({"role": "assistant", "content": antwort})

                            if len(self.history[context_id]) > self.MAX_HISTORY:
                                self.history[context_id] = self.history[context_id][-self.MAX_HISTORY:]

                            if len(antwort) > 1900:
                                antwort = antwort[:1900] + "...\n*(Antwort war zu lang und wurde gekürzt)*"

                            await ctx.reply(f"{antwort}\n\n *Generiert in {dauer}s*")

                        else:
                            await ctx.send(f"Ollama hat Schwierigkeiten. Status Code: {resp.status}")
                            self.history[context_id].pop()

            except Exception as e:
                await ctx.send(f"Verbindung verloren. Fehler {e}")
                if context_id in self.history and self.history[context_id]:
                    if self.history[context_id][-1]["role"] == "user":
                        self.history[context_id].pop()

async def setup(bot):
    await bot.add_cog(AI(bot))