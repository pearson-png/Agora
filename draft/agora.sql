'''DO NOT RUN THIS'''
use agora_db;

drop table if exists `comments`;
drop table if exists `posts`;
drop table if exists `ratings`;
drop table if exists `users`;
drop table if exists `professors`;
drop table if exists `courses`;
drop table if exists `departments`;


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

CREATE TABLE `ratings` (
  `rating` int,
  `type` enum('course', 'professor'),
  `user` int,
  `id` int,
  CONSTRAINT PK_rating PRIMARY KEY (`type`, `user`, `id`)
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
  `downvotes` int
);

CREATE TABLE `comments` (
  `commentid` int not null auto_increment PRIMARY KEY,
  `postid` int,
  `time` datetime,
  `user` int,
  `text` varchar(1000),
  `attachments` varchar(100),
  `upvotes` int,
  `downvotes` int
);

CREATE TABLE `users` (
  `uid` int not null auto_increment PRIMARY KEY,
  `username` varchar(30),
  `email` varchar(50),
  `password` varchar(50)
);

ALTER TABLE `comments` ADD FOREIGN KEY (`user`) REFERENCES `users` (`uid`);

ALTER TABLE `posts` ADD FOREIGN KEY (`user`) REFERENCES `users` (`uid`);

ALTER TABLE `comments` ADD FOREIGN KEY (`postid`) REFERENCES `posts` (`postid`);

ALTER TABLE `ratings` ADD FOREIGN KEY (`user`) REFERENCES `users` (`uid`);

ALTER TABLE `professors` ADD FOREIGN KEY (`dept`) REFERENCES `departments` (`abbrv`);

ALTER TABLE `posts` ADD FOREIGN KEY (`prof`) REFERENCES `professors` (`pid`);

ALTER TABLE `posts` ADD FOREIGN KEY (`course`) REFERENCES `courses` (`courseid`);

ALTER TABLE `courses` ADD FOREIGN KEY (`dept`) REFERENCES `departments` (`abbrv`);
