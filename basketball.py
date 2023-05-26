from datetime import datetime
from pprint import pprint

import requests
from bs4 import BeautifulSoup

from tools import parce_date
from tools import clean_text
from _config import _headers_


def throws(throw) -> list[int]:
    if throw := throw.text.split():
        return list(map(int, throw[0].split('/')))
    return [0, 0]


def parse_players(soup, home_name) -> list[dict]:
    # таблица игроки
    players = []
    score_tables = soup.find("div", {"class": "match-lineup"})
    teams = score_tables.find_all('table')[:2]

    for team in teams:
        is_home = home_name in team.text

        for player in team.tbody.find_all('tr'):
            cols = player.find_all('td')
            numb = cols[0].text
            if not numb or numb == "Всего:":
                continue

            name = cols[1].text.split()

            hit2 = throws(cols[4])
            hit3 = throws(cols[5])
            hit1 = throws(cols[6])

            time = datetime.strptime(cols[3].text, '%M:%S').time()
            time = time.minute * 60 + time.second

            player_stat = {
                "ishome": is_home,
                "numb": int(numb),
                "pos": name[0],
                "name": " ".join(name[1:]),
                "stats": {
                    "points": int(cols[2].text),
                    "time": time,
                    "hit2": hit2[0],
                    "attempt2": hit2[1],
                    "hit3": hit3[0],
                    "attempt3": hit3[1],
                    "hit1": hit1[0],
                    "attempt1": hit1[1],
                    "oreb": int(cols[7].text),
                    "dreb": int(cols[8].text),
                    "treb": int(cols[9].text),
                    "block": int(cols[10].text),
                    "assist": int(cols[11].text),
                    "turnover": int(cols[12].text),
                    "steal": int(cols[13].text),
                    "foul": int(cols[14].text),
                    "foulagainst": int(cols[15].text),
                    "eff": int(cols[16].text) if cols[16].text else 0
                }
            }
            players.append(player_stat)
    return players


def get_basketball_results(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')

    # главная статистика с датой, счетом, командами и судьёй...
    result = {}
    main_stat = soup.find("div", {"class": "_stat"})

    # названия команд
    teams = main_stat.find_all("div", {"class": "match-info__team-name"})
    home_name, away_name = (team.text for team in teams)
    result["teams"] = {"home": home_name, "away": away_name}

    # тренеры
    trainer_names = []
    trainers = soup.find("h3", string='Главные тренеры')
    for _ in range(2):
        trainers = trainers.next_sibling.next_sibling
        trainer_name = trainers.find('span', 'table-item__name')
        trainer_name = trainer_name.text if trainer_name else ''
        trainer_names.append(trainer_name)

    result["mainTrainers"] = trainer_names

    # главный судья и стадион
    extra_info_boxes = main_stat.find_all("div", {"class": "match-info__extra-row"})
    stadium = extra_info_boxes[0].a.text
    result["stadium"] = stadium
    referees = [i.text for i in extra_info_boxes[1].find_all('a')]
    result["referees"] = referees

    # дата игры
    date = main_stat.find("div", {"class": "match-info__title"})
    start_time = parce_date(date.text)
    result["startTime"] = start_time

    # основной счет
    score_box = soup.find("div", "match-info__score-total")  # все счета
    scores = clean_text(score_box.text)
    scores = map(int, scores.split(':'))
    result["score"] = list(scores)

    # таблица очков
    qscores = []
    strings = soup.find_all("tr", {"class": "match-info__score-details-table-data"})
    for string in strings:
        string = string.find_all('td', {"class": "match-info__score-details-wrap"})
        string = [int(i.text) for i in string]
        for i in range(len(string)):
            if not qscores:
                qscores = [[] for _ in range(len(string))]
            qscores[i].append(string[i])
    result["qscores"] = qscores

    result["players"] = parse_players(soup, home_name)
    return result


if __name__ == '__main__':
    basketball_url = "https://www.championat.com/basketball/_nba/tournament/5347/match/1090989"
    basketball_r = requests.get(basketball_url, headers=_headers_)
    basketball_res = get_basketball_results(basketball_r.text)
    pprint(basketball_res)
    print(len(basketball_res["players"]))
