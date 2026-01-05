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

@bot.command(name="sync")
async def sync(ctx):
    await ctx.send("Synchronisiere...")
    await bot.tree.sync()
    await ctx.send("Fertig!")
# Starten
if __name__ == '__main__':
    token = os.getenv("TOKEN")
    channel_id = os.getenv("CHANNELS")

    ALLOWED_CHANNELS = []

    if channel_id:
        try:
            ALLOWED_CHANNELS = [int(id_str) for id_str in channel_id.split(",")]
            print(f"Erlaube Befehle in {len(ALLOWED_CHANNELS)} Kanälen.")
        except ValueError:
            print("Fehler bei ALLOWED_CHANNELS")
    else:
        print("Keine ALLOWED_CHANNELS gefunden")



    @bot.check
    async def global_channel_check(ctx):
        if not ALLOWED_CHANNELS:
            return True
        return ctx.channel.id in ALLOWED_CHANNELS

    if token:
        bot.run(token)
    else:
        print("Fehler: Kein Token gefunden!")