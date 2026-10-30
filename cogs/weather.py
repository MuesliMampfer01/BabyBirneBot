import aiohttp
import discord
from discord.ext import commands
from discord import app_commands

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_url = "http://frogAPI:4444/weather"

    @app_commands.command(name="weather", description="Zeigt das aktuelle Wetter für einen Wunschort an")
    @app_commands.describe(city="Name der Stadt oder des Ortes")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.guild_id or i.user.id)
    async def weather(self, interaction: discord.Interaction, *, city: str):
        await interaction.response.defer()

        # Daten von FrogAPI abrufen
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url, params={"city": city}) as resp:
                    if resp.status == 404:
                        await interaction.followup.send(f"Der Ort **{city}** wurde nicht gefunden.")
                        return
                    elif resp.status != 200:
                        await interaction.followup.send("Die Wetter-API ist derzeit nicht erreichbar.")
                        return

                    data = await resp.json()

        except Exception as e:
            await interaction.followup.send(f"Verbindungsfehler zur API: {e}")
            return

        # Ort mit Land formatieren (falls von API geliefert)
        location_title = f"{data['city']}, {data['country']}" if data.get("country") else data["city"]

        # Schlichtes, dunkles Embed (passend zum Gesamtdesign des Bots)
        embed = discord.Embed(
            title=f"Wetter — {location_title}",
            description=f"**{data['condition']}**",
            color=discord.Color.dark_embed()
        )

        # Aufgegliederte Werte
        embed.add_field(
            name="Temperatur", 
            value=f"**{data['temperature']} °C**\n*(Min: {data['temp_min']} °C / Max: {data['temp_max']} °C)*", 
            inline=True
        )
        embed.add_field(name="Wind", value=f"{data['wind_speed']} km/h", inline=True)
        embed.add_field(name="Luftfeuchtigkeit", value=f"{data['humidity']} %", inline=True)

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Weather(bot))
