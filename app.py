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
    return redirect('/dashboard')



@app.route("/")
def index():
    return render_template("index.html", title="Rate Your Professor")

@app.route("/login", methods=["GET","POST"])
def login():
    if constants.PROFILE_KEY in session:
        return redirect(url_for('dashboard'), 302)
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)

@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('index', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

@app.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('dashboard.html', title="Dashboard",
                           userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))

@app.route("/result", methods=["POST"])
def getResult():
    name = request.form.get("name").strip()
    college = request.form.get("college").strip()
    result = db.session.query(Teacher, College).filter(and_(Teacher.college_id == College.id, Teacher.name.ilike(f"%{name}%"), College.name.ilike(f"%{college}%"))).all()
    return render_template("result.html", title="Results", result=result)

@app.route("/teacher/<int:teacher_id>")
@requires_auth
def review(teacher_id):
    res = Teacher.query.get(teacher_id)
    return render_template("review.html", title=f"Review {res.name}", res=res, userinfo=session[constants.PROFILE_KEY], userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD]))

@app.route("/teacher/<int:teacher_id>/review")
@requires_auth
def postReview(teacher_id):
    pass