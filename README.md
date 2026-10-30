# BabyBirneBot

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2.svg?logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_AI-black.svg?logo=ollama&logoColor=white)](https://ollama.com/)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)

> Ein schlanker, modularer Discord-Bot mit integrierter KI-Unterstützung (Ollama), lokalem Punkte- & Levelsystem und Minispielen – optimiert für das Self-Hosting auf einem Raspberry Pi.

---

## Features

- **Lokale KI-Integration:** Nutzt Ollama (z. B. Qwen 2.5) für flüssigen Chat mit Kontext-Gedächtnis – direkt berechnet auf dem eigenen Server ohne externe API-Kosten.
- **Exponentielles Levelsystem:** Punkte und XP werden pro Chat-Nachricht und Minispiel-Sieg vergeben. Höhere Level erfordern exponentiell mehr Erfahrungspunkte.
- **Server-Economy:** Inkrementelles Währungssystem auf Basis einer lokalen, performanten SQLite-Datenbank.
- **Interaktive Spiele:** Klassiker wie Blackjack mit Discord-UI-Buttons und Zahlenraten als Slash-Commands.
- **Moderne Slash-Commands:** Vollständige Einbindung von `discord.app_commands` für eine reibungslose User-Experience.
- **Docker-Ready:** Vollständig containerisiert für einfachen Betrieb via Docker Compose und Portainer auf dem Raspberry Pi.

---

## Commands

### KI & Unterhaltung
| Befehl | Beschreibung |
| :--- | :--- |
| `/chat [frage]` | Sendet eine Anfrage an das lokale KI-Modell |
| `/resetbot` | Löscht den aktuellen Chat-Verlauf und setzt den Kontext der KI zurück |

### Level & Economy
| Befehl | Beschreibung |
| :--- | :--- |
| `/points` | Zeigt dein aktuelles Level, gesammelte XP, Punkte und Fortschritt an |
| `/top` | Zeigt die Top 10 Highscore-Liste des Servers (sortiert nach Level) |

### Minispiele
| Befehl | Beschreibung |
| :--- | :--- |
| `/blackjack [bet]` | Starte eine Runde Blackjack mit interaktiven Buttons für Einsatz-Punkte |
| `/zahlenraten` | Starte das Zahlenraten-Minispiel |
| `/coinflip [seite]` | Wirf eine Münze und setze auf Kopf oder Zahl |

### Utilities & Tools
| Befehl | Beschreibung |
| :--- | :--- |
| `/qrcode [url]` | Erstellt automatisch einen scannbaren QR-Code aus einem Link |
| `/weather [ort]` | Fragt die aktuelle Wettervorhersage für einen Ort ab |

---

## Tech-Stack

- **Sprache:** Python 3.10+
- **Framework:** `discord.py` (v2.x)
- **KI-Backend:** [Ollama](https://ollama.com/) 
- **Datenbank:** SQLite (`data/points.db`)
- **Deployment:** Docker & Docker Compose (Host: Raspberry Pi OS / Portainer)

---

## Projektstruktur

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

## Installation & Setup

### 1. Repository klonen

```bash
git clone https://github.com/MuesliMampfer01/BabyBirneBot.git
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

## Neue Features hinzufügen 

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
        await interaction.response.send_message(f"Hallo {interaction.user.mention}!")

async def setup(bot):
    await bot.add_cog(Fun(bot))

```

3. Starte den Bot neu (oder synce die Commands) – das Modul wird automatisch über den `setup_hook` geladen.

