# import os

# from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

# class Users(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String, nullable=False)
#     password = db.Column(db.String, nullable=False)

# class Books(db.Model):
#     __tablename__ = "books"
#     id = db.Column(db.Integer, primary_key=True)
#     isbn = db.Column(db.String, nullable=False)
#     title = db.Column(db.String, nullable=False)
#     author = db.Column(db.String, nullable=False)
#     year = db.Column(db.String, nullable=False)

class Reviews(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.String, nullable=False)
    comment = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

# class Testtable(db.Model):
#     __tablename__ = "testtable"
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.DateTime(timezone=True), server_default=func.now())
#     testcol1 = db.Column(db.String, nullable=False)
#     testcol2 = db.Column(db.String, nullable=False)
#     testcol3 = db.Column(db.String, nullable=False)