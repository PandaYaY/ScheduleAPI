from web_api import web_check_auth
from web_api import web_one_event

from get_events import full_load
from get_events import get_course
from get_events import get_events
from get_events import new_events

from reports import report_event
from reports import bug_report

from freedom import event_freedom
from freedom import free_date

from decodes import decode
from decodes import employee
from decodes import get_skills

from blocks import get_block
from blocks import create_block

from employee import create_user
from employee import set_skills

from classrooms import create_classroom
from classrooms import set_classroom

from create_event import create_event
from create_event import confirm_event
from create_event import update_event

from delete_events import delete_event
from delete_events import get_deleted_events

from share_event import auction
from share_event import take_event


# Функции по уровню доступа и методам
functions = {
    'GET': (
        (
            'get_events',
            'get_course',
            'new_events',
            'decode',
            'event_freedom',
            'get_skills',
            'employee',
            'get_block',
            'free_date',
            'get_deleted_events',
            'full_load',
        ),  # 1
        (
            'get_events',
            'get_course',
            'new_events',
            'decode',
            'event_freedom',
            'get_skills',
            'employee',
            'get_block',
            'free_date',
            'full_load',
        ),  # 2
        (
            'get_events',
            'get_course',
            'new_events',
            'full_load',
        ),  # 3
    ),

    'POST': (
        (
            'report_event',
            'bug_report',
            'create_event',
            'delete_event',
            'update_event',

            'new_events'
        ),  # 1
        (
            'report_event',
            'bug_report',
            'confirm_event',
            'delete_event',
            'update_event',
            'create_block',
            'set_skills',
            'create_user',
            'create_classroom',
            'set_classroom',

            'new_events'
        ),  # 2
        (
            'auction',
            'take_event',
            'report_event',
            'bug_report',

            'web_check_auth',
            'web_one_event',

            #  TODO: костыль
            'new_events',
        ),  # 3
    )
}
