from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database import async_session, Student
import json
import os
import random

router = Router()

class LessonState(StatesGroup):
    waiting = State()

def tr(lang, key):
    data = {
        "ru": {
            "send": "Выбери правильный ответ:",
            "ok": "✅ Правильно! +1 балл",
            "bad": "❌ Неправильно. Попробуй ещё раз или нажми /lesson для нового вопроса.",
            "nolevel": "⚠️ Сначала выбери уровень: /level",
            "noreg": "⚠️ Сначала зарегистрируйся: /start",
            "no_tasks": "📚 Заданий для этого уровня пока нет.",
            "score": "📊 Твои баллы: "
        },
        "en": {
            "send": "Choose the correct answer:",
            "ok": "✅ Correct! +1 point",
            "bad": "❌ Incorrect. Try again or use /lesson for a new question.",
            "nolevel": "⚠️ Choose a level first: /level",
            "noreg": "⚠️ Please register first: /start",
            "no_tasks": "📚 No tasks available for this level yet.",
            "score": "📊 Your score: "
        },
        "kz": {
            "send": "Дұрыс жауапты таңда:",
            "ok": "✅ Дұрыс! +1 ұпай",
            "bad": "❌ Дұрыс емес. Қайта көріңіз немесе жаңа сұрақ үшін /lesson жазыңыз.",
            "nolevel": "⚠️ Алдымен деңгей таңда: /level",
            "noreg": "⚠️ Алдымен тіркеліңіз: /start",
            "no_tasks": "📚 Бұл деңгейге арналған тапсырмалар жоқ.",
            "score": "📊 Ұпайыңыз: "
        },
    }
    return data.get(lang or "ru", data["ru"])[key]

def load_questions(level: str):
    path = os.path.join("prompts", f"{level}.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "questions" in data:
        return data["questions"]
    if isinstance(data, list):
        return data
    return []

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

    tasks = load_questions(student.level)
    if not tasks:
        await message.answer(tr(student.language, "no_tasks"))
        return

    task = random.choice(tasks)
    question = task.get("question", "")
    options_dict = task.get("options", {})
    correct_letter = str(task.get("answer")).strip()

    letters = sorted(options_dict.keys())
    keyboard_rows = []
    for letter in letters:
        text = f"{letter}) {options_dict[letter]}"
        keyboard_rows.append([types.InlineKeyboardButton(text=text, callback_data=f"answer_{letter}")])
    kb = types.InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

    await state.update_data(correct=correct_letter, lang=student.language)
    await message.answer(f"🧩 {question}\n\n{tr(student.language, 'send')}", reply_markup=kb)
    await state.set_state(LessonState.waiting)

@router.callback_query(LessonState.waiting)
async def check_answer(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    correct = data.get("correct")
    if not callback.data.startswith("answer_"):
        await callback.answer()
        return
    chosen = callback.data.split("_", 1)[1].strip()

    if chosen == str(correct).strip():
        async with async_session() as session:
            res = await session.execute(select(Student).where(Student.tg_id == callback.from_user.id))
            student = res.scalar()
            if student:
                student.score += 1
                await session.commit()
        await callback.message.edit_text(tr(lang, "ok"))
        await state.clear()
    else:
        await callback.answer(tr(lang, "bad"), show_alert=True)

@router.message(Command("score"))
async def show_score(message: types.Message):
    async with async_session() as session:
        res = await session.execute(select(Student).where(Student.tg_id == message.from_user.id))
        student = res.scalar()
    if not student:
        await message.answer(tr("ru", "noreg"))
        return
    await message.answer(f"{tr(student.language, 'score')}{student.score}")
