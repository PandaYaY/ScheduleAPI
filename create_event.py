from datetime import datetime, date, timedelta

from flask import abort
from psycopg2.extras import RealDictCursor
from psycopg2.sql import SQL, Identifier

from alarm_manager import Manager
from authorization import User
from avg_subject import avg_subjects
from commands import found_id
from gen_date import gen_date
from new_dict import decodes
from notifications import confirm_event_notif
from notifications import create_event_notif
from notifications import update_event_notif
from typisation import is_date, is_time
from work_with_db import db

_max_children_ = 40

create_one_time_event = """insert into "One_Time_Events" (
    date,
    start_time,
    end_time,
    subject,
    description,
    teacher_id,
    department,
    create_date,
    program_source,
    children_count,
    training_format,
    school,
    classroom
  )
values
(%s, %s, %s, %s, %s, %s, %s, now(), %s, %s, %s, %s, %s)
returning id"""

confirm_one_time = """update "One_Time_Events" set
is_confirm = True
where id = %s"""

create_regular_events = """insert into "Regular_Events" (
    program_source,
    start_date,
    end_date,
    teacher_id,
    school,
    department,
    description,
    subject,
    children_count,
    classroom,
    start_time,
    end_time,
    dates,
    training_format,
    create_date
  )
values"""

generate_regular_events = (
    "\n(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now()),"
)

create_sub_regular = """insert into "Sub_Regular_Events" (
    mother_id,
    date,
    teacher_id,
    start_time,
    end_time,
    training_format,
    classroom
  )
values"""

generate_sub_regular = "\n(%s, %s, %s, %s, %s, %s, %s),"

confirm_sub_regular = """update "Sub_Regular_Events" set
is_confirm = True
where mother_id = %s
returning id"""

update_event_sql = """update {table} set
teacher_id = %s,
classroom = %s,
date = %s,
start_time = %s,
end_time = %s
where id = %s"""

free_teacher_check = """select id
from (
select id, 0 as mother_id, start_date, end_date, start_time, end_time, user_id, 'Blocked_User' as table_name
from "Blocked_User"
union
select id, 0, date, date, start_time, end_time, teacher_id, 'One_Time_Events'
from "One_Time_Events"
union
select id, mother_id, date, date, start_time, end_time, teacher_id, 'Sub_Regular_Events'
from "Sub_Regular_Events"
) as foo
where user_id = %s  -- teacher_id
{}  -- dates
and start_time <= %s and end_time >= %s  -- end_time, start_time
and not ({})  -- event_id"""

free_classroom_check = """select id
from (
select id, 0 as mother_id, start_date, end_date, start_time, end_time, classroom_id, 'Blocked_Classroom' as table_name
from "Blocked_Classroom"
union
select id, 0 as mother_id, date, date, start_time, end_time, classroom, 'One_Time_Events'
from "One_Time_Events"
union
select id, mother_id, date, date, start_time, end_time, classroom, 'Sub_Regular_Events'
from "Sub_Regular_Events"
) as foo
where classroom_id = %s  -- classroom_id
{}  -- dates
and start_time <= %s and end_time >= %s  -- end_time, start_time
and not({})  -- event_id"""


def _alarm(date_: datetime) -> datetime:
    current_date = datetime.now()
    if (current_date + timedelta(1)) > date_:
        return current_date + timedelta(minutes=5)

    if (current_date - timedelta(2)) < date_:
        return date_ - timedelta(1)

    return current_date - timedelta(1)


def _date_check(start_date: date,
                end_date: date,
                days: list[tuple[int, str, str, str]]) -> tuple[date, date, list[list[date], str, str, str]]:
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    if start_date < datetime.now().date():
        abort(604)

    per = list(gen_date(start_date, end_date, days))

    if not per:
        abort(605)

    return start_date, end_date, per


def _create_one_time(start_date: date,
                     periodicity: list[tuple[int, str, str, str]],
                     subject: int,
                     description: str,
                     teacher_id: int,
                     department: int,
                     program_source: int,
                     children_count: int,
                     school: str,
                     classroom_id: str,
                     **_) -> list[int]:
    _, start_time, end_time, t_format = periodicity[0]
    params_ = (
        start_date,
        start_time,
        end_time,
        subject,
        description,
        teacher_id,
        department,
        program_source,
        children_count,
        decodes['Training_Format'][t_format],
        school,
        classroom_id,
    )

    id = db.select(create_one_time_event, params_, True)
    return list(id)


def _create_sub_regular(mother_id: int, mother: list):
    sub_query = create_sub_regular
    sub_params = ()

    teacher_id, classroom, start_time, end_time, dates, t_format, department = mother

    for date_ in dates:
        sub_params += (
            mother_id,
            date_,
            teacher_id,
            start_time,
            end_time,
            t_format,
            classroom,
        )
        sub_query = f"{sub_query}{generate_sub_regular}"

    db.del_ins_upd(sub_query[:-1], sub_params)


def _create_regular(start_date: date,
                    end_date: date,
                    periodicity: list[tuple[list[date], str, str, str]],
                    subject: int,
                    description: str,
                    teacher_id: int,
                    department: int,
                    program_source: int,
                    children_count: int,
                    school: str,
                    classroom_id: str,
                    **_) -> list[int]:
    regular_query = create_regular_events
    regular_params = ()

    for dates, start_time, end_time, t_format in periodicity:
        regular_params += (
            program_source,
            start_date,
            end_date,
            teacher_id,
            school,
            department,
            description,
            subject,
            children_count,
            classroom_id,
            start_time,
            end_time,
            sorted(dates),
            decodes["Training_Format"][t_format],
        )

        regular_query = f"{regular_query}{generate_regular_events}"

    regular_query = f"""{regular_query[:-1]}
returning id, teacher_id, classroom, start_time, end_time, dates, training_format, department"""

    regular = db.select(regular_query, regular_params)

    for event in regular:
        _create_sub_regular(event[0], event[1:])

    return [event[0] for event in regular]


def create_event(data: dict, _: User):
    """
    Создание события
    ##############################################
    temp_data = {'func': 'create_event',
                 'type_event': 'One_Time_Events',
                 'department': 'Биотехнология',
                 'subject': 'Робототехника',
                 'program_source': 'ДОГМ',
                 'description': 'test',
                 'children_count': '132',
                 'periodicity': [(2, '12:32', '14:32', 'Очно')],
                 'start_date': '08/02/2023',
                 'end_date': '08/02/2023',
                 'school': '1315'}

    temp_data = {'func': 'create_event',
                 'type_event': 'Regular_Events',
                 'department': 'Биотехнология',
                 'subject': 'Робототехника',
                 'program_source': 'ДОГМ',
                 'description': 'test',
                 'children_count': '132',
                 'periodicity': [(2, '12:32', '14:32', 'Очно'),
                                 (9, '12:32', '14:32', 'Очно')],
                 'start_date': '13/02/2023',
                 'end_date': '26/02/2023',
                 'school': '1315'}
    """
    ##############################################################
    try:
        data_ = {"table": data["type"],
                 "start_date": is_date(data["start_date"]),
                 "end_date": is_date(data["end_date"]),
                 "periodicity": data["periodicity"],
                 "school": data["school"],
                 "subject": decodes["Subject"][data["subject"]],
                 "description": data["description"],
                 "department": decodes["Department"][data["department"]],
                 "program_source": decodes["Program_Source"][data["program_source"]],
                 "children_count": int(data["children_count"])}
    except Exception as e:
        print("create_event:", e)
        return abort(400)

    if type(data_["periodicity"]) != list and len(data_["periodicity"][0]) != 4:
        abort(400)

    if data_["children_count"] > _max_children_:
        abort(612)

    print(type(data_["start_date"]), type(data_["end_date"]), type(data_["periodicity"]))
    data_["start_date"], data_["end_date"], data_["periodicity"] = _date_check(data_["start_date"],
                                                                               data_["end_date"],
                                                                               data_["periodicity"])

    teacher_id, classroom_id = avg_subjects(data_["department"],
                                            data_["subject"],
                                            data_["start_date"],
                                            data_["periodicity"])

    if not (teacher_id and classroom_id):
        return abort(606)

    data_["teacher_id"] = teacher_id
    data_["classroom_id"] = classroom_id

    if (data_["table"] == "One_Time_Events") and (data_["start_date"] == data_["end_date"]):
        ids = _create_one_time(**data_)
    elif data_["table"] == "Regular_Events":
        ids = _create_regular(**data_)
    else:
        return abort(400)

    temp = data_["start_date"]
    time_trigger = _alarm(datetime(temp.year, temp.month, temp.day))
    for id_ in ids:
        Manager.add('am_confirm_event', [data_["table"], str(id_)], time_trigger)

    create_event_notif(data_["table"], ids, data_["department"])

    db.commit()
    return {"create_event": "success"}


def am_confirm_event(args: list[str]) -> dict:
    table, event_id = args[:2]
    data = {"table": table, "event_id": event_id}
    return confirm_event(data, ...)


def confirm_event(data: dict, _: User) -> dict:
    """
    data = {'func': 'confirm_event',
            'event_id': '89',
            'table': 'One_Time_Events'}
    """
    try:
        event_id = int(data['event_id'])
        table = data['table']
    except Exception as e:
        print("confirm_event:", e)
        return abort(400)

    if not found_id(table, event_id):
        abort(607)

    if table == "One_Time_Events":
        query = """select array[date], teacher_id, start_time, end_time, training_format, classroom,  department
        from "One_Time_Events" where id = %s"""
        round_event = "id = %s and table_name = 'One_Time_Events'"

    else:
        query = """select dates, teacher_id, start_time, end_time, training_format, classroom,  department
        from "Regular_Events" where id = %s"""
        round_event = "mother_id = %s and table_name = 'Sub_Regular_Events'"

    event = db.select(query, (event_id,), True)

    dates, teacher_id, start_time, end_time, training_format, classroom, department = event

    condition = ' or '.join(map(lambda d: f"'{d}' between foo.start_date and foo.end_date", dates))
    condition = f' and ({condition})'

    teacher_params = (teacher_id, end_time, start_time, event_id)
    busy_teacher = db.select(free_teacher_check.format(condition, round_event), teacher_params)

    classroom_params = (classroom, end_time, start_time, event_id)
    busy_classroom = db.select(free_classroom_check.format(condition, round_event), classroom_params)

    if busy_teacher or busy_classroom:
        abort(608)

    if table == "Regular_Events":
        ids = [event[0] for event in db.select(confirm_sub_regular, (event_id,))]
        create_event_notif("Sub_Regular_Events", ids, department, teacher_id)
    else:
        db.del_ins_upd(confirm_one_time, (event_id,))

    confirm_event_notif(table, event_id, department, teacher_id)

    Manager.cancel_by_args(table, event_id)
    db.commit()
    return {'confirm_event': 'success'}


def update_event(data: dict, _: User) -> dict:
    """
    Перенос времени и/или замена преподавателя
    на уже подтвержденное событие
    """
    try:
        event_id = int(data['event_id'])
        table = data['table']
        teacher = data['teacher']
        classroom = data['classroom']
        start_time = is_time(data['start_time'])
        end_time = is_time(data['end_time'])
        date_ = is_date(data['date'])
    except Exception as e:
        print("update_event:", e)
        return abort(400)

    if not found_id(table, event_id):
        abort(607)

    if table == "One_Time_Events":
        event = db.select('select date, department, teacher_id from "One_Time_Events" where id = %s',
                          (event_id,), True, RealDictCursor)
    elif table == "Sub_Regular_Events":
        event = db.select("""select s.date, r.department, s.teacher_id, s.mother_id from "Sub_Regular_Events" s
        join "Regular_Events" r on s.mother_id = r.id
        where s.id = %s""", (event_id,), True, RealDictCursor)
    else:
        return abort(400)

    cur_teacher_id = db.select('select id from "Users" where fio = %s', (teacher,), True)

    if cur_teacher_id:
        cur_teacher_id = cur_teacher_id[0]
    else:
        abort(609)

    condition = f"and ('{date_}' between foo.start_date and foo.end_date)"
    round_event = f"id = %s and table_name = '{table}'"

    teacher_params = (cur_teacher_id, end_time, start_time, event_id)
    busy_teacher = db.select(free_teacher_check.format(condition, round_event), teacher_params)

    classroom_params = (classroom, end_time, start_time, event_id)
    busy_classroom = db.select(free_classroom_check.format(condition, round_event), classroom_params)

    if busy_teacher or busy_classroom:
        abort(608)

    if table == "Sub_Regular_Events":
        db.del_ins_upd('update "Regular_Events" set dates = array_replace(dates, %s, %s) where id = %s',
                       (event["date"], date_, event["mother_id"]))

    if cur_teacher_id != event['teacher_id']:
        update_event_notif(table, event_id, event["department"], event["teacher_id"], cur_teacher_id)
    else:
        update_event_notif(table, event_id, event["department"], event["teacher_id"])

    params = (cur_teacher_id, classroom, date_, start_time, end_time, event_id)
    db.del_ins_upd(SQL(update_event_sql).format(table=Identifier(table)), params)

    db.commit()

    return {'update_event': 'success'}


def update_regular(data: dict, user: User):
    try:
        event_id = int(data['event_id'])
        teacher = data['teacher']
        classroom = data['classroom']
        start_time = is_time(data['start_time'])
        end_time = is_time(data['end_time'])
        start_date = is_date(data['start_date'])
        end_date = is_date(data['end_date'])
    except Exception as e:
        print("update_event:", e)
        return abort(400)

    if not found_id('Regular_Events', event_id):
        abort(607)

    # dates, old_teacher, department = db.select("""select dates, teacher_id, department
    # from "Regular_Events" where id = %s""", (event_id,), True)
    #
    # new_teacher_id = db.select('select id from "Users" where fio = %s', (teacher,), True)
    #
    # if new_teacher_id:
    #     new_teacher_id = new_teacher_id[0]
    # else:
    #     abort(609)
    #
    # condition = ' or '.join(map(lambda x: f"'{x}' between foo.start_date and foo.end_date", dates))
    # condition = f"and ({condition})"
    # round_event = f"mother_id = %s and table_name = 'Sub_Regular_Events'"
    #
    # teacher_params = (new_teacher_id, end_time, start_time, event_id)
    # busy_teacher = db.select(free_teacher_check.format(condition, round_event), teacher_params)
    #
    # classroom_params = (classroom, end_time, start_time, event_id)
    # busy_classroom = db.select(free_classroom_check.format(condition, round_event), classroom_params)
    #
    # if busy_teacher or busy_classroom:
    #     abort(608)
    #
    # if new_teacher_id != old_teacher:
    #     update_event_notif("Regular_Events", event_id, department, old_teacher, new_teacher_id)
    # else:
    #     update_event_notif("Regular_Events", event_id, department, new_teacher_id)
    #
    # params = (new_teacher_id, classroom, date_, start_time, end_time, event_id)
    # db.del_ins_upd(SQL(update_event_sql).format(table=Identifier(table)), params)
    #
    # db.commit()
    #
    # return {'update_event': 'success'}


# bind ######################################################
Manager.bind_func("am_confirm_event", am_confirm_event)
# bind ######################################################


if __name__ == "__main__":
    # print(decodes)

    temp_user = User(1, 1, 99)

    temp_data = {'func': 'create_event',
                 'type': 'One_Time_Events',
                 'department': 'Аддитивных технологий',
                 'program_source': 'Технопарк',
                 'subject': 'Основы 3д  моделирования',
                 'children_count': '13',
                 'school': '...',
                 'description': '...',
                 'periodicity': [(-2, '12:00', '13:00', 'Очно')],
                 'start_date': '2023-04-25',
                 'end_date': '2023-04-25',
                 'auth_id': '64b0248977c38a35c8a41e53'}

    # [[-3, '08:00', '08:45', 'Очно'],
    #  [-1, '08:00', '08:45', 'Очно']], 'start_date': '2023-04-07', 'end_date': '2023-04-08',
    # temp_data = {
    #     "func": "create_event",
    #     "type": "Regular_Events",
    #     "department": "Тестовая кафедра",
    #     "subject": "Упаковка будущего",
    #     "program_source": "ЦТПО",
    #     "description": "test",
    #     "children_count": "30",
    #     "periodicity": [(2, "12:32", "14:32", "Очно"), (9, "12:32", "14:32", "Очно")],
    #     "start_date": "2023-05-01",
    #     "end_date": "2023-05-30",
    #     "school": "1315",
    # }

    # create_event(temp_data, temp_user)

    # temp_data = {'func': 'confirm_event',
    #              'teacher': 'Иванов Иван',
    #              'classroom': '506',
    #              'start_time': '16:00',
    #              'end_time': '17:00',
    #              'date': '2023-04-19',
    #              'event_id': '417',
    #              'table': 'Sub_Regular_Events'}

    temp_data = {'func': 'update_event',
                 'teacher': 'Галченков Сергей',
                 'classroom': '506',
                 'start_time': '11:30',
                 'end_time': '12:30',
                 'table': 'One_Time_Events',
                 'date': '2023-04-11',
                 'event_id': '78'}

    # temp_data = {'func': 'create_event',
    #              'type': 'One_Time_Events',
    #              'department': 'Аддитивных технологий',
    #              'program_source': 'ЦТПО',
    #              'subject': 'Общеразвивающая программа - Экология',
    #              'school': '132',
    #              'children_count': '213',
    #              'description': '123',
    #              'periodicity': [[-4, '08:00', '08:45', 'Очно']],
    #              'start_date': '2023-03-30',
    #              'end_date': '2023-03-30',
    #              'auth_id': 'd6be3e41f29ac4558aaa9df5'}

    # a = update_regular(temp_data, temp_user)
    a = update_event(temp_data, temp_user)
    # a = am_confirm_event(['1', '2'])
    # a = create_event(temp_data, temp_user)
    print(a)
    # d = datetime(2023, 4, 16)
    # print(_alarm(d))
