from flask_admin import BaseView, expose,AdminIndexView
from flask import url_for,redirect
from flask_login import LoginManager, current_user,login_user, login_required, logout_user
from app import app
from .models import Permission

class CustomAdminView(AdminIndexView):
    """View function of Flask-Admin for Custom page."""

    @expose('/', methods=['GET', 'POST'])
    def index(self):
        # Get URL for the custom view method
        user_list_url = url_for('user.index_view')
        return self.render('/admin_index.html', user_list_url=user_list_url)

    @expose('/admin_logout', methods=['GET', 'POST'])
    def admin_logout(self):
        app.logger.debug("trigger function 'admin_logout'")
        logout_user()
        app.logger.debug('logout admin user')
        app.logger.info('logout admin user')
        return self.render('/admin_index.html')

    @expose('/back')
    def back(self):
        app.logger.debug("trigger function 'back'")
        app.logger.debug('admin user back to index page')
        app.logger.info('admin user back to index page')
        return self.render('/admin_index.html')

    def is_accessible(self):
        if current_user.is_authenticated and current_user.can(Permission.ADMIN) :
            return True
        return False

