from flask import abort

from authorization import User
from notifications import read_notification
from commands import processing
from typisation import is_date

from events_sql import teacher_regular_events
from events_sql import all_regular_events
from events_sql import dep_regular_events

from events_sql import teacher_sub_regular_events
from events_sql import dep_sub_regular_events
from events_sql import all_sub_regular_events

from events_sql import teacher_one_time_events
from events_sql import dep_one_time_events
from events_sql import all_one_time_events

from events_sql import full_all_reg
from events_sql import full_all_sub_regular
from events_sql import full_all_one_time

from events_sql import full_dep_reg
from events_sql import full_dep_sub_regular
from events_sql import full_dep_one_time

from events_sql import full_teacher_reg
from events_sql import full_teacher_sub_regular
from events_sql import full_teacher_one_time

from events_sql import new_events_regular
from events_sql import new_events_sub_regular
from events_sql import new_events_one_time

from events_sql import auction_events
from events_sql import new_events_auction


def get_course(_: dict, user: User) -> dict:
    """
    Получение всех курсов по уровню доступа.
    1. Определение параметров запроса по уровню доступа
    2. Запрос в БД по уровню доступа
    """
    lvl = user.access_level
    if lvl == 1:
        query = all_regular_events
        params = ()
    elif lvl == 2:
        query = dep_regular_events
        params = (user.department,)
    else:
        query = teacher_regular_events
        params = (user.real_id,)

    return processing("regular_events", query, params)


def get_events(data: dict, user: User) -> dict:
    """
    Получение всех событий в календарь по уровню доступа.
    1. Определение параметров запроса по уровню доступа
    2. Запрос в БД по уровню доступа
    """
    try:
        start_date = is_date(data["start_date"])
        end_date = is_date(data["end_date"])
    except Exception as e:
        print("get_events:", e)
        return abort(400)

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    lvl = user.access_level
    if lvl == 1:
        sub_regular, one_time = all_sub_regular_events, all_one_time_events
        params = (start_date, end_date)

    elif lvl == 2:
        sub_regular, one_time = dep_sub_regular_events, dep_one_time_events
        params = (start_date, end_date, user.department)

    else:
        sub_regular, one_time = teacher_sub_regular_events, teacher_one_time_events
        params = (start_date, end_date, user.real_id)

    return {
        "sub_regular_events": processing("one_time_events", sub_regular, params),
        "one_time_events": processing("one_time_events", one_time, params),
    }


def full_load(_: dict, user: User) -> dict:
    """
    Подгрузить все таблицы
    """
    lvl = user.access_level
    if lvl == 1:
        reg = full_all_reg
        sub_regular = full_all_sub_regular
        one_time = full_all_one_time
        params = ()

    elif lvl == 2:
        reg = full_dep_reg
        sub_regular = full_dep_sub_regular
        one_time = full_dep_one_time
        params = (user.department,)
    else:
        reg = full_teacher_reg
        sub_regular = full_teacher_sub_regular
        one_time = full_teacher_one_time
        params = (user.real_id,)
    events = {
        "regular_events": processing("regular_events", reg, params),
        "sub_regular_events": processing("one_time_events", sub_regular, params),
        "one_time_events": processing("one_time_events", one_time, params),
        "ads": {"key": [], "value": []},
    }

    if lvl == 3:
        events["ads"] = processing("one_time_events", auction_events, (user.real_id,))
    return events


def new_events(_: dict, user: User) -> dict:
    """
    Подгрузка всех изменений событий,
    то есть мы выводим всю инфу по измененному ивенту и добавляем ему ключ change_type, по которому ориентируемся
    """
    notif = {
        "regular_events": processing(
            "regular_events", new_events_regular, (user.real_id, user.mac)
        ),
        "sub_regular_events": processing(
            "one_time_events", new_events_sub_regular, (user.real_id, user.mac)
        ),
        "one_time_events": processing(
            "one_time_events", new_events_one_time, (user.real_id, user.mac)
        ),
    }

    if user.access_level == 3:
        notif["ads"] = processing(
            "one_time_events", new_events_auction, (user.real_id, user.mac)
        )

    # TODO: update_const
    # if db.select("select event")

    read_notification(user)

    return notif


if __name__ == "__main__":
    temp_user = User(1, 1, 99)

    # res = new_events({"year": 2023, "month": 3}, temp_user)
    res = get_course(..., temp_user)
    from pprint import pprint
    pprint(res)

