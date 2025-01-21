import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from sqlalchemy import select, insert
from sqlalchemy.orm import sessionmaker, Session

from db import User, engine
load_dotenv()

TOKEN = "7585580064:AAEOfa5TteGDwuEkwv-TyqGSWwYPu0QjMoY"
session = sessionmaker(engine)()

dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    query = select(User).where(User.tg_id==message.from_user.id)
    user = session.execute(query).scalar()
    if not user:
        data = {"tg_id":message.from_user.id,
                "first_name":message.from_user.first_name,
                "last_name" : message.from_user.last_name,
                "username" : message.from_user.username}
        user = session.execute(insert(User).values(**data).returning(*User.__table__.c)).fetchone()
        session.commit()
    await message.answer(f"Hello {user.first_name} {user.last_name}")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())