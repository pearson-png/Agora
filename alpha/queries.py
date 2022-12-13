import cs304dbi as dbi

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

def find_prof_avgrating(conn, pid):
    '''Returns all posts about a given professor'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select avg(rating) as avg from prof_ratings 
                    where pid = %s''', [pid])
    return (curs.fetchone())['avg']

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

def add_post(conn, time, user, course, prof, prof_rating, course_rating, text, attachments):
    '''Add a new post about course and professor to the database and returns the postid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into posts(time, user, course, prof, prof_rating, course_rating, text, attachments) 
    values(%s,%s,%s,%s,%s,%s,%s,%s)''',
    [time, user, course, prof, prof_rating, course_rating, text, attachments])
    conn.commit()
    curs.execute('''select last_insert_id() from posts''')
    return curs.fetchone() 

def add_course_post(conn, time, user, course, course_rating, text, attachments):
    '''Add a new post about a course to the database and returns the postid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into posts(time, user, course, course_rating, text, attachments) 
    values(%s,%s,%s,%s,%s,%s)''',
    [time, user, course, course_rating, text, attachments])
    conn.commit()
    curs.execute('''select last_insert_id() from posts''')
    return curs.fetchone()

def add_prof_post(conn, time, user, prof, prof_rating, text, attachments):
    '''Add a new post about a professor to the database and returns the postid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into posts(time, user, prof, prof_rating, text, attachments) 
    values(%s,%s,%s,%s,%s,%s)''',
    [time, user, prof, prof_rating, text, attachments])
    conn.commit()
    curs.execute('''select last_insert_id() from posts''')
    return curs.fetchone() 

def add_comment(conn, postid, time, user, text, attachments, upvotes, downvotes):
    '''Add a new comment associated with a post to the database and returns the commentid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into comments(postid, time, user, text, attachments, upvotes, downvotes)
                    values(%s,%s,%s,%s,%s,%s,%s)''', 
                    [postid, time, user, text, attachments, upvotes, downvotes])
    conn.commit()
    curs.execute('''select last_insert_id() from comments''')
    return curs.fetchone()

def get_comments(conn, postid):
    '''Returns a list of dictionaries of 50 most recent comments with same postid'''
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

# def first_post_upvotes(conn,postid,upvote):
#     '''updates first upvote into posts table'''
#     curs = dbi.dict_cursor(conn)
#     curs.execute(''' 
#         UPDATE posts(upvotes) 
#         values(%s)''', [upvote,postid])
#     conn.commit()


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
    '''Updates comment table to increase downvotes for comment with commentid'''
    curs = dbi.dict_cursor(conn)
    curs.execute(''' 
        UPDATE comments 
        SET downvotes = %s 
        WHERE commentid = %s''', [downvotes, commentid])
    conn.commit()

def check_username(name):
    '''Returns a dictionary of user info with the given username'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from users where username = %s''',
    [name])
    return curs.fetchone() 

def update_username(uid, name):
    '''Updates the username for the given uid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''UPDATE users SET username = %s 
    WHERE uid = %s''', [name, uid])
    conn.commit()

# use code below if we don't get the course browser csv

# def add_professor(conn, name, dept):
#     '''Adds a professor to the database and returns pid'''
#     # add prof
#     curs = dbi.dict_cursor(conn)
#     curs.execute('''
#     insert into professors(name, dept) values(%s,%s)''',[name, dept])
#     conn.commit()
#     # get pid
#     curs.execute('''
#     select last_insert_id() from professors''')
#     return curs.fetchone()    

# def add_course(conn, name, code, dept):
#     '''Adds a course to the database and returns courseid'''
#     curs = dbi.dict_cursor(conn)
#     curs.execute('''
#     insert into courses(title, code, dept) values(%s,%s,%s)''',[name, code, dept])
#     conn.commit()
#     curs.execute('''
#     select last_insert_id() from courses''')
#     return curs.fetchone()  

# def add_department(conn, name, abbrv):
#     '''Add a department to the database'''
#     curs = dbi.dict_cursor(conn)
#     curs.execute('''
#     insert into departments(name, abbrv) values(%s,%s)''',[name, abbrv])
#     conn.commit()
