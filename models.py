from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

db = SQLAlchemy()

class College(db.Model):
    __tablename__ = "colleges"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    location = db.Column(db.String, nullable=False)

class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    department = db.Column(db.String, nullable=False)
    designation = db.Column(db.String, nullable=True)
    college_id = db.Column(db.Integer, db.ForeignKey("colleges.id"), nullable=False)
    reviews = db.relationship("Review", backref="Teacher", lazy=True)
    college = db.relationship("College", backref="Teacher", lazy=True)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    picture = db.Column(db.String, nullable=True)

class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    course = db.Column(db.String, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    anon = db.Column(db.Boolean, default=False)
    

