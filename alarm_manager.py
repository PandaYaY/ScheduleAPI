from datetime import datetime
from threading import Timer

from work_with_db import db

insert_task = """insert into "AlarmManager"
(function, args, time_trigger)
values (%s, %s, %s)
returning id"""


class Executor:
    __slots__ = ("id", "func", "args", "timer")

    def __init__(self,
                 id: int or None,
                 _func_name: str,
                 _func,
                 _args: list[str],
                 _timer: datetime,
                 ignore: bool = False):
        self.func = _func
        self.args = _args

        if not (self.func is None):
            if _timer < datetime.now():
                time = 0
            else:
                time = (_timer - datetime.now()).seconds
            self.timer = Timer(time, self._execute)
            self.timer.start()

        if not ignore:
            self.id = db.select(insert_task, (_func_name, self.args, _timer), True)[0]
        else:
            self.id = id

    def _execute(self):
        try:
            self.func(self.args)
        except:
            ...
        self.delete()

    def cancel(self):
        try:
            self.timer.cancel()
        except:
            ...
        self.delete()

    def delete(self):
        db.del_ins_upd('delete from "AlarmManager" where id = %s', (self.id,))
        db.commit()
        try:
            Manager.remove(self)
        except:
            ...
        del self

    def __str__(self):
        string = f"id: {self.id}, " \
                 f"function: {self.func}, " \
                 f"args: {self.args}, " \
                 f"time_trigger: {self.timer.interval}"
        return string


class AlarmManager(list):
    def __init__(self, *args, **qw):
        self.list_func = {}
        super().__init__(*args, **qw)

    def cancel_by_args(self, table_name: str, event_id: int):
        event_id = str(event_id)
        for timer in self:
            try:
                table_name_, event_id_ = timer.args[:2]
            except:
                continue
            if table_name_ == table_name and event_id_ == event_id:
                return timer.cancel()

    def cancel(self, id: int):
        for timer in self:
            if timer.id == id:
                return timer.cancel()

    def add(self, func_name: str, args: list[str], time_trigger: datetime):
        self.append(Executor(None, func_name, self.list_func[func_name], args, time_trigger))

    def bind_func(self, name: str, func):
        self.list_func[name] = func

    def __str__(self):
        string = [str(executor) for executor in self]
        return str(string)


def load_task():
    tasks = db.select('select * from "AlarmManager"')
    for id, func_name, args, time_trigger in tasks:
        Manager.append(Executor(id, func_name, Manager.list_func[func_name], args, time_trigger, True))


Manager = AlarmManager()
