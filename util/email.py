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

import smtplib
from email.mime.text import MIMEText

from settings import app_settings

app_settings.get_logger()

def send_gmail(subject, message, to, from_email):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to

    smtp_host = 'smtp.gmail.com'
    smtp_port = 587

    server = smtplib.SMTP(smtp_host, smtp_port)
    server.starttls()
    server.login(app_settings.SMTP_USERNAME, app_settings.SMTP_PASSWORD)
    text = msg.as_string()
    server.send_message(msg)
    server.quit()
