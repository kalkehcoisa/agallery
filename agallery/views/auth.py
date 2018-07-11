from datetime import datetime, timedelta
import uuid

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render
from pyramid.security import (
    forget,
    remember
)
from pyramid.view import view_config

from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound

from agallery.forms.auth import LoginForm
from agallery.models import DBSession
from agallery.models.auth import User


@view_config(
    route_name='auth_login',
    renderer='agallery:templates/form.html'
)
def login(request):
    form = LoginForm(request.POST)
    if request.method == 'POST' and form.validate():
        logged = login_user(request, form.login.data, form.password.data)
        if logged is not None:
            headers = remember(request, logged.login)
            return HTTPFound(
                location=request.params.get('next') or '/',
                headers=headers
            )
    return {
        'form': form,
        'action': request.route_url('auth_login')
    }


def login_user(request, login, passwd):
    try:
        user = DBSession.query(User).filter(or_(
            User.login == login,
            User.email == login)
        ).one()
    except NoResultFound:
        user = None
        request.flash(u'danger;; Login or password invalid.')
        return None

    if user.active is False:
        request.flash(u'danger;; User disabled.')
        return None

    if user.password == passwd:
        if request.has_permission('login', userid=user.login):
            request.flash(u'success;; Login successful.')
            return user
        else:
            request.flash(
                u'danger;;User doesn\'t have permission to login.')
    else:
        request.flash(u'danger;; Login or password invalid.')
    return None
