from cork import Cork, AuthException, AAAException
from cork.backends import MongoDBBackend
from settings import app_settings

app_settings.get_logger()

def get_cork_instance():
    smtp_url = 'ssl://{}:{}@smtp.gmail.com:465'.format(app_settings.SMTP_USERNAME, app_settings.SMTP_PASSWORD)
    cork = Cork(
        backend=MongoDBBackend(db_name=app_settings.DATABASE_CORK,
                               username=app_settings.DATABASE_USERNAME,
                               password=app_settings.DATABASE_PASSWORD,
                               authdb=app_settings.DATABASE_MAIN,
                               initialize=False
        ),
        email_sender=app_settings.SMTP_USERNAME+"@gmail.com",
        smtp_url=smtp_url,
        preferred_hashing_algorithm='scrypt',
        pbkdf2_iterations=10,
    )
    return cork
