def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('about', '/about')

    config.add_route('auth_login', '/login')
    config.add_route('auth_logout', '/logout')

    config.add_route('gallery', '/gallery/')
    config.add_route('gallery_approve', '/gallery/approve')
    config.add_route('gallery_like', '/gallery/like')
    config.add_route('gallery_dislike', '/gallery/dislike')
