import os

from flask import Flask, session, render_template, url_for, redirect, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models.modelForms import RegistrationForm


app = Flask(__name__)

app.secret_key = os.urandom(24)

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

@app.route("/")
def index():
    return "Project 1: TODO"

@app.route("/Register", methods=['GET','POST'])
def register():
	form = RegistrationForm(request.form)
	if request.method == 'POST' and form.validate():
		db.execute(SQLInsertIntoUserInfoTableSyntax.format(form.username.data,form.password.data))
		db.commit()
		return redirect(url_for('login'))
	return render_template('register.html',form=form)

@app.route("/login", methods=['GET','POST'])
def login():		
    return render_template('login.html')

if __name__ == "__main__":
	app.run(debug=True)
