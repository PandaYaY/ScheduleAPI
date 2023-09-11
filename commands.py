from psycopg2.extras import RealDictCursor

from work_with_db import db

_key_ = {
    "regular_events": {
        "id": "id_event",
        "start_date": "date",
        "end_date": "end_date",
        "start_time": "start_time",
        "end_time": "end_time",
        "department": "department",
        "fio": "teacher",
        "classroom": "classroom",
        "subject": "program",
        "school": "school",
        "description": "description",
        "children_count": "count_students",
        "program_source": "source",
        "dates": "days_event",
        "training_format": "training_format",
        "course_status": "status",
        "change_type": "change_type",
    },
    "one_time_events": {
        "id": "id_event",
        "date": "date",
        "start_time": "start_time",
        "end_time": "end_time",
        "department": "department",
        "fio": "teacher",
        "classroom": "classroom",
        "subject": "program",
        "school": "school",
        "description": "description",
        "children_count": "count_students",
        "program_source": "source",
        "training_format": "training_format",
        "event_status": "status",
        "change_type": "change_type",
        'type_event': 'type_event',
    },
    "employee": {"id": "employee_id", "fio": "fio", "skills": "skills"},
    "classrooms": {
        "id": "classroom_id",
        "seats_number": "seats_number",
        "computers_number": "computers_number",
        "subject": "skills",
        "description": "description",
    },
    "block": {
        "id": "id_booking",
        "start_date": "start_date",
        "end_date": "end_date",
        "start_time": "start_time",
        "end_time": "end_time",
        "classroom_id": "id_object",
        "user_id": "id_object",
        "type_object": "type_object",
    },
    "deleted_events": {
        "id": "id_event",
        "delete_description": "delete_description",
        "deleting_user": "deleting_user",
        "delete_date": "delete_date",
        "create_date": "create_date",
        "date": "date",
        "start_date": "start_date",
        "end_date": "end_date",
        "start_time": "start_time",
        "end_time": "end_time",
        "department": "department",
        "fio": "teacher",
        "classroom": "classroom",
        "subject": "program",
        "school": "school",
        "description": "description",
        "children_count": "count_students",
        "program_source": "source",
        "training_format": "training_format",
        "event_status": "status",
        "course_status": "status",
        "dates": "days_event",
    },
}


def processing(
        table: str, sql: str, parameters: tuple = None
) -> dict[str: list]:
    """
    После запроса в БД
    Создание словаря формата {'ключ': [ключи...],
                              'значение': [[значения n-ой строки], [...], ...]}
    ключи подменяются функцией replace_keys
    """
    if events := db.select(sql, parameters, cursor_factory_=RealDictCursor):
        return {
            "key": _replace_keys(list(events[0]), table),
            "value": [[event[key] for key in event] for event in events],
        }

    return {"key": [], "value": []}


def _replace_keys(keys: list, table: str) -> list:
    """
    Parameters:
    keys: list - список ключей из бд
    ----------
    Замена бд-ключей, на ключи для интерфейса.
    """
    type_keys = _key_[table]
    return [type_keys[i] for i in keys]


def found_id(table: str, elem_id: int or str) -> bool:
    """
    Проверка существования id в таблице
    """
    if db.select(f'select id from "{table}" where id = %s', (elem_id,)):
        return True
    return False
