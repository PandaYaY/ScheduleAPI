from pprint import pprint

import requests
from bs4 import BeautifulSoup

from tools import clean_text, parce_date
from _config import _headers_


def get_main_info(soup):
    result = {}
    main_stat = soup.find("div", {"class": "_stat"})

    # дата игры
    date = main_stat.find("div", {"class": "match-info__title"})
    start_time = parce_date(date.text)
    result["startTime"] = start_time

    # статус игры (2 тайм, окончена и пр.)
    status = main_stat.find("div", {"class": "match-info__status"})
    status = status.text.replace(' ', '').replace('\n', '')
    result['matchStatus'] = status

    # главный судья
    extra_info_boxes = main_stat.find_all("div", {"class": "match-info__extra-row"})
    stadium = extra_info_boxes[0].a.text
    result["stadium"] = stadium
    referee = extra_info_boxes[1].a.text
    result["mainReferee"] = referee

    # названия команд
    teams = main_stat.find_all("div", {"class": "match-info__team-name"})
    home_name, away_name = (team.text for team in teams)
    # тренеры
    lineup = soup.find("div", {"class": "match-lineup"})
    lineup = lineup.find_all("span", {"class": "table-item__name"})[-2:]
    trainers = [i.text for i in lineup]

    result["teams"] = {"home": home_name, "away": away_name, "mainTrainers": trainers}

    return result


def get_football_results(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')

    # главная статистика с датой, счетом, командами и судьёй...
    result = {}
    main_stat = soup.find("div", {"class": "_stat"})

    # дата игры
    date = main_stat.find("div", {"class": "match-info__title"})
    start_time = parce_date(date.text)
    result["startTime"] = start_time

    # статус игры (2 тайм, окончена и пр.)
    status = main_stat.find("div", {"class": "match-info__status"})
    status = status.text.replace(' ', '').replace('\n', '')
    result['matchStatus'] = status

    # главный судья
    extra_info_boxes = main_stat.find_all("div", {"class": "match-info__extra-row"})
    if extra_info_boxes:
        stadium = extra_info_boxes[0].a.text
        result["stadium"] = stadium
        referee = extra_info_boxes[1].a.text
        result["mainReferee"] = referee

    # названия команд
    teams = main_stat.find_all("div", {"class": "match-info__team-name"})
    home_name, away_name = (team.text for team in teams)
    # тренеры
    trainer_names = []
    trainers = soup.find("h3", string='Главные тренеры')
    for _ in range(2):
        trainers = trainers.next_sibling.next_sibling
        trainer_name = trainers.find('span', 'table-item__name')
        trainer_name = trainer_name.text if trainer_name else ''
        trainer_names.append(trainer_name)

    result["teams"] = {"home": home_name, "away": away_name, "mainTrainers": trainer_names}

    statistics = {}
    # голы и пенальти
    goals = soup.find("div", "match-info__score-total")  # все счета
    if extra_goals := goals.div:
        home_extra_score, away_extra_score = map(int, extra_goals.text.split(' : '))  # если есть пенальти
        statistics["Пенальти"] = {"home": home_extra_score, "away": away_extra_score}
        goals.div.decompose()
    # основной счет
    goals = clean_text(goals.text)
    home_score, away_score = map(int, goals.split(':'))

    statistics["Голы"] = {"home": home_score, "away": away_score}

    # статистика
    stat = soup.find('h2', string="Статистика").parent.find_all('div', {"class": "stat-graph__row"})
    for i in stat:
        stat_name = i.find('div', {"class": "stat-graph__title"}).text.replace(' ', '_')
        home_value = i.find('div', "_left").text
        away_value = i.find('div', "_right").text

        statistics[stat_name] = {"home": int(home_value), "away": int(away_value)}

    result["statistics"] = statistics
    return result


if __name__ == '__main__':
    football_url = "https://www.championat.com/football/_youth/tournament/4363/match/1040057"
    football_r = requests.get(football_url, headers=_headers_)
    football_res = get_football_results(football_r.text)
    pprint(football_res)
