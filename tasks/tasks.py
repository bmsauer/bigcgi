from celery import Celery
from db.mongodbo import ReportingDBOMongo

app = Celery('tasks', broker='pyamqp://guest@localhost//', backend='rpc://')

@app.task
def add(x, y):
    return x + y

@app.task
def generate_monthly_report():
    r = ReportingDBOMongo()
    r.create_monthly_hits_report()
    return True
    
