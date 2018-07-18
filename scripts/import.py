import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
	f = open("../books.csv")
	f2 = open("database.sql")
	database_sql = f2.read()

	db.execute(database_sql)
	reader = csv.reader(f)
	next(reader)
	for isbn, title, author, year in reader:
		print(isbn,title,author,year)
		db.execute('''INSERT INTO books (isbn,title,author,year_)
						VALUES (:isbn,:title,:author,:year);''',
						{"isbn":isbn,"title":title,"author":author,"year":year})
	db.commit()
	f.close()

if __name__ == '__main__':
	main()