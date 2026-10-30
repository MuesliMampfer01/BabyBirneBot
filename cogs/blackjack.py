import discord 
from discord import app_commands
from discord.ext import commands
import random
import asyncio

class BlackjackView(discord.ui.View):
    def __init__(self, cog, interaction: discord.Interaction, bet: int, deck, player_hand, dealer_hand):
        super().__init__(timeout=30.0)
        self.cog = cog
        self.interaction = interaction
        self.bet = bet
        self.deck = deck
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
        self.value = None


    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.interaction.user.id:
            await interaction.response.send_message("Das ist nicht dein Spiel!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player_hand.append(self.deck.pop())
        player_value = self.cog.calc_hand(self.player_hand)

        if player_value >= 21:
            self.value = "busted" if player_value > 21 else "stand"
            self.stop()
            await interaction.response.defer()
        else:
            embed = discord.Embed(title="Blackjack", color=discord.Color.dark_embed())
            embed.add_field(name="Deine Hand", value=f"{self.cog.format_hand(self.player_hand)} `({player_value})`", inline=False)
            embed.add_field(name="Dealer Hand", value=f"{self.dealer_hand[0][1]}{self.dealer_hand[0][0]}, [Verdeckt]", inline=False)
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.secondary)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = "stand"
        self.stop()
        await interaction.response.defer()

    async def on_timeout(self):
        self.value = "timeout"
        self.stop()

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

        while value > 21 and aces > 0:
            value -= 10
            aces -= 1

        return value

    def format_hand(self, hand):
        return ", ".join([f"{color}{card}" for card, color in hand])

    async def give_reward(self, interaction: discord.Interaction, amount: int):
        points_cog = self.bot.get_cog('Pointsystem')
        if points_cog:
            points_cog.add_points(interaction.user.id, interaction.guild_id, amount)
            return True
        else:
            print("Pointsystem konnte nicht geladen werden, keine Punkte vergeben")
            return False


    @app_commands.command(name="blackjack", description="Spiele eine Runde Blackjack um Punkte")
    @app_commands.describe(bet="Dein Einsatz")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.guild_id or i.user.id)
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        points_cog = self.bot.get_cog('Pointsystem')

        if not points_cog:
            await interaction.response.send_message("Punktesystem nicht geladen.", ephemeral=True)
            return

        if bet <= 0:
            await interaction.response.send_message("Bitte setze mindestens 1 Punkt.", ephemeral=True)
            return

        user_id = interaction.user.id
        serv_id = interaction.guild_id
        xp, account = points_cog.get_user_data(user_id, serv_id)

        if account < bet:
            await interaction.response.send_message(f"Nicht genug Punkte! Dein Kontostand: **{account:,}**", ephemeral=True)
            return

        deck = self.create_deck()
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]

        player_value = self.calc_hand(player_hand)
        view = BlackjackView(self, interaction, bet, deck, player_hand, dealer_hand)

        embed = discord.Embed(title="Blackjack", color=discord.Color.dark_embed())
        embed.add_field(name="Deine Hand", value=f"{self.format_hand(player_hand)} `({player_value})`", inline=False)
        embed.add_field(name="Dealer Hand", value=f"{dealer_hand[0][1]}{dealer_hand[0][0]}, [Verdeckt]", inline=False)

        await interaction.response.send_message(embed=embed, view=view)
        await view.wait()

        for child in view.children:
            child.disabled = True

        player_value = self.calc_hand(player_hand)

        if player_value > 21:
            embed_bust = discord.Embed(
                title="Blackjack — Überkauft",
                description=f"Du hast dich überkauft und verlierst **{bet:,}** Punkte.",
                color=discord.Color.dark_embed()
            )
            embed_bust.add_field(name="Deine Hand", value=f"{self.format_hand(player_hand)} `({player_value})`", inline=False)
            points_cog.add_points(user_id, serv_id, -bet)
            await interaction.edit_original_response(embed=embed_bust, view=view)
            return

        dealer_value = self.calc_hand(dealer_hand)
        while dealer_value < 17:
            dealer_hand.append(deck.pop())
            dealer_value = self.calc_hand(dealer_hand)

        embed_end = discord.Embed(title="Blackjack — Ergebnis", color=discord.Color.dark_embed())
        embed_end.add_field(name="Deine Hand", value=f"{self.format_hand(player_hand)} `({player_value})`", inline=True)
        embed_end.add_field(name="Dealer Hand", value=f"{self.format_hand(dealer_hand)} `({dealer_value})`", inline=True)

        if dealer_value > 21:
            embed_end.description = f"Dealer überkauft! Du gewinnst **{bet:,}** Punkte."
            points_cog.add_points(user_id, serv_id, bet)
        elif dealer_value > player_value:
            embed_end.description = f"Dealer gewinnt. Du verlierst **{bet:,}** Punkte."
            points_cog.add_points(user_id, serv_id, -bet)
        elif dealer_value < player_value:
            embed_end.description = f"Du gewinnst **{bet:,}** Punkte!"
            points_cog.add_points(user_id, serv_id, bet)
        else:
            embed_end.description = "Unentschieden (Push). Du behältst deinen Einsatz."

        await interaction.edit_original_response(embed=embed_end, view=view)


async def setup(bot):
    await bot.add_cog(Blackjack(bot))
            