from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from database import async_session, Student
from utils.translator import tr  # добавлено, чтобы сообщения были на нужном языке

router = Router()

# 🗣 Команда выбора языка
@router.message(Command("language"))
async def choose_language(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang_kz")]
    ])
    await message.answer("🌍 Выберите язык:", reply_markup=kb)

# 💾 Обработка выбора языка
@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]

    async with async_session() as session:
        res = await session.execute(select(Student).where(Student.tg_id == callback.from_user.id))
        student = res.scalar()

        if student:
            student.language = lang
            await session.commit()
        else:
            student = Student(tg_id=callback.from_user.id, language=lang)
            session.add(student)
            await session.commit()

    await callback.answer()
    await callback.message.answer(tr(lang, "language_saved"))
    await callback.message.answer(tr(lang, "choose_level_hint") + " /start")
