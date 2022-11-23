use agora_db;

insert into users(`uid`, username, email, `password`) values(null, 'lazy_panda', 'na1', 'password1');

insert into posts(postid,`time`, user, course, prof, prof_rating, course_rating, `text`, attachments, upvotes, downvotes) values 
(null, '2022-07-24', 1, 1, 1, 5, 5, 'This class is awesome', '', 5, 1);
insert into posts(postid, `time`, user, course, prof, prof_rating, course_rating, `text`, attachments, upvotes, downvotes) values 
(null, '2022-07-27', 1, 1, 1, 4, 3, 'Idk how I feel', '', 0, 10);

