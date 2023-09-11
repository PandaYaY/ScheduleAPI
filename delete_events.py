from flask import abort

from alarm_manager import Manager
from authorization import User
from work_with_db import db

from notifications import delete_event_notif
from commands import found_id
from commands import processing

from events_sql import all_deleted_regular
from events_sql import all_deleted_sub_regular
from events_sql import all_deleted_one_time
from events_sql import dep_deleted_regular
from events_sql import dep_deleted_sub_regular
from events_sql import dep_deleted_one_time


def _delete_one(event_id: int, description: str, user_id: int):
    event = db.select(
        'delete from "One_Time_Events" where id = %s returning *', (event_id,), True
    )

    db.del_ins_upd(
        """insert into "Deleted_One_Time_Events" values
    (%s, now(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (description, user_id) + event[:-1],
    )

    delete_event_notif("One_Time_Events", event_id, event[8], event[6])


def _delete_reg(event_id: int, description: str, user_id: int):
    event = db.select(
        'delete from "Regular_Events" where id = %s returning *', (event_id,), True
    )

    db.del_ins_upd(
        """insert into "Deleted_Regular_Events" values
    (%s, now(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (description, user_id, *event),
    )

    delete_event_notif("Regular_Events", event_id, event[6], event[4])

    sub_events = db.select(
        'delete from "Sub_Regular_Events" where mother_id = %s returning *',
        (event_id,),
    )
    if not sub_events:
        return

    query = """insert into "Deleted_Sub_Regular_Events" values"""
    params = ()

    for sub in sub_events:
        query = f"{query}\n(%s, now(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s),"
        params += (
            description,
            user_id,
            sub[0],  # event_id
            sub[1],  # mother_id
            sub[2],  # date
            sub[5],  # start_time
            sub[6],  # end_time
            event[9],  # subject
            event[8],  # description
            sub[3],  # teacher_id
            sub[4],  # status
            event[6],  # department
            event[15],  # create_date
            event[1],  # program_source
            event[10],  # children_count
            sub[7],  # training_format
            event[5],  # school
            sub[8],  # classroom
        )
        delete_event_notif("Sub_Regular_Events", sub[0], event[6], sub[3])

    db.del_ins_upd(query[:-1], params)


def _delete_sub(event_id: int, description: str, user_id: int):
    """
    1. Получили информацию из материнской таблицы
    2. получили информацию по событию после его удаления
    3. Формирование параметров
    4. Добавление в таблицу удаленных
    5. Создание уведомления
    6. Фиксация
    """

    event = db.select(
        'delete from "Sub_Regular_Events" where id = %s returning *', (event_id,), True
    )

    mother_event = db.select(
        'select * from "Regular_Events" where id = %s', (event[1],), True
    )

    params = (
        description,
        user_id,
        event[0],  # event_id
        event[1],  # mother_id
        event[2],  # date
        event[5],  # start_time
        event[6],  # end_time
        mother_event[9],  # subject
        mother_event[8],  # description
        event[3],  # teacher_id
        event[4],  # status
        mother_event[6],  # department
        mother_event[15],  # create_date
        mother_event[1],  # program_source
        mother_event[10],  # children_count
        event[7],  # training_format
        mother_event[5],  # school
        event[8],  # classroom
    )

    db.del_ins_upd(
        """insert into "Deleted_Sub_Regular_Events" values
    (%s, now(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        params,
    )

    delete_event_notif("Sub_Regular_Events", event_id, mother_event[6], event[3])


def delete_event(data: dict, user: User) -> dict:
    """
    1. Типизация данных
    2. Если нет описания удаления -> оно превращается в пустую строку
    3. Если нет такого события -> return
    4. Ветвление по типу события
    5. Если все в порядке return "Success"
    ####################################################

    data = {'func': 'delete_event',
            'table': 'Regular_Events',
            'event_id': '32',
            'description': 'Захотел удалить просто так'}
    data = {'func': 'delete_event',
            'table': 'Regular_Events',
            'event_id': '32'}
    """
    try:
        table = data["table"]
        event_id = int(data["event_id"])
    except Exception as e:
        print('delete_event', e)
        return abort(400)

    if not found_id(table, event_id):
        return abort(607)

    if not (description := data.get("description")):
        description = ""

    if table == "One_Time_Events":
        _delete_one(event_id, description, user.real_id)
    elif table == "Sub_Regular_Events":
        _delete_sub(event_id, description, user.real_id)
    elif table == "Regular_Events":
        _delete_reg(event_id, description, user.real_id)
    else:
        return abort(400)

    Manager.cancel_by_args(table, event_id)

    db.commit()

    return {"delete_event": "success"}


def get_deleted_events(data: dict, user: User) -> dict:
    """
    Получение всех событий в календарь по уровню доступа.
    1. Определение параметров запроса по уровню доступа
    2. Запрос в БД по уровню доступа
    """
    lvl = user.access_level
    if lvl == 1:
        regular = all_deleted_regular
        sub_regular = all_deleted_sub_regular
        one_time = all_deleted_one_time
        params = ()

    elif lvl == 2:
        regular = dep_deleted_regular
        sub_regular = dep_deleted_sub_regular
        one_time = dep_deleted_one_time
        params = (user.department,)
    else:
        return abort(403)

    return {
        "regular_events": processing("deleted_events", regular, params),
        "sub_regular_events": processing("deleted_events", sub_regular, params),
        "one_time_events": processing("deleted_events", one_time, params),
    }


if __name__ == "__main__":
    temp_user = User(1, 1, 0)

    temp_data = {
        "table": "Regular_Events",
        "event_id": "4",
        "description": "Очень тяжело...",
    }

    a = get_deleted_events(temp_data, temp_user)
    print(a)

    # print(get_deleted_events({}, temp_user))
