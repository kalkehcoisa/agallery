from pyramid.view import (
    notfound_view_config,
    view_config
)


@view_config(
    permissions=('can_login',),
    route_name='home',
    renderer='agallery:templates/home.html'
)
def home(request):
    return {'one': '', 'project': 'Anchor Gallery'}


@notfound_view_config(renderer='../templates/404.html')
def notfound_view(request):
    request.response.status = 404
    return {}
