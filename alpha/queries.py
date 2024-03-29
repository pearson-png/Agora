from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
import cs304dbi as dbi
import helper

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

def recent_posts(conn):
    '''Returns a list of dictionaries of 50 most recent posts'''
    '''IMPORTANT note: switch this to be with infinite scrolling later'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select * from posts
        order by time desc
        limit 50''')
    return curs.fetchall()


def post_user(conn, postid):
    '''Returns username that wrote a specific post '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select users.username
    from posts inner join users 
    on (posts.user = users.uid)
    where postid = %s''', [postid])
    return curs.fetchone()

def post_course_rating(conn, postid):
    '''Returns single course rating from a specific post '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select posts.course_rating
    from posts inner join courses 
    on (posts.course = courses.courseID)
    where postid = %s''',[postid]) 
    #returns course rating
    return curs.fetchone()

def post_course_code(conn, postid):
    '''Returns single course code from a specific post '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select courses.code
    from posts inner join courses 
    on (posts.course = courses.courseID)
    where postid = %s''',[postid]) 
    #returns course course code
    return curs.fetchone()

def post_course_name(conn, postid):
    '''Returns single course name from a specific post '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select courses.title
    from posts inner join courses 
    on (posts.course = courses.courseID)
    where postid = %s''',[postid]) 
    return curs.fetchone()

def post_prof_rating(conn, postid):
    '''Returns single prof rating from a specific post '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select posts.prof_rating
    from posts inner join professors 
    on (posts.prof = professors.pid)
    where postid = %s''', [postid]) 
    return curs.fetchone()

def post_prof_name(conn, postid):
    '''Returns single prof name from a specific post '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select professors.name
    from posts inner join professors 
    on (posts.prof = professors.pid)
    where postid = %s''', [postid]) 
    return curs.fetchone()

def post_text(conn, postid):
    '''Returns text from a specific post '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select posts.text
    from posts 
    where postid = %s''', [postid]) 
    return curs.fetchone()

def post_time(conn, postid):
    '''Returns timestamp from a specific post '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select posts.time
    from posts 
    where postid = %s''', [postid]) 
    return curs.fetchone()

def find_prof_name(conn, department,pid):
    '''Returns name of professor with given department and pid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select name 
                    from professors 
                    where dept=%s and pid=%s''', [department,pid])
    #returns one matching name
    return curs.fetchone()

def search_course(conn, dept, query):
    '''find a course that is similar to the search query'''
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

def find_course_info(conn, department,courseid):
    '''Returns info of course with given department and course id'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from courses 
                    where dept=%s and courseid=%s''', [department,courseid])
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
    flash(avg)
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
 attachments):
    '''Add a new post about course and professor to the database and returns
    the postid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into posts(time, user, course, prof, prof_rating,
    course_rating, text, attachments) 
    values(%s,%s,%s,%s,%s,%s,%s,%s)''',
    [time, user, course, prof, prof_rating, course_rating, text, attachments])
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
    curs.execute('''select last_insert_id() from posts''')
    return curs.fetchone() 

def add_course_post(conn, time, user, course, course_rating, text, attachments):
    '''Add a new post about a course to the database and returns the postid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into posts(time, user, course, course_rating, text,
    attachments) 
    values(%s,%s,%s,%s,%s,%s)''',
    [time, user, course, course_rating, text, attachments])
    conn.commit()
    curs.execute('''insert into course_ratings(rating, user, courseid)
                    values(%s, %s, %s)
                    on duplicate key update rating = %s''', 
                    [course_rating, user, course, course_rating])
    conn.commit()
    curs.execute('''select last_insert_id() from posts''')
    return curs.fetchone()

def add_prof_post(conn, time, user, prof, prof_rating, text, attachments):
    '''Add a new post about a professor to the database and returns the 
    postid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into posts(time, user, prof, prof_rating, text,
    attachments) 
    values(%s,%s,%s,%s,%s,%s)''',
    [time, user, prof, prof_rating, text, attachments])
    conn.commit()
    curs.execute('''insert into prof_ratings(rating, user, pid)
                    values(%s, %s, %s)
                    on duplicate key update rating = %s''', 
                    [prof_rating, user, prof, prof_rating])
    conn.commit()
    curs.execute('''select last_insert_id() from posts''')
    return curs.fetchone() 


def add_comment(conn, postid, time, user, text, attachments, upvotes, 
downvotes):
    '''Add a new comment associated with a post to the database and returns the
    commentid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into comments(postid, time, user, text, attachments,
    upvotes, downvotes)
                    values(%s,%s,%s,%s,%s,%s,%s)''', 
                    [postid, time, user, text, attachments, upvotes, 
                    downvotes])
    conn.commit()
    curs.execute('''select last_insert_id() from comments''')
    return curs.fetchone()

def get_comments(conn, postid):
    '''Returns a list of dictionaries of 50 most recent comments with same
    postid'''
    '''IMPORTANT note: switch this to be with infinite scrolling later'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select * from comments
        where postid = %s
        order by time asc
        limit 50''', [postid])
    return curs.fetchall()

def get_post_upvotes(conn,postid):
    '''Gets upvotes for post with postid '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select upvotes 
        from posts
        where postid = %s''', [postid])
    return curs.fetchone()

def update_post_upvotes(conn,postid,upvotes):
    '''Updates posts table to increase upvote for post with postid'''
    curs = dbi.dict_cursor(conn)
    curs.execute(''' 
        UPDATE posts 
        SET upvotes = %s 
        WHERE postid = %s''', [upvotes, postid])
    conn.commit()
    
def get_post_downvotes(conn,postid):
    '''Gets downvotes for post with postid '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select downvotes 
        from posts
        WHERE postid = %s''', [postid])
    return curs.fetchone()

def update_post_downvotes(conn,postid,downvotes):
    '''Updates posts table to increase downvotes for post with postid'''
    curs = dbi.dict_cursor(conn)
    curs.execute(''' 
        UPDATE posts 
        SET downvotes = %s 
        WHERE postid = %s''', [downvotes, postid])
    conn.commit()

def get_comment_upvotes(conn,commentid):
    '''Gets upvotes for comment with commentid '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select upvotes 
        from comments
        where commentid = %s''', [commentid])
    return curs.fetchone()

def update_comment_upvotes(conn,commentid,upvotes):
    '''Updates comment table to increase upvote for comment with commentid'''
    curs = dbi.dict_cursor(conn)
    curs.execute(''' 
        UPDATE comments 
        SET upvotes = %s 
        WHERE commentid = %s''', [upvotes, commentid])
    conn.commit()
    
def get_comment_downvotes(conn,commentid):
    '''Gets downvotes for comment with commentid '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select downvotes 
        from comments
        where commentid = %s''', [commentid])
    return curs.fetchone()

def update_comment_downvotes(conn,commentid,downvotes):
    '''Updates comment table to increase downvotes for comment with
    commentid'''
    curs = dbi.dict_cursor(conn)
    curs.execute(''' 
        UPDATE comments 
        SET downvotes = %s 
        WHERE commentid = %s''', [downvotes, commentid])
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