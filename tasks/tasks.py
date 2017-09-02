"""
This file is part of bigCGI.

bigCGI is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

bigCGI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with bigCGI.  If not, see <http://www.gnu.org/licenses/>.
"""

from celery import Celery
from celery.schedules import crontab
from db.mongodbo import ReportingDBOMongo
from settings import app_settings

"""
run a worker: celery -A tasks.tasks worker --loglevel=info
start beat process: celery -A tasks.tasks beat
"""

app = Celery('tasks.tasks', broker='pyamqp://guest@localhost//', backend='rpc://')
app.conf.beat_schedule = {
    'generate_monthly_report': {
        'task': 'tasks.tasks.generate_monthly_report',
        'schedule': crontab(0, 0, day_of_month='1'),
        'args': tuple(),
    },
}
app.conf.timezone = 'UTC'
app.conf.worker_concurrency = 2

@app.task
def generate_monthly_report():
    r = ReportingDBOMongo(app_settings.get_database())
    r.create_monthly_hits_report()
    return True
    
