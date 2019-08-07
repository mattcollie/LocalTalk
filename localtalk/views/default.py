from flask import Blueprint


default_blueprint = Blueprint('views', __name__, template_folder='../templates')


@default_blueprint.route('')
def index():
    return 'Hello World!'
