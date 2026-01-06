import discord
from discord.ext import commands, tasks
import random

class Spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_active  = False
        self.target_channel = None

        self.spam_loop.start()

    def cog_unload(self):
        self.spam_loop.cancel()

    async def sende_zufalls_nachricht(self, channel):
        try:
            messages = []
            async for message in channel.history(limit = 1000):
                if not message.author.bot and message.content:
                    messages.append(message)

            if messages:
                random_msg = random.choice(messages)
                await channel.send(random_msg.content)
            else:
                print(f"Keine Nachrichten in {channel.name} gefunden")

        except Exception as e:
            print(f"Fehler beim Senden: {e}")

    @commands.command(name="spam", help="Startet/Stoppt zufällige Nachrichten. !spam an / !spam aus")
    async def control_spam(self, ctx, aktion: str):
        if aktion is None:
            await ctx.send("an oder aus anhängen")

        if aktion.lower() == "an":
            self.is_active = True
            self.target_channel = ctx.channel
            await ctx.send("Ab jetzt jede stunde ne alte nachricht")

        elif aktion.lower() == "aus":
            self.is_active = False
            await ctx.send("Ab jetzt wieder aus")

        else:
            await ctx.send("'!spam an' oder '!spam aus'nutzen.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.bot.user in message.mentions:
            await self.sende_zufalls_nachricht(message.channel)

    @tasks.loop(hours=1)
    async def spam_loop(self):
        if not self.is_active or self.target_channel is None:
            return

        await self.sende_zufalls_nachricht(self.target_channel)

    @spam_loop.before_loop
    async def before_spam_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Spam(bot))