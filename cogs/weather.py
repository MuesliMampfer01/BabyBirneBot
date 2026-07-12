import aiohttp
import discord
from discord.ext import commands

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_url = "http://frogAPI:4444/weather"

    def get_weather_info(self, code):
        if code == 0:
            return "☀️", "Klarer Himmel"
        elif code in [1, 2, 3]:
            return "⛅", "Bewölkt"
        elif code in [45, 48]:
            return "🌫️", "Nebel"
        elif code in [51, 53, 55, 56, 57]:
            return "🌧️", "Nieselregen"
        elif code in [61, 63, 65, 66, 67, 80, 81, 82]:
            return "☔", "Regen"
        elif code in [71, 73, 75, 77, 85, 86]:
            return "❄️", "Schnee"
        elif code in [95, 96, 99]:
            return "⛈️", "Gewitter"
        return "🌡️", "Unbekannt"

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="weather", aliases=["w", "wetter"], help="Zeigt das aktuelle Wetter an: !weather <Ort>")
    # * = Name geht auch mit Leerzeichen
    async def weather(self, ctx, *, city: str):

        #Daten von FrogAPI abrufen
        try:
            async with aiohttp.ClientSession() as session:
                #Stadt wird als Parameter an die FrogAPI übergeben
                async with session.get(self.api_url, params={"city": city}) as resp:
                    if resp.status == 404:
                        await ctx.send(f"Konnte den Ort **{city}** auf der Landkarte nicht finden...")
                        return
                    elif resp.status != 200:
                        await ctx.send("FrogAPI gerade nicht erreichbar")
                        return

                    data = await resp.json()

        except Exception as e:
            await ctx.send(f"Verbindungsfehler: {e}")
            return

        #Wetter in Emojis übersetzen
        emoji, description = self.get_weather_info(data["weather_code"])
        temperature = data["temperature"]

        #dynamische Farbe je nach Temperatur
        embed_color = discord.Color.blue() if temperature < 15 else discord.Color.orange()

        #Embed aufbauen
        embed = discord.Embed(
            title=f"Wetter in {data['city']} {emoji}",
            description=f"**{description}**",
            color=embed_color
        )

        embed.add_field(name="Aktuell", value=f"{temperature} °C", inline=True)
        embed.add_field(name="Gefühlt", value=f"{data['feels_like']} °C", inline=True)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Weather(bot))