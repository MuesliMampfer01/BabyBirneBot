import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class Bot(commands.Bot):
    async def setup_hook(self):
        # 1. Cogs laden (dein Code)
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

        #slash-commands hinzufügen
        try:
            synced = await self.tree.sync()
            print(f"{len(synced)} Slash-Commands erfolgreich synchronisiert.")
        except Exception as e:
            print(f"Fehler beim Syncen der Commands: {e}")

bot = Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f" {bot.user} ist online und bereit!")

@bot.command(name="sync")
async def sync(ctx):
    await ctx.send("Synchronisiere...")
    await bot.tree.sync()
    await ctx.send("Fertig!")

@bot.command()
async def module(ctx):
    # Zeigt alle geladenen Cogs an
    extensions = list(bot.extensions.keys())
    if not extensions:
        await ctx.send("❌ Keine Cogs geladen!")
    else:
        await ctx.send(f"✅ Geladene Module: {', '.join(extensions)}")

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