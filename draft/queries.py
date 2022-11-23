import cs304dbi as dbi

def find_depts(conn):
    '''Returns a list of dictionaries of all departments'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select * from departments''')
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
    '''Returns course rating  single course from a specific post '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select posts.course_rating
    from posts inner join courses 
    on (posts.course = courses.courseID)
    where postid = %s''',[postid]) 
    #returns course rating and course code
    return curs.fetchone()

def post_course_code(conn, postid):
    '''Returns course code for single course from a specific post '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select courses.code
    from posts inner join courses 
    on (posts.course = courses.courseID)
    where postid = %s''',[postid]) 
    #returns course rating and course code
    return curs.fetchone()

def post_prof_rating(conn, postid):
    '''Returns rating single prof from a specific post '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select posts.prof_rating
    from posts inner join professors 
    on (posts.prof = professors.pid)
    where postid = %s''', [postid]) 
    #returns prof rating and prof name
    return curs.fetchone()

def post_prof_name(conn, postid):
    '''Returns name for single prof from a specific post '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select professors.name
    from posts inner join professors 
    on (posts.prof = professors.pid)
    where postid = %s''', [postid]) 
    #returns prof rating and prof name
    return curs.fetchone()

def post_text(conn, postid):
    '''Returns text from a specific post '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select posts.text
    from posts 
    where postid = %s''', [postid]) 
    #returns text from one post
    return curs.fetchone()

def post_time(conn, postid):
    '''Returns timestamp from a specific post '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select posts.time
    from posts 
    where postid = %s''', [postid]) 
    #returns time from one post
    return curs.fetchone()

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

