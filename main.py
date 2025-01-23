import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv
from sqlalchemy import select, insert, join
from sqlalchemy.orm import sessionmaker, Session

from db import User, engine, Data

load_dotenv()

TOKEN = "7585580064:AAEOfa5TteGDwuEkwv-TyqGSWwYPu0QjMoY"
session = sessionmaker(engine)()
bot = Bot(token=TOKEN)

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
    rkb = ReplyKeyboardBuilder()
    rkb.add(KeyboardButton(text="Saqlangan fayllarni korish"))
    await message.answer(f"Salom {user.first_name} bu bot sizning fayllaringizni turli formatlarda saqlaydi faylni yuborishingizni kutyabman", reply_markup=rkb.as_markup(resize_keyboard=True))

@dp.message(F.text=="Saqlangan fayllarni korish")
async def show_all_kategories(message:Message):
    j = join(
        Data, User, Data.user_id == User.tg_id
    )
    stmt = select(Data).select_from(j).where(Data.file_type=="rasm")
    vieo_q =select(Data).select_from(j).where(Data.file_type=="video")
    doc_q = select(Data).select_from(j).where(Data.file_type=="doc")

    rasm = len(session.execute(stmt).fetchall())
    vieo_son = len(session.execute(vieo_q).fetchall())
    doc_son = len(session.execute(doc_q).fetchall())
    r = rasm if rasm else 0
    v = vieo_son if vieo_son else 0
    d = doc_son if doc_son else 0
    rkb = ReplyKeyboardBuilder()
    rkb.add(KeyboardButton(text=f"Rasmlar {r}"),
            KeyboardButton(text=f"Videolar {v}"),
            KeyboardButton(text=f"Documentlar {d}"),
            KeyboardButton(text="Boshqa 0")).adjust(2, 2)
    await message.answer(text="Sizdagi fayllar middori", reply_markup=rkb.as_markup(resize_keyboard=True))

class VideoCallback(CallbackData, prefix="video"):
    gender: str
@dp.message(F.text.startswith('Videolar'))
async def inline_photo(message:Message):
    j = join(
        Data, User, Data.user_id == User.tg_id
    )
    stmt = select(Data).select_from(j).where(Data.file_type == "video")
    rasm = session.execute(stmt).fetchall()
    buttons = []
    for i in rasm:
        if i[0].file_name == None:
            das = i[0].file_id
            buttons.append([InlineKeyboardButton(text=das, callback_data=PhotoCallback(gender=f"video_{das}").pack())])
        else:
            das = i[0].file_name
            buttons.append([InlineKeyboardButton(text=das, callback_data=PhotoCallback(gender=f"video_{das}").pack())])
    ikb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text="Sizdagi videolar", reply_markup=ikb)

@dp.callback_query(VideoCallback.filter())
async def photo_taker(message:Message, callback_data:VideoCallback):
    dats = callback_data.gender
    query =  dats.split("_")
    j = join(
        Data, User, Data.user_id == User.tg_id
    )
    stmt = select(Data).select_from(j).where(Data.file_name == query[1])
    malu = session.execute(stmt).fetchone()
    if not malu:
        stmt = select(Data).select_from(j).where(Data.file_id == query[1])
        malu = session.execute(stmt).fetchone()
    epladim = malu[0].file_id
    nomi = malu[0].file_name
    await bot.send_video(chat_id=message.from_user.id, video=epladim,
                         caption= nomi)

class DocCallback(CallbackData, prefix="doc"):
    gender: str
@dp.message(F.text.startswith('Documentlar'))
async def inline_photo(message:Message):
    j = join(
        Data, User, Data.user_id == User.tg_id
    )
    stmt = select(Data).select_from(j).where(Data.file_type == "doc")
    rasm = session.execute(stmt).fetchall()
    buttons = []
    for i in rasm:
        if i[0].file_name == None:
            das = i[0].file_id
            buttons.append([InlineKeyboardButton(text=das, callback_data=PhotoCallback(gender=f"doc_{das}").pack())])
        else:
            das = i[0].file_name
            buttons.append([InlineKeyboardButton(text=das, callback_data=PhotoCallback(gender=f"doc_{das}").pack())])
    ikb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text="Sizdagi dokumentaringiz", reply_markup=ikb)

@dp.callback_query(DocCallback.filter())
async def photo_taker(message:Message, callback_data:DocCallback):
    dats = callback_data.gender
    query =  dats.split("_")
    j = join(
        Data, User, Data.user_id == User.tg_id
    )
    stmt = select(Data).select_from(j).where(Data.file_name == query[1])
    malu = session.execute(stmt).fetchone()
    if not malu:
        stmt = select(Data).select_from(j).where(Data.file_id == query[1])
        malu = session.execute(stmt).fetchone()
    epladim = malu[0].file_id
    nomi = malu[0].file_name
    await bot.send_document(chat_id=message.from_user.id, document=epladim,
                         caption= nomi)


class PhotoCallback(CallbackData, prefix="rasm"):
    gender: str
@dp.message(F.text.startswith('Rasmlar'))
async def inline_photo(message:Message):
    j = join(
        Data, User, Data.user_id == User.tg_id
    )
    stmt = select(Data).select_from(j).where(Data.file_type == "rasm")
    rasm = session.execute(stmt).fetchall()
    buttons = []
    for i in rasm:
        if i[0].file_name == None:
            das = i[0].file_id
            buttons.append([InlineKeyboardButton(text=das, callback_data=PhotoCallback(gender=f"rasm_{das}").pack())])
        else:
            das = i[0].file_name
            buttons.append([InlineKeyboardButton(text=das, callback_data=PhotoCallback(gender=f"rasm_{das}").pack())])
    ikb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text="Sizdagi rasmlar", reply_markup=ikb)

@dp.callback_query(PhotoCallback.filter())
async def photo_taker(message:Message, callback_data:PhotoCallback):
    dats = callback_data.gender
    query =  dats.split("_")
    j = join(
        Data, User, Data.user_id == User.tg_id
    )
    stmt = select(Data).select_from(j).where(Data.file_name == query[1])
    malu = session.execute(stmt).fetchone()
    if not malu:
        stmt = select(Data).select_from(j).where(Data.file_id == query[1])
        malu = session.execute(stmt).fetchone()
    epladim = malu[0].file_id
    nomi = malu[0].file_name
    await bot.send_photo(chat_id=message.from_user.id, photo=epladim,
                         caption= nomi)



@dp.message(F.photo)
async def photo_saver(message:Message):
    photo_id = message.photo[0].file_id
    query = insert(Data).values(file_id=photo_id, user_id=message.from_user.id, file_name=message.caption, file_type="rasm")
    session.execute(query)
    session.commit()
    await message.answer(text="Fayl muvoffaqiyatli saqlandi. Kategoriya Rasmlar")

@dp.message(F.video)
async def video_saver(message:Message):
    print(message.video.file_id)
    video_id = message.video.file_id
    query = insert(Data).values(file_id=video_id, user_id=message.from_user.id, file_name=message.caption,
                                file_type="vidoe")
    session.execute(query)
    session.commit()
    await message.answer(text="Fayl muvoffaqiyatli saqlandi. Kategoriya Vidyolar")

@dp.message(F.document)
async def document_saver(message:Message):
    print(message.document)
    doc_id = message.document.file_id
    query = insert(Data).values(file_id=doc_id, user_id=message.from_user.id, file_name=message.caption,
                                file_type="doc")
    session.execute(query)
    session.commit()
    await message.answer(text="Fayl muvoffaqiyatli saqlandi. Kategoriya Documentlar")



async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())