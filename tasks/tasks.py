from celery import Celery
from celery.schedules import crontab
from db.mongodbo import ReportingDBOMongo

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
    r = ReportingDBOMongo()
    r.create_monthly_hits_report()
    return True
    
