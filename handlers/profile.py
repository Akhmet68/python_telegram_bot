from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.future import select
from database import async_session, Student, Progress

router = Router()


# 🧾 Команда для просмотра профиля
@router.message(Command("profile"))
async def show_profile(message: types.Message):
    user_id = message.from_user.id

    async with async_session() as session:
        result = await session.execute(select(Student).where(Student.tg_id == user_id))
        student = result.scalar()

        if not student:
            await message.answer("⚠️ Сначала зарегистрируйтесь с помощью /register")
            return

        # Проверяем язык профиля
        lang = student.language or "ru"

        # Строим сообщение в зависимости от языка
        if lang == "kz":
            text = (
                f"🧍 *Профиль*\n\n"
                f"📛 Аты-жөні: {student.full_name}\n"
                f"🎓 Топ: {student.group or '—'}\n"
                f"📱 Телефон: {student.phone or '—'}\n"
                f"🌐 Тіл: Қазақша 🇰🇿\n"
                f"📘 Деңгей: {student.level or 'Белгісіз'}\n"
                f"🏆 Ұпай: {student.score}\n"
            )
        elif lang == "en":
            text = (
                f"🧍 *Profile*\n\n"
                f"📛 Name: {student.full_name}\n"
                f"🎓 Group: {student.group or '—'}\n"
                f"📱 Phone: {student.phone or '—'}\n"
                f"🌐 Language: English 🇬🇧\n"
                f"📘 Level: {student.level or 'Not set'}\n"
                f"🏆 Score: {student.score}\n"
            )
        else:  # по умолчанию русский
            text = (
                f"🧍 *Профиль*\n\n"
                f"📛 Имя: {student.full_name}\n"
                f"🎓 Группа: {student.group or '—'}\n"
                f"📱 Телефон: {student.phone or '—'}\n"
                f"🌐 Язык: Русский 🇷🇺\n"
                f"📘 Уровень: {student.level or 'Не выбран'}\n"
                f"🏆 Очки: {student.score}\n"
            )

        # Добавляем статистику прогресса
        result = await session.execute(select(Progress).where(Progress.user_id == student.id))
        progress_list = result.scalars().all()

    if progress_list:
        text += "\n📊 *Прогресс:*\n\n"
        for p in progress_list:
            percent = int(p.correct_answers / p.total_questions * 100) if p.total_questions else 0
            if lang == "kz":
                text += f"🔹 {p.topic}: {percent}% ({p.correct_answers}/{p.total_questions})\n"
            elif lang == "en":
                text += f"🔹 {p.topic}: {percent}% ({p.correct_answers}/{p.total_questions})\n"
            else:
                text += f"🔹 {p.topic}: {percent}% ({p.correct_answers}/{p.total_questions})\n"
    else:
        if lang == "kz":
            text += "\n📊 Прогресс туралы ақпарат жоқ 😅"
        elif lang == "en":
            text += "\n📊 No progress data yet 😅"
        else:
            text += "\n📊 Пока нет данных о прогрессе 😅"

    await message.answer(text, parse_mode="Markdown")
