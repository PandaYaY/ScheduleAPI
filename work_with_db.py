from flask import abort
from psycopg2 import connect
from psycopg2 import Error
from psycopg2.extras import RealDictCursor
from psycopg2.sql import SQL


class DbCommands:
    """
    Работа с базой данных(подключение, команды)
    Variable:
        user: пользователь БД
        password: пароль пользователя,
        host: ip, по которому располагается БД,
        port: порт,
        database: название БД,
        cursor: курсор для команд в БД
    ----------
    Working with the database(connection, queries)
    Variable:
        user: DB user
        password: user password,
        host: ip address where the database is located,
        port: port,
        database: name of the database,
        cursor: cursor for queries in the database
    """

    __slots__ = ("_connection",)

    def __init__(self, user, password, host, port, database):
        self._connection = None
        self.start(user, password, host, port, database)

    def start(self, user, password, host, port, database):
        """Подключение к БД, если соединение разорвано или нет курсора"""
        if self._connection is not None:
            self._connection.close()

        self._connection = connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database,
        )

    def select(
        self,
        query: str or SQL,
        param: tuple = (),
        one: bool = False,
        cursor_factory_: RealDictCursor = None,
    ) -> list[tuple] or tuple or None:
        """
        Select в БД и вывод данных
        query: sql-запрос
        param: параметры запроса
        one: выдать все результаты или один
        cursor_factory_: вид предоставляемой информации, где
            None - список кортежей [(...), (...), ...]
            RealDictCursor - можно преобразовать в словарь dict(res) или брать элементы по ключу res["id"]
        """
        try:
            with self._connection.cursor(cursor_factory=cursor_factory_) as cursor:
                cursor.execute(query, param)

                if not one:
                    return cursor.fetchall()
                else:
                    return cursor.fetchone()

        except (Exception, Error) as err:
            self._connection.rollback()
            print(f"sql:\n{query}\nparameters:\n{param}, {type(param)}")
            print(f"БД: {err}")
            abort(555)

    def del_ins_upd(self, query: str, param: tuple = ()):
        """
        Функция для выполнения команд DELETE, INSERT, UPDATE
        без получения отобранных результатов
        """
        try:
            with self._connection.cursor() as cursor:
                cursor.execute(query, param)
        except (Exception, Error) as er:
            self._connection.rollback()
            print(f"БД: {er}")
            print(f"sql:\n{query}\nparameters:\n{param}, {type(param)}")
            abort(555)

    def commit(self):
        """Фиксация транзакции"""
        self._connection.commit()


server_dsn = {
    "user": "postgres",
    "password": "admin",
    "host": "127.0.0.1",
    "port": "5433",
    "database": "Calendar"
}

local_dsn = {
    "user": "postgres",
    "password": "dnEX3Or6",
    "host": "127.0.0.1",
    "port": "5432",
    "database": "Calendar"
}

db = DbCommands(**local_dsn)
