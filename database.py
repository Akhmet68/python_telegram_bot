from sqlalchemy import (
    Column, Integer, String, BigInteger, ForeignKey,
    Boolean, Float, Text, DateTime, func
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from config import DATABASE_URL

Base = declarative_base()


# 👤 Таблица пользователей
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, unique=True, index=True)
    full_name = Column(String(255))
    group = Column(String(100))
    phone = Column(String(50))
    language = Column(String(10), default="ru")
    level = Column(String(20), default="beginner")
    score = Column(Integer, default=0)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи с другими таблицами
    progress = relationship("Progress", back_populates="student", cascade="all, delete-orphan")
    statistics = relationship("Statistics", back_populates="student", uselist=False)
    feedback = relationship("Feedback", back_populates="student", cascade="all, delete-orphan")
    history = relationship("LessonHistory", back_populates="student", cascade="all, delete-orphan")


# 📈 Прогресс пользователя по темам
class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("students.id"))
    topic = Column(String(255))
    correct_answers = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    student = relationship("Student", back_populates="progress")


# 🏅 Общая статистика
class Statistics(Base):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("students.id"))
    total_lessons = Column(Integer, default=0)
    total_tests = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)

    student = relationship("Student", back_populates="statistics")


# 💬 Отзывы пользователей
class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("students.id"))
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="feedback")


# 🧾 История уроков
class LessonHistory(Base):
    __tablename__ = "lesson_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("students.id"))
    lesson_level = Column(String(50))
    topic_title = Column(String(255))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    score = Column(Integer, default=0)

    student = relationship("Student", back_populates="history")


# ⚙️ Настройка движка и сессии
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# 🧩 Инициализация базы данных
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ База данных успешно инициализирована!")


# 🔧 Утилиты для работы
async def add_user(session, tg_id, full_name, group=None, phone=None, language="ru"):
    """Добавление нового пользователя"""
    new_user = Student(
        tg_id=tg_id,
        full_name=full_name,
        group=group,
        phone=phone,
        language=language
    )
    session.add(new_user)
    await session.commit()
    return new_user


async def update_progress(session, user_id, topic, correct, total):
    """Обновление прогресса пользователя"""
    progress = await session.execute(
        func.count(Progress.id).filter(Progress.user_id == user_id, Progress.topic == topic)
    )
    existing = await session.execute(
        session.query(Progress).filter_by(user_id=user_id, topic=topic)
    )
    record = existing.scalar_one_or_none()

    if record:
        record.correct_answers += correct
        record.total_questions += total
        record.completed = record.correct_answers >= record.total_questions
    else:
        new_progress = Progress(
            user_id=user_id,
            topic=topic,
            correct_answers=correct,
            total_questions=total
        )
        session.add(new_progress)
    await session.commit()


async def add_feedback(session, user_id, message):
    """Добавить отзыв"""
    feedback = Feedback(user_id=user_id, message=message)
    session.add(feedback)
    await session.commit()


async def log_lesson(session, user_id, level, topic_title, score=0):
    """Сохранить историю прохождения урока"""
    history = LessonHistory(
        user_id=user_id,
        lesson_level=level,
        topic_title=topic_title,
        score=score
    )
    session.add(history)
    await session.commit()
