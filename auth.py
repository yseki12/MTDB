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
        error = None

        if not username:
            error = "No username provided!"
        elif not password:
            error = "No password provided!"
        elif db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 1:
            error =  f"Sorry, username {username} already taken"

        if error is None:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", 
                {"username":username, "password": generate_password_hash(password)})

            db.commit()
            
            flash('Successful Registration!', category='success')
            session.clear()

            return redirect(url_for('index'))     
        
        flash(error, 'error')

    return render_template("auth/register.html")
     
@bp.route("/login", methods = ["POST", "GET"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        error = None

        user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()

        if user is None:
            error =  f"Username: {username} does not exist"
        elif not check_password_hash(user['password'], password):
            error =  "Incorrect password"

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            flash('Successful Login!', category='success')
            return redirect(url_for('index'))

        flash(error, 'error')

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