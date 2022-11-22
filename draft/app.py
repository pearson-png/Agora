from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi

import random
import queries

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/', methods=['GET','POST'])
def home():
    conn = dbi.connect()
    if request.method == 'GET':
        #gets homepage with dropdown menu of all choices and recent posts
        departments = queries.find_depts(conn)
        professors = queries.find_profs(conn)
        courses = queries.find_courses(conn)
        posts = queries.recent_posts(conn)
        return render_template('home_page.html',title='Hello', 
        departments = departments, courses = courses, 
        professors = professors, posts = posts)
    if request.method == 'POST':
        #redirects according to filter options to dept/prof/course route
        filters = request.form
        dept = filters['department']
        prof = filters['professor']
        course = filters['course']
        ##options here
        if dept == "0":
            #if no dept chosen, reload the homepage no matter other fields
            departments = queries.find_depts(conn)
            professors = queries.find_profs(conn)
            courses = queries.find_courses(conn)
            posts = queries.recent_posts(conn)
            flash("Please choose a department")
            return render_template('home_page.html',title='Hello', 
            departments = departments, courses = courses, 
            professors = professors, posts = posts)
        elif prof == "0" and course == "0":
            #if only department chosen, direct to dept page
            return redirect(url_for('department', department=dept))
        elif course == "0" and prof != "0":
            #if only prof chosen, direct to prof page
            return redirect(url_for('professor', department=dept, professor=prof))
        elif course != "0" and prof == "0":
            #if only course chosen, direct to course page
            return redirect(url_for('course', department=dept, course=course))
        else:
            #if all three were chosen, give specific prof and course page
            return redirect(url_for('course_section', department=dept, professor=prof, course=course))


@app.route('/view/<postid>', methods=['GET','POST'])
#view individual posts
def view_post(postid):
    conn = dbi.connect()
    # if user clicks on a post
    if request.method == 'GET':
        user = queries.post_user(conn, postid)['username']
        course_code = queries.post_course_code(conn, postid)['code'] 
        course_rating = queries.post_course_rating(conn, postid)['course_rating']
        prof_name = queries.post_prof_name(conn, postid)['name']
        prof_rating = queries.post_prof_rating(conn, postid)['prof_rating']
        text = queries.post_text(conn,postid)['text']
        time = queries.post_time(conn,postid)['time']

    return render_template('view_post.html', action= url_for('view_post', postid=postid), 
        user=user, course_code=course_code, course_rating=course_rating, prof_name=prof_name, prof_rating=prof_rating, text=text, time=time) 
        


@app.before_first_request
def init_db():
    dbi.cache_cnf()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use = 'agora_db' 
    dbi.use(db_to_use)
    print('will connect to {}'.format(db_to_use))

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
