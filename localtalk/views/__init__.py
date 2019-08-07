from localtalk.views.default import default_blueprint


def init_views(app):
    app.register_blueprint(default_blueprint, url_prefix='/')
