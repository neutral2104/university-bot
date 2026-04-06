# 🎓 University Admissions Telegram Bot

A clean Telegram bot built with **Python + aiogram 3** that helps users search university admission data from a CSV file.

---

## 📁 Project Structure

```
.
├── bot.py              # Main bot logic
├── universities.csv    # University data
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
- Open Telegram and message [@BotFather](https://t.me/BotFather)
- Send `/newbot`, follow the prompts
- Copy the token you receive

### 3. Set your token

**Option A – Environment variable (recommended):**
```bash
export BOT_TOKEN="123456:ABC-your-token-here"
python bot.py
```

**Option B – Edit directly in `bot.py`:**
```python
BOT_TOKEN = "123456:ABC-your-token-here"
```

---

## ▶️ Run

```bash
python bot.py
```

You'll see: `🤖 Bot is starting...`

---

## 🤖 Bot Features

| Button | Action |
|--------|--------|
| 🔍 Search by Field | Pick a field → see all universities offering it |
| 🏛 Search by University | Pick a university → see all its programs |
| 📋 All Universities | List all universities with program counts |
| ℹ️ Help | Usage guide |

### Each result shows:
- 📊 **Quotas** for 2024 and 2025
- 🎯 **Min / Max** entrance scores
- 💰 **Annual tuition** in USD
- 📅 **Application deadline**
- 📝 **Required documents**
- 🔗 **Direct application link**

---

## 📊 Updating the CSV

Edit `universities.csv` to add or change universities. The columns are:

```
university, field, quota_2024, quota_2025, min_score, max_score,
tuition_usd, deadline, requirements, application_link
```

The bot reloads the CSV **on startup** — just restart it after editing.

---

## 🔧 Requirements

- Python 3.10+
- aiogram 3.7+
