from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# login operation
from flask_login import LoginManager

# moment - time display
from flask_moment import Moment

# page down
from flask_pagedown import PageDown
# format in Bootstrap
from flask_bootstrap import Bootstrap

import logging
from flask import request
from flask.logging import default_handler


# searching
import flask_whooshalchemyplus
from flask_whooshalchemyplus import index_all
# file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)

from flask import url_for

from flask_security import Security,SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required



# Create app
app = Flask(__name__)
# app interface format
bootstrap = Bootstrap(app)

# context FOR TEST CASE
app_ctx = app.app_context()
app_ctx.push()

# moment
moment = Moment(app)
# page down for Markdown
pagedown = PageDown(app)


# config
app.config.from_object('config')

db = SQLAlchemy(app)


from .models import Permission
@app.context_processor
def inject_permissions():
    return dict(Permission=Permission)

# # email
# app.config['MAIL_SERVER']='stmp.qq.com'
# app.config['MIAL_PORT']=587
# app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USERNAME'] = 'xiaobizhang13@qq.com'
# # authentication code provide by mail settings
# app.config['MAIL_PASSWORD'] = 'fquxmjtfqyjxdijj'
# from flask_mail import Mail
# mail = Mail(app)

from .models import User,Comment,Post,Role,Follow

from flask_admin.contrib.sqla import ModelView
from .admin import CustomAdminView
from flask_admin import Admin

admin = Admin(app,template_mode='bootstrap3',
              index_view=CustomAdminView())
admin.add_view(ModelView(User, db.session,name=u'User Management',category='Models'))
admin.add_view(ModelView(Comment, db.session, name=u'Comment Management',category='Models'))
admin.add_view(ModelView(Post, db.session, name=u'Post Management',category='Models'))
admin.add_view(ModelView(Role, db.session, name=u'Role Management',category='Models'))
admin.add_view(ModelView(Follow, db.session, name=u'Follow Management',category='Models'))

# initialise LoginManager
login_manager = LoginManager(app)
login_manager.session_protection = 'strong'
# initialise url with out blueprint
login_manager.login_view = 'login'
# LoginManager
login_manager.init_app(app)
# if not login, give error message
login_manager.login_message = 'Please Log in or Sign up first'



# init app
# initialise pagedown
pagedown.init_app(app)
# search
flask_whooshalchemyplus.init_app(app)
# # index data that exist before add flask_whooshalchemyplus
# index_all(app)

from app import views, models
from .models import Role,User
# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# root_handler = logging.FileHandler('logs/root.log')
# root_handler.setLevel(logging.DEBUG)
# info_handler = logging.FileHandler('logs/info.log')
# info_handler.setLevel(logging.INFO)
# warnig_handler = logging.FileHandler('logs/warning.log')
# warnig_handler.setLevel(logging.WARNING)
# error_handler = logging.FileHandler('logs/error.log')
# error_handler.setLevel(logging.ERROR)
# logging_format = logging.Formatter(
#     '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
# root_handler.setFormatter(logging_format)
# info_handler.setFormatter(logging_format)
# warnig_handler.setFormatter(logging_format)
# error_handler.setFormatter(logging_format)
#
# # root logger
# root = logging.getLogger()
# root.addHandler(root_handler)
# root.addHandler(info_handler)
# root.addHandler(warnig_handler)
# root.addHandler(error_handler)
# root.addHandler(default_handler)
#
