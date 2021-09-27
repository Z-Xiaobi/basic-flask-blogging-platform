import os

basedir = os.path.abspath(os.path.dirname(__file__))
# enable CSRF prevetion
WTF_CSRF_ENABLED = True
# secret key
SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
# admin email set in consle
# FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
FLASKY_ADMIN = '935213752@qq.com'

# upload folder path
UPLOAD_FOLDER = os.getcwd() + '/app/static/img/avatar_uploads/'
# print(UPLOAD_FOLDER)
#


MAX_SEARCH_RESULTS = 100

SQLALCHEMY_RECORD_QUERIES = True
SLOW_DB_QUERY_TIME=0.5


SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True
