from flask import abort

from authorization import User
from commands import found_id
from work_with_db import db

from new_dict import decodes

# Создание пользователя в таблице User(регистрация)
insert_user = """insert into "Users"
(fio, login, skills, department)
values
(%s, %s, %s,
(select id from "Decode_Department" where name = %s))"""


def create_user(data: dict, user: User) -> dict:
    """
    Parameters:
        data: dict
        user: User class
    ----------
    Creating an account in the database by the administration:
        1) password hashing
        2) search for the department number by name
        3) adding a user to the User table
    ----------
    Создание аккаунта в БД администрацией:
        1) хеширование пароля
        2) поиск номера кафедры по названию
        3) добавление пользователя в таблицу User
    """
    try:
        # hash_pw = sha512("".join([data['password'], 'Eva']).encode()).hexdigest()

        params = (
            data["FIO"],
            data["login"],
            [decodes["Subject"][i] for i in data["skills"]],
            user.department,
        )
    except Exception as e:
        print("create_user:", e)
        return abort(400)

    db.del_ins_upd(insert_user, params)
    db.commit()
    return {"create_user": "success"}


edit_user = 'update "Users" set skills = %s where id = %s'


def set_skills(data: dict, user: User) -> dict:
    """
    Редактирование скилов пользователя
    1. Типизация полученных данных
    2. Если id не найден -> return 'не найден'
    3. Преобразование skills в индексы
    4. Запись в БД

    ############################################

    data = {'func': 'set_skills',
            'employee': 1,
            'skills': ['Робототехника', 'мк']}
    """

    try:
        user_id = data["employee"]
        skills = data["skills"]
    except Exception as e:
        print("set_skills:", e)
        return abort(400)

    if not found_id("Users", user_id):
        return abort(609)

    subjects = decodes["Subject"]
    skills = [subjects[skill] for skill in skills]

    db.del_ins_upd(edit_user, (skills, user_id))
    db.commit()
    return {"set_skills": "success"}


if __name__ == "__main__":
    print(decodes)

    temp_user = User(2, 2, 99)

    temp_data = {
        "func": "set_skills",
        "employee": 1,
        "skills": [
            "Проектно-исследовательская - Микробиология",
            "Общеразвивающая программа - Пищевая экспертиза",
        ],
    }

    a = set_skills(temp_data, temp_user)

    print(a)
