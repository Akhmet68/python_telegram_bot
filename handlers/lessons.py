from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database import async_session, Student
from utils.generator import load_task
from utils.checker import is_correct

router = Router()

class LessonState(StatesGroup):
    waiting = State()

def tr(lang, key):
    data = {
        "ru": {"send": "Напиши ответ:", "ok": "Правильно. +1 балл", "bad": "Неправильно. /lesson для нового задания", "nolevel": "Сначала выбери уровень: /level", "noreg": "Сначала зарегистрируйся: /register"},
        "en": {"send": "Type your answer:", "ok": "Correct. +1 point", "bad": "Not correct. Use /lesson for a new task", "nolevel": "Choose a level first: /level", "noreg": "Please register first: /register"},
        "kz": {"send": "Жауабыңды жаз:", "ok": "Дұрыс. +1 ұпай", "bad": "Дұрыс емес. Жаңа тапсырма үшін /lesson", "nolevel": "Алдымен деңгей таңда: /level", "noreg": "Алдымен тіркел: /register"}
    }
    return data.get(lang or "ru", data["ru"])[key]

@router.message(Command("lesson"))
async def start_lesson(message: types.Message, state: FSMContext):
    async with async_session() as session:
        res = await session.execute(select(Student).where(Student.tg_id == message.from_user.id))
        student = res.scalar()
    if not student:
        await message.answer(tr("ru", "noreg"))
        return
    if not student.level:
        await message.answer(tr(student.language, "nolevel"))
        return
    task = load_task(student.level)
    await state.update_data(correct=str(task["answer"]), lang=student.language)
    await message.answer(f"Задание:\n{task['question']}")
    await message.answer(tr(student.language, "send"))
    await state.set_state(LessonState.waiting)

@router.message(LessonState.waiting)
async def check_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if is_correct(message.text, data["correct"]):
        async with async_session() as session:
            res = await session.execute(select(Student).where(Student.tg_id == message.from_user.id))
            st = res.scalar()
            if st:
                st.score += 1
                await session.commit()
        await message.answer(tr(data["lang"], "ok"))
        await state.clear()
    else:
        await message.answer(tr(data["lang"], "bad"))
