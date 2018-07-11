from agallery.forms import OrderedSubmitForm
from agallery.models.auth import User


class LoginForm(OrderedSubmitForm):
    class Meta:
        model = User
        only = ('login', 'password')
        field_order = ('*', 'submit')
