from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from database import async_session, Student

router = Router()

@router.message(Command("language"))
async def choose_language(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang_kz")]
    ])
    await message.answer("Выберите язык:", reply_markup=kb)

@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    async with async_session() as session:
        res = await session.execute(select(Student).where(Student.tg_id == callback.from_user.id))
        student = res.scalar()
        if student:
            student.language = lang
            await session.commit()
    await callback.message.answer("Язык сохранён. Выберите уровень: /level")
    await callback.answer()
