
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS student;
CREATE TABLE student (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                      name VARCHAR (32));

DROP TABLE IF EXISTS category;
CREATE TABLE category (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                      name VARCHAR (64));

DROP TABLE IF EXISTS course;
CREATE TABLE course (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                      name VARCHAR (512),
                      category_id INTEGER NOT NULL,
                      FOREIGN KEY (category_id) REFERENCES category (id));

DROP TABLE IF EXISTS course_student;
CREATE TABLE course_student (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                      course_id INTEGER NOT NULL,
                      student_id INTEGER NOT NULL,
                      FOREIGN KEY (course_id) REFERENCES course (id),
                      FOREIGN KEY (student_id) REFERENCES student (id));
COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
