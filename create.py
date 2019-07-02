import os

from flask import Flask, session, render_template, request, redirect, url_for, g
from flask_session import Session

def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY","prod")
    # Configure session to use filesystem
    app.config["SESSION_PERMANENT"] = True
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    from mtdb import auth
    app.register_blueprint(auth.bp)

    from mtdb import main_app
    app.register_blueprint(main_app.bp)
    app.add_url_rule('/', endpoint='index')

    from mtdb import database
    database.init_app(app)

    return app