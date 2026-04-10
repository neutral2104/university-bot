import asyncio
import csv
from pathlib import Path
from openai import OpenAI
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

# ── Config ────────────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "8666414561:AAG52ftogficyXMVGNGzHPE5YQn65KlUZkY")
CSV_FILE = Path(__file__).parent / "universities.csv"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# ── Data loading ──────────────────────────────────────────────────────────────

def load_data() -> list[dict]:
    """Load and return all rows from the CSV."""
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def get_unique(data: list[dict], key: str) -> list[str]:
    seen, result = set(), []
    for row in data:
        val = row[key].strip()
        if val not in seen:
            seen.add(val)
            result.append(val)
    return sorted(result)


# ── FSM States ────────────────────────────────────────────────────────────────

class SearchState(StatesGroup):
    choosing_mode = State()
    searching_by_field = State()
    searching_by_university = State()


# ── Keyboards ─────────────────────────────────────────────────────────────────

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Search by Field")],
        [KeyboardButton(text="🏛 Search by University")],
        [KeyboardButton(text="📋 All Universities")],
        [KeyboardButton(text="ℹ️ Help")],
    ],
    resize_keyboard=True,
)


def build_inline_keyboard(items: list[str], prefix: str) -> InlineKeyboardMarkup:
    """Build a 2-column inline keyboard from a list of strings."""
    buttons = [
        InlineKeyboardButton(text=item, callback_data=f"{prefix}:{item}")
        for item in items
    ]
    # pair up into rows of 2
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── Formatting ────────────────────────────────────────────────────────────────

def format_entry(row: dict) -> str:
    return (
        f"🏛 <b>{row['university']}</b>\n"
        f"📚 <b>Field:</b> {row['field']}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Quotas:</b>  2024 → <code>{row['quota_2024']}</code>  |  2025 → <code>{row['quota_2025']}</code>\n"
        f"🎯 <b>Scores:</b>  Min <code>{row['min_score']}</code>  –  Max <code>{row['max_score']}</code>\n"
        f"💰 <b>Tuition:</b> <code>${row['tuition_usd']}/year</code>\n"
        f"📅 <b>Deadline:</b> {row['deadline']}\n"
        f"📝 <b>Requirements:</b>\n   {row['requirements']}\n"
        f"🔗 <b>Apply:</b> {row['application_link']}"
    )


def format_summary(rows: list[dict], title: str) -> list[str]:
    """Split results into pages of max 4096 chars each."""
    pages, current = [], f"<b>{title}</b>\n\n"
    for row in rows:
        block = format_entry(row) + "\n\n" + "─" * 30 + "\n\n"
        if len(current) + len(block) > 4000:
            pages.append(current.strip())
            current = block
        else:
            current += block
    if current.strip():
        pages.append(current.strip())
    return pages or [f"<b>{title}</b>\n\nNo results found."]


# ── Bot & Dispatcher ──────────────────────────────────────────────────────────

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())
DATA = load_data()


# ── Handlers ──────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "👋 <b>Welcome to the University Admissions Bot!</b>\n\n"
        "I can help you find information about universities in Uzbekistan — "
        "quotas, scores, tuition, deadlines, and more.\n\n"
        "Choose an option below 👇",
        reply_markup=MAIN_MENU,
    )


@dp.message(Command("help"))
@dp.message(F.text == "ℹ️ Help")
async def cmd_help(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "📖 <b>How to use this bot</b>\n\n"
        "• <b>Search by Field</b> — pick a field of study and see all universities offering it\n"
        "• <b>Search by University</b> — pick a university and browse its programs\n"
        "• <b>All Universities</b> — list every university in the database\n\n"
        "Each result shows:\n"
        "  📊 Quotas (2024 & 2025)\n"
        "  🎯 Min / Max entrance scores\n"
        "  💰 Annual tuition (USD)\n"
        "  📅 Application deadline\n"
        "  📝 Required documents\n"
        "  🔗 Application link\n\n"
        "Use /start to return to the main menu.",
        reply_markup=MAIN_MENU,
    )
    



# ── Search by Field ───────────────────────────────────────────────────────────

@dp.message(F.text == "🔍 Search by Field")
async def search_by_field(msg: Message, state: FSMContext):
    fields = get_unique(DATA, "field")
    await state.set_state(SearchState.searching_by_field)
    await msg.answer(
        "📚 <b>Select a field of study:</b>",
        reply_markup=build_inline_keyboard(fields, "field"),
    )


@dp.callback_query(SearchState.searching_by_field, F.data.startswith("field:"))
async def handle_field_choice(cb: CallbackQuery, state: FSMContext):
    field = cb.data.split(":", 1)[1]
    results = [r for r in DATA if r["field"].strip() == field]
    await cb.message.edit_text(
        f"📚 Results for field: <b>{field}</b>\nFound <b>{len(results)}</b> program(s)."
    )
    pages = format_summary(results, f"📚 {field} — All Universities")
    for page in pages:
        await cb.message.answer(page)
    await state.clear()
    await cb.message.answer("🏠 Back to main menu:", reply_markup=MAIN_MENU)
    await cb.answer()


# ── Search by University ──────────────────────────────────────────────────────

@dp.message(F.text == "🏛 Search by University")
async def search_by_university(msg: Message, state: FSMContext):
    universities = get_unique(DATA, "university")
    await state.set_state(SearchState.searching_by_university)
    await msg.answer(
        "🏛 <b>Select a university:</b>",
        reply_markup=build_inline_keyboard(universities, "uni"),
    )


@dp.callback_query(SearchState.searching_by_university, F.data.startswith("uni:"))
async def handle_uni_choice(cb: CallbackQuery, state: FSMContext):
    uni = cb.data.split(":", 1)[1]
    results = [r for r in DATA if r["university"].strip() == uni]
    await cb.message.edit_text(
        f"🏛 Results for: <b>{uni}</b>\nFound <b>{len(results)}</b> program(s)."
    )
    pages = format_summary(results, f"🏛 {uni}")
    for page in pages:
        await cb.message.answer(page)
    await state.clear()
    await cb.message.answer("🏠 Back to main menu:", reply_markup=MAIN_MENU)
    await cb.answer()


# ── All Universities ──────────────────────────────────────────────────────────

@dp.message(F.text == "📋 All Universities")
async def all_universities(msg: Message, state: FSMContext):
    universities = get_unique(DATA, "university")
    text = "🏛 <b>Universities in the database:</b>\n\n"
    for i, uni in enumerate(universities, 1):
        count = sum(1 for r in DATA if r["university"].strip() == uni)
        text += f"{i}. <b>{uni}</b> — {count} program(s)\n"
    text += "\n💡 Use <b>Search by University</b> to see full details."
    await msg.answer(text, reply_markup=MAIN_MENU)



# ── Entry point ───────────────────────────────────────────────────────────────

async def main():
    print("🤖 Bot is starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    
    
    
# ---ask-ai---
def ask_ai(user_input: str, data_sample: list[dict]) -> str:
    context = "\n".join([
        f"{d['university']} - {d['faculty']} - {d['city']} - ${d['tuition_usd']}"
        for d in data_sample[:15]
    ])

    prompt = f"""
You are a university advisor in Uzbekistan.

User request:
{user_input}

Available data:
{context}

Recommend suitable universities and explain briefly.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
    
@dp.message()
async def ai_handler(msg: Message, state: FSMContext):
    await state.clear()

    text = msg.text

    # ignore menu buttons
    if text in [
        "🔍 Search by Field",
        "🏛 Search by University",
        "📋 All Universities",
        "ℹ️ Help"
    ]:
        return

    await msg.answer("🤖 Thinking...")
    try:
        loop = asyncio.get_event_loop()
        reply = await loop.run_in_executor(None, ask_ai, text, DATA)
        
        await msg.answer(reply)
        
    except Exception as e:
        print("AI ERROR:", repr(e))
        await msg.answer("⚠️ AI error.")
