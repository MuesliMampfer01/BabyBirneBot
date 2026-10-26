import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import os
import time
import json

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        self.history = {}
        self.MAX_HISTORY = 6
        self.system_prompt = (
            "Du bist 'BabyBirneBot', ein Discord-Bot. "
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
    @app_commands.describe(question="Deine Frage an den Bot")
    @app_commands.checks.cooldown(1, 20.0, key=lambda i: i.guild_id or i.user.id)  # Korrekter Cooldown für Slash-Commands
    async def chat(self, interaction: discord.Interaction, question: str):

        MAX_TOKEN = 300

        if len(question) > MAX_TOKEN:
            await interaction.response.send_message(f"Deine Nachricht ist zu lang! Bitte maximal **{MAX_TOKEN} Zeichen** (Du hast {len(question)} genutzt).", ephemeral=True)
            return

        context_id = interaction.guild.id if interaction.guild else interaction.user.id

        if context_id not in self.history:
            self.history[context_id] = []

        self.history[context_id].append({"role": "user", "content": question})

        start_time = time.time()

        await interaction.response.defer()

        message = await interaction.followup.send("*BabyBirneBot denkt nach...*")

        try:
            messages_payload = [{"role": "system", "content": self.system_prompt}] + self.history[context_id]

            payload = {
                "model": self.model,
                "messages": messages_payload,
                "stream": True,
                "keep_alive": "2m",
                "options": {
                    "temperature": 0.5,
                    "num_ctx": 1024,
                    "num_thread": 3
                }
            }

            full_url = f"{self.ollama_url}/api/chat"

            async with aiohttp.ClientSession() as session:
                timeout = aiohttp.ClientTimeout(total=90)

                async with session.post(full_url, json=payload, timeout=timeout) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        await message.edit(content=f"❌ **Ollama Fehler (Status {resp.status}):**\n```{error_text}```")
                        if context_id in self.history and self.history[context_id]:
                            self.history[context_id].pop()
                        return

                    full_resp = ""
                    last_update_time = time.time()

                    async for line in resp.content:
                        if not line:
                            continue

                        data = json.loads(line.decode('utf-8'))
                        chunk = data.get("message", {}).get("content", "")
                        full_resp += chunk

                        current_time = time.time()
                        if current_time - last_update_time > 0.9 and full_resp.strip():
                            display_text = full_resp
                            if len(display_text) > 1800:
                                display_text = display_text[:1800] + "..."

                            await message.edit(content=f"{display_text} ✍️")
                            last_update_time = current_time

                        if data.get("done", False):
                            break

                    duration = round(time.time() - start_time, 1)

                    self.history[context_id].append({"role": "assistant", "content": full_resp})

                    if len(self.history[context_id]) > self.MAX_HISTORY:
                        self.history[context_id] = self.history[context_id][-self.MAX_HISTORY:]

                    if len(full_resp) > 1900:
                        full_resp = full_resp[:1900] + "...\n*(Antwort war zu lang und wurde gekürzt)*"

                    await message.edit(content=f"{full_resp}\n\n⚡ *Generiert in {duration}s")

        except Exception as e:
            await interaction.followup.send(f"Verbindung verloren. Fehler: {e}")
            if context_id in self.history and self.history[context_id]:
                if self.history[context_id][-1]["role"] == "user":
                    self.history[context_id].pop()

async def setup(bot):
    await bot.add_cog(AI(bot))
