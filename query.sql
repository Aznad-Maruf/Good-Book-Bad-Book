CREATE TABLE authors(
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL
);

CREATE TABLE books(
    id SERIAL PRIMARY KEY,
    isbn VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    year INTEGER NOT NULL,
    author_id INTEGER REFERENCES authors
);

CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    password VARCHAR NOT NULL
);

CREATE TABLE reviews(
    id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES books,
    user_id INTEGER REFERENCES users,
    rating INTEGER NOT NULL,
    review VARCHAR NOT NULL
);

CREATE VIEW books_view AS 
    SELECT b.id as id, b.isbn as isbn, b.title as title, a.name AS author, b.year as year FROM authors AS a LEFT JOIN books AS b ON a.id = b.author_id;

CREATE VIEW reviews_view AS
SELECT r.book_id as book_id, u.name as user_name, r.review as review, r.rating as rating FROM reviews as r LEFT JOIN users as u ON r.user_id = u.id;

SELECT b.title, b.author, b.year, b.isbn as isbn, COUNT(r.id) AS review_count, AVG(r.rating) AS average_rating FROM books_view AS b LEFT JOIN reviews AS r ON b.id = r.book_id GROUP BY r.book_id;

ALTER TABLE reviews ADD COLUMN author_id INTEGER REFERENCES authors;

SELECT COUNT(id), ROUND(AVG(rating), 2) as rat FROM reviews WHERE isbn = 0553803700;