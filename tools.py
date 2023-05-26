from datetime import datetime, time

from locale import setlocale, LC_ALL


setlocale(LC_ALL, 'ru_RU')


def clean_text(string: str) -> str:
    """
    delete \n and spaces
    """
    del_char = ['\n', ' ']
    for char in del_char:
        string = string.replace(char, '')
    return string


def parce_date(full_date: str) -> str:
    full_date = full_date.split()

    day = full_date[0]
    month = full_date[1]
    year = full_date[2][:4]
    hour, minute = full_date[4].split(':')

    date = "".join([year, month, day, hour, minute])
    date = datetime.strptime(date, "%Y%B%d%H%M").isoformat()
    return date


def secToMin(sec: int):
    minutes = sec // 60
    seconds = sec % 60
    answer = f'{minutes} мин {seconds} сек'
    print(answer)
    return time(minute=minutes, second=seconds)


def minToSec(min: int, sec: int):
    seconds = min*60 + sec
    print(f"{seconds} секунд")
    return seconds


if __name__ == '__main__':
    urls = [
        "https://www.championat.com/football/_youth/tournament/4363/match/1040057",  # футбол
        "https://www.championat.com/hockey/_superleague/tournament/5255/match/1075783",  # хоккей
        "https://www.championat.com/basketball/_nba/tournament/5347/match/1090989/#stats"  # баскетбол
    ]

    football_url = urls[0]
    hokey_url = urls[1]
    basketball_url = urls[2]

    secToMin(3502)
    minToSec(37, 50)
