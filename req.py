import requests

schedule_urls = ['https://www.championat.com/football/_russiapl/tournament/4987/calendar/',
                 'https://www.championat.com/football/_ucl/tournament/4993/calendar/',
                 'https://www.championat.com/football/_europeleague/tournament/4995/calendar/',
                 'https://www.championat.com/football/_conferenceleague/tournament/4999/calendar/',
                 'https://www.championat.com/football/_nationsleague/tournament/4841/calendar/',
                 'https://www.championat.com/football/_russia/tournament/5251/calendar/',
                 'https://www.championat.com/football/_euro/tournament/5287/calendar/',
                 'https://www.championat.com/football/_worldcup/tournament/4949/calendar/',
                 'https://www.championat.com/football/_england/tournament/5025/calendar/',
                 'https://www.championat.com/football/_italy/tournament/5057/calendar/',
                 'https://www.championat.com/football/_spain/tournament/5047/calendar/',
                 'https://www.championat.com/football/_france/tournament/5029/calendar/',
                 'https://www.championat.com/football/_germany/tournament/5027/calendar/',
                 'https://www.championat.com/football/_russiacup/tournament/5135/calendar/',
                 'https://www.championat.com/football/_youth/tournament/4363/calendar/',
                 'https://www.championat.com/football/_women/tournament/5281/calendar/',
                 'https://www.championat.com/football/_russia1d/tournament/5017/calendar/',
                 'https://www.championat.com/football/_russia2d/tournament/5101/calendar/',
                 'https://www.championat.com/football/_southamerica/tournament/4851/calendar/',
                 'https://www.championat.com/football/_other/tournament/5237/calendar/',
                 'https://www.championat.com/football/_llc/tournament/4403/calendar/',
                 'https://www.championat.com/hockey/_superleague/tournament/5255/calendar/',
                 'https://www.championat.com/hockey/_nhl/tournament/5297/calendar/',
                 'https://www.championat.com/hockey/_eurotour/tournament/5193/calendar/',
                 'https://www.championat.com/hockey/_whc/tournament/5033/calendar/',
                 'https://www.championat.com/hockey/_whcu20/tournament/5155/calendar/',
                 'https://www.championat.com/hockey/_holympic/tournament/3551/calendar/',
                 'https://www.championat.com/hockey/_ahl/tournament/4997/calendar/',
                 'https://www.championat.com/hockey/_highleague/tournament/5257/calendar/',
                 'https://www.championat.com/hockey/_mhl/tournament/5259/calendar/',
                 'https://www.championat.com/hockey/_foreign/tournament/5379/calendar/',
                 'https://www.championat.com/basketball/_nba/tournament/5347/calendar/',
                 'https://www.championat.com/basketball/_vtbleague/tournament/5167/calendar/',
                 'https://www.championat.com/basketball/_euroleague/tournament/5169/calendar/',
                 'https://www.championat.com/basketball/_eurocups/tournament/5171/calendar/',
                 'https://www.championat.com/basketball/_bworldcup/tournament/5071/calendar/',
                 'https://www.championat.com/basketball/_bteam/tournament/5079/calendar/',
                 'https://www.championat.com/basketball/_otherleagues/tournament/5173/calendar/']

for url in schedule_urls:
    par = {"url": url}
    r = requests.get(f"http://127.0.0.1:8000/getTournamentSchedule/", params=par)
    print(r.status_code)

    if r.status_code == 200:
        resp = r.json()
        print(type(resp), resp)
    elif r.status_code == 500:
        print(url)


# TODO использовать async requests
# par = {"name": "Артём"}
# r = requests.get(f"http://127.0.0.1:8000/", params=par)
#
# if r.status_code == 200:
#     resp = r.json()
#     print(r.url)
#     print(resp)
# else:
#     print(r.status_code)
