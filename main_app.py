import os
from datetime import date

from flask import Flask, session, render_template, request, redirect, url_for, g, Blueprint
from flask_session import Session

from .auth import login_required
from .database import db

current_date = date.today()

bp = Blueprint('main_app', __name__)

@bp.route("/")
def index():
    gyms = db.execute("""SELECT gyms.id, gyms.gym, locations.city, ROUND(AVG(reviews.rating)::numeric,1) as average,
                         COUNT(reviews.rating) as count FROM gyms JOIN locations on locations.id = gyms.location
                        LEFT JOIN reviews on gyms.id = reviews.gym_id GROUP BY gyms.id, locations.city ORDER BY gyms.id""").fetchall()
                        
    return render_template("main_app/index.html", gyms = gyms)

@bp.route("/gyms/<int:gym_id>")
def gym(gym_id):
    ###List details about certain gym###

    gyms = db.execute("SELECT * FROM gyms JOIN locations ON locations.id = gyms.location WHERE gyms.id = :id", {"id": gym_id}).fetchone()
    if gyms is None:
        return render_template("error.html", message = "Gym does not exist")

    ratings = db.execute("""SELECT gym_id, reviews.rating, reviews.rating_training, reviews.rating_facility, 
                            reviews.rating_location, reviews.review, reviews.review_date, users.username, reviews.stay_length
                            FROM reviews JOIN users ON users.id = reviews.user_id WHERE gym_id = :gym_id 
                            ORDER BY reviews.review_date DESC""", {"gym_id": gym_id}).fetchall()      

    return render_template("main_app/gym.html", gyms = gyms, ratings = ratings)

def calc_days(length, unit):
    if unit == 'Days':
        return length
    elif unit == 'Weeks':
        return 7*length
    elif unit == 'Months':
        return 30 * length
    elif unit == 'Years':
        return 365 * length

@bp.route("/reviewgym", methods = ["POST", "GET"])
@login_required
def reviewgym():

    if request.method == "POST":
        
        units_of_time = ['Days', 'Weeks', 'Months', 'Years']

        gym_id = int(request.form.get("gym_id"))
        review = request.form.get("review")
        unit_stay = request.form.get('unit_stay')
        ratings_form_name = ["rate_training", "rate_facility", "rate_locationcost", "rate_overall"]
        ratings_dict = {}

        if not unit_stay in units_of_time:
            return render_template("error.html", message = "Please choose a unit of time")
        elif not review:
            return render_template("error.html", message = "No Review Provided!")

        try:
            length_stay = int(request.form.get('length_stay'))
        except ValueError:
            return render_template("error.html", message = "Invalid Length of Stay!")

        total_stay = str(length_stay) + ' ' + unit_stay
        stay_days = calc_days(length_stay, unit_stay)

        for rating in ratings_form_name:
            if request.form.get(rating):
                try:
                    rating_input = int(request.form.get(rating))
                    if not 0 <= rating_input <= 5:
                        raise ValueError
                except ValueError:
                    return render_template("error.html", message = "Invalid rating!")
                else:
                    ratings_dict[rating] = rating_input
            else:
                return render_template("error.html", message = "Please include all ratings!")
        
        db.execute("""INSERT INTO reviews (rating, review, gym_id, review_date, user_id, rating_training, rating_facility, rating_location, stay_length, stay_days) 
                      VALUES (:rating, :review, :gym_id , :review_date, :user_id, :rating_training, :rating_facility, :rating_location, :stay_length, :stay_days)""", 
                      {"rating": ratings_dict["rate_overall"], "review": review, "gym_id": gym_id, "review_date": current_date, "user_id": g.user['id'], 
                      "rating_training": ratings_dict["rate_training"], "rating_facility": ratings_dict["rate_facility"], 
                      "rating_location": ratings_dict["rate_locationcost"], "stay_length": total_stay, "stay_days": stay_days})
        
        db.commit()

        return render_template("success.html", message = "You have successfully posted a review")
    
    gyms = db.execute("SELECT * FROM gyms").fetchall()

    return render_template("main_app/reviewpage.html", gyms = gyms)