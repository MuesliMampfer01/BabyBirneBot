import discord
from discord.ext import commands

class Greet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(title= "Willkommen",
                              description=f"Welcome {member.mention}!",
                              colour=discord.Color.green()
        )

        channel = await self.bot.fetch_channel(1309645527302017146)
        await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Greet(bot))