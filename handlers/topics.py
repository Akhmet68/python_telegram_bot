from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database import async_session, Student
from sqlalchemy import select
import os
from utils.translator import tr

router = Router()

@router.message(Command("topic"))
async def show_topic(message: types.Message):
    """
    Показывает учебный материал (тему) по выбранному уровню пользователя.
    """
    async with async_session() as session:
        res = await session.execute(select(Student).where(Student.tg_id == message.from_user.id))
        student = res.scalar()

    if not student:
        await message.answer(tr("ru", "noreg"))
        return

    if not student.level:
        await message.answer(tr(student.language, "nolevel"))
        return

    file_path = os.path.join("topics", f"{student.level}.txt")
    if not os.path.exists(file_path):
        await message.answer(tr(student.language, "no_tasks"))
        return

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for part in parts:
        await message.answer(part)

    await message.answer(tr(student.language, "ok"))
