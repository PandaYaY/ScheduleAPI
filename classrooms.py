from flask import abort

from authorization import User
from commands import found_id
from work_with_db import db

from new_dict import decodes

# Создание аудитории в таблице Classrooms(регистрация)
insert_classroom = """insert into "Classrooms"
(id, seats_number, computers_number, subject, description, department)
values
(%s, %s, %s, %s, %s, %s)"""


def create_classroom(data: dict, user: User) -> dict:
    """
    Создание новой аудитории
    #################################################
    temp_data = {'classroom': 'test_class',
                 'seats_number': '15',
                 'computers_number': '14',
                 'skills': ['Питон', 'Скретч', 'Блендер'],
                 'description': 'Тестовая аудитория'}
    """
    try:
        number = data["classroom"]
        seats_number = int(data["seats_number"])
        computers_number = int(data["computers_number"])
        skills = data["skills"]
        description = data["description"]
    except Exception as e:
        print("create_classroom:", e)
        return abort(400)

    if seats_number < computers_number:
        abort(601)

    if found_id("Classrooms", number):
        abort(602)

    subjects = decodes["Subject"]

    params = (
        number,
        seats_number,
        computers_number,
        sorted([subjects[i] for i in skills]),
        description,
        user.department,
    )

    db.del_ins_upd(insert_classroom, params)
    db.commit()
    return {"create_classroom": "success"}


edit_classroom = """update "Classrooms" set
subject = %s,
seats_number = %s,
computers_number = %s
where id = %s"""


def set_classroom(data: dict, _: User) -> dict:
    """
    Редактирование аудитории
    1. Типизация данных
    2. Если не найдена аудитория -> return 'не найден'
    3. Проверка на разницу посадочных мест и компьютеров
    4. Запись в БД

    #####################################################

    temp_data = {'classroom': '506',
                 'seats_number': '12',
                 'computers_number': '11',
                 'skills': ['Питон', 'Робототехника']}
    """
    try:
        classroom_id = data["classroom"]
        seats_number = int(data["seats_number"])
        computers_number = int(data["computers_number"])
        skills = data["skills"]
    except Exception as e:
        print("set_classroom:", e)
        return abort(400)

    if not found_id("Classrooms", classroom_id):
        return abort(603)

    if seats_number < computers_number:
        return abort(601)

    subjects = decodes["Subject"]
    params = (
        [subjects[skill] for skill in skills],
        seats_number,
        computers_number,
        classroom_id,
    )

    db.del_ins_upd(edit_classroom, params)
    return {"set_classroom": "success"}


if __name__ == "__main__":
    # print(decodes)
    temp_user = User(2, 2, 99)

    # temp_data = {
    #     "classroom": "test_class",
    #     "seats_number": "15",
    #     "computers_number": "14",
    #     "skills": ["Общеразвивающая программа - Пищевая экспертиза"],
    #     "description": "Тестовая аудитория",
    # }

    temp_data = {
        "func": "set_classroom",
        "classroom": "506",
        "skills": ["Общеразвивающая программа - Пищевая экспертиза"],
        "seats_number": "100",
        "computers_number": "15",
    }

    # a = create_classroom(temp_data, temp_user)
    b = set_classroom(temp_data, temp_user)

    print(b)
