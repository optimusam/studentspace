from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, jsonify, render_template, redirect, session, url_for, flash
from sqlalchemy import *
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode
from models import *
import psycopg2
import constants
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)
if AUTH0_AUDIENCE is '':
    AUTH0_AUDIENCE = AUTH0_BASE_URL + '/userinfo'


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = env.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = env.get("SECRET_KEY")

@app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response


oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile',
    },
)
db.init_app(app)

def isLoggedin():
    if constants.PROFILE_KEY in session:
        userinfo=session[constants.PROFILE_KEY]
        return (True,userinfo)
    return (False, None)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.PROFILE_KEY not in session:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated

@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    session[constants.JWT_PAYLOAD] = userinfo
    session[constants.PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect(session["prevURL"], 302)

@app.route("/")
def index():
    return render_template("index.html", title="Rate My Teacher", islog=isLoggedin())

@app.route("/login", methods=["GET","POST"])
def login():
    if constants.PROFILE_KEY in session:
        return redirect(request.referrer, 302)
    session["prevURL"] = request.referrer
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)

@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('index', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

@app.route("/result", methods=["GET","POST"])
def getResult():
    name = request.args.get("name").strip() or None
    dept = request.args.get("dept").strip() or None
    college = request.args.get("college").strip() or None
    if name and dept and college:
        result = db.session.query(Teacher, College).filter(and_(Teacher.college_id == College.id, Teacher.name.ilike(f"%{name}%"),Teacher.department.ilike(f"%{dept}%"),College.name.ilike(f"%{college}%"))).all()
        return render_template("result.html", title="Results", result=result, islog=isLoggedin())
    else:
        flash('Please enter all the details!')
        return redirect(url_for('index'), 302)

@app.route("/teacher/<int:teacher_id>")
def review(teacher_id):
    islog = isLoggedin()

    res = Teacher.query.get(teacher_id)
    reviews = db.session.query(Review, User).filter(and_(Review.user_id == User.id, Review.teacher_id == teacher_id)).all()
    review_count = len(reviews)
    avgRating = "N/A"

    if review_count > 0:
        avgRating = db.session.query(func.avg(Review.rating).label('average')).filter_by(teacher_id=teacher_id).first()[0]
        avgRating = round(avgRating,2)

    if not islog[0]:
        return render_template("review.html", title=f"Review {res.name}", res=res, reviews=reviews, avgRating=avgRating, alreadyReviewed=False, islog=islog, count=review_count)
    
    userinfo = islog[1]
    user_review = Review.query.filter_by(user_id=userinfo['user_id'],teacher_id=teacher_id).first()
    alreadyReviewed = True if user_review != None else False
    return render_template("review.html", title=f"Review {res.name}", avgRating=avgRating, res=res, reviews=reviews, alreadyReviewed=alreadyReviewed, user_review=user_review, userinfo=userinfo, islog=islog, count=review_count)
            

@app.route("/teacher/<int:teacher_id>/review", methods=["POST"])
@requires_auth
def postReview(teacher_id):
    userinfo=session[constants.PROFILE_KEY]
    rating = request.form.get("rating")
    course = request.form.get("course").strip() or None
    review = request.form.get("review").strip() or None
    isAnon = request.form.get("anon") != None

    user = User.query.get(userinfo['user_id'])
    if user is None:
        userID=userinfo["user_id"]
        name = userinfo["name"]
        if userID.startswith('email'):
            name=name[0:3]
        u = User(id=userID,name=name, picture=userinfo["picture"])
        db.session.add(u)

    if int(rating) >= 1 and int(rating)<=5 and review and course:
        r = Review.query.filter_by(user_id=userinfo['user_id'], teacher_id=teacher_id).first()
        if r == None:
            newReview = Review(rating=rating, review=review, course=course, user_id=userinfo['user_id'], teacher_id=teacher_id, anon=isAnon)
            db.session.add(newReview)
            db.session.commit()
            return redirect(f"/teacher/{teacher_id}", 302)
        else:
            r.rating = rating
            r.review = review
            r.course = course
            r.anon = isAnon
            r.date = datetime.utcnow()
            db.session.commit()
            return redirect(f"/teacher/{teacher_id}", 302)
    else :
        flash('Please enter all the required details')
        return redirect(f"/teacher/{teacher_id}", 302)

@app.route("/review/recent")
def recentReviews():
    islog = isLoggedin()
    res = db.session.query(Teacher.name, Teacher.id,func.max(Review.date)).filter(Review.teacher_id == Teacher.id).group_by(Teacher.name, Teacher.id).order_by(func.max(Review.date).desc()).limit(12).all()
    return render_template("recentReviews.html", title="Recently Reviewed", res=res, islog=islog)