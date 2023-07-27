import asyncio
import logging
import os
from datetime import datetime, timedelta

import peewee
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from models import Link, User, UserEvent
from pyparsing import ParseException, Word, alphas, nums

load_dotenv()
tg_token = os.getenv("TOKEN")
hour = os.getenv("HOUR")
minute = os.getenv("MINUTE")
rus_alphas = 'йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ'
chars = r"+.,-?:;'_=()/|\&^*%$#@!№"+" "
symbols = alphas + rus_alphas + chars + nums + """"""""
logging.basicConfig(level='WARNING')
logger = logging.getLogger()


try:
    User.create_table()
    Link.create_table()
    logger.info("Table of users created successfully!")
except peewee.OperationalError:
    logger.warning("Table of users already exists")


bot = Bot(token=tg_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Action(StatesGroup):
    entering_event = State()
    deleting_event = State()


class NewUser(StatesGroup):
    adding_user = State()


@dp.message_handler(commands=['start'])
async def start_msg(message: types.Message):
    """
    This function shows the keyboad.
    """
    kb = [[types.KeyboardButton(text="Добавить событие")],
          [types.KeyboardButton(text="Удалить событие")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Выберете действие", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == 'Добавить событие')
async def add_event(message: types.Message, state: FSMContext):
    """
    This function processes button Добавить событие, sends message
    with format of message with format for adding event and set state
    of waiting message with data of users event.
    """
    msg = "Введите сообщение в следующем фоормате:\n"
    msg += "Название: название_события\n"
    msg += "Место: место_исполнения\n"
    msg += "Время: время_исполнения\n"
    msg += "Описание: описание_события\n\n"
    msg += "Время нужно ввести в следующем формате:\n"
    msg += " год-месяц-день-час-минута"
    await message.answer(msg, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Action.entering_event)


@dp.message_handler(state=Action.entering_event)
async def event_insert(message: types.Message, state: FSMContext):
    """
    This function recieves message with data of event and parsing it.
    Recieved data after parsing enserts entry to table of events.
    If time difference between time of event and time now is less
    than one day, event (UserEvent object) and chat id are
    transmited to near_event().
    If user not found, function set state of adding of new user.
    """
    symbols = alphas + rus_alphas + chars + nums
    event_name = "Название:" + Word(symbols).setResultsName("name")
    event_place = "Место:" + Word(symbols).setResultsName("place")
    hours = Word(nums).setResultsName("hour")
    minutes = Word(nums).setResultsName("minute")
    time = hours + "-" + minutes
    years = Word(nums).setResultsName("year")
    months = Word(nums).setResultsName("month")
    date = years + "-" + months
    days = Word(nums).setResultsName("day")
    event_time = "Время:" + date + "-" + days + "-" + time
    desc = Word(symbols).setResultsName("description")
    event_description = "Описание:" + desc
    info = event_place + event_time + event_description
    message_format = event_name + info
    try:
        data = message_format.parseString(str(message.text))
    except ParseException:
        logger.critical("Entered time is uncorrect")
        await message.answer("Некорректный формат сообщения")
        await state.finish()
        return
    except ValueError:
        logger.critical("Entered time is uncorrect")
        await message.answer("Неправильно указано время")
        await state.finish()
        return
    event_name = data["name"]
    event_place = data["place"]
    year = int(data["year"])
    month = int(data["month"])
    day = int(data["day"])
    hour = int(data["hour"])
    minute = int(data["minute"])
    event_description = data["description"]
    try:
        user = User.get(User.id == message.from_user.id)
    except peewee.DoesNotExist:
        logger.warning("User not fount")
        warn_msg = "Пользователь не найден.\n"
        warn_msg += "Введите название вашей группы и"
        warn_msg += " попробуйте добавить событие снова."
        await message.answer(warn_msg)
        await state.set_state(NewUser.adding_user)
    UserEvent.create_table()
    try:
        new_event = UserEvent.create(name=event_name,
                                     place=event_place,
                                     description=event_description,
                                     time=datetime(year,
                                                   month,
                                                   day,
                                                   hour,
                                                   minute))
    except ValueError:
        await message.answer("Введено неправильное время.")
        logger.critical("Entered time is uncorrect")
        return
    new_event.save()
    new_link = Link.create(user_id=user.id, event_id=new_event.id)
    new_link.save()
    await message.answer("Событие успешно добавлено в базу данных.")
    logger.warning("Event added successfully!")
    period = datetime(year,
                      month,
                      day,
                      hour,
                      minute) - datetime.now()
    if period <= timedelta(days=1):
        await near_events(message.chat.id, [new_event])
    await state.finish()


@dp.message_handler(state=NewUser.adding_user)
async def add_user(message: types.Message, state: FSMContext):
    """
    This function processes state of adding of new user,
    recieves name of group and add user in table of users.
    """
    user_group = message.text
    user = User.create(id=message.from_user.id,
                       group=user_group)
    user.save()
    await state.finish()
    await message.answer("Пользователь успешно добавлен в базу данных.")
    logger.info("User added successful")


async def today_tasks(chat, task):
    """
    This function recieves chat id and event (UserEvent object) and sends
    recall message in telegram.
    """
    period = task.time-datetime.now()
    sleep_time = period.total_seconds()
    if sleep_time < 0:
        sleep_time = 0
    await asyncio.sleep(sleep_time)
    msg = f"Название: {task.name}\n"
    msg += f"есто проведения: {task.place}\n"
    msg += f"Описание: {task.description}"
    await bot.send_message(chat_id=chat, text=msg)
    return


async def near_events(chat, task_list):
    """
    This function recieves chat id and list of events
    delete it and its link and transmit event and chat id
    to today_tasks().
    """
    tasks = []
    for task in task_list:
        trash_task = UserEvent.get(UserEvent.id == task.id)
        trash_link = Link.delete().where(Link.event_id == trash_task.id)
        trash_link.execute()
        trash_task.delete_instance()
        task_coroutine = today_tasks(chat, task)
        tasks.append(task_coroutine)
        await asyncio.gather(*tasks)


async def get_event(chat):
    """
    This function recieves chat id and retrieve events (UserEvent objects)
    for user with this chat id and sends message with lists of events in
    telegram.
    If time difference between time of event and time now is less
    than one day, event (UserEvent object) and chat id are
    transmited to near_event().
    """
    try:
        user = User.get(User.id == chat)
    except peewee.DoesNotExist:
        logger.critical("User not fount")
        return
    time_now = datetime.now()
    event_day = UserEvent.time.day
    event_time = UserEvent.time
    time_now_3 = time_now + timedelta(days=3)
    time_now_7 = time_now + timedelta(days=7)
    time_now_14 = time_now + timedelta(days=14)
    today_list = UserEvent.select().join(Link).where(Link.user_id == user.id,
                                                     event_day == time_now.day)
    near_list = UserEvent.select().join(Link).where(Link.user_id == user.id,
                                                    event_time >= time_now_3,
                                                    event_time <= time_now_7)
    week_list = UserEvent.select().join(Link).where(Link.user_id == user.id,
                                                    event_time >= time_now_7,
                                                    event_time <= time_now_14)
    recall_msg = "Сегодняшние дела:\n"
    for task in today_list:
        recall_msg += f"Название: {task.name}\n"
        recall_msg += f"Место проведения: {task.place}\n"
        recall_msg += f"Описание: {task.description}\n"
    recall_msg += "\nДела на  этой неделе:\n"
    for task in near_list:
        recall_msg += f"Название: {task.name}\n"
        recall_msg += f"Место проведения: {task.place}\n"
        recall_msg += f"Описание: {task.description}\n"
    recall_msg += "\nДела через неделю:\n"
    for task in week_list:
        recall_msg += f"Название: {task.name}\n"
        recall_msg += f"Место проведения: {task.place}\n"
        recall_msg += f"Описание: {task.description}\n"
    await bot.send_message(chat_id=chat, text=recall_msg)
    await near_events(chat, today_list)


async def massive_recall():
    """
    This function retrieves ids of users and
    run get_event() for each user in table of users.
    """
    user_list = User.select()
    for user_entry in user_list:
        await get_event(user_entry.id)


def day_recall():
    """
    This function runs daily run of massive_recall().
    """
    scheduler = AsyncIOScheduler()
    scheduler.add_job(massive_recall, "cron", hour=hour, minute=minute)
    scheduler.start()


@dp.message_handler(lambda message: message.text == 'Удалить событие')
async def drop_event(message: types.Message, state: FSMContext):
    """
    This function processes button Удалить событие and set state
    of waiting message with name of users event.
    """
    await message.answer("Введите название события",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Action.deleting_event)


@dp.message_handler(state=Action.deleting_event)
async def event_delete(message: types.Message, state: FSMContext):
    """
    This function processes state of waiting message with name
    of event that user want to delete and delete it.
    """
    event_name = message.text
    links = Link.select().where(Link.user_id == message.from_user.id)
    for link in links:
        try:
            event = UserEvent.get(UserEvent.id == link.event_id,
                                  UserEvent.name == event_name)
            this_link = Link.get(Link.event_id == event.id,
                                 Link.user_id == link.user_id)
            event.delete_instance()
            this_link.delete_instance()
        except peewee.DoesNotExist:
            logger.debug("Event doesn't exist")
    await message.answer(f"Событие {event_name} удалено.")
    await state.finish()


if __name__ == '__main__':
    day_recall()
    executor.start_polling(dp)
