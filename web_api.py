from datetime import datetime

from flask import abort
from psycopg2.extras import RealDictCursor

from authorization import User
from work_with_db import db

from events_sql import sample_one_time
from events_sql import sample_sub_regular


teacher_one_time = f'{sample_one_time}\nwhere one.date = %s and u.id = %s'
teacher_sub_regular = f'{sample_sub_regular}\nwhere s.date = %s and u.id = %s'

dep_one_time = f'''{sample_one_time}\nwhere one.date = %s and
one.department = %s and one.teacher_id <> -1'''

dep_sub_regular = f'''{sample_sub_regular}\nwhere s.date = %s and
r.department = %s and s.teacher_id <> -1'''


def web_check_auth(_: dict, __: User):
    return {'check': True}


def web_one_event(data: dict, user: User):
    try:
        date = data['date']
    except Exception as e:
        print('web_one_event', e)
        return abort(400)

    event_date = datetime.strptime(date, '%d.%m.%Y').date()

    if user.access_level == 3:
        one_time = db.select(teacher_one_time, (event_date, user.real_id), cursor_factory_=RealDictCursor)
        sub_regular = db.select(teacher_sub_regular, (event_date, user.real_id), cursor_factory_=RealDictCursor)

    elif user.access_level == 2:
        one_time = db.select(dep_one_time, (event_date, user.department), cursor_factory_=RealDictCursor)
        sub_regular = db.select(dep_sub_regular, (event_date, user.department), cursor_factory_=RealDictCursor)
    else:
        return {'events': []}
    
    return {'events': [dict(i) for i in one_time] + [dict(i) for i in sub_regular]}


if __name__ == '__main__':
    data = {'date': '12.04.2023'}
    a = web_one_event(data, User(3, 3, 99))
    print(a)
