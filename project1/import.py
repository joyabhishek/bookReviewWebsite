import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os

#Reading csv in a pandas dataframe
df = pd.read_csv("C:/Users/Abhisheksen/Documents/Projects/bookReviewWebsite/project1/books.csv")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"),pool_pre_ping=True)
db = scoped_session(sessionmaker(bind=engine))

#Insert into stateagegroupnumber string
SQLInsertIntobookinfoTableSyntax = "INSERT INTO bookinfo (isbn , title , author , year) VALUES (\'{0}\',\'{1}\',\'{2}\',\'{3}\');"

#inserting one by one row to database
for i in range(len(df)) :
	print(f"Going to enter ISBN:{df.loc[i, 'isbn']} TITLE:{df.loc[i, 'title']} AUTHOR:{df.loc[i, 'author']} YEAR:{df.loc[i, 'year']}")
	db.execute(SQLInsertIntobookinfoTableSyntax.format(df.loc[i, "isbn"],df.loc[i, "title"].replace("'","''"),df.loc[i, "author"].replace("'","''"),df.loc[i, "year"]))
	db.commit()