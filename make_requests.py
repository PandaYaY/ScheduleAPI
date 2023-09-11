from socket import socket, AF_INET, SOCK_DGRAM
from time import time
from requests import get, post
from orjson import dumps

from main import url_salt


def get_my_ip() -> str:
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


main_url = f"http://{get_my_ip()}:5000/{url_salt}/"
print(main_url)


def get_user(number: int) -> dict:
    """
    маки
    {91081C24-3219-11EC-810D-7C8AE1AAC4FB,
     3C49C0AD-BD40-F94B-A6DF-C3E866475EA8}
    """

    user = {
        "login": str(number),
        "password": str(number),
        # "mac_address": '91081C24-3219-11EC-810D-7C8AE1AAC4FB',
        "mac_address": "3C49C0AD-BD40-F94B-A6DF-C3E866475EA8"
    }
    return user


def auth(auth_payload: dict):
    auth_data = post(f"{main_url}auth", data=dumps(auth_payload)).json()
    print(auth_data)
    return auth_data['auth_id']


def main(payload: dict, user: int, is_post: bool = None):
    payload["auth_id"] = auth(get_user(user))

    start = time()

    if is_post:
        r = post(f"{main_url}api", data=dumps(payload))
    else:
        r = get(f"{main_url}api", data=dumps(payload))

    request_time = time() - start

    if str(r.status_code)[0] == "2":
        print(r.json())
    else:
        print(r.status_code)
        print(r.json()['description'])

    print(request_time)


def test(payload: dict = None, is_post: bool = False):
    if is_post:
        r = post(f"{main_url}test", data=dumps(payload))
    else:
        r = get(f"{main_url}test", data=dumps(payload))

    if str(r.status_code)[0] == "2":
        print(r.status_code, vars(r), r.json(), type(r.json()))
    else:
        print(r.status_code)
        print(r.text)


if __name__ == "__main__":
    # payload = {
    #     "func": "create_event",
    #     "type": "One_Time_Events",
    #     "department": "Тестовая кафедра",
    #     "subject": "Упаковка будущего",
    #     "program_source": "ЦТПО",
    #     "description": "test",
    #     "children_count": "132",
    #     "periodicity": [(2, "12:32", "14:32", "Очно")],
    #     "start_date": "2023-04-05",
    #     "end_date": "2023-04-05",
    #     "school": "1315",
    # }

    # payload = {
    #     "func": "create_event",
    #     "type": "Regular_Events",
    #     "department": "Тестовая кафедра",
    #     "subject": "Упаковка будущего",
    #     "program_source": "ЦТПО",
    #     "description": "test",
    #     "children_count": "13",
    #     "periodicity": [(9, "12:32", "14:32", "Очно")],
    #     "start_date": "2023-05-01",
    #     "end_date": "2023-05-30",
    #     "school": "1315",
    # }

    # payload = {"func": "confirm_event",
    #            "table": "One_Time_Events",
    #            "event_id": 47}

    # payload = {"func": "confirm_event",
    #            "table": "Regular_Events",
    #            "event_id": 135}

    # payload = {"func": "auction",
    #            "table": "One_Time_Events",
    #            "description": "нихачу",
    #            "event_id": 4}

    # payload = {"func": "take_event",
    #            "table": "One_Time_Events",
    #            "event_id": 4}

    # payload = {"func": "new_events"}
    # payload = {"func": "get_events",
    #            "start_date": "2023-05-01",
    #            "end_date": "2023-05-30"}
    # payload = {"func": "full_load"}

    payload = {"func": "event_freedom",
               "table": "One_Time_Events",
               "event_id": 1,
               "date": '2023-04-17'}

    user = 2
    post_ = False
    # post_ = True

    main(payload, user, post_)

    # test()
