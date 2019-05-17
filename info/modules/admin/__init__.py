from flask import Blueprint, request, url_for, session, redirect

admin_blue = Blueprint('admin',__name__,url_prefix='/admin')
from . import views

@admin_blue.before_request
def before_request():
    if not request.url.endswith(url_for('admin.admin_login')):
        user_id = session.get('user_id')
        is_admin = session.get('is_admin',False)
        if not user_id and not is_admin:
            return redirect('/')