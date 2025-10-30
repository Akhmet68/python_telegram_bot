from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from database import async_session, Student
from sqlalchemy import select
from utils.translator import tr

router = Router()

class RegisterForm(StatesGroup):
    language = State()
    full_name = State()
    group = State()
    phone = State()

@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    async with async_session() as session:
        res = await session.execute(select(Student).where(Student.tg_id == message.from_user.id))
        student = res.scalar()

    if student:
        if not student.language:
            await send_language_choice(message)
        elif not student.level:
            await send_level_choice(message, student.language)
        else:
            await message.answer(tr(student.language, "already_registered"))
        return

    await message.answer("👋 Привет! Добро пожаловать в курс по Python!")
    await send_language_choice(message)

# ===== Выбор языка =====
async def send_language_choice(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang_kz")]
    ])
    await message.answer("🌍 Выберите язык:", reply_markup=kb)

@router.callback_query(lambda c: c.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    async with async_session() as session:
        res = await session.execute(select(Student).where(Student.tg_id == callback.from_user.id))
        student = res.scalar()
        if not student:
            student = Student(tg_id=callback.from_user.id, language=lang)
            session.add(student)
        else:
            student.language = lang
        await session.commit()

    await state.update_data(language=lang)
    await callback.answer()
    await callback.message.answer(tr(lang, "ask_fullname"), parse_mode="Markdown")
    await state.set_state(RegisterForm.full_name)

# ===== Регистрация =====
@router.message(RegisterForm.full_name)
async def reg_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")
    await state.update_data(full_name=message.text.strip())
    await message.answer(tr(lang, "ask_group"), parse_mode="Markdown")
    await state.set_state(RegisterForm.group)

@router.message(RegisterForm.group)
async def reg_group(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")
    await state.update_data(group=message.text.strip())
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=tr(lang, "send_phone_button"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(tr(lang, "ask_phone"), reply_markup=kb)
    await state.set_state(RegisterForm.phone)

@router.message(RegisterForm.phone)
async def reg_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")
    phone = message.contact.phone_number if message.contact else message.text.strip()

    async with async_session() as session:
        res = await session.execute(select(Student).where(Student.tg_id == message.from_user.id))
        student = res.scalar()
        if student:
            student.full_name = data["full_name"]
            student.group = data["group"]
            student.phone = phone
            await session.commit()

    await state.clear()
    await message.answer(tr(lang, "register_done"), reply_markup=ReplyKeyboardRemove())
    await send_level_choice(message, lang)

# ===== Выбор уровня =====
async def send_level_choice(message: types.Message, lang="ru"):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐍 Beginner", callback_data="level_beginner")],
        [InlineKeyboardButton(text="🔥 Intermediate", callback_data="level_intermediate")],
        [InlineKeyboardButton(text="🧠 Advanced", callback_data="level_advanced")]
    ])
    await message.answer(tr(lang, "choose_level"), reply_markup=kb)

@router.callback_query(lambda c: c.data.startswith("level_"))
async def set_level(callback: types.CallbackQuery):
    level = callback.data.split("_")[1]
    lang = "ru"  # значение по умолчанию

    async with async_session() as session:
        res = await session.execute(select(Student).where(Student.tg_id == callback.from_user.id))
        student = res.scalar()

        if student:
            student.level = level
            lang = student.language or "ru"
            await session.commit()
        else:
            # если студент не найден — создаём запись
            student = Student(tg_id=callback.from_user.id, level=level, language=lang)
            session.add(student)
            await session.commit()

    await callback.answer()
    await callback.message.answer(tr(lang, "ready"))

# ===== Команды =====
@router.message(Command("restart"))
async def restart(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🔄 Перезапуск регистрации.")
    await send_language_choice(message)

@router.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "ℹ️ Команды:\n"
        "/start — начать регистрацию\n"
        "/profile — мой профиль\n"
        "/restart — перезапуск регистрации\n"
        "/help — помощь\n"
        "/lesson — начать урок\n"
        "/score — мои баллы"
    )
