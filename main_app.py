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
    gyms = db.execute("""SELECT gyms.id, gyms.gym, locations.city, 
                                ROUND(AVG(reviews.rating)::numeric,1) as average,
                                COUNT(reviews.rating) as count
                        FROM gyms
                        JOIN locations on locations.id = gyms.location
                        LEFT JOIN reviews on gyms.id = reviews.gym_id
                        GROUP BY gyms.id, locations.city
                        ORDER BY gyms.id""").fetchall()
                        
    return render_template("main_app/index.html", gyms = gyms)

@bp.route("/gyms/<int:gym_id>")
def gym(gym_id):
    ###List details about certain gym###

    gyms = db.execute("SELECT * FROM gyms JOIN locations ON locations.id = gyms.location WHERE gyms.id = :id", {"id": gym_id}).fetchone()
    if gyms is None:
        return render_template("error.html", message = "Gym does not exist")

    ratings = db.execute("SELECT gym_id, reviews.rating, reviews.review, reviews.review_date, users.username FROM reviews JOIN users ON users.id = reviews.user_id WHERE gym_id = :gym_id ORDER BY reviews.review_date DESC", {"gym_id": gym_id}).fetchall()      

    return render_template("main_app/gym.html", gyms = gyms, ratings = ratings)

@bp.route("/reviewgym", methods = ["POST", "GET"])
@login_required
def reviewgym():

    if request.method == "POST":

        gym_id = int(request.form.get("gym_id"))
        review = request.form.get("review")

        if not review:
            return render_template("error.html", message = "No Review Provided!")

        try:
            rating = int(request.form.get("rating"))
            if not 0 <= rating <= 5:
                raise ValueError
        except ValueError:
            return render_template("error.html", message = "Invalid rating!")
        
        db.execute("INSERT INTO reviews (rating, review, gym_id, review_date, user_id) VALUES (:rating, :review, :gym_id , :review_date, :user_id)", {"rating": rating, "review": review, "gym_id": gym_id, "review_date": current_date, "user_id": g.user['id']})
        
        db.commit()

        return render_template("success.html", message = "You have successfully posted a review")
    
    gyms = db.execute("SELECT * FROM gyms").fetchall()

    return render_template("main_app/reviewpage.html", gyms = gyms)
