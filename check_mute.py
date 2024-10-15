from aiogram.fsm.state import State, StatesGroup
import asyncio
from red import r
import asyncio
from aiogram.fsm.context import FSMContext
from collections import deque


class MuteStates(StatesGroup):
    muted = State()


LIMIT = 5
MUTE_TIME = 30


async def check_redis(message, state: FSMContext):
    count = r.get(str(message.from_user.id))
    if count is None:
        r.set(str(message.from_user.id), 1, ex=MUTE_TIME)
        return False
    else:
        count = int(count)
        if count >= LIMIT:
            current_state = await state.get_state()
            if current_state != MuteStates.muted.state:
                print(f"Пользователь: {message.from_user.full_name} был замучен")
                await state.set_state(MuteStates.muted)  # Устанавливаем состояние мута
                await asyncio.sleep(MUTE_TIME)  # Ждем время мута
                await state.clear()  # Завершаем состояние мута (очищаем состояние)
                r.delete(str(message.from_user.id))
                print(f"Пользователь: {message.from_user.full_name} был размучен")
            return True
        else:
            r.set(str(message.from_user.id), count + 1, ex=MUTE_TIME)
            return False


async def mutekub(message, state: FSMContext):
    r.set(str(message.from_user.id), 1, ex=600)
    current_state = await state.get_state()
    if current_state != MuteStates.muted.state:
        print(f"Пользователь: {message.from_user.full_name} кинул куб и замутился")
        await state.set_state(MuteStates.muted)  # Устанавливаем состояние мута
        await asyncio.sleep(600)# Ждем время мута 
        await state.clear()  # Завершаем состояние мута (очищаем состояние)
        print(f"Пользователь: {message.from_user.full_name} размутился")
