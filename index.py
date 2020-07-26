import os

from flask import Flask, session, render_template, url_for, redirect, request, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models.modelForms import RegistrationForm, LoginForm
from functools import wraps
import requests
import locale
locale.setlocale(locale.LC_NUMERIC,'')

app = Flask(__name__)

app.secret_key = os.urandom(24)
print(app.secret_key)
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
'''


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] =" filesystem"
Session(app)

'''
# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

SQLInsertIntoUserInfoTableSyntax = "INSERT INTO user_info (name , password) VALUES (\'{0}\',\'{1}\');"
SQLSelectIntoUserInfoTableSyntax = "SELECT * FROM user_info WHERE name = \'{0}\';"
SQLSelectIntobookInfoTableSyntax = "SELECT * FROM bookInfo;"

def login_required(func):
	@wraps(func)
	def wrapper(*args,**kwargs):
		if 'userid' in session:
			return func(*args,**kwargs)
		return redirect(url_for('login'))
	return wrapper

@app.route("/user")
@login_required
def user():
	user_id = session['userid']
	usernameQueryRes = db.execute(f"select name from user_info where user_id ={user_id};").fetchone()
	userReviewInfoQueryRes = db.execute(f"select b.isbn, b.title, b.author, b.year, r.review, r.rating from bookinfo b JOIN review_info r ON (b.isbn = r.book_id) where r.user_id = {user_id};").fetchall()
	return render_template('user.html',userReviewInfo=userReviewInfoQueryRes,username=usernameQueryRes)


@app.route("/search",  methods=['POST'])
def search():
	searchText = request.form.get("searchText")
	query = f"SELECT title,isbn FROM bookInfo WHERE LOWER(isbn) LIKE LOWER(\'%{searchText}%\') OR LOWER(title) LIKE LOWER(\'%{searchText}%\') OR LOWER(author) LIKE LOWER(\'%{searchText}%\');"
	booknameListResult = db.execute(query).fetchall()
	booknameList = []
	for bookname in booknameListResult:
		booknameList.append({'title':bookname.title,'isbn':bookname.isbn})
	print(booknameList)
	return jsonify({'response': True, "booknameList": booknameList})

@app.route("/addReview", methods=['POST'])
def addReview():
	reviewText = request.form.get('reviewText')
	rating = request.form.get('rating')
	isbn = request.form.get('isbn')
	user_id = session['userid']

	#getUserIdQuery = db.execute(f'SELECT user_id FROM user_info WHERE name=\'{username}\'').fetchone()
	#print(f'USER ID: {getUserIdQuery.user_id} for USERname:{username}')

	db.execute(f'insert into review_info (book_id, user_id, rating, review)  VALUES (\'{isbn}\',{user_id},{rating},\'{reviewText}\');')
	db.commit()
	return jsonify({'response': True, "username": getUsername(user_id)})

def getUsername(userid):
	userInfoRes = db.execute(f'SELECT * FROM user_info WHERE user_id=\'{userid}\'').fetchone()
	print(userInfoRes)
	return userInfoRes.name

@app.route("/api/<string:isbnNumber>")
def api_bookInfo(isbnNumber):
	bookInfo = getBookInfo(isbnNumber,-1)
	if bookInfo:
		print(bookInfo)
		noOfReviews = len(bookInfo['reviews'])
		bookInfo.pop('reviews')
		bookInfo.pop('noOfRating')
		bookInfo.pop('reviewAllowed')
		bookInfo['review_count'] = noOfReviews
		return jsonify(bookInfo)
	else:
		return jsonify({"error": "Invalid isbn"}), 422

def getBookInfo(isbnNumber,user_id):
    getbookInfoQuery = f'SELECT * FROM bookInfo WHERE isbn=\'{isbnNumber}\';'
    print(getbookInfoQuery)
    bookInfo = {}
    if db.execute(getbookInfoQuery).rowcount == 1:
    	bookQueryRes = db.execute(getbookInfoQuery).fetchone()
    	print(f"Book found:{bookQueryRes}")
    	noOfRating = 0
    	totalRating = 0
    	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "FsIe0iBKBNxR3hWRtRszw", "isbns":{bookQueryRes.isbn} })
    	
    	bookInfo['title'] = bookQueryRes.title
    	bookInfo['author'] = bookQueryRes.author
    	bookInfo['year'] = bookQueryRes.year
    	bookInfo['isbn'] = bookQueryRes.isbn
    	bookInfo['reviewAllowed'] = True
    	bookInfo['reviews'] = []
    	print(f"Good reads book info:{res.json()}")
    	for book in res.json()['books']:
    		noOfRating+=int(book['work_ratings_count'])
    		totalRating+=(float(book['work_ratings_count']) * float(book['average_rating']))
    		print(f"No of ratings:{book['work_ratings_count']} Rating:{book['average_rating']}")
    	gettingReviewInfoFromreview_infoDBquery = f'SELECT * FROM review_info WHERE book_id=\'{isbnNumber}\''
    	reviewInfoDBqueryRes = db.execute(gettingReviewInfoFromreview_infoDBquery).fetchall()
    	for reviewInfo in reviewInfoDBqueryRes:
    		if reviewInfo.user_id == user_id:
    			bookInfo['loggedInUserReview'] = {'username':getUsername(user_id),'rating':reviewInfo.rating,'review':reviewInfo.review}
    			bookInfo['reviewAllowed'] = False
    		else:
    			bookInfo['reviews'].append({'username':getUsername(reviewInfo.user_id),'rating':reviewInfo.rating,'review':reviewInfo.review})
    		noOfRating += 1 
    		totalRating += reviewInfo.rating

    	averageRating = 0
    	if noOfRating > 0:
    		averageRating = totalRating/noOfRating

    	#bookInfo['noOfRating'] = noOfRating
    	bookInfo['noOfRating'] = locale.format("%d", noOfRating, grouping=True)
    	bookInfo['average_score'] = averageRating
    	return bookInfo
    	#return f"<h1>Title:{bookQueryRes.title} Author:{bookQueryRes.author} Year:{bookQueryRes.year}</h1><br>No Of Rating:{noOfRating} Average Rating:{averageRating}"
    else:
    	return None	

@app.route("/book/<string:isbnNumber>")
@login_required
def book(isbnNumber):
    '''
	1. Get all the info from DB
	2. rInfo = Get all the entries for isbn from review_info
	3. gr = Get info about an ISBN no. from goodRead API
	4. rating = ((gr.work_ratings_count * gr.average_rating)  + (loop rInfo.ratings add)) / (gr.work_ratings_count + rInfo.Size)
	5. noOfReviews = (gr.work_ratings_count + rInfo.Size)
	6. Send it to bookInfo.html

	If ISBN not found <SHOW ERROR>
    '''
    user_id = session['userid']
    bookInfo = getBookInfo(isbnNumber,user_id)
    if bookInfo:
    	return render_template('book.html',bookInfo=bookInfo)
    else:
    	return "<H1>Book not found</H1>"

def getBookDetailsBasedOnAuthor(authorName):
	authorsBookDetails = db.execute(f"select * from bookinfo where author=\'{authorName}\' LIMIT 4;").fetchall()
	return authorsBookDetails


@app.route("/")
@login_required
def index():
	yearList = db.execute("SELECT year FROM bookInfo GROUP BY year ORDER BY year DESC;").fetchall()
	indexDataDictionary = {}
	forNumberOfYears=0
	for year in yearList:
		if forNumberOfYears < 2:
			bookInfoForYearList = db.execute(f"SELECT isbn,title,author,year FROM bookInfo WHERE year=\'{year.year}\' LIMIT 4;")
			indexDataDictionary[year.year] = bookInfoForYearList
			forNumberOfYears+=1
		else:
			break
	topAuthorsRes = db.execute("select author from bookinfo group by author order by COUNT(*) DESC LIMIT 3;").fetchall()
	for author in topAuthorsRes:
		indexDataDictionary[author.author] = getBookDetailsBasedOnAuthor(author.author) 
	return render_template('index.html',indexDataDictionary=indexDataDictionary)

def userExistsInDb(username):
	userInfoList =  db.execute("SELECT name, password FROM user_info;").fetchall()
	userAlreadyExists = False
	for userInfo in userInfoList:
		if userInfo.name == username:
			userAlreadyExists = True
			break
	return userAlreadyExists

@app.route("/Register", methods=['GET','POST'])
def register():
	form = RegistrationForm(request.form)
	if request.method == 'POST' and form.validate():
		if not userExistsInDb(form.username.data):
			db.execute(SQLInsertIntoUserInfoTableSyntax.format(form.username.data,form.password.data))
			db.commit()
		else:
			error='User already exists'
			return render_template('register.html',form=form,error=error)		
		return redirect(url_for('login'))
	return render_template('register.html',form=form)

@app.route("/Login", methods=['GET','POST'])
def login():	
	form = LoginForm(request.form)
	if request.method == 'POST' and form.validate():
		if db.execute(SQLSelectIntoUserInfoTableSyntax.format(form.username.data)).rowcount == 0:
			error = f'Username: <b>{form.username.data}</b> does\'nt exist'
			return render_template('login.html',form=form,error=error)
		else:
			userInfo = db.execute(SQLSelectIntoUserInfoTableSyntax.format(form.username.data)).fetchone()
			if userInfo[1] == form.username.data and userInfo[2] == form.password.data:
				flash('Login was successfull')
				session['userid'] = userInfo[0]
				return redirect(url_for('index'))
			else:
				error = 'Username and Password combination did\'nt match'
				return render_template('login.html',form=form,error=error)
	return render_template('login.html',form=form)

@app.route('/logout')
def logout():
	session.pop('userid',None)
	return render_template('login.html',form=LoginForm())

if __name__ == "__main__":
	app.run(debug=True)
