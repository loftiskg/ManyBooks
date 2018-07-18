CREATE TABLE users (
	id          SERIAL     PRIMARY KEY,
	username    VARCHAR    NOT NULL UNIQUE,
	pass        VARCHAR    NOT NULL,
	name        VARCHAR    NOT NULL
);
CREATE TABLE books (
	id         SERIAL      PRIMARY KEY,
	isbn       VARCHAR     UNIQUE,
	title      VARCHAR,
	author     VARCHAR,
	year_      INTEGER
);

DROP TYPE IF EXISTS rating_options;
CREATE TYPE rating_options AS ENUM('1','2','3','4','5');

CREATE TABLE review (
	id         SERIAL      PRIMARY KEY,
	book_id    INTEGER     REFERENCES books(id),
	user_id    INTEGER     REFERENCES users(id),
	rating     rating_options,
	comment_   VARCHAR
);