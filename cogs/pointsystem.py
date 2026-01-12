import discord
from discord.ext import commands
import sqlite3
import os

class Pointsystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "./data/points.db"
        self.setup_db()

    def setup_db(self):
        os.makedirs("./data", exist_ok=True)
        #Telefonverbindung in Lagerhalle
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS serv_points (
                    user_id INTEGER,
                    serv_id INTEGER,
                    points INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, serv_id))
                    """)
            conn.commit()

    #Hilfsmethoden
    def add_points(self, user_id, serv_id, amount):
        #automatisch öffnen und schließen der Verbindung am Ende des Blocks
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            #neuer Eintrag falls nicht vorhanden
            cursor.execute("""
                INSERT OR IGNORE INTO serv_points (user_id, serv_id, points)
                VALUES (?, ?, 0)
                """, (user_id, serv_id))

            #hinzufügen neuer Punkte
            cursor.execute("""
                UPDATE serv_points
                SET points = points + ?
                WHERE user_id = ? AND serv_id = ?
                """, (amount, user_id, serv_id))

            conn.commit()

    def get_points(self, user_id, serv_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT points FROM serv_points 
                WHERE user_id = ? AND serv_id = ?
                """, (user_id, serv_id))

            res = cursor.fetchone()
            return res[0] if res else 0

    @commands.cooldown(1, 5)
    @commands.command(name="points", aliases=["punkte", "p"], help="Zeigt deinen Punktestand an")
    async def balance(self, ctx):
        points = self.get_points(ctx.author.id, ctx.guild.id)
        await ctx.reply(f"Du hast aktuell auf {ctx.guild.name} **{points}** Punkte")

    @commands.cooldown(1, 5)
    @commands.command(name="top", aliases=["leaderboard"], help="Zeigt die Bestenliste dieses Servers an")
    async def leaderboard(self, ctx):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, points FROM serv_points
                WHERE serv_id = ?
                ORDER BY points DESC LIMIT 10
                """, (ctx.guild.id,))

            top_users = cursor.fetchall()

        if not top_users:
            await ctx.send("Auf diesem Server hat noch niemand Punkte!")
            return

        embed  = discord.Embed(title=f"🏆 Top 10 auf {ctx.guild.name} 🏆", color=discord.Color.gold())
        text = ""
        for i, (user_id, points) in enumerate(top_users, start=1):
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else "Unbekannter User"

            medaille = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            text += f"{medaille} {name}: {points} Punkte\n"

        embed.description = text
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Pointsystem(bot))


