import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
	f = open('database.sql','r')
	sql = f.read()
	db.execute(sql)
	db.commit()
	f.close()


if __name__ == '__main__':
	main()