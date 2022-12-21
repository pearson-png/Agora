from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
import cs304dbi as dbi
import helper

def get_recent_post_allinfo(conn):
    '''Returns postid, username, text, timestamp, 
        course code, course title, course rating
        prof name, prof rating, from recent posts'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT X.postid, X.username, X.text, X.time, Y.code,
        Y.title, X.course_rating, Z.name, X.prof_rating,
        X.upvotes, X.downvotes
        from ( 
            (SELECT postid, username, text, time, upvotes, downvotes,
                course, prof, prof_rating,course_rating FROM posts) X
            LEFT OUTER JOIN
            (SELECT code, title, courseid FROM courses) Y 
            on X.course=Y.courseid
            LEFT OUTER JOIN
            (SELECT name, pid FROM professors) Z
            on X.prof=Z.pid
            )
        order by time desc limit 50''')
    return curs.fetchall()

def get_dept_post_allinfo(conn, department):
    '''Returns postid, username, text, timestamp, 
        course code, course title, course rating
        prof name, prof rating, from matching dept posts'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT X.postid, X.username, X.text, X.time, Y.code,
            Y.title, X.course_rating, Z.name, X.prof_rating,
            X.upvotes, X.downvotes
        from ( 
            (SELECT postid, username, text, time, upvotes, downvotes,
                course, prof, prof_rating,course_rating FROM posts) X
            LEFT OUTER JOIN
            (SELECT code, title, courseid, dept FROM courses) Y 
            on X.course=Y.courseid
            LEFT OUTER JOIN
            (SELECT name, pid, dept FROM professors) Z
            on X.prof=Z.pid
            )
        where Y.dept = %s or Z.dept = %s
        order by time desc 
        limit 50''', [department, department])
    return curs.fetchall()

def get_prof_post_allinfo(conn, professor):
    '''Returns postid, username, text, timestamp, 
        course code, course title, course rating
        prof name, prof rating, from matching prof posts'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT X.postid, X.username, X.text, X.time, Y.code,
        Y.title, X.course_rating, Z.name, X.prof_rating,
        X.upvotes, X.downvotes
        from ( 
            (SELECT postid, username, text, time, upvotes, downvotes,
                course, prof, prof_rating,course_rating FROM posts) X
            LEFT OUTER JOIN
            (SELECT code, title, courseid FROM courses) Y 
            on X.course=Y.courseid
            LEFT OUTER JOIN
            (SELECT name, pid FROM professors) Z
            on X.prof=Z.pid
            )
        where Z.pid = %s
        order by time desc 
        limit 50''', [professor])
    return curs.fetchall()

def get_course_post_allinfo(conn, course):
    '''Returns postid, username, text, timestamp, 
        course code, course title, course rating
        prof name, prof rating, from matching prof posts'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT X.postid, X.username, X.text, X.time, Y.code,
        Y.title, X.course_rating, Z.name, X.prof_rating,
        X.upvotes, X.downvotes
        from ( 
            (SELECT postid, username, text, time, upvotes, downvotes,
                course, prof, prof_rating,course_rating FROM posts) X
            LEFT OUTER JOIN
            (SELECT code, title, courseid FROM courses) Y 
            on X.course=Y.courseid
            LEFT OUTER JOIN
            (SELECT name, pid FROM professors) Z
            on X.prof=Z.pid
            )
        where Y.courseid = %s
        order by time desc 
        limit 50''', [course])
    return curs.fetchall()

def get_section_post_allinfo(conn, course, professor):
    '''Returns postid, username, text, timestamp, 
        course code, course title, course rating
        prof name, prof rating, from matching prof and course posts'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT X.postid, X.username, X.text, X.time, Y.code,
        Y.title, X.course_rating, Z.name, X.prof_rating,
        X.upvotes, X.downvotes
        from ( 
            (SELECT postid, username, text, time, upvotes, downvotes,
                course, prof, prof_rating,course_rating FROM posts) X
            LEFT OUTER JOIN
            (SELECT code, title, courseid FROM courses) Y 
            on X.course=Y.courseid
            LEFT OUTER JOIN
            (SELECT name, pid FROM professors) Z
            on X.prof=Z.pid
            )
        where Y.courseid = %s and Z.pid = %s
        order by time desc 
        limit 50''', [course, professor])
    return curs.fetchall()

def find_depts(conn):
    '''Returns a list of dictionaries of all departments'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select * from departments''')
    return curs.fetchall()

def find_profs_indepartment(conn, department):
    '''Returns a list of dictionaries of professors
    in a given department'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select pid, name from professors where dept = %s''',
        [department])
    return curs.fetchall()

def find_courses_indepartment(conn, department):
    '''Returns a list of dictionaries of courses in
    a given department'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select courseid, title, code from courses where
        dept = %s''', [department])
    return curs.fetchall()

def find_profs(conn):
    '''Returns a list of dictionaries of all professors'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select pid, name from professors''')
    return curs.fetchall()

def find_courses(conn):
    '''Returns a list of dictionaries of all courses'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select courseid, title, code from courses''')
    return curs.fetchall()


def get_post_info(conn,postid):
    '''Returns username, text and timestamp, upvotes, downvotes, and 
    attachments from a specific post'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select username, text, time, upvotes, downvotes, attachments
    from posts
    where postid = %s''', [postid])
    return curs.fetchone()

def get_course_info(conn, postid):
    '''Returns course name, code and rating from a specific post '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select courses.title, courses.code, posts.course_rating
    from posts inner join courses
    on (posts.course = courses.courseID)
    where postid = %s''',[postid]) 
    return curs.fetchone()

def get_prof_info(conn,postid):
    '''Returns prof name and rating a specific post '''
    curs = dbi.dict_cursor(conn)
    curs.execute(''' 
    select name, posts.prof_rating
    from posts inner join professors
    on (posts.prof = professors.pid)
    where postid = %s''', [postid]) 
    return curs.fetchone()

def find_prof_name(conn,pid):
    '''Returns name of professor with given pid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select name 
                    from professors 
                    where pid=%s''', [pid])
    #returns one matching name
    return curs.fetchone()

def search_course(conn, dept, query):
    '''find courses that is similar to the search query'''
    curs = dbi.dict_cursor(conn)
    query_string = '%' + query.lower() + '%' # create string for use in 
    #wildcard
    if dept =="0":
        curs.execute("""select dept, courseid, title, code
                        from courses 
                        where lower(title) like %s""", [query_string]) 
    else:
        curs.execute("""select dept, courseid, title, code
                        from courses 
                        where lower(title) like %s and dept=%s""", 
                        [query_string, dept]) 
    return curs.fetchall()

def search_prof(conn, dept, query):
    '''find professors that is similar to the search query'''
    curs = dbi.dict_cursor(conn)
    query_string = '%' + query.lower() + '%' # create string for use in 
    #wildcard
    if dept =="0":
        curs.execute("""select pid, dept, name
                        from professors 
                        where lower(name) like %s""", [query_string]) 
    else:
        curs.execute("""select pid, dept, name
                        from professors 
                        where lower(name) like %s and dept=%s""", 
                        [query_string, dept]) 
    return curs.fetchall()

def find_dept_course(conn, dept):
    '''get all courses in a department'''
    curs = dbi.dict_cursor(conn)
    curs.execute("""select dept, courseid, title, code
                    from courses 
                    where dept=%s""", [dept]) 
    return curs.fetchall()

def find_dept_name(conn, dept):
    '''get the name of a department given the abbreviation'''
    curs = dbi.dict_cursor(conn)
    curs.execute("""select name
                    from departments
                    where abbrv=%s""", [dept]) 
    return curs.fetchone()

def find_course_info(conn,courseid):
    '''Returns info of course with given course id'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from courses 
                    where courseid=%s''', [courseid])
    return curs.fetchone()

def find_prof_posts(conn, pid):
    '''Returns all posts about a given professor'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from posts 
                    where prof = %s''', [pid])
    return curs.fetchall()

def find_course_posts(conn, courseid):
    '''Returns all posts about a given course'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from posts where course = %s''', [courseid])
    return curs.fetchall()

def find_course_section_posts(conn, courseid, pid):
    '''Returns all posts about a given course'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from posts where course = %s and prof = %s''',
    [courseid, pid])
    return curs.fetchall()

def find_prof_avgrating(conn, pid):
    '''Returns all posts about a given professor'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select avg(rating) as avg from prof_ratings 
                    where pid = %s''', [pid])
    avg = (curs.fetchone())['avg']
    return avg

def find_course_avgrating(conn, courseid):
    '''Returns all posts about a given course'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select avg(rating) as avg 
                    from course_ratings 
                    where courseid = %s''', [courseid])
    return (curs.fetchone())['avg']

def find_users(conn):
    '''Returns a list of dictionaries of all users'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select uid, username from users''')
    return curs.fetchall()

def username_from_uid(conn, uid):
    '''Returns the current username associated with the give uid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select username from users where uid = %s''', [uid])
    return curs.fetchone()

def add_post(conn, time, user, course, prof, prof_rating, course_rating, text,
 attachments, username, upvotes, downvotes):
    '''Add a new post about course and professor to the database and returns
    the postid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into posts(time, user, course, prof, prof_rating,
    course_rating, text, attachments, username, upvotes, downvotes) 
    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
    [time, user, course, prof, prof_rating, course_rating, text, attachments, username, upvotes,downvotes])
    curs.execute('''select last_insert_id()''')
    id = curs.fetchone()
    conn.commit()
    curs.execute('''insert into prof_ratings(rating, user, pid)
                    values(%s, %s, %s)
                    on duplicate key update rating = %s''', 
                    [prof_rating, user, prof, prof_rating])
    conn.commit()
    curs.execute('''insert into course_ratings(rating, user, courseid)
                    values(%s, %s, %s)
                    on duplicate key update rating = %s''', 
                    [course_rating, user, course, course_rating])
    conn.commit()
    return id


def add_course_post(conn, time, user, course, course_rating, text, attachments, username, upvotes, downvotes):
    '''Add a new post about a course to the database and returns the postid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into posts(time, user, course, course_rating, text,
    attachments, username, upvotes, downvotes) 
    values(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
    [time, user, course, course_rating, text, attachments, username, upvotes, downvotes])
    curs.execute('''select last_insert_id()''')
    id = curs.fetchone()
    conn.commit()
    curs.execute('''insert into course_ratings(rating, user, courseid)
                    values(%s, %s, %s)
                    on duplicate key update rating = %s''', 
                    [course_rating, user, course, course_rating])
    conn.commit()
    return id

def add_prof_post(conn, time, user, prof, prof_rating, text, attachments, username, upvotes, downvotes):
    '''Add a new post about a professor to the database and returns the 
    postid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into posts(time, user, prof, prof_rating, text,
    attachments, username, upvotes, downvotes) 
    values(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
    [time, user, prof, prof_rating, text, attachments, username, upvotes, downvotes])
    curs.execute('''select last_insert_id()''')
    id = curs.fetchone()
    conn.commit()
    curs.execute('''insert into prof_ratings(rating, user, pid)
                    values(%s, %s, %s)
                    on duplicate key update rating = %s''', 
                    [prof_rating, user, prof, prof_rating])
    conn.commit()
    return id


def add_comment(conn, postid, time, user, text, attachments, upvotes, 
downvotes, username):
    '''Add a new comment associated with a post to the database and returns the
    commentid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into comments(postid, time, user, text, attachments,
    upvotes, downvotes, username)
                    values(%s,%s,%s,%s,%s,%s,%s,%s)''', 
                    [postid, time, user, text, attachments, upvotes, 
                    downvotes, username])
    conn.commit()
    curs.execute('''select last_insert_id()''')
    return curs.fetchone()

def get_comments(conn, postid):
    '''Returns a list of dictionaries of 50 most recent comments with same
    postid'''
    '''IMPORTANT note: switch this to be with infinite scrolling later'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select * from comments
        where postid = %s
        order by time asc''', [postid])
    return curs.fetchall()

def update_post_votes(conn,postid,votes):
    '''Updates posts table to modify votes for post with postid'''
    curs = dbi.dict_cursor(conn)
    if votes == 'up':
        curs.execute(''' 
            UPDATE posts 
            SET upvotes = upvotes + 1 
            WHERE postid = %s''', [postid])
    if votes == 'down':
        curs.execute(''' 
            UPDATE posts 
            SET downvotes = downvotes + 1 
            WHERE postid = %s''', [postid])
    conn.commit()

def update_comment_votes(conn,commentid,votes):
    '''Updates comment table to modify votes for comment with commentid'''
    curs = dbi.dict_cursor(conn)
    if votes == 'up':
        curs.execute(''' 
            UPDATE comments 
            SET upvotes = upvotes + 1 
            WHERE commentid = %s''', [commentid])
    if votes == 'down':
        curs.execute(''' 
            UPDATE comments 
            SET downvotes = downvotes + 1 
            WHERE commentid = %s''', [commentid])
    conn.commit()


def check_username(conn, name):
    '''Returns a dictionary of user info with the given username'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from users where username = %s''',
    [name])
    return curs.fetchone() 

def update_username(conn, uid, name):
    '''Updates the username for the given uid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''UPDATE users 
    SET username = %s 
    WHERE uid = %s''', [name, uid])
    conn.commit()

def check_user_registration(conn, email):
    '''
    Checks if a person is registered in the database using a given email.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''
    select uid 
    from users
    where email = %s
    '''
    curs.execute(sql, [email])
    return curs.fetchone()

def register_user(conn, email):
    '''
    Adds a new user to the database and returns the new uid.
    '''
    # make a random username
    un = helper.random_username()
    # add the user
    curs = dbi.dict_cursor(conn)
    sql = '''
    insert into users (username, email)
    values (%s, %s)
    '''
    curs.execute(sql, [un, email])
    conn.commit()
    # get the uid
    curs.execute('''select last_insert_id() from posts''')
    return curs.fetchone()

def add_file(conn, uid, filename):
    '''
    Enters a user-uploaded file into the database.
    '''
    sql = '''insert into documents(uid) values (%s)'''
    curs = dbi.dict_cursor(conn)
    curs.execute(sql, [uid])
    conn.commit()
    curs.execute('''select last_insert_id() from documents''')
    id = curs.fetchone()
    id = id['last_insert_id()']
    new_filename = '{}_{}'.format(id, filename)
    curs.execute('''update documents
    set filepath=%s
    where docid=%s''', [new_filename, id])
    conn.commit()
    # get updated filepath
    curs.execute('''select *
    from documents
    where docid = %s''', [id])
    return curs.fetchone()


def get_filepath(conn, fileid):
    '''
    Given the fileid, returns the file path.
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select filepath
    from documents
    where docid = %s''', [fileid])
    return curs.fetchone()