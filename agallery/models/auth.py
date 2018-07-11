from pyramid.security import unauthenticated_userid

from sqlalchemy import (
    Boolean,
    Column,
    String
)
from sqlalchemy.orm import relationship, synonym
from sqlalchemy_utils import PasswordType

from agallery.models import DBSession, types
from agallery.models.meta import Base
from agallery.models.gallery import likes_table


class User(Base):
    __tablename__ = 'user'

    uid = synonym('login')
    login = Column(String, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(
        PasswordType(schemes=['***REMOVED***']), nullable=False
    )

    profiles = Column(types.SetType, default=set())
    permissions = Column(types.SetType, default=set())

    active = Column(Boolean(name='bool'), default=True)

    def __str__(self):
        return self.name

    likes = relationship(
        'gallery.Photo',
        secondary=likes_table,
        back_populates="likes"
    )

    def as_dict(self):
        return {
            'login': self.login,
            'name': self.name,
            'email': self.email,
        }


class Permission(Base):
    __tablename__ = 'permission'

    name = Column(String, primary_key=True, nullable=False)
    description = Column(String, nullable=False)
    active = Column(Boolean(name='bool'), default=True)

    def __str__(self):
        return self.name


class UserGroup(Base):
    __tablename__ = 'user_group'

    alias = Column(String, primary_key=True, unique=True)
    name = Column(String, nullable=False)

    permissions = Column(types.SetType, default=set())

    def __str__(self):
        return self.name


def get_permissions(user_id):
    permissions = set()
    if not user_id:
        return set()
    elif isinstance(user_id, User):
        user = user_id
    else:
        if isinstance(user_id, dict):
            user_id = user_id['login']
        user = DBSession.query(User).get(user_id)

    perms = set()
    # recupera as permissões dos groups associados ao usuário
    for profile in set(user.profiles or []):
        group = DBSession.query(UserGroup)\
            .filter(UserGroup.alias == profile).first()
        perms |= set(group.permissions or [])

    perms |= set(user.permissions or [])
    for perm in perms:
        p = DBSession.query(Permission).get(perm)
        if p is not None:
            permissions.add(p.name)

    return permissions


def get_login(request):
    return unauthenticated_userid(request)


# @cache_region('uma_hora', 'dados_user')
def do_get_user(userid):
    user = DBSession.query(User)\
        .filter(User.login == userid).first()
    return user.as_dict() if user else {}


def get_user(request):
    userid = request.login
    if userid is not None:
        userdict = do_get_user(userid)
        if len(userdict) > 0:
            return userdict
    return {}


def group_finder(user_id, request=None):
    if request:
        if 'user' not in request.session:
            user = DBSession.query(User).get(user_id)
            if user is None:
                return
            request.session['user'] = user.as_dict()
        else:
            user = request.session['user']

        return get_permissions(user_id)
    else:
        user = DBSession.query(User).get(user_id)
        if user:
            return get_permissions(user.uid)


def check_permissions(request, permissions, userid=None):
    '''
    Returns boolean showing if the user has any permission
    from the list `permissions` or not.
    '''

    if userid is None:
        userid = request.user
    if hasattr(userid, 'login'):
        userid = userid.login
    if userid is None:
        return False

    user_perms = get_permissions(userid)
    if u'ROOT' in user_perms:
        return True

    if not hasattr(permissions, '__iter__'):
        permissions = [permissions]
    for permission in permissions:
        if permission in user_perms:
            return True

    return False
