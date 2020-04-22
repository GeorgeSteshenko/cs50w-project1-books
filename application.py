import os
import requests
import xmltodict
import json

from flask import Flask, render_template, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html", message="Test")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        userExists = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()

        hashedPassword = generate_password_hash(password, method="sha256", salt_length=10)

        if userExists:
            return render_template("error.html", message=f"User {userExists.username} already exists.")

        if not username:
            return render_template("error.html", message="Please, provide your username.")

        if not password:
            return render_template("error.html", message="Please, provide a password.")

        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": username, "password": hashedPassword})
        user_id = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        
        db.commit()
        
        session["user_id"] = user_id.id
        session["username"] = username

        return render_template("success.html", message="You have successfully registered.")
    else:
        return render_template("register.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        userExists = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()

        if not username:
            return render_template("error.html", message="Please, provide your username.")

        if not password:
            return render_template("error.html", message="Please, provide a password.")

        if not userExists or not check_password_hash(userExists.password, password):            
            return render_template("error.html", message="User name or password is wrong.")

        session["user_id"] = userExists.id
        session["username"] = username
        
        return render_template("index.html")

    else:

        return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return render_template("index.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("index.html")

    else:
        searchQuery = request.form.get("book")
        books = db.execute("SELECT * FROM books WHERE \
                        isbn LIKE :searchQuery OR \
                        LOWER(title) LIKE :searchQuery OR \
                        lOWER(author) LIKE :searchQuery OR \
                        year LIKE :searchQuery", {"searchQuery": "%" + searchQuery.lower() + "%"})
                        # SQL LOWER() and searchQuery.lower() apllied to emulate case insensitive search
                        # so inserted query (in upper/lowercase or capitalized) won't affect the search results

        if not searchQuery:
            return render_template("error.html", message="Please, provide an ISBN number, title or author's name.")
            
        if books.rowcount == 0:
            return render_template("error.html", message="There is no such book.")

        booksList = books.fetchall()

        return render_template("index.html", booksList=booksList)

@app.route("/book/<isbn>", methods=["GET", "POST"])
def book(isbn):
    reviews = db.execute("SELECT * FROM reviews \
                              JOIN users ON users.id = reviews.user_id WHERE book_id = :book", {
                                  "book": isbn
                              }).fetchall()

    # Call for GoodReeds API endpoint to get all info about the book
    goodReadsKey = os.getenv("KEY")
    goodReadsBookXMLInfo = requests.get(f"https://www.goodreads.com/book/isbn/{isbn}", params={"key": goodReadsKey}).text
    goodReadsResponse = xmltodict.parse(goodReadsBookXMLInfo)
    goodReadsResponse = goodReadsResponse["GoodreadsResponse"]["book"]
    # Extract needed values into separate dict
    bookInfo = {
        "url": goodReadsResponse["url"],
        "image_url": goodReadsResponse["image_url"],
        "description": goodReadsResponse["description"]
    }

    if request.method == "POST":
        currentUser = int(session["user_id"])
        rating = int(request.form.get("rating"))
        comment = request.form.get("comment")
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        reviewExists = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id", {"user_id": str(currentUser), "book_id": isbn}).fetchone()

        if reviewExists:
            return render_template("book.html", 
                                    book=book,
                                    bookInfo=bookInfo,
                                    reviews=reviews,
                                    alert_type="alert-warning", 
                                    message="You have already reviewed this book.")

        db.execute("INSERT INTO reviews (user_id, book_id, comment, rating) VALUES \
                    (:user_id, :book_id, :comment, :rating)", {
                        "user_id": currentUser,
                        "book_id": isbn,
                        "comment": comment,
                        "rating": rating
                    })
        db.commit()

        return render_template("book.html", 
                                isbn=isbn, 
                                book=book,
                                bookInfo=bookInfo,
                                reviews=reviews,
                                alert_type="alert-success", 
                                message="You review has been submitted.")
        
    else:

        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

        if book is None:
            return render_template("error.html", message="There is no such book.")
        
        return render_template("book.html", 
                                book=book,
                                bookInfo=bookInfo,
                                reviews=reviews)

@app.route("/api/book/<isbn>", methods=["GET"])
def book_api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn =:isbn", {"isbn": isbn}).fetchone()
    goodReadsKey = os.getenv("KEY")

    if book is None:
        return jsonify({"error": "Invalid ISBN number"}), 404

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": goodReadsKey, "isbns": book.isbn })
    res = res.json()["books"][0]
    # print(res)

    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": int(book.year),
        "isbn": book.isbn,
        "review_count": int(res["reviews_count"]),
        "average_score": float(res["average_rating"])
    })
    

@app.route("/api/book/gr-info/<isbn>", methods=["GET"])
def book_api_grinfo(isbn):
    goodReadsKey = os.getenv("KEY")
    goodReadsBookXMLInfo = requests.get(f"https://www.goodreads.com/book/isbn/{isbn}", params={"key": goodReadsKey}).text
    res = xmltodict.parse(goodReadsBookXMLInfo)
    res = res["GoodreadsResponse"]["book"]

    # return jsonify(res)

    return jsonify({
        "title": res["title"],
        "author": res["authors"]["author"]["name"],
        "url": res["url"],
        "image_url": res["image_url"],
        "description": res["description"]
    })