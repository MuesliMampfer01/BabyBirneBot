import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
import qrcode
from ipykernel import embed


class QRCodeGen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="qrcode", description="Generiert eine beliebige URL in einen QR-Code")
    @app_commands.describe(url="Gebe die URL ein")
    @app_commands.checks.cooldown(1, 20, key=lambda i : i.guild_id or i.user_id)
    async def qrcode(self, interaction: discord.Interaction, url: str):

        MAX_LENGTH = 300

        if len(url) > MAX_LENGTH:
            await interaction.response.send_message(f"Die angegebene URL ist zu lang! Bitte maximal **{MAX_LENGTH}** Zeichen nutzen.", ephemeral=True)
            return

        elif url.startswith("http://"):
            await interaction.response.send_message(f"**http://**-Links werden nicht angenommen! Bitte verwende **https://**")
            return

        elif url.startswith("https://"):
            try:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(url)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")

                qrcode_embed = discord.Embed(
                    title="QR-Code Generator",
                    description=f"Hier ist dein generierter QR-Code für:\n`{url}`",
                    color=discord.Color.random(),
                )
                qrcode_embed.set_image(url=img)
                await interaction.response.send_message(embed=qrcode_embed, ephemeral=True)

            except Exception as e:
                await interaction.followup.send(f"Es konnte kein QR Code generiert werden! Überprüfe die Richtigkeit deines Links und bitte verwende ausschließlich **https://**-Links")


