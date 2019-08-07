def create_app():
    from flask import Flask
    from localtalk.views import init_views

    app = Flask(__name__)

    # init views
    init_views(app)

    return app
