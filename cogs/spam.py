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

    @commands.command(name="spam", help="Startet/Stoppt zufällige Nachrichten. !spam an / !spam aus")
    async def control_spam(self, ctx, aktion: str):
        if aktion.lower() == "an":
            self.is_active = True
            self.target_channel = ctx.channel
            await ctx.send("Ab jetzt jede stunde ne alte nachricht")

        elif aktion.lower() == "aus":
            self.is_active = False
            await ctx.send("Ab jetzt wieder aus")

        else:
            await ctx.send("'!spam an' oder '!spam aus'nutzen.")

    @tasks.loop(hours=1)
    async def spam_loop(self):
        if not self.is_active or self.target_channel is None:
            return

        try:
            messages = []
            async for message in self.target_channel.history(limit=500):
                if not message.author.bot and message.content:
                    messages.append(message)

            if messages:
                random_msg = random.choice(messages)
                await self.target_channel.send(random_msg.content)

        except Exception as e:
            print(f"Fehler im Chaos-Modul: {e}")

    @spam_loop.before_loop
    async def before_spam_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Spam(bot))