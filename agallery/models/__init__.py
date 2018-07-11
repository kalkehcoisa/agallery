from sqlalchemy import create_engine
from sqlalchemy.orm import (
    configure_mappers,
    scoped_session,
    sessionmaker
)
from sqlalchemy.pool import StaticPool
import zope.sqlalchemy
from zope.sqlalchemy import ZopeTransactionExtension

# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()


DBSession = scoped_session(
    sessionmaker(
        extension=ZopeTransactionExtension(),
        autoflush=False,
        expire_on_commit=True))


def get_engine(settings, prefix='sqlalchemy.'):
    engine = create_engine(
        settings['sqlalchemy.url'],
        connect_args={'check_same_thread': False},
        poolclass=StaticPool
    )
    return engine


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, transaction_manager):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example::

          import transaction

          engine = get_engine(settings)
          session_factory = get_session_factory(engine)
          with transaction.manager:
              dbsession = get_tm_session(session_factory, transaction.manager)

    """
    dbsession = session_factory()
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction_manager)
    return dbsession


def includeme(config):
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('agallery.models')``.

    """
    settings = config.get_settings()
    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'

    # use pyramid_tm to hook the transaction lifecycle to the request
    config.include('pyramid_tm')

    # use pyramid_retry to retry a request when transient exceptions occur
    config.include('pyramid_retry')

    session_factory = get_session_factory(get_engine(settings))
    config.registry['dbsession_factory'] = session_factory

    # make request.dbsession available for use in Pyramid
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(session_factory, r.tm),
        'dbsession',
        reify=True
    )
