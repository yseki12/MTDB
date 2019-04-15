import os

from flask import Flask, session, render_template, request, redirect, url_for, g
from flask_session import Session

def create_app():

    app = Flask(__name__)

    # Configure session to use filesystem
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem" 
    Session(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import main_app
    app.register_blueprint(main_app.bp)
    app.add_url_rule('/', endpoint='index')

    from . import database
    database.init_app(app)

    return app
