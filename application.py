import os

from flask import Flask, session, render_template,request,url_for, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Goodreads API key
#KEY = AWLYBKmWHJB0UpYwRoHEw

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
#app.secret_key = Flask.secret_key

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    if session['username'] == None:
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

    result = db.execute(f"SELECT * FROM books WHERE LOWER({search_type}) LIKE LOWER(:input)",
                             {'column':search_type,'input':'%'+search_input+'%'})
    books = []
    for row in result:
        books.append(row)

    result.close()
    
    return render_template('results.html',books=books)

@app.route("/login")
def login():
	return render_template("login.html")
@app.route("/logout")
def logout():
    session['username'] = None
    return redirect(url_for('index'))

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

