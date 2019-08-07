from flask import Blueprint


default_blueprint = Blueprint('views', __name__, template_folder='../templates')


@default_blueprint.route('')
def index():
    from localtalk.application import server
    count = server._addresses
    return f'Hello World! {len(count)}'
