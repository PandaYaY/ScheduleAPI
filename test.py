from json import dumps
from pprint import pprint

from bs4 import BeautifulSoup
from requests import get
from fastapi import FastAPI
import pandas as pd

from _config import mainURL
from _config import _headers_
from _config import tournamentsURLs

from main import getTournamentSchedule


def get_tournaments():
    page = get(mainURL, headers=_headers_)

    soup = BeautifulSoup(page.text, 'html.parser')

    games = ["Футбол", "Хоккей", "Баскетбол"]

    cals = []
    for game in games:
        print(game)
        game_iner = soup.find("a", string=game)
        parent = game_iner.parent

        for league in parent.find_all("a")[1:]:
            if league.text in ["Все чемпионы в лигах Европы", "Рейтинг УЕФА", "Рейтинг ФИФА"]:
                continue

            url = "".join([mainURL, league['href']])
            r = get(url, headers=_headers_)

            soup = BeautifulSoup(r.text, 'html.parser')
            cal = soup.find(attrs={"data-type": "calendar"})

            cal_url = "".join([mainURL, cal['href']])

            cals.append(cal_url)

    print(cals)
    return cals


def get_matches():
    matches = []
    for url in tournamentsURLs:
        if 'football' in url:
            matches += [i["id"] for i in getTournamentSchedule(url)]

    with open('matches.json', 'w') as f:
        matches = dumps(matches)
        f.write(matches)


app = FastAPI()


def req(url: str):
    def _wrapper():
        r = get

    return

    return _wrapper()


@app.get("/")
def index(name: str = "Лира"):
    return {"hello": name}


def get_table():
    r = get("https://www.championat.com/basketball/_nba/tournament/5347/match/1090989/#stats",
            headers=_headers_)

    soup = BeautifulSoup(r.text, 'html.parser')
    score_tables = soup.find("div", {"class": "match-lineup"})
    teams = score_tables.find_all('table')[:2]

    headers = ["numb", "namepos", "points", "time",
               "hit2/attempt2", "hit3/attempt3", "hit1/attempt1",
               "oreb", "dreb", "treb",

               "block", "assist", "turnover", "steal",
               "foul", "foulagainst", "eff"]

    mydata = pd.DataFrame(columns=headers)
    for j in teams[0].find_all('tr')[1:]:
        row_data = j.find_all('td')
        row = [i.text for i in row_data]
        length = len(mydata)
        print(row)
        print(length)
        print(mydata)
        try:
            mydata.loc[length] = row
        except:
            continue
    print(mydata["numb"])
    return mydata


if __name__ == '__main__':
    # with open('results.json', 'r', encoding='utf-8') as f:
    #     print(f.read())

    # get_table()

    proxies = {
        'http': "http://v-ecb9.int.maxmin.ru:31243",
        'https': "http://v-ecb9.int.maxmin.ru:31243",
    }

    r = get(
        "https://freeipapi.com/api/json",
        proxies=proxies
    )

    print(r.status_code)
    if r.status_code == 200:
        pprint(r.json())

    # r = get('http://82.114.100.253:1194')
    # print(r.status_code)
