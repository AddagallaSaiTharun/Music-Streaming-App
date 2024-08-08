from flask import Flask
from flask_restful import Resource, Api
from application.database import db
from application.config import localConfig

APP = None
API = None

def create_app():
    """
    Creates and configures the Flask application.

    This function initializes the Flask app, loads configuration settings,
    initializes the database, and creates a Flask-RESTful API instance.

    Returns:
        A tuple containing the Flask app and the Flask-RESTful API instance.
    """
    flask_app = Flask(__name__)
    flask_app.config.from_object(localConfig)
    db.init_app(flask_app)
    flask_api = Api(flask_app)
    flask_app.app_context().push()
    return flask_app, flask_api

APP,API = create_app()

def decodeutf8(value):
    """
    Decodes a UTF-8 encoded string.

    This function takes a UTF-8 encoded string and decodes it to a regular string.

    Args:
        value: The UTF-8 encoded string to decode.

    Returns:
        The decoded string.
    """
    decoded_value = value.decode('utf-8')
    return decoded_value

APP.jinja_env.filters['decodeutf8'] = decodeutf8
from application.controllers import *


if __name__ == '__main__':
    APP.run(debug=True)