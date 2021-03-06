import os
from datetime import date

from flask import Flask, session, render_template, request, redirect, url_for, g, Blueprint, flash
from flask_session import Session
from werkzeug.exceptions import abort

from mtdb.auth import login_required
from mtdb.database import db

current_date = date.today()

bp = Blueprint('main_app', __name__)

@bp.route("/")
def index():
    gyms = db.execute("""SELECT gyms.id, gyms.gym, locations.city, ROUND(AVG(reviews.rating)::numeric,1) as average,
                         COUNT(reviews.rating) as count, SUM(reviews.stay_days) as sum_days FROM gyms JOIN locations on locations.id = gyms.location
                        LEFT JOIN reviews on gyms.id = reviews.gym_id GROUP BY gyms.id, locations.city ORDER BY gyms.gym""").fetchall()
                        
    return render_template("main_app/index.html", gyms = gyms)

@bp.route("/gyms/<int:gym_id>")
def gym(gym_id):
    ###List details about certain gym###

    gyms = db.execute("SELECT * FROM gyms JOIN locations ON locations.id = gyms.location WHERE gyms.id = :id", {"id": gym_id}).fetchone()
    if gyms is None:
        return render_template("error.html", message = "Gym does not exist")

    ratings = db.execute("""SELECT gym_id, reviews.rating, reviews.rating_training, reviews.rating_facility, 
                            reviews.rating_location, reviews.review, reviews.review_date, users.username, 
                            users.id AS userid, reviews.stay_length, reviews.id AS reviewid, COUNT(likes.liked) as count
                            FROM reviews 
                            JOIN users ON users.id = reviews.user_id 
                            LEFT JOIN likes ON reviews.id = likes.review_id
                            WHERE gym_id = :gym_id 
                            GROUP BY reviews.id, users.username, users.id
                            ORDER BY reviews.review_date DESC""", {"gym_id": gym_id}).fetchall()  

    likes = db.execute("""SELECT l.id, l.review_id, l.user_id as like_userid, l.liked, r.gym_id FROM likes l JOIN reviews r on l.review_id = r.id WHERE gym_id = :gym_id""",
                        {"gym_id": gym_id}).fetchall()

    return render_template("main_app/gym.html", gyms = gyms, ratings = ratings, likes = likes)

def calc_days(length, unit):
    if unit == 'Days' or unit == 'Day':
        return length
    elif unit == 'Weeks' or unit == 'Week':
        return 7*length
    elif unit == 'Months' or unit == 'Month':
        return 30 * length
    elif unit == 'Years' or unit == 'Year':
        return 365 * length

@bp.route("/reviewgym", methods = ["POST", "GET"])
@login_required
def reviewgym():

    if request.method == "POST":
        
        error = None

        units_of_time = ['Days', 'Weeks', 'Months', 'Years']

        gym_id = int(request.form.get("gym_id"))
        review = request.form.get("review")
        unit_stay = request.form.get('unit_stay')
        ratings_form_name = ["rate_training", "rate_facility", "rate_locationcost", "rate_overall"]
        ratings_dict = {}

        if db.execute("SELECT * FROM gyms WHERE id = :id", {"id": gym_id}).rowcount == 0:
            error = "No gym with that ID"

        if not unit_stay in units_of_time:
            error =  "Please choose a unit of time"
        elif not review:
            error = "No Review Provided!"

        try:
            length_stay = int(request.form.get('length_stay'))
            if length_stay == 0:
                raise ValueError
        except ValueError:
            error = "Invalid Length of Stay!"

        for rating in ratings_form_name:
            if request.form.get(rating):
                try:
                    rating_input = int(request.form.get(rating))
                    if not 0 <= rating_input <= 5:
                        raise ValueError
                except ValueError:
                    error = "Invalid rating!"
                else:
                    ratings_dict[rating] = rating_input
            else:
                error = "Please include all ratings!"
        
        if error is None:

            if length_stay == 1:
                unit_stay = unit_stay[:-1]

            total_stay = str(length_stay) + ' ' + unit_stay
            stay_days = calc_days(length_stay, unit_stay)

            db.execute("""INSERT INTO reviews (rating, review, gym_id, review_date, user_id, rating_training, rating_facility, rating_location, stay_length, stay_days) 
                        VALUES (:rating, :review, :gym_id , :review_date, :user_id, :rating_training, :rating_facility, :rating_location, :stay_length, :stay_days)""", 
                        {"rating": ratings_dict["rate_overall"], "review": review, "gym_id": gym_id, "review_date": current_date, "user_id": g.user['id'], 
                        "rating_training": ratings_dict["rate_training"], "rating_facility": ratings_dict["rate_facility"], 
                        "rating_location": ratings_dict["rate_locationcost"], "stay_length": total_stay, "stay_days": stay_days})
            db.commit()

            flash('You have successfully posted a review', category='success')
            return redirect(url_for('index'))

        flash(error, 'error')
    
    gyms = db.execute("SELECT * FROM gyms ORDER BY gym").fetchall()

    return render_template("main_app/reviewpage.html", gyms = gyms)

def get_review(id, check_author=True):

    review = db.execute("""SELECT r.id, r.gym_id, r.rating, r.rating_training, r.rating_facility, r.rating_location, r.review, r.review_date, 
                            r.stay_length, user_id, g.gym as gym_name
                            FROM reviews r JOIN users u on r.user_id = u.id JOIN gyms g on r.gym_id = g.id WHERE r.id = :id""", {"id": id}).fetchone() 
    
    if review is None:
        abort(404, "Review id {0} doesn't exist.".format(id))
    
    if check_author and review['user_id'] != g.user['id']:
        abort(403)

    return review
    
@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    get_review(id)
    db.execute("DELETE FROM reviews WHERE id = :id", {"id": id})
    db.commit()
    flash('Review Deleted!', category='success')
    return redirect(url_for('index'))

@bp.route('/<int:id>/update', methods = ["POST", "GET"])
@login_required
def update(id):

    old_review = get_review(id)

    if request.method == "POST":
        
        error = None
        units_of_time = ['Days', 'Weeks', 'Months', 'Years']

        gym_id = old_review['gym_id']
        review = request.form.get("review")
        unit_stay = request.form.get('unit_stay')
        ratings_form_name = ["rate_training", "rate_facility", "rate_locationcost", "rate_overall"]
        ratings_dict = {}

        if not unit_stay in units_of_time:
            error = "Please choose a unit of time"
        elif not review:
            error = "No Review Provided!"

        try:
            length_stay = int(request.form.get('length_stay'))
        except ValueError:
            error = "Invalid Length of Stay!"

        for rating in ratings_form_name:
            if request.form.get(rating):
                try:
                    rating_input = int(request.form.get(rating))
                    if not 0 <= rating_input <= 5:
                        raise ValueError
                except ValueError:
                    error =  "Invalid rating!"
                else:
                    ratings_dict[rating] = rating_input
            else:
                error = "Please include all ratings!"

        if error is None:

            if length_stay == 1:
                unit_stay = unit_stay[:-1]

            total_stay = str(length_stay) + ' ' + unit_stay
            stay_days = calc_days(length_stay, unit_stay)
        
            db.execute("""UPDATE reviews SET rating = :rating, review = :review, gym_id = :gym_id, review_date = :review_date, user_id = :user_id, 
                        rating_training = :rating_training, rating_facility = :rating_facility, rating_location = :rating_location, stay_length = :stay_length, stay_days = :stay_days
                        WHERE id = :id""", 
                        {"rating": ratings_dict["rate_overall"], "review": review, "gym_id": gym_id, "review_date": current_date, "user_id": g.user['id'], 
                        "rating_training": ratings_dict["rate_training"], "rating_facility": ratings_dict["rate_facility"], 
                        "rating_location": ratings_dict["rate_locationcost"], "stay_length": total_stay, "stay_days": stay_days, "id": id})
            
            db.commit()
            
            flash('Review Edited!', category='success')

            return redirect(url_for('index'))

        flash(error, 'error')

    return render_template("main_app/update.html", old_review = old_review)

@bp.route('/user/edit/<username>', methods = ["POST","GET"])
@login_required
def edit_user_profile(username):

    profile = db.execute("SELECT id, username, name, email, location, experience, fighter FROM users WHERE username = :username", {"username": username}).fetchone()

    if request.method == "POST":

        error = None

        form_items = ["realname","email","location","experience","fighter"]
        form_dict = {}

        for item in form_items:

            form_input = request.form.get(item)

            if not form_input or form_input == '':
                form_input = None

            form_dict[item] = form_input

        if error is None:

            db.execute("UPDATE users SET name = :name, email = :email, location = :location, experience = :experience, fighter = :fighter WHERE username = :username", 
            {"name": form_dict["realname"], "email": form_dict["email"], "location":form_dict["location"], "experience":form_dict["experience"], "fighter":form_dict["fighter"], "username": username})
            db.commit()

            flash('Profile Updated!', category='success')

            return redirect(url_for('main_app.edit_user_profile', username = username))

    return render_template("main_app/editprofile.html", profile = profile)

@bp.route('/user/view/<username>', methods = ["GET"])
@login_required
def view_user_profile(username):

    profile = db.execute("SELECT id, username, name, email, location, experience, fighter FROM users WHERE username = :username", {"username": username}).fetchone()

    if profile is None:
        flash("User does not exist", 'error')

    return render_template("main_app/viewprofile.html", profile = profile)

def get_gym(id):

    gym = db.execute("SELECT r.id AS review_id, g.id AS gym_id FROM reviews r JOIN gyms g ON r.gym_id = g.id WHERE r.id = :id", {"id": id}).fetchone()

    return gym

@bp.route('/<int:id>/like', methods=['POST'])
@login_required
def like_review(id):

    error = None
    user_id = session.get('user_id')
    gym = get_gym(id)

    if db.execute("SELECT * FROM likes WHERE review_id = :review_id AND user_id = :user_id", {"review_id": id, "user_id": user_id}).rowcount != 0:
        error = "You already liked this review!"

    if error is None:
        db.execute("INSERT INTO likes (review_id, user_id, liked) VALUES (:review_id, :user_id, :liked)", {"review_id": id, "user_id": user_id, "liked": "1"})
        db.commit()

        flash('Liked!', category='success')
        return redirect(url_for('main_app.gym', gym_id = gym['gym_id']))

    flash(error, 'error')

    return redirect(url_for('main_app.gym', gym_id = gym['gym_id']))

@bp.route('/<int:id>/unlike', methods=['POST'])
@login_required
def unlike_review(id):

    error = None
    user_id = session.get('user_id')
    gym = get_gym(id)

    if db.execute("SELECT * FROM likes WHERE review_id = :review_id AND user_id = :user_id", {"review_id": id, "user_id": user_id}).rowcount == 0:
        error = "You have not liked this review!"

    if error is None:
        db.execute("DELETE FROM likes WHERE review_id = :review_id AND user_id = :user_id", {"review_id": id, "user_id": user_id})
        db.commit()

        flash('Unliked!', category='success')
        return redirect(url_for('main_app.gym', gym_id = gym['gym_id']))

    flash(error, 'error')

    return redirect(url_for('main_app.gym', gym_id = gym['gym_id']))