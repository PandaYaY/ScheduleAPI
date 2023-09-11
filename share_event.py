from flask import abort
from psycopg2.sql import SQL, Identifier

from authorization import User
from commands import found_id
from work_with_db import db
from notifications import share_event_notif, unshare_event_notif
from notifications import update_event_notif

available_teacher = f"""select id from "Users" where id not in(
select u.id from (
    select start_date, end_date, start_time, end_time, user_id from "Blocked_User"
    union
    select date, date, start_time, end_time, teacher_id from "One_Time_Events"
    union
    select date, date, start_time, end_time, teacher_id from "Sub_Regular_Events"
) as foo
right join "Users" u on foo.user_id = u.id  -- date, end_time, start_time
where %s between start_date and end_date and start_time <= %s and end_time >= %s) 
and department = %s and %s = any(skills) and id <> %s -- department, subject, u_id"""

free_teacher_check = """select id
from (
select id, start_date, end_date, start_time, end_time, user_id, 'Blocked_User' as table_name
from "Blocked_User"
union
select id, date, date, start_time, end_time, teacher_id, 'One_Time_Events'
from "One_Time_Events"
union
select id, date, date, start_time, end_time, teacher_id, 'Sub_Regular_Events'
from "Sub_Regular_Events"
) as foo
where user_id = %s  -- teacher_id
and %s between start_date and end_date  -- date
and start_time <= %s and end_time >= %s  -- end_time, start_time"""

share_update = """update {table} set
teacher_id = %s
where id = %s"""


def auction(data: dict, user: User):
    """
    Share an event with a teacher.
    """
    try:
        table = data["event_type"]
        event_id = int(data["event_id"])
        description = data["description"]
    except Exception as e:
        print('share_event', e)
        return abort(400)

    if not found_id(table, event_id):
        abort(607)

    if table == 'One_Time_Events':
        params = db.select("""select date, end_time, start_time, department, subject
        from "One_Time_Events" where id = %s""", (event_id,), True)
    else:
        params = db.select("""select date, s.end_time, s.start_time, department, subject from "Sub_Regular_Events" s
        join "Regular_Events" r on r.id = s.mother_id where s.id = %s""", (event_id,), True)

    teachers = db.select(available_teacher, (*params, user.real_id))

    teacher_ids = [teacher[0] for teacher in teachers]

    if teacher_ids:
        auc_id = db.select("""insert into "Auction" (table_name, event_id, teachers, description, create_date)
        values (%s, %s, %s, %s, now()) returning id""", (table, event_id, teachers, description), True)[0]
        share_event_notif("Auction", auc_id, teacher_ids)
        db.commit()
    else:
        abort(606)
    return {"share_event": "success"}


def take_event(data: dict, user: User):
    """

    """
    try:
        table = data["table"]
        event_id = int(data["event_id"])
    except Exception as e:
        print('share_event', e)
        return abort(400)
    if not found_id(table, event_id):
        abort(607)

    date, start_time, end_time, teacher_id = db.select(SQL("""select date, end_time, start_time, teacher_id
    from {table} where id = %s""").format(table=Identifier(table)), (event_id,), True)

    params = (user.real_id, date, end_time, start_time)
    busy_teacher = db.select(free_teacher_check, params)

    if busy_teacher:
        abort(611)

    db.del_ins_upd(SQL(share_update).format(table=Identifier(table)), (user.real_id, event_id))
    update_event_notif(table, event_id, user.department, teacher_id, user.real_id)

    auction = db.select("""delete from "Auction"
    where table_name = %s and event_id = %s
    returning id, teachers""", (table, event_id), True)

    if auction:
        unshare_event_notif(*auction)
    else:
        abort(607)

    db.commit()
    return {"teke_event": "success"}


if __name__ == "__main__":
    temp_user = User(3, 3, 99)
    temp_data = {"table": "Sub_Regular_Events", "event_id": 1}
    a = auction(temp_data, temp_user)
    print(a)
