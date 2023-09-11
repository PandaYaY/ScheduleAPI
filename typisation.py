from datetime import date, time
from flask import abort

    
def is_date(txt: str, is_raise=True) -> date or None:
    try:
        return date(*map(int, txt.split("-")))
    except:
        if is_raise:
            print(f'{txt} - дата херня')
            return abort(614)
        

def is_time(txt: str, is_raise=True) -> time or None:
    try:
        return time(*map(int, txt.split(":")))
    except:
        if is_raise:
            print(f'{txt} - время херня')
            return abort(613)


if __name__ == '__main__':
    date_ = is_date('21/12/sadl;fgj', False)
    print(date_, type(date_))
