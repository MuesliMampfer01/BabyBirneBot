import asyncio
import discord
from discord.ext import commands
import random
import aiohttp


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coinflip",aliases=["cf", "münze"], help="mache einen Coinflip")
    async def coinflip(self,ctx):
        seiten =["Kopf", "Zahl"]
        ergebnis = random.choice(seiten)
        await ctx.send(f"{ctx.author.mention} hat eine Münze geworfen... \nDas Ergebnis ist {ergebnis}")

    @commands.command(name="zahlenraten",aliases=["zr", "raten"],help="errate die gesuchte Zahl")
    async def zahlenraten(self,ctx):
        gesuchte_zahl = random.randint(1, 100)
        versuche = 5
        await ctx.send("Willkommen beim Zahlenraten!\nEs wird eine Zahl zwischen 1 und 100 gesucht.\nDu hast 5 Versuche um die geheime Zahl zu finden!")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        while True:
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=60.0)
                geratene_zahl = int(msg.content)

                if geratene_zahl == gesuchte_zahl:
                    await ctx.send(f"Du hast die richtige Zahl gefunden!  Die gesuchte Zahl war {gesuchte_zahl}!")
                    break

                versuche -= 1

                if versuche == 0:
                    await ctx.send(f"Du hast verloren! Die gesuchte Zahl war {gesuchte_zahl}!")
                    break

                if geratene_zahl > gesuchte_zahl:
                    await ctx.send(f"Meine Zahl ist niedriger! (Noch {versuche} Versuch(e))")
                else:
                    await ctx.send(f"Meine Zahl ist höher! (Noch {versuche} Versuch(e))")

            except ValueError:
                await ctx.send("Bitte gib eine echte Zahl ein!")

            except asyncio.TimeoutError:
                await ctx.send(f"Zu langsam! Die gesuchte Zahl war {gesuchte_zahl}")
                break

    @commands.command(name="hirse",help="hirse")
    async def hirse(self,ctx):
        try:
            with open("pics/hirsebrei-suess.png", "rb") as f:
                pic = discord.File(f, filename="hirsebrei-suess.png")
                await ctx.send(file=pic)
        except FileNotFoundError:
            await ctx.send("Bild nicht gefunden")

    @commands.command(name="frosch",aliases=["frog", "quak"],help="Zeigt einen zufälligen Frosch")
    async def frosch(self,ctx):
        url = "https://some-random-api.com/animal/amphibian/frog"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()

                    img_url = data['image']
                    fact = data['fact']

                    embed = discord.Embed(title="Quak! 🐸",description=fact,color=discord.Color.green())
                    embed.set_image(url=img_url)

                    await ctx.send(embed=embed)

                else:
                    await ctx.send("API FEHLER")

async def setup(bot):
    await bot.add_cog(Gambling(bot))