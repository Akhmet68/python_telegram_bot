from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.future import select
from database import async_session, Student, Progress

router = Router()


# 📊 Команда для просмотра прогресса пользователя
@router.message(Command("progress"))
async def show_progress(message: types.Message):
    user_id = message.from_user.id

    async with async_session() as session:
        # Ищем студента
        res = await session.execute(select(Student).where(Student.tg_id == user_id))
        student = res.scalar()

        if not student:
            await message.answer("⚠️ Сначала зарегистрируйтесь: /register")
            return

        lang = student.language or "ru"

        # Получаем все записи прогресса
        res = await session.execute(select(Progress).where(Progress.user_id == student.id))
        progress_list = res.scalars().all()

    if not progress_list:
        if lang == "kz":
            await message.answer("📊 Сізде әлі прогресс туралы деректер жоқ 😅")
        elif lang == "en":
            await message.answer("📊 You don’t have any progress data yet 😅")
        else:
            await message.answer("📊 У вас пока нет данных о прогрессе 😅")
        return

    # Формируем текст в зависимости от языка
    if lang == "kz":
        text = f"📈 *Сіздің оқу барысыңыз:*\n\n"
        for p in progress_list:
            percent = int(p.correct_answers / p.total_questions * 100) if p.total_questions else 0
            text += f"🔹 {p.topic}: {percent}% ({p.correct_answers}/{p.total_questions})\n"
        text += "\nЖарайсың! Жалғастыра бер 💪"
    elif lang == "en":
        text = f"📈 *Your learning progress:*\n\n"
        for p in progress_list:
            percent = int(p.correct_answers / p.total_questions * 100) if p.total_questions else 0
            text += f"🔹 {p.topic}: {percent}% ({p.correct_answers}/{p.total_questions})\n"
        text += "\nKeep it up! 💪"
    else:
        text = f"📈 *Ваш прогресс обучения:*\n\n"
        for p in progress_list:
            percent = int(p.correct_answers / p.total_questions * 100) if p.total_questions else 0
            text += f"🔹 {p.topic}: {percent}% ({p.correct_answers}/{p.total_questions})\n"
        text += "\nТак держать! 💪"

    await message.answer(text, parse_mode="Markdown")



# 🧮 Функция для обновления прогресса (например, после прохождения теста)
async def update_progress(user_id: int, topic: str, correct: int, total: int):
    async with async_session() as session:
        res = await session.execute(select(Student).where(Student.tg_id == user_id))
        student = res.scalar()

        if not student:
            return

        # Проверяем, есть ли запись по этому топику
        res = await session.execute(
            select(Progress).where(
                Progress.user_id == student.id, Progress.topic == topic
            )
        )
        progress = res.scalar()

        if progress:
            progress.correct_answers = correct
            progress.total_questions = total
        else:
            new_progress = Progress(
                user_id=student.id,
                topic=topic,
                correct_answers=correct,
                total_questions=total,
            )
            session.add(new_progress)

        await session.commit()
