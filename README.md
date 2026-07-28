# 🤖 BabyBirneBot

> Ein kleiner Discord-Bot mit integrierter KI-Unterstützung (Ollama), modularem Cog-System und integrierten Spielen.

---

## ✨ Features

* **Intelligenter KI-Chat:** Nutzt eine kleine lokale LLM (`llama3.2`) für natürliche Unterhaltungen und Kontext-Gedächtnis.
* **Modulare Architektur:** Dank des `discord.py`-Cog-Systems können neue Funktionen einfach hinzugefügt oder entfernt werden.
* **Moderne Slash-Commands:** Voll integrierte Interaktionen (`/`) für eine saubere Benutzererfahrung in Discord.
* **Sicher & Lokal:** Läuft komplett selbstgehostet auf eigener Hardware (Raspberry Pi via Docker & Portainer).

---

## 🛠️ Tech-Stack

* **Sprache:** Python 3.10+
* **Bibliothek:** `discord.py`
* **KI-Backend:** Ollama (Llama 3.2)
* **Hosting:** Docker & Portainer (GitOps / CI/CD)

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
