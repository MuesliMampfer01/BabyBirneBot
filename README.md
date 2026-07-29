# 🤖 BabyBirneBot

> Ein kleiner Discord-Bot mit integrierter KI-Unterstützung (Ollama), modularem Cog-System und integrierten Spielen.

---

## ✨ Features

* **Intelligenter KI-Chat:** Nutzt eine kleine lokale LLM (`llama3.2`) für natürliche Unterhaltungen und Kontext-Gedächtnis.
* **Modulare Architektur:** Dank des `discord.py`-Cog-Systems können neue Funktionen einfach hinzugefügt oder entfernt werden.
* **Moderne Slash-Commands:** Voll integrierte Interaktionen (`/`) für eine saubere Benutzererfahrung in Discord.
* **Sicher & Lokal:** Läuft komplett selbstgehostet auf eigener Hardware (Raspberry Pi via Docker & Portainer).

---

## 🎮 Commands 

| Befehl | Beschreibung |
| --- | --- |
| `/chat [Frage]` | Stellt eine Frage an die lokale KI (mit Gedächtnis). |
| `/resetbot` | Löscht den aktuellen Chat-Verlauf/Gedächtnis des Bots. |
| *fehlende Dokumentation, weitere Befehle werden künftig eingetragen* |  |

---

## 🛠️ Tech-Stack

* **Sprache:** Python 3.10+
* **Bibliothek:** `discord.py`
* **KI-Backend:** Ollama (Llama 3.2)
* **Hosting:** Docker & Portainer auf Raspberry Pi Server 

---

## 📂 Projektstruktur

Das Projekt ist modular aufgebaut, um die Wartung zu erleichtern:

```text
BabyBirneBot/
│
├── cogs/
│   └── (<feature>).py  # eigene .py für jedes Feature oder geclustert für mehrere Features
│
├── main.py             # Hauptdatei zum Starten des Bots und Laden der Cogs
└── docker-compose.yml  # Docker-Konfiguration für Bot und Ollama

```
---

## 🚀 Installation & Setup

### 1. Repository klonen

```bash
git clone [https://github.com/MuesliMampfer01/BabyBirneBot.git](https://github.com/MuesliMampfer01/BabyBirneBot.git)
cd BabyBirneBot

```

### 2. `.env`-Datei erstellen

Erstelle im Hauptverzeichnis eine `.env`-Datei mit folgenden Inhalten:

```env
TOKEN=dein_discord_bot_token_hier
OLLAMA_URL=http://localhost:11434
CHANNELS=123456789012345678  # Optional: Erlaubte Kanal-IDs

```

### 3. Starten mit Docker 

Starte den Bot und das KI-Backend bequem über Docker Compose:

```bash
docker compose up -d --build

```

---

## 🧩 Neue Features hinzufügen 

Um den Bot zu erweitern, musst du eine neue **Cog** im Ordner `cogs/` anlegen.

1. Erstelle eine neue Datei, z. B. `cogs/fun.py`.
2. Nutze folgendes Grundgerüst:

```python
import discord
from discord import app_commands
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hallo", description="Sagt Hallo zu dir!")
    async def hallo(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Hallo {interaction.user.mention}! 👋")

async def setup(bot):
    await bot.add_cog(Fun(bot))

```

3. Starte den Bot neu (oder synce die Commands) – das Modul wird automatisch über den `setup_hook` geladen.

