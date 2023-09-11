from datetime import date, time
from datetime import datetime
from work_with_db import db

teachers_query = """with available (id) as (select id from "Users"
where id not in (
select id from "Users" usr
join (select date(generate_series(start_date, end_date, '1 day')), start_time, end_time, user_id from "Blocked_User"
      union
      select date, start_time, end_time, teacher_id from "One_Time_Events"
      union
      select date, start_time, end_time, teacher_id from "Sub_Regular_Events") as foo on usr.id = foo.user_id
where ({})))

select usr.id, coalesce(sum(end_time - start_time), '00:00') as delta from (
select * from 
(select date(generate_series(start_date, end_date, '1 day')), start_time, end_time, user_id from "Blocked_User"
union
select date, start_time, end_time, teacher_id from "One_Time_Events"
union
select date, start_time, end_time, teacher_id from "Sub_Regular_Events") as _
where date > %s -- start_month
) as foo

right join "Users" usr on usr.id = foo.user_id
where usr.id in (select * from available) and department = %s and %s = any(skills) -- department, subject

group by usr.id
order by delta"""

classrooms_query = """with available (id) as (select id from "Classrooms"
where id not in (
select id from "Classrooms" c
join (select date(generate_series(start_date, end_date, '1 day')), start_time, end_time, classroom_id from "Blocked_Classroom"
      union
      select date, start_time, end_time, classroom from "One_Time_Events"
      union
      select date, start_time, end_time, classroom from "Sub_Regular_Events") as foo on c.id = foo.classroom_id
where ({})))

select c.id, coalesce(sum(end_time - start_time), '00:00') as delta from (
select * from 
(select date(generate_series(start_date, end_date, '1 day')), start_time, end_time, classroom_id from "Blocked_Classroom"
union
select date, start_time, end_time, classroom from "One_Time_Events"
union
select date, start_time, end_time, classroom from "Sub_Regular_Events") as _
where date > %s -- start_month
) as foo
right join "Classrooms" c on c.id = foo.classroom_id

where c.id in (select * from available) and department = %s and %s = any(subject)

group by c.id
order by delta"""


#############################################################################################################


def gen_query(per: list[list[date], time, time, str]) -> str:
    query = []
    for days, s_time, e_time, _ in per:
        for day in days:
            query.append(f"(foo.date = '{day}' and foo.start_time <= '{e_time}' and foo.end_time >= '{s_time}')")
    return ' or '.join(query)


def avg_subjects(
        department: int,
        subject: int,
        start_date: date,
        periodicity: list[list[date], time, time, str],
) -> tuple[int, str] or tuple[None, None]:
    dates_query = gen_query(periodicity)

    start_month = datetime(start_date.year, start_date.month, 1)

    params = (start_month, department, subject)

    teachers = db.select(teachers_query.format(dates_query), params)
    classrooms = db.select(classrooms_query.format(dates_query), params)

    if not all((teachers, classrooms)):
        return None, None

    return teachers[0][0], classrooms[0][0]


if __name__ == "__main__":
    department_ = 1
    subject_ = 15

    s_date = date(2023, 3, 30)
    e_date = date(2023, 3, 30)

    per_ = [[-4, '08:00', '08:45', 'Очно']]

    from gen_date import gen_date

    per_ = gen_date(s_date, e_date, per_)

    a = avg_subjects(department_, subject_, s_date, per_)
    print(a)
