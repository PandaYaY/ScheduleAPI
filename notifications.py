from work_with_db import db
from authorization import User


__change_keys__ = {
    key[1]: key[0] for key in db.select('select * from "Decode_Change_Type"')
}

select_1_2_lvl = """select id, mac_address from "Users"
where access_level = 1 or (access_level = 2 and department = %s)"""

users_for_delete = """select id, mac_address from "Users"
where access_level = 1 or (access_level = 2 and department = %s) or id = %s"""


def _insert_notif(users: list[tuple[int, list[str]]],
                  change_type: str,
                  table: str,
                  event_ids: list[int]):
    if not users:
        return
    query = 'insert into "Events_Changes" values'
    change_type = __change_keys__[change_type]
    params = ()
    for event_id in event_ids:
        for user in users:
            query = f"{query}\n(%s, %s, %s, %s, %s),"
            params += (user[0], table, event_id, change_type, user[1])

    db.del_ins_upd(query[:-1], params)


def read_notification(_user: User):
    if _user.access_level == 3:
        db.del_ins_upd("""update "Events_Changes"
set mac = array_remove(mac, %s)
where user_id = %s""", (_user.mac, _user.real_id))

    elif _user.access_level in (1, 2):
        db.del_ins_upd("""update "Events_Changes" set mac = array_remove(mac, %s)
where user_id = %s and change_type in (2, 3)""", (_user.mac, _user.real_id))

    db.del_ins_upd("delete from \"Events_Changes\" where mac = '{}'")
    db.commit()


def _remove_notifications(table: str, event_id: int):
    """Удаление всех связанных уведомлений"""
    db.del_ins_upd('delete from "Events_Changes" where table_name = %s and id = %s',
                   (table, event_id))


def create_event_notif(table: str, event_ids: list[int], department: int, teacher: int = None):
    users = db.select("""select id, mac_address from "Users" as u
where u.access_level = 1 or (u.access_level = 2 and u.department = %s) or u.id = %s""",
                      (department, teacher))

    _insert_notif(users, "create", table, event_ids)


def confirm_event_notif(table: str, event_id: int, department: int, teacher: int):
    _remove_notifications(table, event_id)

    users = db.select(select_1_2_lvl, (department,))
    _insert_notif(users, "update", table, [event_id])

    teacher = db.select('select id, mac_address from "Users" where id = %s', (teacher,))
    _insert_notif(teacher, "create", table, [event_id])


def update_event_notif(table: str, event_id: int, department: int, old_teacher: int, new_teacher: int = None):
    _remove_notifications(table, event_id)

    if new_teacher:
        users = db.select(select_1_2_lvl, (department,))
        _insert_notif(users, "update", table, [event_id])

        old_teacher = db.select('select id, mac_address from "Users" where id = %s and access_level <> 2',
                                (old_teacher,))
        _insert_notif(old_teacher, "delete", table, [event_id])

        new_teacher = db.select('select id, mac_address from "Users" where id = %s ', (new_teacher,))
        _insert_notif(new_teacher, "create", table, [event_id])
    else:
        users = db.select(f"{select_1_2_lvl} or id = %s", (department, old_teacher))
        _insert_notif(users, "update", table, [event_id])


def share_event_notif(table: str, auc_id: int, teachers: list[int]):
    users = db.select('select id, mac_address from "Users" where id in %s', (tuple(teachers),))

    _insert_notif(users, "create", table, [auc_id])


def unshare_event_notif(auc_id: int, teachers: list[int]):
    select_online_3_lvl = 'select id, mac_address from "Users" where id in %s'
    users = db.select(select_online_3_lvl, (tuple(teachers),))

    _remove_notifications("Auction", auc_id)

    _insert_notif(users, "delete", "Auction", [auc_id])


def delete_event_notif(table: str,
                       event_id: int,
                       department: int,
                       teacher: int):
    _remove_notifications(table, event_id)
    users = db.select(users_for_delete, (department, teacher))

    _insert_notif(users, "delete", table, [event_id])
