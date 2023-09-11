from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import default_exceptions
from flask import Blueprint
from orjson import dumps
from create_event import _max_children_

blueprint = Blueprint('error_handlers', __name__)


@blueprint.app_errorhandler(400)
def page_not_found(e):
    response = e.get_response()
    response.data = dumps({
        "code": e.code,
        "name": e.name,
        "description": 'Неверные данные',
    })
    response.content_type = "application/json"
    return response, e.code


@blueprint.app_errorhandler(HTTPException)
def db_error_handler(e):
    response = e.get_response()
    response.data = dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response, e.code


class DbError(HTTPException):
    code = 555
    description = "Ошибка записи в базу данных"
    name = "Db_Error"


default_exceptions[555] = DbError


class ClassroomSeats(HTTPException):
    code = 601
    name = "Number of seats"
    description = "Посадочных мест планируется меньше, чем компьютеров"


default_exceptions[601] = ClassroomSeats


class ClassroomDouble(HTTPException):
    code = 602
    name = "Classroom double"
    description = "Аудитория с таким именем уже существует"


default_exceptions[602] = ClassroomDouble


class ClassroomNotFound(HTTPException):
    code = 603
    name = "Not found"
    description = "Информация об этой аудитории не найдена"


default_exceptions[603] = ClassroomNotFound


class EarlyDate(HTTPException):
    code = 604
    name = "Early date"
    description = "Данная дата меньше текущей"


default_exceptions[604] = EarlyDate


class NoDate(HTTPException):
    code = 605
    name = "No date"
    description = "По данным условиям не сгенерировалось ни одной даты"


default_exceptions[605] = NoDate


class NonStaff(HTTPException):
    code = 606
    name = "Non staff"
    description = "Для данного события не были найдены аудитория и/или преподаватель"


default_exceptions[606] = NonStaff


class EventNotFound(HTTPException):
    code = 607
    name = "Event not found"
    description = "Информация по данному событию не найдена"


default_exceptions[607] = EventNotFound


class BusyStaff(HTTPException):
    code = 608
    name = "Busy staff"
    description = "Аудитория и/или преподаватель уже заняты в это время"


default_exceptions[608] = BusyStaff


class TeacherNotFound(HTTPException):
    code = 609
    name = "User not found"
    description = "Преподаватель не найден"


default_exceptions[609] = TeacherNotFound


class EmptyReport(HTTPException):
    code = 610
    name = "Empty report"
    description = "Описание пусто"


default_exceptions[610] = EmptyReport


class BusyTeacher(HTTPException):
    code = 611
    name = "You are busy"
    description = "Вы неожиданно уже заняты на это время"


default_exceptions[611] = BusyTeacher


class ChildrenCount(HTTPException):
    code = 612
    name = "Too many children"
    description = f"Слишком много детей (максимум {_max_children_})"


default_exceptions[612] = ChildrenCount


class BadTime(HTTPException):
    code = 613
    name = "Bad Time"
    description = "Не верный формат времени"


default_exceptions[613] = BadTime


class BadDate(HTTPException):
    code = 614
    name = "Bad Date"
    description = "Плохой формат даты"


default_exceptions[614] = BadDate
