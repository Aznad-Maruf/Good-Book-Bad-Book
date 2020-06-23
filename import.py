import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
engine = create_engine(os.getenv('DATABASE_URL'))
db = scoped_session(sessionmaker(bind=engine))

def main():
    with open('books.csv') as f:
        reader = csv.reader(f)
        next(reader)
        for isbn, title, author, year in reader:
            if db.execute('SELECT * FROM authors where name=:name', {'name':author}).rowcount == 0:
                db.execute('INSERT INTO authors (name) VALUES (:name)', {'name':author})
        db.commit()

    with open('books.csv') as f:
        reader = csv.reader(f)
        next(reader)
        for isbn, title, author, year in reader:
            if db.execute('SELECT * FROM books where isbn=:isbn', {'isbn':isbn}).rowcount == 0:
                author_id = db.execute('SELECT id FROM authors WHERE name=:name', {'name':author}).first()
                author_id = author_id.id
                try:
                    author_id = int(author_id)
                except:
                    print(f"{author} has no entry in authors table")
                year = int(year)
                db.execute('INSERT INTO books (isbn, title, author_id, year) VALUES (:isbn, :title, :author_id, :year)', {'isbn':isbn, 'title':title, 'author_id':author_id, 'year':year})
        db.commit()

if __name__ == "__main__":
    main()