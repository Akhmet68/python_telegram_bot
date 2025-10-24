from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from database import async_session, Student

router = Router()

@router.message(Command("level"))
async def choose_level(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Beginner", callback_data="level_beginner")],
        [InlineKeyboardButton(text="Intermediate", callback_data="level_intermediate")],
        [InlineKeyboardButton(text="Advanced", callback_data="level_advanced")]
    ])
    await message.answer("Выберите уровень:", reply_markup=kb)

@router.callback_query(F.data.startswith("level_"))
async def set_level(callback: types.CallbackQuery):
    level = callback.data.split("_", 1)[1]
    async with async_session() as session:
        res = await session.execute(select(Student).where(Student.tg_id == callback.from_user.id))
        student = res.scalar()
        if student:
            student.level = level
            await session.commit()
    await callback.message.answer("Уровень сохранён. Начать урок: /lesson")
    await callback.answer()
