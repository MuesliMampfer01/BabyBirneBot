import discord
from discord import app_commands
from discord.ext import commands
import qrcode
import io

class QRCodeGen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="qrcode", description="Generiert eine beliebige URL in einen QR-Code")
    @app_commands.describe(url="Gebe die URL ein")
    @app_commands.checks.cooldown(1, 20, key=lambda i : i.guild_id or i.user_id)
    async def qrcode(self, interaction: discord.Interaction, url: str):

        #Begrenzung Zeichenlänge
        MAX_LENGTH = 300

        #Format und Sicherheit Check
        if len(url) > MAX_LENGTH:
            await interaction.response.send_message(f"Die angegebene URL ist zu lang! Bitte maximal **{MAX_LENGTH}** Zeichen nutzen.", ephemeral=True)
            return

        elif url.startswith("http://"):
            await interaction.response.send_message(f"**http://**-Links werden nicht angenommen! Bitte verwende **https://**")
            return

        elif url.startswith("https://"):
            try:
                await interaction.response.defer()

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10, #Größe der Kästchen im Code
                    border=4, #Rand um den QR-Code
                )
                qr.add_data(url)
                qr.make(fit=True)

                #Generierung finales Bild
                img = qr.make_image(fill_color="black", back_color="white")

                #Zwischenspeicher
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)

                file = discord.File(buf, filename="qrcode.png")

                #Embed erstellen
                qrcode_embed = discord.Embed(
                    title="QR-Code Generator",
                    description=f"Hier ist der generierter QR-Code für:\n`{url}`\n*Angefragt von {interaction.user.mention}*",
                    color=discord.Color.random(),
                )
                qrcode_embed.set_image(url="attachment://qrcode.png")

                await interaction.followup.send(embed=qrcode_embed, file=file)

            except Exception as e:
                await interaction.followup.send(f"Es konnte kein QR Code generiert werden! Überprüfe die Richtigkeit deines Links und bitte verwende ausschließlich **https://**-Links")
                print(f"QR-Code Fehler: {e}")

        else:
            await interaction.response.send_message("**Ungültige Eingabe!** Bitte gib einen gültigen Link ein, der mit **https://** beginnt.")

#Setup
async def setup(bot):
    await bot.add_cog(QRCodeGen(bot))