from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

db = SQLAlchemy()

class College(db.Model):
    __tablename__ = "colleges"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    location = db.Column(db.String, nullable=True)


class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    department = db.Column(db.String, nullable=False)
    designation = db.Column(db.String, nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey("colleges.id"), nullable=False)
    reviews = db.relationship("Review", backref="Teacher", lazy=True)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)

class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())
    course = db.Column(db.String, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"), nullable=False)
    user_id = db.Column(db.Integer, db. ForeignKey("users.id"), nullable=False)
