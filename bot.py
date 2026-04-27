import asyncio
import csv
from pathlib import Path
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
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from openai import AsyncOpenAI

#  Config
BOT_TOKEN = os.getenv("BOT_TOKEN", "8666414561:AAG52ftogficyXMVGNGzHPE5YQn65KlUZkY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
CSV_FILE = Path(__file__).parent / "universities.csv"

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Translations
LANG_NAMES = {"en": "🇬🇧 English", "ru": "🇷🇺 Русский", "uz": "🇺🇿 O'zbekcha"}

T = {
    "welcome": {
        "en": (
            "👋 <b>Welcome to the University Admissions Bot!</b>\n\n"
            "I can help you find information about universities in Uzbekistan — "
            "quotas, scores, tuition, deadlines, and more.\n\n"
            "Choose an option below 👇"
        ),
        "ru": (
            "👋 <b>Добро пожаловать в бот по поступлению в университеты!</b>\n\n"
            "Я помогу найти информацию об университетах Узбекистана — "
            "квоты, баллы, оплата, дедлайны и многое другое.\n\n"
            "Выберите опцию ниже 👇"
        ),
        "uz": (
            "👋 <b>Universitetga qabul botiga xush kelibsiz!</b>\n\n"
            "Men Oʻzbekiston universitetlari haqida maʼlumot berishga yordam beraman — "
            "kvotalar, ballar, toʻlov, muddatlar va boshqalar.\n\n"
            "Quyidagi variantni tanlang 👇"
        ),
    },
    "lang_prompt": {
        "en": "🌐 Please choose your language:",
        "ru": "🌐 Пожалуйста, выберите язык:",
        "uz": "🌐 Iltimos, tilni tanlang:",
    },
    "lang_set": {
        "en": "✅ Language set to English.",
        "ru": "✅ Язык установлен: Русский.",
        "uz": "✅ Til tanlandi: O'zbekcha.",
    },
    "btn_field": {
        "en": "🔍 Search by Field",
        "ru": "🔍 Поиск по направлению",
        "uz": "🔍 Yo'nalish bo'yicha qidirish",
    },
    "btn_uni": {
        "en": "🏛 Search by University",
        "ru": "🏛 Поиск по университету",
        "uz": "🏛 Universitet bo'yicha qidirish",
    },
    "btn_all": {
        "en": "📋 All Universities",
        "ru": "📋 Все университеты",
        "uz": "📋 Barcha universitetlar",
    },
    "btn_help": {
        "en": "ℹ️ Help",
        "ru": "ℹ️ Помощь",
        "uz": "ℹ️ Yordam",
    },
    "btn_lang": {
        "en": "🌐 Language",
        "ru": "🌐 Язык",
        "uz": "🌐 Til",
    },
    "btn_ai": {
        "en": "🤖 Ask AI",
        "ru": "🤖 Спросить ИИ",
        "uz": "🤖 AIdan so'rash",
    },
    "help_text": {
        "en": (
            "📖 <b>How to use this bot</b>\n\n"
            "• <b>Search by Field</b> — pick a field of study and see all universities offering it\n"
            "• <b>Search by University</b> — pick a university and browse its programs\n"
            "• <b>All Universities</b> — list every university in the database\n"
            "• <b>Ask AI</b> — chat with ChatGPT about admissions, documents, or any question\n\n"
            "Each result shows:\n"
            "  📊 Quotas (2024 & 2025)\n"
            "  🎯 Min / Max entrance scores\n"
            "  💰 Annual tuition (USD)\n"
            "  📅 Application deadline\n"
            "  📝 Required documents\n"
            "  🔗 Application link\n\n"
            "Use /start to return to the main menu.\n"
            "Use /lang to change language."
        ),
        "ru": (
            "📖 <b>Как пользоваться ботом</b>\n\n"
            "• <b>Поиск по направлению</b> — выберите направление и увидите все университеты\n"
            "• <b>Поиск по университету</b> — выберите университет и просмотрите программы\n"
            "• <b>Все университеты</b> — список всех университетов в базе\n"
            "• <b>Спросить ИИ</b> — чат с ChatGPT о поступлении, документах или любом вопросе\n\n"
            "Каждый результат показывает:\n"
            "  📊 Квоты (2024 и 2025)\n"
            "  🎯 Мин / Макс вступительные баллы\n"
            "  💰 Годовая оплата (USD)\n"
            "  📅 Дедлайн подачи документов\n"
            "  📝 Требуемые документы\n"
            "  🔗 Ссылка для поступления\n\n"
            "Используйте /start для возврата в главное меню.\n"
            "Используйте /lang для смены языка."
        ),
        "uz": (
            "📖 <b>Botdan foydalanish</b>\n\n"
            "• <b>Yo'nalish bo'yicha qidirish</b> — yo'nalish tanlang va universitetlarni ko'ring\n"
            "• <b>Universitet bo'yicha qidirish</b> — universitent tanlang va dasturlarni ko'ring\n"
            "• <b>Barcha universitetlar</b> — bazadagi barcha universitetlar ro'yxati\n"
            "• <b>AIdan so'rash</b> — qabul, hujjatlar yoki istalgan savol bo'yicha ChatGPT bilan suhbatlashing\n\n"
            "Har bir natijada:\n"
            "  📊 Kvotalar (2024 va 2025)\n"
            "  🎯 Min / Maks kirish ballari\n"
            "  💰 Yillik toʻlov (USD)\n"
            "  📅 Hujjat topshirish muddati\n"
            "  📝 Talab qilingan hujjatlar\n"
            "  🔗 Ariza topshirish havolasi\n\n"
            "Asosiy menyuga qaytish uchun /start bosing.\n"
            "Tilni oʻzgartirish uchun /lang bosing."
        ),
    },
    "select_field": {
        "en": "📚 <b>Select a field of study:</b>",
        "ru": "📚 <b>Выберите направление обучения:</b>",
        "uz": "📚 <b>Ta'lim yo'nalishini tanlang:</b>",
    },
    "select_uni": {
        "en": "🏛 <b>Select a university:</b>",
        "ru": "🏛 <b>Выберите университет:</b>",
        "uz": "🏛 <b>Universitetni tanlang:</b>",
    },
    "found_programs": {
        "en": "Found <b>{n}</b> program(s).",
        "ru": "Найдено <b>{n}</b> программ(а).",
        "uz": "<b>{n}</b> ta dastur topildi.",
    },
    "results_for_field": {
        "en": "📚 Results for field: <b>{val}</b>\n",
        "ru": "📚 Результаты по направлению: <b>{val}</b>\n",
        "uz": "📚 Yo'nalish natijalari: <b>{val}</b>\n",
    },
    "results_for_uni": {
        "en": "🏛 Results for: <b>{val}</b>\n",
        "ru": "🏛 Результаты для: <b>{val}</b>\n",
        "uz": "🏛 Natijalar: <b>{val}</b>\n",
    },
    "all_unis_title": {
        "en": "🏛 <b>Universities in the database:</b>\n\n",
        "ru": "🏛 <b>Университеты в базе данных:</b>\n\n",
        "uz": "🏛 <b>Bazadagi universitetlar:</b>\n\n",
    },
    "programs_count": {
        "en": "{n} program(s)",
        "ru": "{n} программ(а)",
        "uz": "{n} ta dastur",
    },
    "all_unis_tip": {
        "en": "\n💡 Use <b>Search by University</b> to see full details.",
        "ru": "\n💡 Используйте <b>Поиск по университету</b> для полной информации.",
        "uz": "\n💡 Toʻliq maʼlumot uchun <b>Universitet bo'yicha qidirish</b> dan foydalaning.",
    },
    "back_menu": {
        "en": "🏠 Back to main menu:",
        "ru": "🏠 Назад в главное меню:",
        "uz": "🏠 Asosiy menyuga qaytish:",
    },
    "no_results": {
        "en": "No results found.",
        "ru": "Результаты не найдены.",
        "uz": "Natija topilmadi.",
    },
    # AI chat
    "ai_intro": {
        "en": (
            "🤖 <b>AI Assistant is ready!</b>\n\n"
            "Ask me anything about university admissions, required documents, "
            "entrance exams, or studying in Uzbekistan.\n\n"
            "Type your question below. Send /start to return to the main menu."
        ),
        "ru": (
            "🤖 <b>ИИ-ассистент готов!</b>\n\n"
            "Задайте любой вопрос о поступлении в университеты, документах, "
            "вступительных экзаменах или учёбе в Узбекистане.\n\n"
            "Напишите вопрос ниже. Отправьте /start для возврата в главное меню."
        ),
        "uz": (
            "🤖 <b>AI assistent tayyor!</b>\n\n"
            "Universitetga qabul, hujjatlar, kirish imtihonlari yoki "
            "O'zbekistonda o'qish haqida istalgan savol bering.\n\n"
            "Savolingizni yozing. Asosiy menyuga qaytish uchun /start yuboring."
        ),
    },
    "ai_thinking": {
        "en": "🤖 Thinking...",
        "ru": "🤖 Думаю...",
        "uz": "🤖 O'ylamoqda...",
    },
    "ai_error": {
        "en": "⚠️ Sorry, I couldn't get a response from AI. Please try again.",
        "ru": "⚠️ Извините, не удалось получить ответ от ИИ. Попробуйте ещё раз.",
        "uz": "⚠️ Kechirasiz, AIdan javob olishning imkoni bo'lmadi. Qaytadan urinib ko'ring.",
    },
    # Entry card field labels
    "lbl_field":    {"en": "Field",     "ru": "Направление", "uz": "Yo'nalish"},
    "lbl_quotas":   {"en": "Quotas",    "ru": "Квоты",       "uz": "Kvotalar"},
    "lbl_scores":   {"en": "Scores",    "ru": "Баллы",       "uz": "Ballar"},
    "lbl_tuition":  {"en": "Tuition",   "ru": "Оплата",      "uz": "To'lov"},
    "lbl_deadline": {"en": "Deadline",  "ru": "Дедлайн",     "uz": "Muddat"},
    "lbl_reqs":     {"en": "Requirements", "ru": "Документы", "uz": "Hujjatlar"},
    "lbl_apply":    {"en": "Apply",     "ru": "Подать заявку", "uz": "Ariza"},
    "unknown_cmd": {
        "en": "❓ Unknown command. Use the menu buttons or /help.",
        "ru": "❓ Неизвестная команда. Используйте кнопки меню или /help.",
        "uz": "❓ Noma'lum buyruq. Menyu tugmalaridan yoki /help dan foydalaning.",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    text = T.get(key, {}).get(lang) or T.get(key, {}).get("en", key)
    return text.format(**kwargs) if kwargs else text


#  Data loading

def load_data() -> list[dict]:
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


#  FSM States

class BotState(StatesGroup):
    choosing_language = State()
    main_menu = State()
    searching_by_field = State()
    searching_by_university = State()
    ai_chat = State()  # NEW: AI conversation state


#  Keyboards

def main_menu_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_field", lang))],
            [KeyboardButton(text=t("btn_uni", lang))],
            [KeyboardButton(text=t("btn_all", lang))],
            [KeyboardButton(text=t("btn_ai", lang))],
            [KeyboardButton(text=t("btn_help", lang)), KeyboardButton(text=t("btn_lang", lang))],
        ],
        resize_keyboard=True,
    )


def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=v, callback_data=f"setlang:{k}") for k, v in LANG_NAMES.items()]
    ])


def build_inline_keyboard(items: list[str], prefix: str) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=item, callback_data=f"{prefix}:{item}")
        for item in items
    ]
    rows = [buttons[i: i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


#  Formatting

def format_entry(row: dict, lang: str) -> str:
    return (
        f"🏛 <b>{row['university']}</b>\n"
        f"📚 <b>{t('lbl_field', lang)}:</b> {row['field']}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>{t('lbl_quotas', lang)}:</b>  2024 → <code>{row['quota_2024']}</code>  |  2025 → <code>{row['quota_2025']}</code>\n"
        f"🎯 <b>{t('lbl_scores', lang)}:</b>  Min <code>{row['min_score']}</code>  –  Max <code>{row['max_score']}</code>\n"
        f"💰 <b>{t('lbl_tuition', lang)}:</b> <code>${row['tuition_usd']}/year</code>\n"
        f"📅 <b>{t('lbl_deadline', lang)}:</b> {row['deadline']}\n"
        f"📝 <b>{t('lbl_reqs', lang)}:</b>\n   {row['requirements']}\n"
        f"🔗 <b>{t('lbl_apply', lang)}:</b> {row['application_link']}"
    )


def format_summary(rows: list[dict], title: str, lang: str) -> list[str]:
    pages, current = [], f"<b>{title}</b>\n\n"
    for row in rows:
        block = format_entry(row, lang) + "\n\n" + "─" * 30 + "\n\n"
        if len(current) + len(block) > 4000:
            pages.append(current.strip())
            current = block
        else:
            current += block
    if current.strip():
        pages.append(current.strip())
    return pages or [f"<b>{title}</b>\n\n{t('no_results', lang)}"]


#  Helpers

async def get_lang(state: FSMContext) -> str:
    data = await state.get_data()
    return data.get("lang", "en")


def all_menu_texts() -> set[str]:
    texts = set()
    for key in ("btn_field", "btn_uni", "btn_all", "btn_help", "btn_lang", "btn_ai"):
        for lang in ("en", "ru", "uz"):
            texts.add(T[key][lang])
    return texts


# AI helper

AI_SYSTEM_PROMPT = (
    "You are a helpful university admissions assistant specializing in Uzbekistan universities. "
    "You help students with questions about university admissions, entrance exams, required documents, "
    "tuition fees, quotas, deadlines, and studying in Uzbekistan. "
    "Be concise, friendly, and accurate. "
    "If the user writes in Russian or Uzbek, respond in the same language. "
    "If you don't know something specific, say so honestly and suggest they check official university websites."
)


async def ask_openai(user_message: str, history: list[dict]) -> str:
    """Send a message to OpenAI and return the reply text."""
    messages = [{"role": "system", "content": AI_SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=800,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


#  Bot & Dispatcher

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())
DATA = load_data()
MENU_TEXTS = all_menu_texts()


#  Language selection

@dp.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(BotState.choosing_language)
    await msg.answer(
        "🌐 Please choose your language / Выберите язык / Tilni tanlang:",
        reply_markup=lang_kb(),
    )


@dp.message(Command("lang"))
async def cmd_lang(msg: Message, state: FSMContext):
    await state.set_state(BotState.choosing_language)
    lang = await get_lang(state)
    await msg.answer(t("lang_prompt", lang), reply_markup=lang_kb())


@dp.callback_query(F.data.startswith("setlang:"))
async def handle_lang_choice(cb: CallbackQuery, state: FSMContext):
    lang = cb.data.split(":")[1]
    await state.update_data(lang=lang)
    await state.set_state(BotState.main_menu)
    await cb.message.edit_text(t("lang_set", lang))
    await cb.message.answer(t("welcome", lang), reply_markup=main_menu_kb(lang))
    await cb.answer()


#  Help

@dp.message(Command("help"))
async def cmd_help_command(msg: Message, state: FSMContext):
    lang = await get_lang(state)
    await msg.answer(t("help_text", lang), reply_markup=main_menu_kb(lang))


#  Search by Field

@dp.message(lambda msg: msg.text in [T["btn_field"][l] for l in ("en", "ru", "uz")])
async def search_by_field(msg: Message, state: FSMContext):
    lang = await get_lang(state)
    fields = get_unique(DATA, "field")
    await state.set_state(BotState.searching_by_field)
    await msg.answer(t("select_field", lang), reply_markup=build_inline_keyboard(fields, "field"))


@dp.callback_query(BotState.searching_by_field, F.data.startswith("field:"))
async def handle_field_choice(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(state)
    field = cb.data.split(":", 1)[1]
    results = [r for r in DATA if r["field"].strip() == field]
    header = t("results_for_field", lang, val=field) + t("found_programs", lang, n=len(results))
    await cb.message.edit_text(header)
    pages = format_summary(results, f"📚 {field}", lang)
    for page in pages:
        await cb.message.answer(page)
    await state.set_state(BotState.main_menu)
    await cb.message.answer(t("back_menu", lang), reply_markup=main_menu_kb(lang))
    await cb.answer()


#  Search by University

@dp.message(lambda msg: msg.text in [T["btn_uni"][l] for l in ("en", "ru", "uz")])
async def search_by_university(msg: Message, state: FSMContext):
    lang = await get_lang(state)
    universities = get_unique(DATA, "university")
    await state.set_state(BotState.searching_by_university)
    await msg.answer(t("select_uni", lang), reply_markup=build_inline_keyboard(universities, "uni"))


@dp.callback_query(BotState.searching_by_university, F.data.startswith("uni:"))
async def handle_uni_choice(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(state)
    uni = cb.data.split(":", 1)[1]
    results = [r for r in DATA if r["university"].strip() == uni]
    header = t("results_for_uni", lang, val=uni) + t("found_programs", lang, n=len(results))
    await cb.message.edit_text(header)
    pages = format_summary(results, f"🏛 {uni}", lang)
    for page in pages:
        await cb.message.answer(page)
    await state.set_state(BotState.main_menu)
    await cb.message.answer(t("back_menu", lang), reply_markup=main_menu_kb(lang))
    await cb.answer()


#  All Universities

@dp.message(lambda msg: msg.text in [T["btn_all"][l] for l in ("en", "ru", "uz")])
async def all_universities(msg: Message, state: FSMContext):
    lang = await get_lang(state)
    universities = get_unique(DATA, "university")
    text = t("all_unis_title", lang)
    for i, uni in enumerate(universities, 1):
        count = sum(1 for r in DATA if r["university"].strip() == uni)
        text += f"{i}. <b>{uni}</b> — {t('programs_count', lang, n=count)}\n"
    text += t("all_unis_tip", lang)
    await msg.answer(text, reply_markup=main_menu_kb(lang))


#  Help button

@dp.message(lambda msg: msg.text in [T["btn_help"][l] for l in ("en", "ru", "uz")])
async def help_button(msg: Message, state: FSMContext):
    lang = await get_lang(state)
    await msg.answer(t("help_text", lang), reply_markup=main_menu_kb(lang))


#  Language button

@dp.message(lambda msg: msg.text in [T["btn_lang"][l] for l in ("en", "ru", "uz")])
async def lang_button(msg: Message, state: FSMContext):
    lang = await get_lang(state)
    await state.set_state(BotState.choosing_language)
    await msg.answer(t("lang_prompt", lang), reply_markup=lang_kb())


# ── AI Chat ────────────────────────────────────────────────────────────────────

@dp.message(lambda msg: msg.text in [T["btn_ai"][l] for l in ("en", "ru", "uz")])
async def ai_chat_start(msg: Message, state: FSMContext):
    """Enter AI chat mode."""
    lang = await get_lang(state)
    await state.set_state(BotState.ai_chat)
    await state.update_data(ai_history=[])  # reset conversation history
    await msg.answer(t("ai_intro", lang), reply_markup=main_menu_kb(lang))


@dp.message(BotState.ai_chat)
async def ai_chat_message(msg: Message, state: FSMContext):
    """Handle messages in AI chat mode."""
    # If user taps a menu button, exit AI mode and handle normally
    if msg.text in MENU_TEXTS:
        await state.set_state(BotState.main_menu)
        # Re-dispatch to the appropriate handler by re-triggering
        await fallback(msg, state)
        return

    lang = await get_lang(state)
    data = await state.get_data()
    history: list[dict] = data.get("ai_history", [])

    # Show "thinking" indicator
    thinking_msg = await msg.answer(t("ai_thinking", lang))

    try:
        reply = await ask_openai(msg.text, history)

        # Update conversation history (keep last 10 turns to avoid token overflow)
        history.append({"role": "user", "content": msg.text})
        history.append({"role": "assistant", "content": reply})
        history = history[-20:]  # keep last 20 messages (10 turns)
        await state.update_data(ai_history=history)

        await thinking_msg.delete()
        await msg.answer(f"🤖 {reply}")

    except Exception as e:
        await thinking_msg.delete()
        await msg.answer(t("ai_error", lang))
        print(f"OpenAI error: {e}")


#  Fallback

@dp.message()
async def fallback(msg: Message, state: FSMContext):
    lang = await get_lang(state)
    await msg.answer(t("unknown_cmd", lang), reply_markup=main_menu_kb(lang))


#  Entry point

async def main():
    print("🤖 Bot is starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
