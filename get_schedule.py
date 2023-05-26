from datetime import datetime

from bs4 import BeautifulSoup

from _config import mainURL


def parce_date(date: list[str]) -> str:
    if len(date) == 2:
        return datetime.strptime(" ".join(date), "%d.%m.%Y %H:%M").isoformat()
    elif len(date) == 1:
        date_ = date[0]
        if len(date_) == 10:
            return datetime.strptime(date_, "%d.%m.%Y").isoformat()


def parce_match(match, teams: dict) -> dict:
    """
    :param teams: dict[name: team_id]
    :param match: PageElement
    :return: {
  id: string;
  start_time: DateTimeISO;
  home_team: string;
  id_home_team string;
  away_team: string;
  id_away_team: string;
}
    """
    match_id = "".join([mainURL, match.a['href']])

    cur_teams = match.attrs["data-team"].split('/')
    if '0' in cur_teams:
        return {}

    id_home_team, id_away_team = cur_teams
    home_team, away_team = (teams[team] for team in cur_teams)

    date = match.find(class_="stat-results__date-time _hidden-td")
    start_time = parce_date(date.text.split())
    if not date:
        return {}

    event = {
        "id": match_id,
        "start_time": start_time,
        "home_team": home_team,
        "id_home_team": id_home_team,
        "away_team": away_team,
        "id_away_team": id_away_team,
    }
    return event


def tournament_schedule(html: str) -> list[dict]:
    """
    :param html: html-string
    :return: list[Event {
  id: string;
  start_time: DateTimeISO;
  home_team: string;
  id_home_team string;
  away_team: string;
  id_away_team: string;
}]
    """
    soup = BeautifulSoup(html, 'html.parser')

    tournament = soup.findAll('tr')[1:]

    team_names = soup.find('select', {'id': 'team_selector'})
    team_names = {team['value']: team.text for team in team_names.find_all('option') if team['value']}

    matches = []
    for match in tournament:
        match = parce_match(match, team_names)
        if match:
            matches.append(match)

    return matches
