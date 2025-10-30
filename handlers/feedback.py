from aiogram import Router, types, F
from aiogram.filters import Command
from database import async_session, add_feedback, Student
from sqlalchemy.future import select

router = Router()


@router.message(Command("feedback"))
async def start_feedback(message: types.Message):
    async with async_session() as session:
        res = await session.execute(select(Student).where(Student.tg_id == message.from_user.id))
        student = res.scalar()

    lang = student.language if student and student.language else "ru"

    texts = {
        "ru": (
            "💬 Напиши свой отзыв или предложение.\n"
            "Начни сообщение с ключевого слова: 'Отзыв:'.\n\n"
            "Пример:\nОтзыв: Хотелось бы больше заданий на Intermediate уровне."
        ),
        "kz": (
            "💬 Өз пікіріңді немесе ұсынысыңды жаз.\n"
            "Хабарды 'Пікір:' сөзімен баста.\n\n"
            "Мысалы:\nПікір: Intermediate деңгейінде көбірек тапсырмалар болса екен."
        ),
        "en": (
            "💬 Write your feedback or suggestion.\n"
            "Start your message with the keyword 'Feedback:'.\n\n"
            "Example:\nFeedback: I’d like to have more tasks at the Intermediate level."
        )
    }

    await message.answer(texts.get(lang, texts["ru"]))


@router.message(F.text.regexp(r"^(Отзыв:|Пікір:|Feedback:)"))
async def save_feedback(message: types.Message):
    feedback_text = (
        message.text
        .replace("Отзыв:", "")
        .replace("Пікір:", "")
        .replace("Feedback:", "")
        .strip()
    )

    if not feedback_text:
        await message.answer("⚠️ Пожалуйста, напиши текст после ключевого слова.")
        return

    async with async_session() as session:
        res = await session.execute(select(Student).where(Student.tg_id == message.from_user.id))
        student = res.scalar()

        if not student:
            await message.answer("⚠️ Сначала зарегистрируйтесь: /register")
            return

        lang = student.language or "ru"
        await add_feedback(session, student.id, feedback_text)

    responses = {
        "ru": "🙏 Спасибо за отзыв! Мы обязательно учтём твоё мнение ❤️",
        "kz": "🙏 Пікірің үшін рақмет! Біз міндетті түрде ескереміз ❤️",
        "en": "🙏 Thank you for your feedback! We truly appreciate it ❤️",
    }

    await message.answer(responses.get(lang, responses["ru"]))


@router.message(Command("show_feedbacks"))
async def show_feedbacks(message: types.Message):
    ADMIN_ID = 8249864320 

    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 У тебя нет доступа к просмотру отзывов.")
        return

    from database import Feedback
    async with async_session() as session:
        res = await session.execute(select(Feedback))
        feedbacks = res.scalars().all()

    if not feedbacks:
        await message.answer("Пока нет отзывов 💭")
        return

    text = "📋 *Отзывы пользователей:*\n\n"
    for f in feedbacks:
        text += f"🧑‍💻 Пользователь ID {f.user_id}:\n{f.message}\n\n"

    await message.answer(text, parse_mode="Markdown")
