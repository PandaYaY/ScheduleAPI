from threading import Timer
from hashlib import sha512
from os import urandom

from flask import abort
from flask import request
from orjson import loads

from work_with_db import db


# const
_time_clear_ = 60  # время между очисткой таблицы Auth
_live_time_ = 600  # время на то, чтобы остаться в сети


# Проверка на наличие в уже авторизованных
is_auth = """update "Auth" a set
time_end = now()
from "Users" u
where u.id = a.real_id and login = %s and password = %s and mac = %s
returning real_id, u.access_level, u.department, mac, auth_id"""

# Первичная авторизация
auth_sql = """select id, access_level, department, mac_address, new from "Users"
where login = %s and password = %s"""

# Авторизация в таблицу "Auth"
insert_auth = 'insert into "Auth" values (%s, %s, now(), %s)'

# добавление мака если его нет
update_mac = """update "Users"
set
mac_address = %s,
new = %s
where id = %s"""


# Сборщик мусора деавторизованных с истекшим сроком жизни
trash_clear = f"""delete from "Auth" a
    using "Users" u
where a.real_id = u.id and now() - time_end > interval '{_live_time_}' second
returning real_id, access_level, department, mac, auth_id"""

clear_notifications = '''delete from "Events_Changes"
where (user_id = %s and %s = any(mac))'''

# Поиск среди авторизованных по пути на /api
auth_search = """update "Auth" a set
time_end = now()
from "Users" u
where u.id = a.real_id and auth_id = %s
returning real_id, u.access_level, u.department, mac, auth_id"""


class User:
    """
    Абстракция пользователя на сервер.
        Отслеживание подключённых клиентов для ускорения доступа к информации.
    Variable:
        auth_id: уникальное значения для устройства одного пользователя,
            которое генерируется из mac-адреса (mac) и случайных чисел в формате hex -> str.
        real_id: id пользователя в БД в таблице "User" -> int.
        time_end: время определения или авторизации пользователя,
            по которому определяется, может ли пользователь оставаться в сети.
    ----------
    Abstraction of the user to the server.
        Tracking connected clients to speed up access to information.
    Variable:
        auth_id: unique value for a single user's device,
            which is generated from the mac address (mac) and random numbers in hex format -> str.
        real_id: user id in DB in the table "User" -> int.
        time_end: time of user identification or authorization,
            which determines whether the user can stay online.
    """

    __slots__ = ("update_const", "auth_id", "real_id", "mac", "time_end", "access_level", "department", "timer")

    def __init__(self, real_id: int, access_level: int, department: int, mac: str = "", auth_id: str = ""):
        self.real_id = real_id
        self.access_level = access_level
        self.department = department
        self.mac = mac

        if not auth_id:
            self.auth_id = urandom(12).hex()
        else:
            self.auth_id = auth_id

        self.update_const = False

    def __str__(self):
        string = f"""---------------User---------------
        \rreal_id: {self.real_id},
        \raccess_level: {self.access_level},
        \rdepartment: {self.department},
        \rmac: {self.mac},
        \rauth_id: {self.auth_id}
        \r----------------------------------"""
        return string


def gen_password(password):
    return sha512("".join([password, "Eva"]).encode()).hexdigest()


def get_request_data(funk):
    """
    Декоратор для получения данных из запроса
    Если не получается получить request.data,
    то запрос пришел с сайта и выгружаются request_values.
    ----------
    Decorator for getting data from a request
    If it is not possible to get request.data,
    then the request came from the site and request_values are unloaded.
    """

    def _wrapper():
        try:
            data = loads(request.data)
        except:
            data = request.values.to_dict()

        return funk(data)

    return _wrapper


def check_mac(mac_list: list, mac: str, user: User, new: int) -> bool:
    """
    Проверка мак адреса:
    1. Если вход с сайта, то все в порядке
    2. Если mac уже имеется в БД
    """
    if mac == "1":  # web
        return True

    # Если с зареганого устройства
    if mac in mac_list:
        return True

    # если право на одно добавление
    if new == 1:
        db.del_ins_upd(update_mac, (mac_list + [mac], 0, user.real_id))
        return True

    # если можно добавлять бесконечно
    if new == 2:
        db.del_ins_upd(update_mac, (mac_list + [mac], 2, user.real_id))
        return True

    abort(401)


def _get_params(data: dict) -> tuple[str, str, str]:
    """
    Проверка параметров авторизации
    ----------
    Check auth parameters
    ----------
    return -> (login, password, mac)
    """
    try:
        login = data["login"]
        password = data["password"]
        mac = data["mac_address"]
    except KeyError:
        return abort(400)

    if not mac:
        abort(400)

    password = gen_password(password)

    return login, password, mac


def authorisation(data: dict) -> User or None:
    """
    Базовая авторизация с помощью БД
    1. Если пользователь уже авторизовывался,
    то ему будет выдан предыдущий auth_id
    2. Если же пользователь авторизуется в первый раз за последнее время,
    то ему выдается новый auth_id
    """
    # Проверка данных
    login, password, mac = _get_params(data)
    # Проверка в таблице Auth
    if user_data := db.select(is_auth, (login, password, mac), one=True):
        return User(*user_data)

    # Проверка на первичную авторизацию
    if user_data := db.select(auth_sql, (login, password), True):
        user_id, lvl, dep, mac_list, new = user_data

        user = User(user_id, lvl, dep, mac)

        check_mac(mac_list, mac, user, new)

        # Добавление авторизованного пользователя
        auth_params = (user.auth_id, user.real_id, user.mac)
        db.del_ins_upd(insert_auth, auth_params)
        db.commit()

        return user


@get_request_data
def auth(data: dict):
    user = authorisation(data)
    if user is None:
        abort(401)
    return {"auth_id": user.auth_id, "access_level": user.access_level}


def search(auth_id: str or None) -> User or None:
    user_data = db.select(auth_search, (auth_id,), one=True)
    if user_data:
        return User(*user_data)


def check_auth(func):
    """
    Декоратор-авторизация
    1. Получение данных от приложения или web-версии
    2. Попытка найти пользователя по выданному ключу аутентификации (auth_id)
        True: обработка пользователя и обработка функции по найденному пользователю
        False: ошибка 401(некорректная авторизация)
    ----------
    Decorator-authorization
    1. Getting data from the application or web version
    2. Attempt to find the user by the issued authentication key (auth_id)
        True: processing the user and processing the function by the found user
        False: error 401 (incorrect authorization)
    """

    @get_request_data
    def _wrapper(data: dict) -> func:
        if user := search(data.get("auth_id")):
            return func(data, user)
        abort(401)

    _wrapper.__name__ = func.__name__
    return _wrapper


def trash_collector():
    """
    Рекурсивная функция очистки Auth.
    ----------
    Удаление авторизованных пользователей,
    время с последнего ответа которых
    превысило время ожидания.
    Возвращает объекты User
    для последующей чистки уведомлений
    ----------
    Recursive Auth cleanup function.
    ----------
    Deleting authorized users
    whose time since the last response
    has exceeded the waiting time.
    Returns User objects
    for subsequent notification cleanup
    """
    auth_data = db.select(trash_clear)
    db.commit()

    deleted_users = []
    for user_data in auth_data:
        deleted_users.append(User(*user_data))

    for user in deleted_users:
        db.del_ins_upd(clear_notifications, (user.real_id, user.mac))
    Timer(_time_clear_, trash_collector).start()

    return deleted_users
