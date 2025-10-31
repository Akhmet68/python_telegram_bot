from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database import async_session, Student
import json, os, random

router = Router()


# ============================
#  FSM Состояния
# ============================
class LessonMode(StatesGroup):
    choosing_mode = State()
    waiting_answer = State()


# ============================
#  Переводы интерфейса
# ============================
def tr(lang, key):
    data = {
        "ru": {
            "choose_mode": "📚 Что хочешь сделать?",
            "learn_topic": "📖 Учить тему",
            "take_test": "🧩 Пройти тест",
            "send": "Выбери правильный ответ:",
            "ok": "✅ Правильно! +1 балл",
            "bad": "❌ Неправильно. Попробуй снова или напиши /lesson, чтобы начать заново.",
            "nolevel": "⚠️ Сначала выбери уровень: /level",
            "noreg": "⚠️ Сначала зарегистрируйся: /register",
            "no_tasks": "📚 Заданий для этого уровня пока нет.",
            "topic_end": "🎯 Тема окончена. Теперь можешь пройти тест!"
        },
        "en": {
            "choose_mode": "📚 What do you want to do?",
            "learn_topic": "📖 Learn topic",
            "take_test": "🧩 Take test",
            "send": "Choose the correct answer:",
            "ok": "✅ Correct! +1 point",
            "bad": "❌ Incorrect. Try again or use /lesson to start over.",
            "nolevel": "⚠️ Choose a level first: /level",
            "noreg": "⚠️ Please register first: /register",
            "no_tasks": "📚 No tasks available for this level yet.",
            "topic_end": "🎯 Topic completed! You can now take the test!"
        },
        "kz": {
            "choose_mode": "📚 Не істегің келеді?",
            "learn_topic": "📖 Тақырыпты оқу",
            "take_test": "🧩 Тест тапсыру",
            "send": "Дұрыс жауапты таңда:",
            "ok": "✅ Дұрыс! +1 ұпай",
            "bad": "❌ Дұрыс емес. Қайта көріңіз немесе /lesson жазыңыз.",
            "nolevel": "⚠️ Алдымен деңгей таңда: /level",
            "noreg": "⚠️ Алдымен тіркеліңіз: /register",
            "no_tasks": "📚 Бұл деңгейге арналған тапсырмалар жоқ.",
            "topic_end": "🎯 Тақырып аяқталды. Енді тест тапсыруға болады!"
        },
    }
    return data.get(lang or "ru", data["ru"]).get(key, key)


# ============================
#  /lesson
# ============================
@router.message(Command("lesson"))
async def start_lesson(message: types.Message, state: FSMContext):
    async with async_session() as session:
        res = await session.execute(
            select(Student).where(Student.tg_id == message.from_user.id)
        )
        student = res.scalar()

    if not student:
        await message.answer(tr("ru", "noreg"))
        return

    if not student.level:
        await message.answer(tr(student.language, "nolevel"))
        return

    lang = student.language or "ru"

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=tr(lang, "learn_topic"), callback_data="mode_topic")],
            [types.InlineKeyboardButton(text=tr(lang, "take_test"), callback_data="mode_test")]
        ]
    )

    await message.answer(tr(lang, "choose_mode"), reply_markup=kb)
    await state.set_state(LessonMode.choosing_mode)


# ============================
#  Выбор режима
# ============================
@router.callback_query(LessonMode.choosing_mode)
async def choose_mode(callback: types.CallbackQuery, state: FSMContext):
    mode = callback.data.split("_")[1]

    async with async_session() as session:
        res = await session.execute(
            select(Student).where(Student.tg_id == callback.from_user.id)
        )
        student = res.scalar()

    lang = student.language or "ru"
    level = student.level or "beginner"

    # === Учить тему ===
    if mode == "topic":
        topic_path = os.path.join("topics", f"{level}_{lang}.txt")
        if not os.path.exists(topic_path):
            await callback.message.answer(tr(lang, "no_tasks"))
            await state.clear()
            return

        with open(topic_path, "r", encoding="utf-8") as f:
            text = f.read()

        await callback.message.answer(f"📖 {text}")
        await callback.message.answer(tr(lang, "topic_end"))
        await state.clear()
        return

    # === Пройти тест ===
    elif mode == "test":
        json_path = os.path.join("prompts", f"{level}.json")
        if not os.path.exists(json_path):
            await callback.message.answer(tr(lang, "no_tasks"))
            await state.clear()
            return

        # Загружаем JSON
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        lang_data = data.get(lang)
        if not lang_data or "questions" not in lang_data:
            await callback.message.answer(tr(lang, "no_tasks"))
            await state.clear()
            return

        questions = lang_data["questions"]
        if not questions:
            await callback.message.answer(tr(lang, "no_tasks"))
            await state.clear()
            return

        # Выбор вопроса
        task = random.choice(questions)
        opts = task["options"]
        correct = str(task["answer"])

        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=f"{k}) {v}", callback_data=f"ans_{k}")]
                for k, v in opts.items()
            ]
        )

        await state.update_data(correct=correct, lang=lang)
        await callback.message.answer(f"🧩 {task['question']}", reply_markup=kb)
        await state.set_state(LessonMode.waiting_answer)


# ============================
#  Проверка ответа
# ============================
@router.callback_query(LessonMode.waiting_answer)
async def check_answer(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    correct = data.get("correct")
    chosen = callback.data.split("_")[1]

    if chosen == correct:
        async with async_session() as session:
            res = await session.execute(
                select(Student).where(Student.tg_id == callback.from_user.id)
            )
            student = res.scalar()
            if student:
                student.score += 1
                await session.commit()

        await callback.message.edit_text(tr(lang, "ok"))
        await state.clear()
    else:
        await callback.answer(tr(lang, "bad"), show_alert=True)
