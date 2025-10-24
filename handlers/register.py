from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database import async_session, Student

router = Router()

class RegisterForm(StatesGroup):
    full_name = State()
    group = State()
    phone = State()

@router.message(Command("register"))
async def start_register(message: types.Message, state: FSMContext):
    async with async_session() as session:
        res = await session.execute(select(Student).where(Student.tg_id == message.from_user.id))
        if res.scalar():
            await message.answer("Вы уже зарегистрированы. Выберите язык: /language")
            return
    await message.answer("Введи ФИО:")
    await state.set_state(RegisterForm.full_name)

@router.message(RegisterForm.full_name)
async def set_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await message.answer("Введи группу:")
    await state.set_state(RegisterForm.group)

@router.message(RegisterForm.group)
async def set_group(message: types.Message, state: FSMContext):
    await state.update_data(group=message.text.strip())
    await message.answer("Введи номер телефона:")
    await state.set_state(RegisterForm.phone)

@router.message(RegisterForm.phone)
async def finish_register(message: types.Message, state: FSMContext):
    data = await state.get_data()
    async with async_session() as session:
        student = Student(
            tg_id=message.from_user.id,
            full_name=data["full_name"],
            group=data["group"],
            phone=message.text.strip()
        )
        session.add(student)
        await session.commit()
    await state.clear()
    await message.answer("Регистрация завершена. Выберите язык: /language")
