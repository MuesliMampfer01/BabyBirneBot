import asyncio
import discord
from discord.ext import commands
import random
import aiohttp
import io


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_url = "http://frogAPI:4444/randomfrog"

    #---------Hilfsmethoden für Blackjack----------
    def create_deck(self):
        colors_list = ["♠️", "♥️", "♦️", "♣️"]
        values_list = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        deck = [(values, colors) for colors in colors_list for values in values_list]
        random.shuffle(deck)
        return deck

    def calc_hand(self, hand):
        value = 0
        aces = 0

        for card, color in hand:
            if card in ["J", "Q", "K"]:
                value += 10
            elif card == "A":
                aces += 1
                value += 11
            else:
                value += int(card)

        #Asse behandeln (wenn über 21, Ass = 1
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1

        return value

    def format_hand(self, hand):
        return ", ".join([f"{color}{card}" for card, color in hand])

    #--------Punktevergabe---------
    async def give_reward(self, ctx, amount):
        punktesys = self.bot.get_cog('Pointsystem')

        if punktesys:
            punktesys.add_points(ctx.author.id, ctx.guild.id, amount)
            return True
        else:
            print("Pointsystem konnte nicht geladen werden, keine Punkte vergeben")
            return False

    #---------Coinflip---------
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command(name="coinflip",aliases=["cf", "münze"], help="mache einen Coinflip")
    async def coinflip(self,ctx, wahl: str = None):
        if wahl is None:
            await ctx.send("Bitte wähle 'Kopf' oder 'Zahl'! Bsp: '!cf kopf'")
            return

        seiten = ["kopf", "zahl"]
        wahl = wahl.lower()

        if wahl not in seiten:
            await ctx.send("Es gibt nur 'kopf' oder 'zahl'")
            return

        ergebnis = random.choice(seiten)

        msg = await ctx.send("Die Münze wurde geworfen...")
        await asyncio.sleep(1)

        if wahl == ergebnis:
            punkte = 10
            try:
                hat_punkte_bekommen = await self.give_reward(ctx, punkte)
            except AttributeError:
                hat_punkte_bekommen = False

            text = f"**{ergebnis.capitalize()}!** Du hast gewonnen!"
            if hat_punkte_bekommen:
                text += f"\n **+{punkte} Punkte** wurden dir gutgeschrieben"

            await msg.edit(content=text)
        else:
            await msg.edit(content=f"**{ergebnis.capitalize()}!** Schade, leider ist das die falsche Seite")

    #---------Zahlenraten---------
    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.command(name="zahlenraten",aliases=["zr", "raten"],help="Errate die gesuchte Zahl")
    async def zahlenraten(self, ctx):
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

    #--------BlackJack--------
    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.command(name="blackjack", aliases=["bj"], help="Spiele eine Runde Blackjack!")
    async def blackjack(self, ctx, bet: int):
        points_cog = self.bot.get_cog('Pointsystem')

        if not points_cog:
            await ctx.send("Punktesystem nicht geladen")
            return

        if bet <= 0:
            await ctx.reply("Bitte setze mindestens 1 Punkt")
            return

        user_id = ctx.author.id
        serv_id = ctx.guild.id
        account = points_cog.get_points(user_id, serv_id)

        if account < bet:
            await ctx.reply(f"Du hast nicht genug Punkte! Dein Kontostand: **{account}**")
            return

        deck = self.create_deck()
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]

        playing = True

        while playing:
            player_value = self.calc_hand(player_hand)

            if player_value > 21:
                embed_bust = discord.Embed(title="💥 Bust! - Überkauft", color=discord.Color.red())
                embed_bust.add_field(name="Deine End-Hand",value=f"{self.format_hand(player_hand)} (**{player_value}**)", inline=False)
                embed_bust.description = f"Das war zu viel! Du verlierst deinen Einsatz von **{bet}** Punkten."

                await ctx.send(embed=embed_bust)

                points_cog.add_points(user_id, serv_id, -bet)
                return

            embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.blue())
            embed.add_field(name="Deine Hand", value=f"{self.format_hand(player_hand)} (**{player_value}**)", inline=False)
            embed.add_field(name="Dealer Hand", value=f"{dealer_hand[0][1]}{dealer_hand[0][0]}, 🎴 ?", inline=False)
            embed.set_footer(text="Schreibe 'hit' (ziehen) oder 'stand' (bleiben)")

            await ctx.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["hit", "stand", "h", "s"]

            try:
                antwort = await self.bot.wait_for("message", check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await ctx.send(f"Zeit abgelaufen! Du bleibst stehen")
                break

            if antwort.content.lower() in ["hit", "h"]:
                player_hand.append(deck.pop())
            else:
                break

        player_value = self.calc_hand(player_hand)
        dealer_value = self.calc_hand(dealer_hand)

        while dealer_value < 17:
            dealer_hand.append(deck.pop())
            dealer_value = self.calc_hand(dealer_hand)

        embed_end = discord.Embed(title="🃏 Blackjack - Ergebnis", color=discord.Color.gold())
        embed_end.add_field(name="Deine Hand", value=f"{self.format_hand(player_hand)} (**{player_value}**)", inline=True)
        embed_end.add_field(name="Dealer Hand", value=f"{self.format_hand(dealer_hand)} (**{dealer_value}**)", inline=True)

        if dealer_value > 21:
            embed_end.description = f"🎉 Dealer Bust! Du gewinnst **{bet}** Punkte!"
            embed_end.color = discord.Color.green()
            points_cog.add_points(user_id, serv_id, bet)

        elif dealer_value > player_value:
            embed_end.description = f"❌ Dealer gewinnt. Du verlierst **{bet}** Punkte!"
            embed_end.color = discord.Color.red()
            points_cog.add_points(user_id, serv_id, -bet)

        elif dealer_value < player_value:
            embed_end.description = f"🎉 Glückwunsch! Du gewinnst **{bet}** Punkte!"
            embed_end.color = discord.Color.green()
            points_cog.add_points(user_id, serv_id, bet)

        else:
            embed_end.description = "🤝 Unentschieden (Push). Du behältst deinen Einsatz."
            embed_end.color = discord.Color.light_gray()

        await ctx.send(embed=embed_end)

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