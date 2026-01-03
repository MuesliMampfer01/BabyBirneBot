import discord
import os
from dotenv import load_dotenv

intents  = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = discord.Bot(intents=intents, debug_guilds=[963883042810785822])

@bot.event
async def on_ready():
    print(f"{bot.user} ist online")

@bot.event
async def on_message(msg):
    if msg.author.bot:
        return
    await msg.channel.send("Ich bin die Babybirne")

@bot.event
async def on_message_delete(msg):
    await msg.channel.send(f"Eine Nachricht von {msg.author.name} wurde gelöscht: {msg.content}")


if __name__ == '__main__':
    for filename in os.listdir(".venv/cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")

    load_dotenv()
    bot.run(os.getenv("TOKEN"))