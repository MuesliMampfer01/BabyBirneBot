import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import os
import math
import time

class Pointsystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "./data/points.db"
        self.xp_cooldowns = {}
        self.setup_db()

    def setup_db(self):
        os.makedirs("./data", exist_ok=True)
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

    # --- HILFSMETHODEN ---
    def calc_level(self, xp):
        if xp <= 0:
            return 1
        return int(math.sqrt(xp / 100)) + 1

    def xp_for_level(self, level: int) -> int:
        return ((level - 1) ** 2) * 100

    def calc_level_reward(self, level):
        return 100 + (level * 50)

    def get_user_data(self, user_id, serv_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT xp, points FROM serv_points 
                WHERE user_id = ? AND serv_id = ?
                """, (user_id, serv_id))
            res = cursor.fetchone()
            return res if res else (0, 0)

    def add_xp(self, user_id, serv_id, amount):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR IGNORE INTO serv_points (user_id, serv_id, points, xp)
                VALUES (?, ?, 0, 0)
                """, (user_id, serv_id))

            cursor.execute("""
                SELECT xp, points FROM serv_points WHERE user_id = ? AND serv_id = ?
                """, (user_id, serv_id))
            
            current_xp, points = cursor.fetchone()

            old_level = self.calc_level(current_xp)
            new_xp = current_xp + amount
            new_level = self.calc_level(new_xp)

            bonus = 0
            leveled_up = new_level > old_level

            if leveled_up:
                for lvl in range(old_level + 1, new_level + 1):
                    bonus += self.calc_level_reward(lvl)

            cursor.execute("""
                UPDATE serv_points
                SET xp = ?, points = points + ?
                WHERE user_id = ? AND serv_id = ?
                """, (new_xp, bonus, user_id, serv_id))

            conn.commit()

            return leveled_up, old_level, new_level, bonus

    # --- AUTOMATISCHE CHAT-XP ---
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        user_id = message.author.id
        serv_id = message.guild.id
        now = time.time()

        last_xp_time = self.xp_cooldowns.get((user_id, serv_id), 0)
        if now - last_xp_time < 60:
            return

        self.xp_cooldowns[(user_id, serv_id)] = now

        xp_gained = 20
        leveled_up, old_level, new_level, bonus = self.add_xp(user_id, serv_id, xp_gained)

        if leveled_up:
            embed = discord.Embed(
                title="🎉 LEVEL UP!",
                description=f"{message.author.mention} ist von **Level {old_level}** auf **Level {new_level}** aufgestiegen!",
                color=discord.Color.gold()
            )
            embed.add_field(name="💰 Belohnungs-Bonus", value=f"**+{bonus} Punkte** erhalten!")
            await message.channel.send(embed=embed)

    # --- SLASH COMMANDS ---
    @app_commands.command(name="points", description="Zeigt dein Level und deine Punkte an")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.guild_id or i.user.id)
    async def balance(self, interaction: discord.Interaction):
        xp, points = self.get_user_data(interaction.user.id, interaction.guild.id)
        level = self.calc_level(xp)
        next_level_xp = self.xp_for_level(level + 1)
        xp_needed = next_level_xp - xp

        embed = discord.Embed(title=f"📊 Profil von {interaction.user.display_name}", color=discord.Color.blue())
        embed.add_field(name="💰 Punkte", value=f"**{points:,}**", inline=True)
        embed.add_field(name="⭐ Level", value=f"**{level}**", inline=True)
        embed.add_field(name="✨ XP Gesamt", value=f"**{xp:,}** XP", inline=True)
        embed.add_field(name="🎯 Nächstes Level", value=f"Noch **{xp_needed:,}** XP", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="top", description="Zeigt die Bestenliste dieses Servers an")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.guild_id or i.user.id)
    async def leaderboard(self, interaction: discord.Interaction):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, points, xp FROM serv_points
                WHERE serv_id = ?
                ORDER BY points DESC LIMIT 10
                """, (interaction.guild.id,))

            top_users = cursor.fetchall()

        if not top_users:
            await interaction.response.send_message("Auf diesem Server hat noch niemand Punkte!", ephemeral=True)
            return

        embed = discord.Embed(title=f"🏆 Top 10 auf {interaction.guild.name} 🏆", color=discord.Color.gold())
        text = ""
        for i, (user_id, points, xp) in enumerate(top_users, start=1):
            member = interaction.guild.get_member(user_id)
            name = member.display_name if member else "Unbekannter User"
            level = self.calc_level(xp)

            medaille = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            text += f"{medaille} **{name}**: {points:,} Punkte *(Level {level})*\n"

        embed.description = text
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Pointsystem(bot))
