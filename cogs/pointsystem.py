import discord
from discord.ext import commands
import sqlite3
import os
import math

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
                    xp INTEGER DEFAULT 0,
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
                INSERT OR IGNORE INTO serv_points (user_id, serv_id, points, xp)
                VALUES (?, ?, 0, 0)
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


    def calc_level(self, xp):
        if xp <= 0:
            return 1
        return int(math.sqrt(xp/100)) + 1

    def calc_level_reward(self, level):
        return 100 + (level * 50)

    def get_user_data(self, user_id, serv_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT xp, points FROM serv_points 
                WHERE user_id = ? AND serv_ID = ?
                """, (user_id, serv_id))
            res = cursor.fetchone()
            return res if res else (0, 0)

    def add_xp(self, user_id, serv_id, amount):
        with sqlite3.connect(self.db_path) as conn:
            cursor =  conn.cursor()
            #neuer Eintrag falls nicht vorhanden
            cursor.execute("""
                INSERT OR IGNORE INTO serv_points (user_id, serv_id, points, xp)
                VALUES (?, ?, 0, 0)
                """, (user_id, serv_id))

            cursor.execute("""
                SELECT xp, points FROM serv_points WHERE user_id = ? AND serv_id = ?
                """, (user_id, serv_id))
            points, current_xp = cursor.fetchone()

            old_level = self.calc_level(current_xp)
            new_xp = current_xp + amount
            new_level = self.calc_level(new_level)

            bonus = 0;
            leveled_up = new_level > old_level

            if leveled_up:
                for lvl in range(old_level + 1, new_level + 1):
                    bonus_points += self.calc_level_reward(lvl)

            

            #hinzufügen neuer Punkte
            cursor.execute("""
                UPDATE serv_points
                SET xp = ?, points = points + ?
                WHERE user_id = ? AND serv_id = ?
                """, (new_xp, bonus, user_id, serv_id))

            conn.commit()

            return leveled_up, old_level, new_level, bonus
        

    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command(name="points", aliases=["punkte", "p"], help="Zeigt deinen Punktestand an")
    async def balance(self, ctx):
        points = self.get_points(ctx.author.id, ctx.guild.id)
        await ctx.reply(f"Du hast aktuell auf {ctx.guild.name} **{points}** Punkte")

    @commands.cooldown(1, 5, commands.BucketType.guild)
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
