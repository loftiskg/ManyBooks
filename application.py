import os
import sys
import json
import requests
from flask import Flask, session, render_template,request,url_for, redirect, jsonify
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
#app.secret_key = Flask.secret_key

# Set up database
engine = create_engine(os.getenv('DATABASE_URL'))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    if session.get('username',None) == None:
        return render_template('index.html')
    else:
        return redirect(url_for('search'))
        #return render_template('search.html')

@app.route("/search")
def search():
    return render_template('search.html')
@app.route("/results",methods=["POST"])
def result():
    search_type = request.form.get('search-type')
    search_input = request.form.get('search')

    books = db.execute(f"SELECT * FROM books WHERE LOWER({search_type}) LIKE LOWER(:input)",
                             {'column':search_type,'input':'%'+search_input+'%'}).fetchall()
    return render_template('results.html',books=books)

@app.route('/book/<int:id>')
def book(id):
    result = db.execute(f"SELECT * from books WHERE id=:id",
        {'id':id})
    book = result.fetchone()
    user_review_exists = reviewExists(session['user_id'],id)
    reviews = getReviews(id)
    goodreadsData = getGoodreadsRating(book['isbn'])
    if goodreadsData is None:
        goodreadsData = {'average_rating':'Not found','num_ratings':'Not found','work_ratings_count':'Not found'}
    return render_template('book.html',book=book,
                                       reviews=reviews, 
                                       user_review_exists=user_review_exists,
                                       rating=goodreadsData['average_rating'],
                                       num_ratings=goodreadsData['work_ratings_count'])

def getReviews(book_id):
    reviews = db.execute("SELECT * FROM review JOIN users ON (review.user_id=users.id) WHERE book_id = :book_id",
        {'book_id':book_id}).fetchall()
    return reviews

@app.route("/login")
def login():
	return render_template("login.html")
@app.route("/logout")
def logout():
    session['username'] = None
    return redirect(url_for('index'))

@app.route('/api/<string:isbn>')
def getBook(isbn):
    data = db.execute("SELECT title,author,year_,isbn FROM books WHERE isbn = :isbn",
                            {"isbn":isbn}).fetchone()
    if data is None:
        data = {'error':'invalid isbn'}
        return jsonify(data), 404
    data = {'title':data[0],'author':data[1],'year_published':data[2],'isbn':data[3]}
    return jsonify(data)

@app.route("/addReview/<int:id>", methods=["POST"])
def addReview(id):
    review = request.form.get("review")
    rating = request.form.get('rating')

    db.execute("INSERT INTO review(book_id,user_id,rating,comment_) VALUES (:book_id,:user_id,:rating,:comment)",
        {'book_id':id,'user_id':session['user_id'],'rating':rating,'comment':review})
    db.commit()
    return redirect(url_for('book',id=id))

def reviewExists(user_id,book_id):
    row = db.execute("SELECT * FROM review WHERE user_id=:user_id AND book_id=:book_id",
        {'user_id':user_id,'book_id':book_id}).fetchone()
    if row:
        return True
    return False

@app.route("/verify", methods=["POST"])
def verify():
    username = request.form.get("username")
    password = request.form.get("password")
    result = db.execute("SELECT id,pass FROM users WHERE username = :username", {"username":username})
    credentials = result.fetchone()
    if result.rowcount == 0 or credentials["pass"] != password:
        result.close()
        return render_template("login.html",invalid=True);
    result.close()
    session['username'] = username
    session['user_id'] =  credentials["id"]
    return redirect(url_for('index'))

@app.route("/register")
def register():
	return render_template("register.html")

@app.route("/adduser",methods=['POST'])
def adduser():
    username = request.form.get("username")
    password = request.form.get("password")
    conf_pass = request.form.get("confirm-password")
    name = request.form.get("name")
    invalid = []
    
    if(password != conf_pass):
        invalid.append("Passwords do not match.")

    if db.execute("SELECT * from users where username = :username ", {'username':username}).rowcount > 0:
        invalid.append("Username already taken. Try another name.")

    if invalid:
        return render_template('register.html',invalid=invalid)

    db.execute("INSERT INTO users(username,pass,name) VALUES (:username,:password, :name)",
        {'username':username,'password':password,'name':name})
    db.commit()
    return redirect(url_for('login'))


def getGoodreadsRating(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", 
                       params={"key": GOODREADS_API_KEY, "isbns": isbn})
    if res.status_code != 200:
        return None
    return res.json()['books'][0]

GOODREADS_API_KEY = sys.argv[1]
app.run('0.0.0.0',port=5000)

