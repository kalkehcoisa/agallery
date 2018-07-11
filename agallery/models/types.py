import pickle
import uuid

from sqlalchemy import types


class SetType(types.TypeDecorator):
    '''
    '''

    impl = types.LargeBinary

    def __init__(self):
        types.TypeDecorator.__init__(self)

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not isinstance(value, set):
                raise Exception(
                    'The value must be an instance of set().'
                    'Gotten "{}"'.format(value)
                )
            value = pickle.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = set(pickle.loads(value))
        return value


class UUIDType(types.TypeDecorator):
    '''
    '''

    impl = types.Text

    def __init__(self):
        types.TypeDecorator.__init__(self)

    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, uuid.UUID):
                value = str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = uuid.UUID(value)
        return value
