# 🎓 University Admissions Telegram Bot (Multilingual)

A Telegram bot built with **Python + aiogram 3** that helps users search university admission data in **English 🇬🇧, Russian 🇷🇺, and Uzbek 🇺🇿**.

---

## 📁 Project Structure

```
.
├── bot.py              # Main bot logic (multilingual)
├── universities.csv    # University data (includes full WIUT faculties)
├── requirements.txt    # Python dependencies
└── README.md
```

---

## ⚙️ Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get a Bot Token
- Message [@BotFather](https://t.me/BotFather) on Telegram
- Send `/newbot`, follow the prompts, copy your token

### 3. Set your token

**Option A – Environment variable (recommended):**
```bash
export BOT_TOKEN="123456:ABC-your-token-here"
python bot.py
```

**Option B – Edit `bot.py` directly:**
```python
BOT_TOKEN = "123456:ABC-your-token-here"
```

---

## ▶️ Run Locally

```bash
python bot.py
```

You'll see: `🤖 Bot is starting...`

---

## 🌐 Hosting (24/7 on a Server)

### Option A — Railway (Easiest, Free tier available)

1. Push your project to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add environment variable: `BOT_TOKEN` = your token
4. Done — Railway keeps it running 24/7

### Option B — Render (Free tier)

1. Push to GitHub
2. Go to [render.com](https://render.com) → New → Background Worker
3. Set **Build Command:** `pip install -r requirements.txt`
4. Set **Start Command:** `python bot.py`
5. Add env variable `BOT_TOKEN`
6. Deploy

### Option C — VPS (Ubuntu/Debian)

```bash
# Install Python & pip
sudo apt update && sudo apt install python3 python3-pip -y

# Clone/upload your project files
# Install dependencies
pip3 install -r requirements.txt

# Run with systemd (auto-restart on crash/reboot)
sudo nano /etc/systemd/system/unibot.service
```

Paste this into the file:
```ini
[Unit]
Description=University Admissions Telegram Bot
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/bot.py
Restart=always
Environment=BOT_TOKEN=123456:ABC-your-token-here
WorkingDirectory=/path/to/your/project

[Install]
WantedBy=multi-user.target
```

Then run:
```bash
sudo systemctl daemon-reload
sudo systemctl enable unibot
sudo systemctl start unibot
sudo systemctl status unibot  # check it's running
```

### Option D — Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]
```

```bash
docker build -t unibot .
docker run -d -e BOT_TOKEN="your-token" unibot
```

---

## 🤖 Bot Features

| Button (EN / RU / UZ) | Action |
|---|---|
| 🔍 Search by Field / Поиск по направлению / Yo'nalish bo'yicha | Pick a field → see all universities |
| 🏛 Search by University / Поиск по университету / Universitet bo'yicha | Pick a university → see all programs |
| 📋 All Universities / Все университеты / Barcha universitetlar | List all with program counts |
| ℹ️ Help / Помощь / Yordam | Usage guide |
| 🌐 Language / Язык / Til | Switch language at any time |

### Each result shows:
- 📊 **Quotas** for 2024 and 2025
- 🎯 **Min / Max** entrance scores
- 💰 **Annual tuition** (USD)
- 📅 **Application deadline**
- 📝 **Required documents**
- 🔗 **Direct application link**

---

## 🏛 WIUT Faculties in the Database

Westminster International University in Tashkent now includes all 10 programs:

| Faculty | Tuition/yr | IELTS |
|---|---|---|
| Business Administration | $4,200 | 5.5 |
| Finance | $4,200 | 5.5 |
| Accounting | $4,200 | 5.5 |
| Marketing | $4,200 | 5.5 |
| Economics | $4,200 | 5.5 |
| Computing | $4,500 | 5.5 + Math Test |
| Law | $4,500 | 6.0 + Interview |
| International Relations | $4,500 | 6.0 + Interview |
| Psychology | $4,500 | 5.5 + Interview |
| Media and Communications | $4,200 | 5.5 + Portfolio |

---

## 📊 Updating the CSV

Edit `universities.csv` to add or change data. Columns:

```
university, field, quota_2024, quota_2025, min_score, max_score,
tuition_usd, deadline, requirements, application_link
```

The bot reloads the CSV **on startup** — restart after editing.

---

## 🔧 Requirements

- Python 3.10+
- aiogram 3.7+
