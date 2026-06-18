import aiohttp
import discord
from discord.ext import commands, tasks
from discord.ext.commands.parameters import empty


class Systemcheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_system_url = "http://frogAPI:4444/system/stats"

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.command(name="system", aliases=["sys"], help="Zeigt den aktuellen Ressourcenverbrauch des Servers an")
    async def system(self, ctx):
        try:
            async with aiohttp.ClientSession() as session:
               async with session.get(self.api_system_url) as resp:
                   if resp.status == 200:
                       data = await resp.json()
                   else:
                       await ctx.send("FrogAPI nicht erreichbar")
                       return
        except Exception as e:
            await ctx.send(f"Verbindungsfehler: {e}")
            return

        cpu_percent = data["cpu"]["usage_percent"]
        filled_blocks = int(cpu_percent / 10)
        empty_blocks = 10 - filled_blocks
        progress_bar = f"[{'█' * filled_blocks}{'░' * empty_blocks}] {cpu_percent}%"

        if cpu_percent > 80:
            embed_color = discord.Color.red()
        elif cpu_percent > 50:
            embed_color = discord.Color.gold()
        else:
            embed_color = discord.Color.green()

        embed = discord.Embed(
            title= "Server Status Dashboard",
            color = embed_color
        )

        embed.add_field(name="Uptime", value=data["uptime"], inline=False)

        embed.add_field(name="CPU Auslastung", value=progress_bar, inline=False)

        embed.add_field(name="RAM",
                        value=f"{data['ram']['used_gb']} GB / {data['ram']['total_gb']} GB ({data['ram']['usage_percent']}%)",
                        inline=False
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Systemcheck(bot))
