__all__ = ("free_date", "time_to_str", "free_time", "join_list")

from datetime import date as date_
from datetime import time as time_
from datetime import datetime
from datetime import timedelta

# const
_delta_ = 5
_min_range_ = time_(0, 45)
_min_time_ = time_(8, 0)
_max_time_ = time_(20, 0)
_half_load_ = (time_(16, 5), _max_time_) # Сб
_full_load_ = (_min_time_, _max_time_) # Вс



def _gap_range_(intervals: list[tuple[time_, time_]]) -> list[tuple[time_, time_]]:
    def _add(t: time_):
        temp = t.hour * 60 + t.minute + _delta_
        return time_(temp//60, temp % 60)

    def _sub(t: time_):
        temp = t.hour * 60 + t.minute - _delta_
        return time_(temp//60, temp % 60)

    for interval in intervals:
        if not interval:
            yield ()

        st, end = interval

        if st != _min_time_:  # Левая граница
            st = _add(st)

        if end != _max_time_:  # Правая граница
            end = _sub(end)

        if _is_range(st, end):
            yield (st, end)
        else:
            yield tuple()


def _is_range(st: time_, end: time_) -> tuple[time_, time_]:
    return (end.minute + end.hour*60) - (st.minute + st.hour*60) > 45


def _packing(data: list[list[tuple[date_, time_, time_]],
                        list[tuple[date_, time_, time_]]]):
    """ Соеденяет несколько списков с диапазоном дат в один """
    rez = [[] for i in range(len(max(data, key=len)))]

    for obj in data:
        for i, val in enumerate(obj):
            rez[i].extend(val)

    return rez


def _get_void_date(start_date: date_, end_date: date_, is_regular=False) -> list[list]:
    def _get_void_date_1() -> list[list]:
        cur = date_.today().toordinal() + 6
        s = start_date.toordinal() + 6
        e = end_date.toordinal() + 7
        for i in range(s, e):
            if i < cur:  # Прошлая дата
                yield [_full_load_]

            elif i == cur:  # Текущая дата
                cur_time = (datetime.now() + timedelta(hours=2)).time()
                if cur_time > _min_time_:
                    yield [(_min_time_, cur_time)]
                else:  # Выставление ночью
                    yield []

            elif (i % 7) == 6:  # Вс
                yield [_full_load_]

            elif (i % 7) == 5:  # Сб
                yield [_half_load_]

            else:
                yield []

    def _get_void_date_2() -> list[list]:
        res = [[] for i in range(14)]
        res[6].append(_full_load_)
        res[13].append(_full_load_)

        return res

    if is_regular:
        return list(_get_void_date_2())
    return list(_get_void_date_1())


def _breaking_by_date(data: list[tuple[date_, time_, time_]],
                      start_date: date_,
                      end_date: date_) -> list[list[tuple[time_, time_]]]:
    """ Распределяет даты по дням """

    res = _get_void_date(start_date, end_date)
    if not data:
        return res

    if not any(data[0]):
        return res

    ind = 0
    count_date = date_(start_date.year, start_date.month, start_date.day)

    for d, s, e in data:
        if d > count_date:
            ind = d.toordinal() - start_date.toordinal()
            count_date = d

        res[ind].append((s, e))

    return res


def _breaking_by_date_2(data: list[tuple[date_, time_, time_]],
                        start_date: date_,
                        end_date: date_) -> list[list[tuple[time_, time_]]]:
    """ Распределяет даты по двум неделям """
    res = _get_void_date(start_date, end_date, True)

    if not data:
        return res

    if not any(data[0]):
        return res

    ind = (data[0][0].toordinal() + 6) % 14
    count_date = date_(start_date.year, start_date.month, start_date.day)

    for d, s, e in data:
        if d > count_date:
            ind = (d.toordinal() + 6) % 14
            count_date = d

        res[ind].append((s, e))
    return res


def _connection_employment(data: list[tuple[time_, time_]]) -> list[list[tuple[time_, time_]]]:
    """ объеденение занятых часов """
    def wrapper(day: list):
        if not day:
            return []

        res = [day[0]]
        for st, end in day[1:]:
            if res[-1][1] < st:  # Не пересекает
                if _is_range(res[-1][1], st):  # Перекрытие диапазона
                    res.append((st, end))
                else:
                    res[-1] = (res[-1][0], end)

            elif res[-1][1] < end:  # За первой границой
                res[-1] = (res[-1][0], end)

        return res

    return [wrapper(sorted(i)) for i in data]


def _reversed_time(data: list[list[tuple[time_, time_]]]):
    def wrapper(day) -> tuple[time_, time_]:
        if not day:
            yield [(_min_time_, _max_time_)]
        else:
            new = [(_min_time_, _min_time_)] + day + [(_max_time_, _max_time_)]
            last_end = _min_time_
            for st, end in  new:
                if _is_range(last_end, st):
                    yield (last_end, st)
                last_end = max(end, last_end)

    return [tuple(wrapper(sorted(i))) for i in data]


def _all_join(data):
    """ Нахождение пересечений свободного времени, уберая копии """
    def wrapper(day):
        if not day:
            return []

        res = [day[0]]
        for st, end in day[1:]:
            if st <= res[-1][0] and end >= res[-1][1]:  # Внутри диапазона
                res[-1] = (st, end)

            elif st > res[-1][1] or end < res[-1][0]:
                res.append((st, end))

        return res

    return [wrapper(sorted(day)) for day in data]


def join_list(one: list, other: list) -> list:
    """
    Объединяет два массива с диапазонами дат в их пересечения
    days: [(start_time, end_time), ...]
    """
    def _is_present(list_: list, start: time_, end_: time_):
        """ Присутствует ли диапазон в списке """
        for st, end in list_:
            if st <= start and end_ <= end:
                return

            if start < st and end_ > end:
                list_.remove((st, end))
                continue

        list_.append((start, end_))

    answer = []
    for i in range(min(len(one), len(other))):

        if not (one[i] or other[i]):
            answer.append([])
            continue

        temp = []

        for one_ in one[i]:
            st, end = one_
            for other_ in other[i]:
                st_, end_ = other_

                if st_ > st:  # в правой части диапазона
                    new_s = st_
                    new_e = min(end, end_)
                else:  # в левой части диапазона
                    new_s = max(st_, st)
                    new_e = end

                _is_present(temp, new_s, new_e)
        answer.append(temp)

    return answer


def time_to_str(data: list):
    return [[f"{st.strftime('%H:%M')}—{end.strftime('%H:%M')}" for st, end in _gap_range_(day)]
            for day in data]


def free_date(datas: list[list[tuple[date_, time_, time_]]],
              start_date: date_,
              end_date: date_,
              is_regular=False):
    """
    datas: должна быть отсортирована по date
    Принимает на вход все объекты в итерируемом списке
    """
    def wrapper(data):
        if is_regular:
            break_date = _breaking_by_date_2(data, start_date, end_date)
        else:
            break_date = _breaking_by_date(data, start_date, end_date)

        connection = _connection_employment(break_date)
        return _reversed_time(connection)

    return _all_join(_packing([wrapper(i) for i in datas]))


def free_time(datas: dict[list[tuple[time_, time_]]],
              date: date_,
              is_regular=False,):
    """
    datas: должна быть отсортирована по date
    Принимает на вход все объекты в итерируемом списке в формате {name: data}
    """
    def wrapper(data):
        if date < currend_date:
            data.append(_full_load_)
        elif date == currend_date:
            cur_time = (datetime.now() + timedelta(hours=2)).time()
            if cur_time > _min_time_:
                data.append((_min_time_, cur_time))

        connection = _connection_employment([data])
        return _reversed_time(connection)

    currend_date = date_.today()
    return {key: time_to_str(wrapper(val)) for key, val in datas.items()}


if __name__ == "__main__":
    from time import time as global_time
    data_0 = [
        (date_(2023, 4, 17), time_(10, 0), time_(20, 0)),

        (date_(2023, 4, 18), time_(11, 0), time_(12, 0)),
        (date_(2023, 4, 17), time_(11, 55), time_(14, 0)),
        (date_(2023, 4, 18), time_(10, 55), time_(16, 0)),

        (date_(2023, 4, 21), time_(14, 0), time_(20, 0)),
        (date_(2023, 4, 21), time_(16, 0), time_(20, 0)),
    ]  # * 1_000_0

    data_1 = [
        (date_(2023, 4, 10), time_(10, 0), time_(20, 0)),

        (date_(2023, 4, 11), time_(11, 0), time_(12, 0)),
        (date_(2023, 4, 11), time_(11, 55), time_(14, 0)),
        (date_(2023, 4, 11), time_(10, 55), time_(16, 0)),

        (date_(2023, 4, 14), time_(14, 0), time_(20, 0)),
        (date_(2023, 4, 16), time_(16, 0), time_(20, 0)),
    ]   #* 1_000_0

    data_2 = [
        (date_(2023, 4, 10), time_(10, 0), time_(20, 0)),

        (date_(2023, 4, 11), time_(11, 0), time_(12, 0)),
        (date_(2023, 4, 11), time_(11, 55), time_(14, 0)),
        (date_(2023, 4, 11), time_(10, 55), time_(16, 0)),

        (date_(2023, 4, 14), time_(14, 0), time_(20, 0)),
        (date_(2023, 4, 16), time_(16, 0), time_(20, 0)),
    ]   #* 1_000_0

    data_3 = [
        (date_(2023, 4, 10), time_(10, 0), time_(20, 0)),

        (date_(2023, 4, 11), time_(11, 0), time_(12, 0)),
        (date_(2023, 4, 11), time_(11, 55), time_(14, 0)),
        (date_(2023, 4, 11), time_(10, 55), time_(16, 0)),

        (date_(2023, 4, 14), time_(14, 0), time_(20, 0)),
        (date_(2023, 4, 16), time_(16, 0), time_(20, 0)),
    ]   #* 1_000_0

    st = date_(2023, 4, 1)
    end = date_(2023, 4, 30)
    names = ["Первый", "Второй", "Третий", "Чертвёртый"]
    # datas = [sorted(data_0), sorted(data_1), sorted(data_2), sorted(data_3)]
    datas = [sorted(data_0)]
    datas_time = {"Вася пупкин": [(time_(15, 0), time_(14, 0)), ]}

    times = global_time()
    # """ Логика использлования в free_Date """

    breaking = _breaking_by_date(sorted(data_0), st, end)
    connection = _connection_employment(breaking)
    rev = _reversed_time(connection)
    delta = timedelta(1)
    for i, new in zip(connection, rev):

        print(st, i, "  ->  ", new)
        st += delta

    # teacher = free_date(datas, st, end, False)
    # classrom = free_date(datas, st, end, False)
    # answer = {"online": time_to_str(join_list(teacher, classrom)),
    #           "offline": time_to_str(teacher)}
    # print(answer)

    # """ Логика использлования в free_time """
    # teacher = free_time(datas_time, st, False)
    # classrom = free_time(datas_time, False)
    # andwer = {"teacher": teacher,
    #           "classrom": classrom}
    # print(andwer)
    print(global_time() - times)
