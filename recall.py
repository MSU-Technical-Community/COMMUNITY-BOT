import logging
from datetime import datetime, timedelta
from threading import Thread
from time import sleep

import peewee
from pyparsing import Word, nums

from models import Link, User, UserEvent

rus_alphas = 'йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ'
chars = r"+.,-?:;'_=()/|\&^*%$#@!№"+" "


logging.basicConfig(level='DEBUG')
logger = logging.getLogger()

try:
    User.create_table()
    Link.create_table()
    logger.warning("Table of users created successfully!")
except peewee.OperationalError:
    logger.warning("Table of users already exists")


"""
add_event() adds new event in database.
It recieves strings with user's name and group and
name, time and place of perfomance and description
of event

WARNING!
time_string must have format:
year-month-day-hour-minute
"""


def add_event(name,
              user_group,
              time_string,
              event_name,
              event_place,
              event_description):
    time = Word(nums) + "-" + Word(nums)
    time = Word(nums) + "-" + Word(nums) + "-" + Word(nums) + "-" + time
    try:
        data = time.parseString(str(time_string))
    except ValueError:
        logger.critical("Entered time is uncorrect")
        return
    year = int(data[0])
    month = int(data[2])
    day = int(data[4])
    hour = int(data[6])
    minute = int(data[8])
    try:
        user = User.get(User.username == name)
    except peewee.DoesNotExist:
        logger.warning("User not fount")
        user = User.create(username=name,
                           group=user_group)
        user.save()
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
        logger.warning("Entered time is uncorrect")
        return
    new_event.save()
    new_link = Link.create(user_id=user.id, event_id=new_event.id)
    new_link.save()
    logger.warning("Event added successfully!")
    period = datetime(year,
                      month,
                      day,
                      hour,
                      minute) - datetime.now()
    if period <= timedelta(days=1):
        near_events([new_event])


"""

"""


def today_tasks(task):
    period = task.time-datetime.now()
    sleep_time = period.total_seconds()
    if sleep_time < 0:
        sleep_time = 0
    sleep(sleep_time)
    print(f"""Название: {task.name} \n
          Место проведения: {task.place}\n
          Описание: {task.description}\n""")
    return


def near_events(task_list):
    threads = []
    for task in task_list:
        trash_task = UserEvent.get(UserEvent.id == task.id)
        trash_link = Link.delete().where(Link.event_id == trash_task.id)
        trash_link.execute()
        trash_task.delete_instance()
        thread = Thread(target=today_tasks, args=(task,))
        threads.append(thread)
        thread.start()
    for th in threads:
        th.join()


def get_event(name):
    try:
        user = User.get(User.username == name)
    except peewee.DoesNotExist:
        logger.critical("User not fount")
        return
    event_now = UserEvent.time.day
    time_now = datetime.now().day
    time_now_3 = datetime.now().day+3
    time_now_7 = datetime.now().day+7
    time_now_14 = datetime.now().day+14
    today_list = UserEvent.select().join(Link).where(Link.user_id == user.id,
                                                     event_now == time_now)
    near_list = UserEvent.select().join(Link).where(Link.user_id == user.id,
                                                    event_now >= time_now_3,
                                                    event_now <= time_now_7)
    week_list = UserEvent.select().join(Link).where(Link.user_id == user.id,
                                                    event_now >= time_now_7,
                                                    event_now <= time_now_14)
    print("Сегодняшние дела:")
    for task in today_list:
        print(f"""Название: {task.name}
              Место проведения: {task.place}
              Описание: {task.description}""")
    print("Дела на этой неделе:")
    for task in near_list:
        print(f"""Название: {task.name}
              Место проведения: {task.place}
              Описание: {task.description}""")
    print("Дела через неделю:")
    for task in week_list:
        print(f"""Название: {task.name}
              Место проведения: {task.place}
              Описание: {task.description}""")
    near_events(today_list)


def drop_event(name, event_name):
    user = User.get(User.username == name)
    links = Link.select().where(Link.user_id == user.id)
    for link in links:
        try:
            event = UserEvent.get(UserEvent.id == link.event_id,
                                  UserEvent.name == event_name)
            this_link = Link.get(Link.event_id == event.id,
                                 Link.user_id == link.user_id)
            event.delete_instance()
            this_link.delete_instance()
            logger.warning(f"Event {event_name} was deleted")
        except peewee.DoesNotExist:
            logger.debug("Event doesn't exist")
