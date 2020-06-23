import os

import requests
from flask import Flask, session, render_template, request, jsonify, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set Set -> postgres://cntdpbogvltstm:207cbd98bb01ef2f1e3a9f54cfaab3439dd2f1d29e73ec675e7800f02f99e0a8@ec2-52-202-146-43.compute-1.amazonaws.com:5432/da8ldhe8qn3kqs")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Global variables
logged_in_user = None

@app.route("/")
def index():
    return render_template('authenticate.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    page_name = request.form.get('page_name')
    return render_template('login_register.html', page_name=page_name)

@app.route('/login', methods=['POST'])
def login():
    name = request.form.get('name_')
    password = request.form.get('password_')
    user = db.execute('SELECT * FROM users WHERE name=:name AND password=:password', {'name':name, 'password':password}).first()
    if user is None:
        return render_template('error.html', message='No user found.\nPlease try again or Register.')
    session['user'] = user
    return render_template('search_result.html', user=user, books="")

@app.route('/logout')
def logout():
    if 'user' not in session:
        return render_template('error.html', message='Log in first')
    session.pop('user', None)
    return render_template('error.html', message='Logged out seccessfully!')

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name_')
    password = request.form.get('password_')
    if db.execute("SELECT * FROM users where name = :name", {'name':name}).rowcount != 0:
        return render_template('error.html', message=f'Name {name} is already taken!\nUse a different name', title='error')
    if password is None or password == "":
        return render_template('error.html', message='Provide a password')

    db.execute('INSERT INTO users (name, password) VALUES(:name, :password)', {'name':name, 'password':password})
    db.commit()

    return render_template('error.html', message=f"Congratulations {name}\nYou are now a registered member of Good Book Bad Book!", title='successful')

@app.route('/search', methods=['POST', 'GET'])
def search():
    if 'user' not in session:
        return render_template('error.html', message='Log in first')
    if request.method == 'POST':
        search_string = request.form.get('search_string')
        search_string = search_string.lower()
        search_string = "%" + search_string + "%"
        searched_books = db.execute("SELECT * FROM books WHERE LOWER(isbn) LIKE (:search_string) OR LOWER(title) LIKE(:search_string)", {'search_string':search_string}).fetchall()

        searched_books = db.execute("SELECT b.isbn as isbn, b.title as title, a.name AS author, b.year as year FROM authors AS a LEFT JOIN books AS b ON a.id = b.author_id WHERE LOWER(isbn) LIKE (:search_string) OR LOWER(title) LIKE(:search_string) OR LOWER(a.name) LIKE(:search_string)", {'search_string':search_string}).fetchall()
    else:
        searched_books=""
    return render_template('search_result.html', books=searched_books)



@app.route('/book/<string:isbn>', methods=['POST', 'GET'])
def book_details(isbn):
    if 'user' not in session:
        return render_template('error.html', message='Log in first')
    
    if request.method == 'POST':
        isbn = request.form.get('isbn')
    book = db.execute('SELECT * FROM books_view WHERE isbn = :isbn', {'isbn':isbn}).fetchone()
    if book is None:
        # abort(404)
        # return jsonify({"error": "Invalid"}), 404
        return render_template('error.html', message="Book doesn't exist."), 404
    user = session['user']
    if request.method == 'POST':

        if db.execute('SELECT * FROM reviews WHERE user_id=:user_id AND book_id=:book_id', {'user_id':user.id, 'book_id':book.id}).rowcount > 0:
            return render_template('error.html', message='You have already given a review.')

        review = request.form.get('review')
        rating = request.form.get('rate')
        db.execute('INSERT INTO reviews (book_id, user_id, review, rating) VALUES(:book_id, :user_id, :review, :rate)', {'book_id':book.id, 'user_id':user.id, 'review':review, 'rate':rating})
        db.commit()
    
    reviews = db.execute('SELECT * FROM reviews_view WHERE book_id = :book_id', {'book_id':book.id}).fetchall()


    KEY = "wJWW3FonxOEDCtGiXXgjTg"

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": str(isbn)})

    ratings_count, average_rating = 0, 0
    if res.status_code == 200:
        res = res.json()
        ratings_count, average_rating = res['books'][0]['work_ratings_count'], res['books'][0]['average_rating']

    return render_template('book_details.html', book=book, reviews = reviews, user=user, ratings_count=ratings_count, average_rating=average_rating)

@app.route('/api/<string:isbn>')
def give_api(isbn, methods=['GET']):
    book = db.execute('SELECT * FROM books_view WHERE isbn = :isbn', {'isbn':isbn}).fetchone()
    if book is None:
        abort(404)
    rating = db.execute("SELECT COUNT(id) as review_count, ROUND(AVG(rating), 2) as average_score FROM reviews WHERE book_id = :book_id;", {'book_id':book.id}).fetchone()
    average_score = str(rating.average_score)
    dic = {
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": rating.review_count,
        "average_score": average_score
    }
    return jsonify(dic)
    
    