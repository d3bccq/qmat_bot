import db
import asyncio
from datetime import datetime
from config import loggi

date = datetime.now().strftime('%d-%m-%Y, %H:%M')
    
async def add_user(user_id, username, first_name):
    row = db.cur.execute(f"SELECT user_id FROM users WHERE user_id == '{user_id}'").fetchone()
    if row is None:
        db.db_table_val(user_id=user_id, username=username, date=datetime.now().strftime('%d-%m-%Y, %H:%M'), first_name=first_name, answer=None)
        db.db.commit()
        return False
    else:
        return True

    
async def join_chat(message, bot):
    new_member = message.new_chat_members[0]
    username = new_member.username     # Кого пригласили в группу
    who_invited = message.from_user.username            # Кто пригласил
    if username == who_invited:
        await bot.send_message(chat_id=loggi,text="Пользователь: @"f'{username} зашел в чат: \n{message.chat.full_name} [{message.chat.id}]')
    elif username == "qmat_bot":
        await bot.send_message(chat_id=loggi,text=f"Бот добавлен в чат: \n{message.chat.full_name} [{message.chat.id}]'")
        db.db_chat_val(user_id=message.from_user.id, username=who_invited, date=date, first_name=message.from_user.full_name, chat_id=message.chat.id, chat_name=message.chat.full_name, settings=1)
        db.db.commit()
    else:
        await bot.send_message(chat_id=loggi,text="Пользователь: @"f'{username} был приглашен пользователем: @{who_invited} в чат под названием:\n {message.chat.full_name}[{message.chat.id}]')

async def leave_chat(message, bot):
    left_member = message.left_chat_member
    username = left_member.username  
    who_lefted= message.from_user.username   
    if username == who_lefted:
        await bot.send_message(chat_id=loggi,text="Пользователь: @"f'{username} вышел из чата: \n{message.chat.full_name} [{message.chat.id}]')
    elif username == "qmat_bot":
        await bot.send_message(chat_id=loggi,text=f"Бот удалён из чата: \n{message.chat.full_name} [{message.chat.id}]'")
    else:
        await bot.send_message(chat_id=loggi,text="Пользователь: @"f'{username} был удалён пользователем: @{who_lefted} из чата под названием:\n {message.chat.full_name}[{message.chat.id}]')
    