use agora_db;

insert into departments(abbrv, `name`) values ('CS', 'Computer Science');
insert into departments(abbrv, `name`) values ('MATH', 'Mathematics');

insert into courses(dept, title, code, courseid) values ('CS', 'Databases with Web Interfaces', 'CS 304', 1);
insert into courses(dept, title, code, courseid) values ('CS', 'Machine Learning', 'CS 305', 2);
insert into courses(dept, title, code, courseid) values ('CS', 'Data Structures', 'CS 230', 3);
insert into courses(dept, title, code, courseid) values ('CS', 'Theory of Computation', 'CS 235', 4);
insert into courses(dept, title, code, courseid) values ('MATH', 'Linear Algebra', 'MATH 206', 5);
insert into courses(dept, title, code, courseid) values ('MATH', 'Combinatorics and Graph Theory', 'MATH 225', 7);

insert into professors(pid, dept, `name`) values (1, 'CS', 'Scott Anderson');
insert into professors(pid, dept, `name`) values (2, 'CS', 'Brian Tjaden');
insert into professors(pid, dept, `name`) values (3, 'CS', 'Takis Metaxas');
insert into professors(pid, dept, `name`) values (4, 'MATH', 'Joe Lauer');
insert into professors(pid, dept, `name`) values (5, 'MATH', 'Ann Trenk');

insert into prof_ratings(rating, user,pid) values (5,1,1);
--insert into prof_ratings(rating, user,pid) values (4,1,2); --can't insert
insert into prof_ratings(rating, user,pid) values (4,2,1);

insert into course_ratings(rating, user,courseid) values (5,1,1);
--insert into course_ratings(rating, user,courseid) values (4,2,1);