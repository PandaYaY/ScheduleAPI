from flask import abort

from authorization import User
from work_with_db import db


def bug_report(data: dict, user: User):
    try:
        description = data['value']
        if not description:
            return abort(610)
    except Exception as e:
        print('bug_report', e)
        return abort(400)

    db.del_ins_upd('insert into "Bug_Report" (user_id, description) values (%s, %s)',
                   (user.real_id, description))
    return {'bug_report': 'success'}


def report_event(data: dict, _: User):
    try:
        table = data['event_type']
        event_id = int(data['event_id'])
        description = data['value']
        if not description:
            abort(610)
    except Exception as e:
        print('report_event', e)
        return abort(400)

    db.del_ins_upd('insert into "Report_Event" (table_name, event_id, description) values (%s, %s, %s)',
                   (table, event_id, description))
    return {'report_event': 'success'}
