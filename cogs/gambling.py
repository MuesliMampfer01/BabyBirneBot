import asyncio
import discord
from discord.ext import commands
import random
import aiohttp


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def give_reward(self, ctx, amount):
        punktesys = self.bot.get_cog('Punktesystem')

        if punktesys:
            punktesys.add_points(ctx.author.id, ctx.guild.id, amount)
            return True
        else:
            print("Punktesystem konnte nicht geladen werden, keine Punkte vergeben")
            return False


    @commands.command(name="coinflip",aliases=["cf", "münze"], help="mache einen Coinflip")
    async def coinflip(self,ctx, wahl: str):
        if not wahl:
            await ctx.send("Bitte wähle 'Kopf' oder 'Zahl'! Bsp: '!cf kopf'")
            return

        seiten = ["kopf", "zahl"]
        wahl = wahl.lower()
        if wahl not in seiten:
            await ctx.send("Es gibt nur 'kopf' oder 'Zahl'")
            return

        ergebnis = random.choice(seiten)

        msg = await ctx.send("Die Münze wurde geworfen...")
        await asyncio.sleep(1)

        if wahl == ergebnis:
            punkte = 10
            hat_punkte_bekommen = await self.give_reward(ctx, punkte)

            text = f"**{ergebnis.capitalize()}!** Du hast gewonnen!"
            if hat_punkte_bekommen:
                text += f"\n **+{punkte} Punkte** wurden dir gutgeschrieben"

            await msg.edit(content=text)
        else:
            await msg.edit(content=f"**{ergebnis.capitalize()}!** Schade, leider ist es die Falsche Zahl")


    @commands.command(name="zahlenraten",aliases=["zr", "raten"],help="Errate die gesuchte Zahl")
    async def zahlenraten(self, ctx, zahl: int = None):
        gesuchte_zahl = random.randint(1, 100)
        versuche = 5
        await ctx.send("**Willkommen beim Zahlenraten!**\nEs wird eine Zahl zwischen 1 und 100 gesucht.\nDu hast 5 Versuche um die geheime Zahl zu finden!")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        while True:
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=60.0)
                geratene_zahl = int(msg.content)

                if geratene_zahl == gesuchte_zahl:#
                    punkte = 50
                    hat_punkte_bekommen = await self.give_reward(ctx, punkte)

                    zusatz = ""
                    if hat_punkte_bekommen:
                        zusatz = f"\n **+{punkte} Punkte** wurden dir gutgeschrieben "
                    await ctx.send(f"Du hast die richtige Zahl gefunden!  Die gesuchte Zahl war {gesuchte_zahl}!{zusatz}")
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
        url = "https://meme-api.com/gimme/frogs"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()

                    img_url = data['url']
                    title = data['title']
                    post_link = data['postLink']

                    embed = discord.Embed(title=title,url=post_link,color=discord.Color.green())
                    embed.set_image(url=img_url)
                    embed.set_footer(text="von r/frogs")

                    await ctx.send(embed=embed)

                else:
                    await ctx.send("API FEHLER")

async def setup(bot):
    await bot.add_cog(Gambling(bot))