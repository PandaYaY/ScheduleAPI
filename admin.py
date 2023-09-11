from secrets import choice
from string import ascii_letters, digits
from hashlib import sha512

from transliterate import translit

from work_with_db import db
from new_dict import decodes

insert_acc = """insert into "Users"
(fio, access_level, login, password, department) values
(%s, %s, %s, %s, %s)"""

_alphabet_ = f"{ascii_letters}{digits}"


def gen_pass():
    password = ''.join(choice(_alphabet_) for _ in range(8))
    hash_password = sha512("".join([password, "Eva"]).encode()).hexdigest()
    return password, hash_password


def create_account(acc: dict):
    first_name = acc["first_name"]
    last_name = acc["last_name"]

    dep_name = acc["Department"]
    department = decodes["Department"][dep_name]

    al_name = acc["Access_Level"]
    access_level = decodes["Access_Level"][al_name]

    fio = f"{last_name} {first_name}"

    login = translit(last_name, language_code='ru', reversed=True)
    password, hash_password = gen_pass()
    # (fio, access_level, login, password, department)
    params = (fio, access_level, login, hash_password, department)
    db.del_ins_upd(insert_acc, params)
    db.commit()
    message = f"""{fio} - {al_name}:
login: {login}
password: {password}
кафедра: {dep_name}"""
    return message


def create_program():
    pass


# 'Access_Level': {'Методист': 1, 'Зав. Кафедры': 2, 'Преподаватель': 3}
# 'Department': {'Методисты': 0, 'Аддитивных технологий': 1, 'Тестовая кафедра': 99}

# res = [
#     ['Малецкий', 'Максим', 'Преподаватель', 'Аддитивных технологий'],
#     ['Бакуменко', 'Полина', 'Преподаватель', 'Аддитивных технологий'],
#     ['Гончаров', 'Дмитрий', 'Преподаватель', 'Аддитивных технологий']
# ]
#
# res = [{"last_name": name[0], "first_name": name[1], "Access_Level": name[2], "Department": name[3]} for name in res]
#
# for i in res:
#     print(create_account(i))
