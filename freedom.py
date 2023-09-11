from datetime import date
from flask import abort

from authorization import User
from work_with_db import db

from reversed_time import free_time
from reversed_time import free_date as free_date_
from reversed_time import time_to_str
from reversed_time import join_list

from commands import found_id
from typisation import is_date
from new_dict import decodes

busy_teacher_date = f"""with vars (date) as (values (%s :: date)) -- date
select
u.fio,
case
when (select * from vars) between start_date and end_date then start_time
else '00:00'
end as start_time,
case
when (select * from vars) between start_date and end_date then end_time
else '08:00'
end as end_time

from (
select * from (
select id, start_date, end_date, start_time, end_time, user_id, 'Blocked_User' as table_name from "Blocked_User"
union	
select id, date, date, start_time, end_time, teacher_id, 'One_Time_Events' from "One_Time_Events"
union
select id, date, date, start_time, end_time, teacher_id, 'Sub_Regular_Events' from "Sub_Regular_Events") as bar
where not (id = %s and table_name = %s)) as foo -- event_id, table

right join "Users" u on foo.user_id = u.id
where department = %s and %s = any(skills) -- department, subject
order by fio, start_time, end_time"""

busy_classroom_date = f"""with vars (date) as (values (%s :: date)) -- date
select
c.id,
case
when (select * from vars) between start_date and end_date then start_time
else '00:00'
end as start_time,
case
when (select * from vars) between start_date and end_date then end_time
else '08:00'
end as end_time

from (
select * from (
select id, start_date, end_date, start_time, end_time, classroom_id, 'Blocked_Classroom' as table_name from "Blocked_Classroom"
union	
select id, date, date, start_time, end_time, classroom, 'One_Time_Events' from "One_Time_Events"
union
select id, date, date, start_time, end_time, classroom, 'Sub_Regular_Events' from "Sub_Regular_Events") as bar
where not (id = %s and table_name = %s)) as foo -- event_id, table
right join "Classrooms" c on foo.classroom_id = c.id
where department = %s and %s = any(subject) -- department, subject
order by classroom_id, start_time, end_time"""

busy_teacher_interval = """select u.id, date, start_time, end_time from (
select * from (
    select date(generate_series(start_date, end_date, '1 day')), start_time, end_time, user_id from "Blocked_User"
    union
    select date, start_time, end_time, teacher_id from "One_Time_Events"
    union
    select date, start_time, end_time, teacher_id from "Sub_Regular_Events" ) as bar
where date between %s and %s -- start_date, end_date
) as foo
right join "Users" u on u.id = foo.user_id
where department = %s and %s = any(skills) -- department, subject
order by u.id, date, start_time, end_time"""

busy_classroom_interval = """select c.id, date, start_time, end_time from (
select * from (
select date(generate_series(start_date, end_date, '1 day')), start_time, end_time, classroom_id from "Blocked_Classroom"
union
select date, start_time, end_time, classroom from "One_Time_Events"
union
select date, start_time, end_time, classroom from "Sub_Regular_Events" ) as bar
where date between %s and %s -- start_date, end_date
) as foo
right join "Classrooms" c on c.id = foo.classroom_id
where department = %s and %s = any(subject) -- department, subject
order by c.id, date, start_time, end_time"""


def _group_time(value: list) -> dict:
    if not value:
        return {}

    res = {}
    for id, start, end in value:
        if temp := res.get(id):
            temp.append((start, end))
        else:
            res[id] = [(start, end)]

    return res


def event_freedom(data: dict, user: User) -> dict:
    """
    получение параметров события по table - id
    параметры department skills

    запрос на данную дату (data['date'])
    найти всех по параметрам и закинуть в free_date сереги

    temp_data = {'table': 'One_Time_Events',
                 'event_id': '58',
                 'date': '2023-2-28'}
    return {"teacher": {"Вася Пупкин": [[start_time, end_time], [start_time, end_time]]}
            "classroom": {"506": [[start_time, end_time], [start_time, end_time]]}}
    """
    try:
        table = data["table"]
        event_id = int(data["event_id"])
        selected_date = is_date(data["date"])
    except Exception as e:
        print('event_freedom', e)
        return abort(400)

    if not found_id(table, event_id):
        return abort(607)

    if selected_date < date.today():
        return {"teacher": [], "classroom": []}

    if table == "One_Time_Events":
        query = 'select date, department, subject from "One_Time_Events" where id = %s'
    elif table == "Sub_Regular_Events":
        query = """select date, department, subject from "Sub_Regular_Events" s
        join "Regular_Events" r on s.mother_id = r.id
        where s.id = %s"""
    else:
        return abort(400)

    event_date, department, subject = db.select(query, (event_id,), True)

    if user.access_level == 2:
        if selected_date != event_date:
            return {"teacher": [], "classroom": []}
        # else:
        #     pass
        #     # TODO: сделать вывод преподов свободных только на это время этого cобытия

    params = (selected_date, event_id, table, department, subject)

    teachers = db.select(busy_teacher_date, params)
    classrooms = db.select(busy_classroom_date, params)

    teachers = free_time(_group_time(teachers), selected_date)
    classrooms = free_time(_group_time(classrooms), selected_date)

    return {
        "teacher": teachers,
        "classroom": classrooms,
    }


def _group_subj(value: list) -> list:
    if not value:
        return []

    name = None
    i = -1
    res = []
    for id, date, start, end in value:
        if name == id:
            res[i].append((date, start, end))
        else:
            name = id
            i += 1
            res.append([(date, start, end)])

    return res


def free_date(data: dict, _: User):
    """
    {
        'start_date': '2023-02-27',
        'end_date': '2023-04-09',
        'type': 'regular',
        'department': 'Биотехнология',
        'subject': 'VR'
    }
    """
    try:
        start_date = is_date(data["start_date"])
        end_date = is_date(data["end_date"])
        department = decodes["Department"][data["department"]]
        subject = decodes["Subject"][data["subject"]]
        is_regular = data["type"] == "Regular_Events"
    except Exception as e:
        print("free_date", e)
        return abort(400)

    params = (start_date, end_date, department, subject,)

    teachers = db.select(busy_teacher_interval, params)
    classrooms = db.select(busy_classroom_interval, params)

    if not (teachers and classrooms):
        return {
            "online": [[] for _ in range((end_date - start_date).days)],
            "offline": [[] for _ in range((end_date - start_date).days)],
        }

    teachers = _group_subj(teachers)
    classrooms = _group_subj(classrooms)

    teachers = free_date_(teachers, start_date, end_date, is_regular)
    classrooms = free_date_(classrooms, start_date, end_date, is_regular)

    return {
        "online": time_to_str(join_list(teachers, classrooms)),
        "offline": time_to_str(teachers),
    }


if __name__ == "__main__":
    temp_user = User(1, 1, 0)

    temp_data = {'date': '2023-04-17',
                 'event_id': '9',
                 'table': 'One_Time_Events'}

    a = event_freedom(temp_data, temp_user)
    print(a)

    temp_data = {'func': 'free_date',
                 'start_date': '2023-03-27',
                 'end_date': '2023-05-07',
                 'type': 'One_Time_Events',
                 'department': 'Аддитивных технологий',
                 'program_source': 'ЦТПО',
                 'subject': 'Scratch - программирование с нуля',
                 'children_count': '312',
                 'school': '132',
                 'description': '132',
                 'auth_id': 'cf66792d567548cfbae73c55'}

    # a = free_date(temp_data, temp_user)
    # print(a)
