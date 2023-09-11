from flask import abort

from authorization import User
from commands import processing
from new_dict import decodes
from work_with_db import db

get_emp_skills = '''select array_agg(unnest) from (
select unnest(skills) from "Users" where department = %s
) as foo'''

get_class_subject = '''select array_agg(unnest) from (
select unnest(subject) from "Classrooms" where department = %s
) as foo'''

# Отобрать сотрудников по кафедре
dep_employee = """select id, fio, skills from "Users"
where department = %s"""


def employee(_: dict, user: User) -> dict:
    """
    Основная информация по сотруднику
    """
    if user.access_level == 1:
        return {"key": [], "value": []}

    res = processing("employee", dep_employee, (user.department,))
    for values in res["value"]:
        if values[2]:
            values[-1] = decodes["Subject"].get_values(values[2])

    return res


# Информация об аудиториях
# добавление индексации идет только к концу списка из-за полного доверия api
select_classrooms = """select id, seats_number, computers_number, subject, description from "Classrooms"
where department = %s"""


def decode(_: dict, user: User) -> dict:
    """
    Расшифровки для выпадающих меню
    """
    access_level = user.access_level

    if access_level == 1:
        classrooms = []
        department = list(decodes["Department"])
        try:
            department.remove("Методисты")
        except:
            ...
    elif access_level == 2:
        department = [decodes["Department"].key_by_value(user.department)]
        classrooms = processing("classrooms", select_classrooms, (user.department,))
        for values in classrooms["value"]:
            values[3] = decodes["Subject"].get_values(values[3])
    else:
        return abort(403)

    return {
        "Classroom": classrooms,
        "Department": department,
        "Program_Source": list(decodes["Program_Source"]),
        "Subject": list(decodes["Subject"]),
        "Training_Format": list(decodes["Training_Format"]),
        "Access_Level": list(decodes["Access_Level"])
    }


def _get_dep_skills(dep_id: int):
    emp_skills = db.select(get_emp_skills, (dep_id,), True)[0]

    emp_skills = emp_skills if emp_skills else []

    class_skills = db.select(get_class_subject, (dep_id,), True)[0]

    class_skills = class_skills if class_skills else []

    return list(set(class_skills) & set(emp_skills))


def get_skills(_: dict, user: User) -> dict:
    if user.access_level == 2:
        departments = [user.department]
    elif user.access_level == 1:
        departments = list(decodes["Department"].values())
    else:
        return abort(403)

    values = []
    for dep in departments:
        skills = _get_dep_skills(dep)

        if skills:
            skills = db.select('select name, program_source, type, description from "Decode_Subject" where id in %s',
                               (tuple(skills),))

            for skill, p_source, s_type, description in skills:
                values.append((skill,
                               decodes["Department"].key_by_value(dep),
                               decodes["Program_Source"].key_by_value(p_source),
                               s_type,
                               description))

    return {"key": ["skill", "department", "source", "type", "description"], "value": values}


if __name__ == "__main__":
    temp_user = User(2, 2, 99)

    a = get_skills(..., temp_user)
    print(a)
    # print(decode(..., temp_user))
