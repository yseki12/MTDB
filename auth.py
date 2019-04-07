import functools
import os

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .database import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route("/register", methods = ["POST", "GET"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return render_template("error.html", message = "No username provided!")
        elif not password:
            return render_template("error.html", message = "No password provided!")
        elif db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 1:
            return render_template("error.html", message = "Sorry, username already taken")

        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", 
                    {"username":username, "password": generate_password_hash(password)})

        db.commit()

        return render_template("success.html", message = "You have successfully registered")      

    return render_template("auth/register.html")
     
@bp.route("/login", methods = ["POST", "GET"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()

        if user is None:
            return render_template("error.html", message = "No username exists")
        elif not check_password_hash(user['password'], password):
            return render_template("error.html", message = "Incorrect password")

        session.clear()
        session['user_id'] = user['id']

        return redirect(url_for('index'))

    return render_template("auth/login.html")
       
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db.execute('SELECT * FROM users WHERE id = :id', {"id" : user_id}).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return render_template("error.html", message = "Must be logged in!")

        return view(**kwargs)

    return wrapped_view