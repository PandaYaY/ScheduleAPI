__all__ = ("gen_date",)

from datetime import date, datetime
from datetime import time
from datetime import timedelta

from typisation import is_time


def _search(datas, _st_, _end_, _format_):
    for i, data in enumerate(datas):
        if data[1] == _st_ and data[2] == _end_ and data[3] == _format_:
            return i


def _merge_clones(days: list[tuple[int, str, str, str]]) -> list[tuple[int, str, str, str]]:
    res = days[:]
    for ind, temp in enumerate(days):
        day, start_time, end_time, t_format = temp
        day += 7

        for other in days:
            day_, start_time_, end_time_, t_format_ = other
            if day_ == day and start_time_ == start_time and end_time_ == end_time:
                res[ind] = (6-day, start_time, end_time, t_format)
                res.remove(other)
                break
    return res


def _set_two_start(s_date: date, number: int) -> date:
    week = s_date.weekday()
    if week > number:
        temp = number - week + (7 if number > 6 else 14)
        return s_date + timedelta(temp)

    return s_date + timedelta(number - week)


def _set_start(s_date: date, number: int) -> date:
    if number > -1:
        return _set_two_start(s_date, number)

    number = -number - 1
    week = s_date.weekday()
    if week > number:
        return s_date + timedelta(7 + number - week)
    return s_date + timedelta(number - week)



def gen_date(s_date: date, e_date: date, days: list[tuple[int, str, str, str]]) -> list[list[date], time, time, str]:
    def week(num: int, is_two: bool = False) -> list[date]:
        if is_two:
            td = timedelta(14)
        else:
            td = timedelta(7)
        s = _set_start(s_date, num)

        cur_date = datetime.now()
        if s == cur_date.date():
            if start_time < (cur_date - timedelta(hours=2)).time():
                s += td

        while s <= e_date:
            yield s
            s += td

    res = []
    for day, start_time, end_time, t_forma in _merge_clones(days):
        start_time, end_time = is_time(start_time), is_time(end_time)
        if temp := tuple(week(day, (day >= 0))):
            ind = _search(res, start_time, end_time, t_forma)
            if ind is None:
                res.append([temp, start_time, end_time, t_forma])
            else:
                res[ind][0] += temp

    return res

if __name__ == "__main__":
    st = date(2023, 4, 1)
    end = date(2023, 4, 20)

    # per = [(-1, '08:00', '08:45', 'Очно')]
    per = [(2, "08:00", "08:45", "Очно")]
    per = [[-3, '08:00', '08:45', 'Очно'],
           [-1, '08:00', '08:45', 'Очно'],
           [-2, '08:00', '08:45', 'Очно']]

    dates = gen_date(st, end, per)
    print(list(dates))

