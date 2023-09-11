from socket import socket
from socket import AF_INET, SOCK_DGRAM

from flask import Flask, make_response
from flask import request
from flask import abort

from flask_cors import CORS

from orjson import dumps

from authorization import User

import functions

from errors import blueprint

from authorization import auth
from authorization import check_auth
from authorization import trash_collector

from alarm_manager import load_task

from updates import get_version
from updates import download_app


@check_auth
def main(data: dict, user: User):
    """
    Parameters:
        data: dict
        user: User
    ----------
    Главная функция с URL-адресом http://{get_my_ip()}:5000/{url_salt}/api.
    При корректной авторизации идёт получение названий функций по параметру подключённого пользователя user.access_level
    из словаря funcs -> получение названия нужной функции 'func': str из словаря data
    Берётся экземпляр функции из словаря func_names по ключу названия функции ({"function": function}).
    Возвращает response из байт строки
    ----------
    The main function with the URL http://{get_my_ip()}:5000/{url_salt}/api.
    With the correct authorization, the function names are received by the parameter of the connected user
    user.access_level from the dictionary funcs -> getting the name of the desired function 'func': str from
    the dictionary data. An instance of the function is taken from the func_name dictionary by the key
    of the function name ({"function": function}).
    Returns a response from a byte string
    """
    print(f'/api: {data}')  # logs
    # print(user)
    # print(vars(request))

    method_funcs = functions.functions[request.method]
    available_funcs = method_funcs[user.access_level - 1]

    if (func_name := data.get('func')) in available_funcs:
        resp = getattr(functions, func_name)(data, user)
        print(resp)
        response = make_response(dumps(resp, default=str))
        response.content_type = "application/json"
        return response

    print(func_name, request.method, available_funcs)  # логгинг ошибок функций
    return abort(403)


def get_my_ip() -> str:
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


app = Flask(__name__)
CORS(app)

# url_salt ########################################################################
url_salt = 'c4361038349ba1adbb2e70f72fc8b050f99912f55713c130c33e37c00a6ce4b2' \
           '3633d3274c6d723acb9d269fbafa2b55ac21635737de0ec95e4f4f9e5cbe3bb1'
# routing #########################################################################
app.add_url_rule(f'/{url_salt}/api', view_func=main, methods=['GET', 'POST'])
app.add_url_rule(f'/{url_salt}/auth', view_func=auth, methods=['POST'])
app.add_url_rule(f'/{url_salt}/version', view_func=get_version, methods=['GET'])
app.add_url_rule(f'/{url_salt}/download', view_func=download_app, methods=['GET'])
# errors ##########################################################################
app.register_blueprint(blueprint)


def start():
    trash_collector()  # delete old notifications
    load_task()  # tasks_manager
    app.run(host=get_my_ip(), port=5000, debug=False)  # start_server


if __name__ == '__main__':
    start()
