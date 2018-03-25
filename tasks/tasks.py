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
import tempfile
import os
from celery import Celery
from celery.schedules import crontab

from db.mongodbo import ReportingDBOMongo, FileDBOMongo
from settings import app_settings

app_settings.get_logger()

"""
run a worker: celery -A tasks.tasks worker --loglevel=info
start beat process: celery -A tasks.tasks beat
"""

app = Celery('tasks.tasks', broker='redis://', backend='redis://localhost:6379/1')
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

@app.task
def sync_file(filename, username, kind):
    try:
        os.mkdir(app_settings.FILE_BASE_PATH_TEMPLATE.format(username), mode=711)
    except FileNotFoundError:
        app_settings.logger.warning("Creating files path failed: home directory doesn't exist", extra={"actor":"INSTANCE " + app_settings.BIGCGI_INSTANCE_ID, "action":"create file directory", "object":username})
    except FileExistsError:
        pass
    try:
        os.mkdir(app_settings.CGI_BASE_PATH_TEMPLATE.format(username), mode=711)
    except FileNotFoundError:
        app_settings.logger.warning("Creating cgi path failed: home directory doesn't exist", extra={"actor":"INSTANCE " + app_settings.BIGCGI_INSTANCE_ID, "action":"create cgi directory", "object":username})
    except FileExistsError:
        pass   
    db = FileDBOMongo(app_settings.get_database())
    sync_file = db.get_file(filename, username, kind)
    if sync_file:
        with tempfile.NamedTemporaryFile(dir=app_settings.TMP_FILE_STORE) as temp_storage:
            temp_storage.write(sync_file)
            if kind == "file":
                final_path = os.path.join(app_settings.FILE_BASE_PATH_TEMPLATE.format(username), filename)
                permissions = "400"
            elif kind == "app":
                final_path = os.path.join(app_settings.CGI_BASE_PATH_TEMPLATE.format(username), filename)
                permissions = "700"
            status = os.system("sudo script/movefile.tcl {} {} {} {}".format(username, tmp_storage.name, final_path, permissions))
                
            app_settings.logger.info("file synced", extra={"actor":"INSTANCE " + app_settings.BIGCGI_INSTANCE_ID, "action": "sync file", "object": username+"/"+filename})
    else: #file could have been deleted before task executed
        app_settings.logger.warning("filed to sync file: does not exist in db", extra={"actor":"INSTANCE " + app_settings.BIGCGI_INSTANCE_ID, "action":"sync file", "object": username+"/"+filename})
