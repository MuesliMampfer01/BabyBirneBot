import discord
from discord import app_commands
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

    @app_commands.command(name="resetbot", description="Löscht das Gedächtnis vom Bot")
    async def resetbot(self, interaction: discord.Interaction):
        context_id = interaction.guild.id if interaction.guild else interaction.user.id

        if context_id in self.history:
            del self.history[context_id]
            await interaction.response.send_message("Mein Gehirn ist jetzt leer...", ephemeral=True)
        else:
            await interaction.response.send_message("Mein Gehirn ist schon leer...", ephemeral=True)

    @app_commands.command(name="chat", description="Frage Ollama3.2 etwas über einen Slash-Befehl")
    @app_commands.describe(frage="Deine Frage an den Bot")
    @app_commands.checks.cooldown(1, 20.0, key=lambda i: i.guild_id or i.user.id)  # Korrekter Cooldown für Slash-Commands
    async def chat(self, interaction: discord.Interaction, frage: str):

        MAX_ZEICHEN = 300

        if len(frage) > MAX_ZEICHEN:
            await interaction.response.send_message(f"Deine Nachricht ist zu lang! Bitte maximal **{MAX_ZEICHEN} Zeichen** (Du hast {len(frage)} genutzt).", ephemeral=True)
            return

        context_id = interaction.guild.id if interaction.guild else interaction.user.id

        if context_id not in self.history:
            self.history[context_id] = []

        self.history[context_id].append({"role": "user", "content": frage})

        start_zeit = time.time()

        # Bot "denken" lassen, da lokale KI etwas dauert
        await interaction.response.defer()

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

                        await interaction.followup.send(f"{antwort}\n\n *Generiert in {dauer}s*")

                    else:
                        await interaction.followup.send(f"Ollama hat Schwierigkeiten. Status Code: {resp.status}")
                        self.history[context_id].pop()

        except Exception as e:
            await interaction.followup.send(f"Verbindung verloren. Fehler: {e}")
            if context_id in self.history and self.history[context_id]:
                if self.history[context_id][-1]["role"] == "user":
                    self.history[context_id].pop()

async def setup(bot):
    await bot.add_cog(AI(bot))