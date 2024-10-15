import asyncio
from aiogram import Bot, Dispatcher, types
from config import TOKEN, loggi
from yan import Text_Yan
import db
from aiogram.types import Message
from aiogram import F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from check_database import leave_chat, join_chat, add_user
from check_mute import check_redis
from aiogram.fsm.context import FSMContext
from datetime import datetime
from aiogram.filters import Command

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    
async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)) 
    name = await bot.get_me()
    await bot.send_message(chat_id=loggi, text=f"Я запустился!\nМоё имя: @{name.username}\nСейчас: {datetime.now().strftime('%d-%m-%Y, %H:%M')}") 
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    print(f"Я ЖИВОЙ: @{name.username}")
    
    
@dp.message(F.new_chat_members)
async def somebody_added(message: Message):
    await join_chat(message, bot)

@dp.message(F.left_chat_member)
async def somebody_added(message: Message):
    await leave_chat(message, bot)
    
@dp.message(CommandStart())
async def command_start_handler(message: Message):
    if message.chat.type == "private":
        in_base = await add_user(user_id=message.from_user.id, username=message.from_user.username, first_name=message.from_user.first_name)
        if not in_base:
            await bot.send_message(chat_id=loggi,text=f"@{message.from_user.username} <b>[{message.from_user.full_name}]</b> Пишет старт в лс и добавлен в бд") # Убрали parse_mode="html"
            await message.reply("Ты можешь задавать вопросы прямо в чате или @qmat_bot (вопрос)")
        else:
            None
              
timer = None
async def set_timer(delay):
    global timer
    if timer:
        timer.cancel()
    timer = asyncio.create_task(asyncio.sleep(delay))
    
@dp.inline_query()
async def inline_query(query: types.InlineQuery):
    global timer
    user_id = query.from_user.id
    username = query.from_user.username
    first_name = query.from_user.first_name
    question = query.query
    in_base = await add_user(user_id, username, first_name)
    if in_base:
        try:
            # Устанавливаем таймер
            await set_timer(1) # 1 секунда задержки
            await timer
            answer = await Text_Yan(question)
            if answer:
                results = [
                    types.InlineQueryResultArticle(
                        id='result_button',  # Уникальный id для кнопки "УЗНАТЬ РЕЗУЛЬТАТ"
                        title=answer,
                        input_message_content=types.InputTextMessageContent(
                            message_text=answer, parse_mode="markdown"
                        )
                    )
                ] 
                await query.answer(results)
                await bot.send_message(chat_id=loggi, text=f"Пользователь @{username} [{first_name}] спросил в инлайн режиме: \n{question}")
                db.cur.execute(f"UPDATE users SET answer = '{question}' WHERE user_id == {user_id}")
                db.db.commit()
            else:
                None
        except Exception as e:
            print(f"Ошибка Telegram: {e}")
            await query.answer([
                types.InlineQueryResultArticle(
                    id='error',
                    title='Ошибка',
                    input_message_content=types.InputTextMessageContent(
                        message_text="Произошла ошибка при обработке запроса. Попробуйте ещё раз."
                    )
                )
            ])

@dp.message(Command("send"))
async def update_links(message:types.Message):
    try:
        parts = message.text.split()
        chat_id = int(parts[1])
        text = " ".join(parts[2:])
        await bot.send_message(chat_id=chat_id, text=text)
        await message.reply("Сообщение отправлено!")
    except Exception as e:
        await message.reply(f"Произошла ошибка! {e}")


@dp.message()
async def anything(message: Message, state: FSMContext):
    is_muted = await check_redis(message, state)
    if message.chat.type == 'private' and not is_muted:
        db.cur.execute(f"UPDATE users SET answer = '{message.text}' WHERE user_id == {message.from_user.id}")
        db.db.commit()
        response = await Text_Yan(question=message.text)
        if response:
            await message.reply(text=response, parse_mode="markdown")
            await bot.send_message(chat_id=loggi,text=f"@"f"{message.from_user.username} <b>"f"[{message.from_user.full_name}]</b> Спрашивает: \n{message.text}") # Убрали parse_mode="html"
    else:
        None

if __name__ == "__main__":
    asyncio.run(main())