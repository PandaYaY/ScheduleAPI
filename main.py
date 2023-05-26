from fastapi import FastAPI
from requests import get

from _config import _headers_, tournamentsURLs
from get_schedule import tournament_schedule

from football import get_football_results
from basketball import get_basketball_results
from hokey import get_hockey_results

app = FastAPI()


@app.get("/getTournamentSchedule")
def getTournamentSchedule(url: str):
    """
    :param url: URL with schedule of tournament
    :return: list[Event {
  id: string;
  start_time: DateTimeISO;
  home_team: string;
  id_home_team string;
  away_team: string;
  id_away_team: string;
}]
    """
    r = get(url, headers=_headers_)
    if r.status_code != 200:
        return {"status_code": r.status_code, "error": "ошибка"}
    else:
        res = tournament_schedule(r.text)
        return res


@app.get("/getFootballResults")
def getFootballResults(url: str):
    r = get(url, headers=_headers_)
    if r.status_code != 200:
        return {"status_code": r.status_code, "error": "ошибка"}
    else:
        res = get_football_results(r.text)
        return res


@app.get("/getBasketballResults")
def getBasketballResults(url: str):
    r = get(url, headers=_headers_)
    if r.status_code != 200:
        return {"status_code": r.status_code, "error": "ошибка"}
    else:
        res = get_basketball_results(r.text)
        return res


@app.get("/getHockeyResults")
def getHockeyResults(url: str):
    r = get(url, headers=_headers_)
    if r.status_code != 200:
        return {"status_code": r.status_code, "error": "ошибка"}
    else:
        res = get_hockey_results(r.text)
        return res


if __name__ == '__main__':
    urls = tournamentsURLs
    for url_ in urls:
        result = getTournamentSchedule(url_)
        print(result)
