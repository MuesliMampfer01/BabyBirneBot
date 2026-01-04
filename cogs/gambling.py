import asyncio

import discord
from discord.ext import commands
import random


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
                    await ctx.send("Du hast verloren! Du hast alle Versuche aufgebraucht!")
                    break

                if geratene_zahl > gesuchte_zahl:
                    await ctx.send(f"Meine Zahl ist niedriger! (Noch {versuche} Versuche)")
                else:
                    await ctx.send(f"Meine Zahl ist höher! (Noch {versuche} Versuche)")

            except ValueError:
                await ctx.send("Bitte gib eine echte Zahl ein!")

            except asyncio.TimeoutError:
                await ctx.send(f"Zu langsam! Die gesuchte Zahl war {gesuchte_zahl}")
                break

async def setup(bot):
    await bot.add_cog(Gambling(bot))