import os
from flask import Flask, request, jsonify, render_template
from sqlalchemy import *
import psycopg2
from models import *
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

@app.route("/")
def index():
    return render_template("index.html", title="Rate Your Professor")

@app.route("/result", methods=["POST"])
def getResult():
    name = request.form.get("name")
    college = request.form.get("college")
    result = db.session.query(Teacher, College).filter(and_(Teacher.college_id == College.id, Teacher.name.ilike(f"%{name}%"), College.name.ilike(f"%{college}%"))).all()
    return render_template("result.html", title="Results", result=result)