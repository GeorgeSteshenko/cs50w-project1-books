# cs50w Project 1 Books

Web Programming with Python and JavaScript
https://courses.edx.org/courses/course-v1:HarvardX+CS50W+Web/course/

# Live version

https://bookreviews-flask.herokuapp.com/

# App features

Build based on Python Flask, Jinja2 template engine and PostgreSQL database. Bootstrap is used as a Front-end framework.

- Register a new user
- Login
- Logout 
- Import books info from `.csv` file
- Search book based on it's ISBN number, title, author name or publish year
- Book page with it's info
- Leave a review feature (one per user)
- Goodreads reviews data (displayed on the book page)
- API Endpoint access (https://www.goodreads.com/api/index#book.review_counts JSON response from Goodreads API Endpoint), reformated e.g: http://bookreviews-flask.herokuapp.com/api/book/0553803700 where `0553803700` is an ISBN number of the book

## Extra features
- Password hashing
- Additional API Endpoint access with detailed info about the book taken from Goodreads API `.xml` endpoint (https://www.goodreads.com/api/index#book.show), reformated and converted into JSON e.g: http://bookreviews-flask.herokuapp.com/api/book/gr-info/0553803700 where `0553803700` is an ISBN number of the book
- Book description, image and link to Goodreads book page added to the book page

# Local install

Create a virual environment

`python3 -m venv .venv`

Install dependencies

`pip install -r requirements.txt`