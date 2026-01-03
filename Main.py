import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MeinBot(commands.Bot):
    async def setup_hook(self):
        if os.path.exists("./cogs"):
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py"):
                    try:
                        await self.load_extension(f"cogs.{filename[:-3]}")
                        print(f"Cog geladen: {filename}")
                    except Exception as e:
                        print(f"Fehler beim Laden von {filename}: {e}")
        else:
            print("Kein 'cogs' Ordner gefunden!")

bot = MeinBot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f" {bot.user} ist online und bereit!")

# Starten
if __name__ == '__main__':
    # Wir nehmen "DISCORD_TOKEN", weil wir das so in Portainer eingestellt haben
    token = os.getenv("TOKEN")

    if token:
        bot.run(token)
    else:
        print("Fehler: Kein Token gefunden!")