from flask import abort
from psycopg2.sql import SQL, Identifier

from authorization import User
from work_with_db import db
from typisation import is_date, is_time
from commands import processing, found_id

################################################################
block_user = """insert into "Blocked_User" 
(start_date, end_date, start_time, end_time, user_id)
values"""

block_classroom = """insert into "Blocked_Classroom" 
(start_date, end_date, start_time, end_time, classroom_id)
values"""
#################################################################


def gen_block(block: list):
    start_date = is_date(block[0])
    end_date = is_date(block[1])
    start_time = is_time(block[2])
    end_time = is_time(block[3])

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    if start_time > end_time:
        start_time, end_time = end_time, start_time

    return start_date, end_date, start_time, end_time


def create_block(data: dict, _: User) -> dict:
    """
    Создание блокировок
    1. Типизация полученных данных
    2. Ветвление по полям employee и classroom
    3. Сравнение времени и дат
    4. Запись в БД

    ##############################################
    # value: [(start_date, end_date, start_time, end_time)]
    temp_data = {'func': 'create_block',
                 'employee': 1,
                 'value': [('2023-04-01', '2023-04-30', '08:00', '12:00'),
                           ('2023-04-15', '2023-04-16', '08:00', '20:00')]}
    temp_data = {'func': 'create_block',
                 'classroom': '6-02',
                 'value': [('2023-04-01', '2023-04-30', '08:00', '12:00'),
                           ('2023-04-15', '2023-04-16', '08:00', '20:00')]}
    """
    if not (dates := data.get("value")):
        return abort(400)

    if "employee" in data:
        query = block_user
        subj_id = int(data["employee"])
    elif "classroom" in data:
        query = block_classroom
        subj_id = data["classroom"]
    else:
        return abort(400)

    params = ()
    for block in dates:
        params += gen_block(block) + (subj_id,)
        query = f"{query}\n(%s, %s, %s, %s, %s),"

    db.del_ins_upd(query[:-1], params)
    db.commit()
    return {"create_block": "success"}


# def _remove_block(date, block):
#
#
#     if not (start_date <= date <= end_date):
#         abort(error)
#
#     if date == start_date:
#         params = (start_date + timedelta(1), end_date)
#     elif date == end_date:



# def delete_block(data: dict, user: User):
#     try:
#         table = data["table"]
#         block_id = data["id"]
#         date = data["date"]
#     except Exception as e:
#         print('delete_block', e)
#         return abort(400)
#
#     if not found_id(table, block_id):
#         abort(607)
#
#     if date == "full":
#         date = None
#     else:
#         date = is_date(date)
#
#     block = db.select(SQL('select * from {table} where id = %s').format(table=Identifier(table)), (block_id,), True)
#
#     _remove_block(date, block)
#
#     return {"result": "success"}



#######################################################################################################################
teachers_blocks = """select
id, start_date :: text, end_date :: text, start_time :: char(5),
end_time :: char(5), user_id, 'employee' as type_object
from "Blocked_User"
where user_id = %s and start_date <= %s and end_date >= %s"""

classrooms_blocks = """select
id, start_date :: text, end_date :: text, start_time :: char(5),
end_time :: char(5), classroom_id, 'classroom' as type_object
from "Blocked_Classroom"
where classroom_id = %s and start_date <= %s and end_date >= %s"""
#######################################################################################################################


def get_block(data: dict, user: User) -> dict:
    """
    Получение блокировок всех пользователей по данной кафедре
    Если ты первый уровень, то получишь ничего

    temp_data = {
        "classroom": '506',
        "start_date": "2023-03-13",
        "end_date": "2023-03-31",
    }

    return key value
    """
    if user.access_level == 1:
        return {"classroom": [], "teacher": []}

    try:
        start_date = is_date(data["start_date"])
        end_date = is_date(data["end_date"])
    except Exception as e:
        print("get_block", e)
        return abort(400)

    if user.access_level == 2:
        if "employee" in data:
            query = teachers_blocks
            subj_id = int(data["employee"])
        elif "classroom" in data:
            query = classrooms_blocks
            subj_id = data["classroom"]
        else:
            return abort(400)

        blocks = processing("block", query, (subj_id, end_date, start_date))
        return blocks
    abort(400)


if __name__ == "__main__":
    temp_user = User(2, 2, 99)

    # temp_data = {'func': 'create_block',
    #              'employee': 1,
    #              'value': [('2023-04-01', '2023-04-30', '08:00', '12:00'),
    #                        ('2023-04-15', '2023-04-16', '08:00', '20:00')]}

    temp_data = {
        "func": "get_block",
        "employee": "1",
        "start_date": "2023-04-13",
        "end_date": "2023-04-30",
    }

    # a = create_block(temp_data, temp_user)
    b = get_block(temp_data, temp_user)

    # print(a)
    print(b)
