import os

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid_nacl_session import EncryptedCookieSessionFactory

from agallery.models import DBSession, get_engine
from agallery.models import auth as m_auth
from agallery.models.meta import Base


class PermissionsPredicate(object):
    '''
    Adds the predicate "permissions" to view_config.
    So we can attach more than a permission to a view.
    '''

    forbidden_msg = u'danger;; User without permission to access this page.'

    def __init__(self, permissions, config):
        self.permissions = permissions

    def text(self):
        return "permissions = (%s)" % ','.join(list(self.permissions))

    phash = text

    def __call__(self, context, request):
        if 'login' in request.user:
            userid = request.user['login']
        else:
            userid = None

        if isinstance(self.permissions, str):
            self.permissions = [self.permissions]

        for perm in self.permissions:
            if request.has_permission(perm, userid=userid):
                return True

        request.session.flash(self.forbidden_msg)
        raise HTTPFound(request.route_url(
            'auth_login', _query={'next': request.environ['PATH_INFO']}))


class CustomRequest(Request):
    def flash(self, msg, queue='', allow_duplicate=True):
        msg = 'info;;' + msg if ';;' not in msg else msg
        # success warning danger info
        self.session.flash(msg, queue, allow_duplicate)

    def peek_flash(self, queue=''):
        return self.session.peek_flash(queue)

    def pop_flash(self):
        return self.session.pop_flash()

    def list_flash(self, queue='', clear=True):
        key = u'_f_%s' % queue
        data = self.session[key][:]
        self.session[key] = []
        return data


class Configurations:
    _instance = None

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    S3_BUCKET = os.environ.get('S3_BUCKET', 'anchor-gallery')

    def __new__(cls, *ag, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *ag, **kw)
        return cls._instance

    @staticmethod
    def get_configs(request):
        return Configurations()


def main(global_config, **settings):
    config = Configurator(settings=settings)

    # database
    engine = get_engine(settings)
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    # authentication/authorization policies
    authn_policy = AuthTktAuthenticationPolicy(
        '^4VhV0sRwqZ' +
        'O-y_If{bea$+v;}qQKl-9.F>>4yM[RQv,lDCfO>cYp2N/gzQiq+R',
        timeout=3600 * 4,
        reissue_time=240,
        max_age=3600 * 24,
        callback=m_auth.group_finder,
        hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.add_view_predicate('permissions', PermissionsPredicate)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    # add custom methods to the request
    config.set_request_factory(CustomRequest)
    config.add_request_method(
        'agallery.models.auth.get_user', 'user',
        reify=True
    )
    config.add_request_method(
        'agallery.models.auth.get_login', 'login',
        property=True, reify=True
    )
    config.add_request_method(
        'agallery.models.auth.check_permissions', 'has_permission'
    )
    config.add_request_method(
        'agallery.Configurations.get_configs', 'config',
        property=True, reify=True
    )

    # session configuration
    hex_secret = bytes.fromhex(settings['agallery.session_secret'].strip())
    session_factory = EncryptedCookieSessionFactory(hex_secret)
    config.set_session_factory(session_factory)

    # files
    config.add_static_view('static', 'agallery:static', cache_max_age=0)
    config.add_static_view('userfiles', 'userfiles', cache_max_age=0)

    # template renderers
    config.add_renderer('.html', 'pyramid_jinja2.renderer_factory')

    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    config.scan()
    return config.make_wsgi_app()
