import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import random
import aiohttp
import io


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_url = "http://frogAPI:4444/randomfrog"

    #--------Punktevergabe---------
    async def give_reward(self, interaction: discord.Interaction, amount: int):
        pointsys = self.bot.get_cog('Pointsystem')

        if pointsys:
            pointsys.add_points(interaction.user.id, interaction.guild_id, amount)
            return True
        else:
            print("Pointsystem konnte nicht geladen werden, keine Punkte vergeben")
            return False

    #---------Coinflip---------
    @app_commands.command(name="coinflip", description="Spiele Coinflip!")
    @app_commands.describe(choice="Gebe 'Kopf' oder 'Zahl' ein")
    @app_commands.choices(choice=[
        Choice(name="Kopf", value="kopf"),
        Choice(name="Zahl", value="zahl")
    ])
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.guild_id or i.user_id)
    async def coinflip(self, interaction: discord.Interaction, choice: Choice[str]):

        await interaction.response.defer()

        user_choice = choice.value
        sides = ["kopf", "zahl"]

        result = random.choice(sides)

        msg = await interaction.followup.send("Die Münze wurde geworfen...")
        await asyncio.sleep(1)

        if user_choice == result:
            points = 10
            try:
                got_points = await self.give_reward(interaction, points)
            except AttributeError:
                got_points = False

            text = f"**{result.capitalize()}!** Du hast gewonnen!"
            if got_points:
                text += f"\n **+{points} Punkte** wurden dir gutgeschrieben"

            await msg.edit(content=text)
        else:
            await msg.edit(content=f"**{result.capitalize()}!** Schade, leider ist das die falsche Seite")

    # -------- Zahlenraten --------
    @app_commands.command(name="zahlenraten", description="Errate die gesuchte Zahl zwischen 1 und 100")
    @app_commands.checks.cooldown(1, 30.0, key=lambda i: i.guild_id or i.user.id)
    async def zahlenraten(self, interaction: discord.Interaction):
        to_be_found = random.randint(1, 100)
        tries = 5

        await interaction.response.send_message(
            "**Zahlenraten**\nEs wird eine Zahl zwischen 1 und 100 gesucht.\nDu hast 5 Versuche!"
        )

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        while True:
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=60.0)
                guessed = int(msg.content)

                if guessed == to_be_found:
                    points = 50
                    got_points = await self.give_reward(interaction, points)

                    extra = ""
                    if got_points:
                        extra = f"\n+{points:,} Punkte wurden dir gutgeschrieben."
                    
                    await interaction.channel.send(f"Richtig! Die gesuchte Zahl war **{to_be_found}**.{extra}")
                    break

                tries -= 1

                if tries == 0:
                    await interaction.channel.send(f"Verloren! Die gesuchte Zahl war **{to_be_found}**.")
                    break

                if guessed > to_be_found:
                    await interaction.channel.send(f"Meine Zahl ist niedriger. (Noch {tries} Versuch(e))")
                else:
                    await interaction.channel.send(f"Meine Zahl ist höher. (Noch {tries} Versuch(e))")

            except ValueError:
                await interaction.channel.send("Bitte gib eine gültige Zahl ein.")

            except asyncio.TimeoutError:
                await interaction.channel.send(f"Zeit abgelaufen! Die gesuchte Zahl war **{to_be_found}**.")
                break

    #--------Hirse--------
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.command(name="hirse",help="hirse")
    async def hirse(self,ctx):
        try:
            with open("pics/hirsebrei-suess.png", "rb") as f:
                pic = discord.File(f, filename="hirsebrei-suess.png")
                await ctx.send(file=pic)
        except FileNotFoundError:
            await ctx.send("Bild nicht gefunden")

    #---------Frosch--------
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.command(name="frosch",aliases=["frog", "quak"],help="Zeigt einen zufälligen Frosch")
    async def frosch(self,ctx):
        async with ctx.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.api_url) as resp:
                        if resp.status == 200:
                            data = await resp.read()

                            file_obj = io.BytesIO(data)
                            file = discord.File(file_obj, filename="frosch.jpg")

                            await ctx.reply("Quak! 🐸", file=file)
                        else:
                            await ctx.send("API FEHLER")
            except Exception as e:
                await ctx.reply(f"Fehler bei der Frosch-Suche: {e}")

async def setup(bot):
    await bot.add_cog(Gambling(bot))
