import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from pyramid.scripts.common import parse_vars

from agallery.models.meta import Base
from agallery.models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)

# import or define all models here to ensure they are attached to the
# Base.metadata prior to any initialization routines
from agallery.models.auth import (  # noqa
    Permission, User, UserGroup
)
from agallery.models.gallery import (  # noqa
    Likes, Photo
)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        perms = [{
            'name': 'ROOT',
            'description': 'Allows absolutely anything.'
        }, {
            'name': 'admin',
            'description': 'Allows the user use the admin interface.'
        }, {
            'name': 'login',
            'description': 'Allows the user login into the system.'
        }, {
            'name': 'image_approve',
            'description': 'Allows the user approve an image sent.'
        }, {
            'name': 'image_send',
            'description': 'Allows the user send an image.'
        }]
        for p in perms:
            dbsession.add(Permission(**p))

        groups = [{
            'alias': 'admin',
            'name': 'Administrator',
            'permissions': set(['ROOT'])
        }, {
            'alias': 'normal',
            'name': 'Normal user',
            'permissions': set(['login', 'image_send'])
        }]
        for g in groups:
            dbsession.add(UserGroup(**g))

        model = User(
            login='someguy',
            name='Some Guy',
            email='someguy@some.mail',
            password='123456',
            profiles=set(['admin'])
        )
        dbsession.add(model)

        model = User(
            login='somegirl',
            name='Some Girl',
            email='somegirl@some.mail',
            password='123456',
            profiles=set(['admin'])
        )
        dbsession.add(model)

        model = User(
            login='normaluser',
            name='Normal User',
            email='normaluser@some.mail',
            password='123456',
            profiles=set(['normal'])
        )
        dbsession.add(model)
