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
from datetime import datetime

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
        
@app.route('/upload/', methods=['GET','POST'])
def upload():
    conn = dbi.connect()
    ### TO DO: Check if user is logged in and get their user id
    # for now assign random user
    people = queries.find_users(conn)
    uid = random.choice([person['uid'] for person in people])
    professors = queries.find_profs(conn)
    courses = queries.find_courses(conn)
    departments = queries.find_depts(conn)

    if request.method == 'GET':
        # load form
        return render_template('post-form.html', title='Create a Post',
        professors = professors, courses = courses, departments = departments)
    else: # method == POST
        # retrieve information
        username = queries.username_from_uid(conn, uid)
        time = datetime.now()
        ### TO DO: ask why i can't retrieve 'prof'
        dept = request.form['dept']
        new_dept_name = request.form['new-dept-name']
        new_dept_abbrv = request.form['new-dept-name']
        profid = request.form['pid']
        new_prof_name = request.form['new-prof-name']
        courseid = request.form['course']
        new_course_name = request.form['new-course-name']
        new_course_code = request.form['new-course-code']
        prof_rating = request.form['prof-rating']
        course_rating = request.form['course-rating']
        review_text = request.form['review-text']

        # make list of recieved info to iterate through and change '' to None
        raw_info = [dept, new_dept_name, new_dept_abbrv, profid, new_prof_name, courseid,
        new_course_name, new_course_code, prof_rating, course_rating, review_text]

        for var in raw_info:
            if var == '':
                var = None
                print(type(var))

        ### TO DO: add pdf table to database; get pdf from form and append to database
        pdf = request.files['pdf']
        print(type(pdf))

        # check if essential information is present
        if dept == "" and new_dept_abbrv == "":
            flash('Please choose a department or enter a new one.')
            return render_template('post-form.html', title='Create a Post',
            professors = professors, courses = courses, departments = departments)
        if profid == "" and courseid == "":
            flash('Please enter a Professor and/or Course.')
            return render_template('post-form.html', title='Create a Post',
            professors = professors, courses = courses, departments = departments)
        elif profid == "" and prof_rating != "":
            flash('Please provide a Professor to rate or remove the \
                    Professor Rating.')
            return render_template('post-form.html', title='Create a Post',
            professors = professors, courses = courses, departments = departments)
        elif courseid == "" and course_rating != "":
            flash('Please provide a Course to rate or remove the \
                    Course Rating.')
            return render_template('post-form.html', title='Create a Post',
                                    professors = professors, courses = courses, 
                                    departments = departments)
        elif (prof_rating == "" and course_rating == "" and review_text 
        == "" and not request.files.get('pdf', None)):
            flash('Please provide content for your post.')
            return render_template('post-form.html', title='Create a Post',
                                    professors = professors, courses = courses,
                                    departments = departments)
        
        # if entering a new department
        if dept == 'other':
            if (new_dept_name == "" or new_dept_abbrv == ""):
                flash('Please enter the required information to add a new \
                department, or select one from the drop down menu above.')
                return render_template('post-form.html', title='Create a Post',
                                        professors = professors, courses = courses, 
                                        departments = departments)
            queries.add_department(conn, new_dept_name, new_dept_abbrv)
            dept = new_dept_abbrv

        # if entering a new professor
        if profid == 'other':
            if (new_prof_name == ""):
                flash('Please enter the required information to add a new \
                professor, or select one from the drop down menu above.')
                return render_template('post-form.html', title='Create a Post',
                                        professors = professors, courses = courses, 
                                        departments = departments)
            profid = queries.add_professor(conn, new_prof_name, dept)
        
        # if entering a new course
        if courseid == 'other':
            if (new_course_name == "" or new_course_code == ""):
                flash('Please enter the required information to add a new \
                course, or select one from the drop down menu above.')
                return render_template('post-form.html', title='Create a Post',
                                        professors = professors, courses = courses, 
                                        departments = departments)
            courseid = queries.add_course(conn, new_course_name, new_course_code, dept)

        # upload post
        postid = queries.add_post(conn, time, uid, courseid, profid, prof_rating, course_rating, review_text, pdf)
        flash('Upload successful')
        # go to post page
        return redirect(url_for('view_post', postid=postid))

@app.route('/<department>')
def department(department):
    return 0

@app.route('/professor/<department>/<professor>')
def professor(department, professor):
    conn = dbi.connect()
    name = queries.find_prof_name(conn, department,professor)
    if name==None:
        flash('Department and professor don\'t match, try again.')
        return redirect(url_for('home'))
    posts = queries.find_prof_posts(conn, professor)
    rating = queries.find_prof_avgrating(conn, professor)
    #rating = 5
    return render_template('professor.html', prof_name=name['name'], department=department, avg_rating=rating, posts=posts)

@app.route('/course/<department>/<course>')
def course(department, course):
    conn = dbi.connect()
    course_info = queries.find_course_info(conn, department,course)
    if course_info==None:
        flash('Department and course don\'t match, try again.')
        return redirect(url_for('home'))
    posts = queries.find_course_posts(conn, course)
    rating = queries.find_course_avgrating(conn, course)
    #rating = 5
    return render_template('course.html', code=course_info['code'], course=course_info['title'], department=course_info['dept'], avg_rating=rating, posts=posts)

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



professor('MATH', 'Joe Lauer')