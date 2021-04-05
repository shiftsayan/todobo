import requests
from datetime import datetime
from collections import namedtuple

from secrets import GOOGLE_SHEETS_ENDPOINT

OverdueCheck = namedtuple('OverdueCheck', 'name due_date ta email')

def get_overdue_checks(dt=datetime.now().replace(hour=0,minute=0,second=0)):
    response = requests.get(GOOGLE_SHEETS_ENDPOINT)
    emails = response.json()['emails']
    checks = response.json()['checks']
    overdue_checks = []
    for check in checks:
        dt_due = datetime.fromtimestamp(check['due_date'])
        if dt <= dt_due:
            continue
        for (ta, complete) in check['tas'].items():
            if not complete:
                overdue_checks.append(
                    OverdueCheck(
                        check['name'], 
                        check['due_date'], 
                        ta, emails[ta]
                    )
                )
    return overdue_checks