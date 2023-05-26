import re
from pprint import pprint

import requests
from bs4 import BeautifulSoup

from tools import clean_text, parce_date
from _config import _headers_


def get_penalty(events):
    parse_events = []
    for i in events.find_all('div', {"class": ["match-stat__row"]}):
        team = 1 if '_team1' in i["class"] else 2

        player = i.find(class_="match-stat__player")
        player_name = " ".join(player.text.split())

        time = i.find("div", "match-stat__main-value").text
        time = list(map(int, clean_text(time).split(':')))
        time = time[0] * 60 + time[1]

        value = i.find('div', 'match-stat__add-info').text
        value = int(clean_text(value)[0])

        parse_events.append({
            "player": player_name,
            "team": team,
            "type": "penalty",
            "value": value,
            "time": time
        })
    return parse_events


def get_goals(events) -> list:
    parse_events = []
    for i in events.find_all('div', {"class": ["match-stat__row"]}):
        team = 1 if '_team1' in i["class"] else 2

        stat_desc = i.find("div", "match-stat__desc")
        counts = stat_desc.text.split('x')
        stat_desc.decompose()

        time = i.find("div", "match-stat__main-value").text
        time = list(map(int, clean_text(time).split(':')))
        time = time[0]*60 + time[1]

        if time > 3600:
            main_type = 'goalsAtOT'
        elif counts[0] == counts[1]:
            main_type = 'goals'
        elif team == 1 and counts[0] > counts[1]:
            main_type = 'goalsAtMore'
        else:
            main_type = 'goalsAtLess'

        goal = i.find("a", "match-stat__player").text
        goal_name = " ".join(goal.split())

        parse_events.append({
            "player": goal_name,
            "team": team,
            "type": main_type,
            "value": 1,
            "time": time
        })

        assist = i.find_all("a", "match-stat__player2")
        for player in assist:
            name = " ".join(player.text.split())
            parse_events.append({
                "player": name,
                "team": team,
                "type": "assist",
                "value": 1,
                "time": time,
            })

    return parse_events


def get_hockey_results(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')

    # главная статистика с датой, счетом, командами и судьёй...
    result = {}
    main_stat = soup.find("div", {"class": "_stat"})

    # названия команд
    teams = main_stat.find_all("div", {"class": "match-info__team-name"})
    home_name, away_name = (team.text for team in teams)
    result["teams"] = {"home": home_name, "away": away_name}

    # дата игры
    date = main_stat.find("div", {"class": "match-info__title"})
    start_time = parce_date(date.text)
    result["startTime"] = start_time

    # главный судья
    referees_boxes = soup.find_all(string=re.compile(r"[\r\n ]*Главный судья:[\r\n ]*"))
    referees = []
    if referees_boxes:
        for referee in referees_boxes:
            referees.append(referee.next.text)

    result["mainReferee"] = referees

    # тренеры
    trainer_names = []
    trainers = soup.find("h3", string='Главные тренеры')
    if trainers:
        for _ in range(2):
            trainers = trainers.next_sibling.next_sibling
            trainer_name = trainers.find('span', 'table-item__name')
            trainer_name = trainer_name.text if trainer_name else ''
            trainer_names.append(trainer_name)

    result["mainTrainers"] = trainer_names

    # статус игры (2 тайм, окончена и пр.)
    status = main_stat.find("div", {"class": "match-info__status"})
    status = status.text.replace(' ', '').replace('\n', '')
    result['matchStatus'] = status

    statistics = {}
    # статистика
    stat = soup.find('h2', string="Статистика")
    if stat:
        stat = stat.parent.find_all('div', {"class": "stat-graph__row"})
        for i in stat:
            stat_name = i.find('div', {"class": "stat-graph__title"}).text.replace(' ', '_')
            home_value = i.find('div', "_left").text.split()[0]
            away_value = i.find('div', "_right").text.split()[-1]

            statistics[stat_name] = {"home": int(home_value), "away": int(away_value)}

    result["statistics"] = statistics

    goals = soup.find('h2', string="Голы")
    goals = get_goals(goals.nextSibling.nextSibling) if goals else []

    penalty = soup.find('h2', string="Удаления")
    penalty = get_penalty(penalty.nextSibling.nextSibling) if penalty else []

    result["events"] = goals + penalty

    return result


if __name__ == '__main__':
    hokey_url = "https://www.championat.com/hockey/_highleague/tournament/5257/match/1075505"
    hockey_r = requests.get(hokey_url, headers=_headers_)
    hockey_res = get_hockey_results(hockey_r.text)
    pprint(hockey_res)
