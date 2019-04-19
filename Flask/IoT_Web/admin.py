from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request
import flask_login as login
from flask_login import current_user


class AdminView(ModelView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_folder = 'static'

    def is_accessible(self):
        if current_user.id == 1:
            return login.current_user.is_authenticated
        else:
            return redirect(url_for('home'))

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('home', next=request.url))

    # def set_password(self, password):
    #     self.pw_hash = generate_password_hash(password)
    #
    # def check_password(self, password):
    #     return check_password_hash(self.pw_hash, password)
