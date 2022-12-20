use agora_db;

drop table if exists `post_votes`;
drop table if exists `comment_votes`;
drop table if exists `documents`;
drop table if exists `comments`;
drop table if exists `posts`;
drop table if exists `prof_ratings`;
drop table if exists `course_ratings`;
drop table if exists `professors`;
drop table if exists `courses`;
drop table if exists `departments`;
drop table if exists `users`;



CREATE TABLE `courses` (
  `dept` varchar(5),
  `title` varchar(50),
  `code` varchar(8),
  `courseid` int PRIMARY KEY
);

CREATE TABLE `professors` (
  `pid` int PRIMARY KEY,
  `dept` varchar(5),
  `name` varchar(30)
);

CREATE TABLE `departments` (
  `abbrv` varchar(5) PRIMARY KEY,
  `name` varchar(30)
);

CREATE TABLE `prof_ratings` (
  `rating` int,
  `user` int,
  `pid` int,
  CONSTRAINT PK_prof_rating PRIMARY KEY (`user`, `pid`)
);

CREATE TABLE `course_ratings` (
  `rating` int,
  `user` int,
  `courseid` int,
  CONSTRAINT PK_course_rating PRIMARY KEY (`user`, `courseid`)
);

CREATE TABLE `posts` (
  `postid` int not null auto_increment PRIMARY KEY,
  `time` datetime,
  `user` int,
  `course` int,
  `prof` int,
  `prof_rating` int,
  `course_rating` int,
  `text` varchar(2500),
  `attachments` varchar(100),
  `upvotes` int,
  `downvotes` int,
  `username` varchar(30)
);

CREATE TABLE `comments` (
  `commentid` int not null auto_increment PRIMARY KEY,
  `postid` int,
  `time` datetime,
  `user` int,
  `text` varchar(1000),
  `attachments` varchar(100),
  `upvotes` int,
  `downvotes` int,
  `username` varchar(30)
);

CREATE TABLE `post_votes` (
  `postid` int,
  `user` int,
  `kind` enum('up', 'down'),
  CONSTRAINT PK_post_votes PRIMARY KEY (`postid`, `user`)
);

CREATE TABLE  `comment_votes` (
  `commentid` int,
  `user` int,
  `kind` enum('up', 'down'),
  CONSTRAINT PK_post_votes PRIMARY KEY (`commentid`, `user`)
);

CREATE TABLE `users` (
  `uid` int not null auto_increment PRIMARY KEY,
  `username` varchar(30),
  `email` varchar(50)
);

CREATE TABLE `documents` (
  `docid` int auto_increment PRIMARY KEY,
  `filepath` varchar(100) not null,
  `uid` int
);

ALTER TABLE `comments` ADD FOREIGN KEY (`user`) REFERENCES `users` (`uid`);

ALTER TABLE `posts` ADD FOREIGN KEY (`user`) REFERENCES `users` (`uid`);

ALTER TABLE `comments` ADD FOREIGN KEY (`postid`) REFERENCES `posts` (`postid`);

ALTER TABLE `prof_ratings` ADD FOREIGN KEY (`user`) REFERENCES `users` (`uid`);

ALTER TABLE `prof_ratings` ADD FOREIGN KEY (`pid`) REFERENCES `professors` (`pid`);

ALTER TABLE `course_ratings` ADD FOREIGN KEY (`user`) REFERENCES `users` (`uid`);

ALTER TABLE `course_ratings` ADD FOREIGN KEY (`courseid`) REFERENCES `courses` (`courseid`);

ALTER TABLE `post_votes` ADD FOREIGN KEY (`user`) REFERENCES `users` (`uid`);

ALTER TABLE `post_votes` ADD FOREIGN KEY (`postid`) REFERENCES `posts` (`postid`);

ALTER TABLE `comment_votes` ADD FOREIGN KEY (`user`) REFERENCES `users` (`uid`);

ALTER TABLE `comment_votes` ADD FOREIGN KEY (`commentid`) REFERENCES `comments` (`commentid`);

ALTER TABLE `professors` ADD FOREIGN KEY (`dept`) REFERENCES `departments` (`abbrv`);

ALTER TABLE `posts` ADD FOREIGN KEY (`prof`) REFERENCES `professors` (`pid`);

ALTER TABLE `posts` ADD FOREIGN KEY (`course`) REFERENCES `courses` (`courseid`);

ALTER TABLE `courses` ADD FOREIGN KEY (`dept`) REFERENCES `departments` (`abbrv`);

ALTER TABLE `documents` ADD FOREIGN KEY (`uid`) REFERENCES `users` (`uid`);