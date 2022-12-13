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
import helper

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
# CAS
from flask_cas import CAS

CAS(app)

app.config['CAS_SERVER'] = 'https://login.wellesley.edu:443'
app.config['CAS_LOGIN_ROUTE'] = '/module.php/casserver/cas.php/login'
app.config['CAS_LOGOUT_ROUTE'] = '/module.php/casserver/cas.php/logout'
app.config['CAS_VALIDATE_ROUTE'] = '/module.php/casserver/serviceValidate.php'
app.config['CAS_AFTER_LOGIN'] = 'after_login'
app.config['CAS_AFTER_LOGOUT'] = 'logout'

@app.route('/', methods=['GET','POST'])
def home():
    # check if logged in
    if len(session.keys()) == 0:
        return redirect('http://cs.wellesley.edu:1950/login/')

    # uid = session.get('uid')
    conn = dbi.connect()
    if request.method == 'GET':
        #gets homepage with dropdown menu of all choices and recent posts
        departments = queries.find_depts(conn)
        professors = {}
        courses = {}
        # professors = queries.find_profs(conn)
        # courses = queries.find_courses(conn)
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
            professors = {}
            courses = {}
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

@app.route('/update_dropdown')
def update_dropdown():
    conn = dbi.connect()

    # the value of the department dropdown (selected by the user)
    department = request.args.get('department')

    # get values for the second dropdown
    professors = queries.find_profs_indepartment(conn, department)

    # get values for the third
    courses = queries.find_courses_indepartment(conn, department)
    # create the values in the dropdown as a html string
    html_string1 = '<option value="0">All</option>'
    for professor in professors:
        html_string1 += '<option value="{}">{}</option>'.format(professor['pid'], professor['name'])

    html_string2 = '<option value="0">All</option>'
    for course in courses:
        html_string2 += '<option value="{}">{}:{}</option>'.format(course['courseid'], course['code'], course['title'])

    return jsonify(html_string1=html_string1, html_string2=html_string2)

@app.route('/login/')
def login():
    return render_template('login.html', title = 'Title')

@app.route('/after_login/')
def after_login():
    # if uid already in session, can delete later but shows functionality
    if session.get('uid'): 
        flash('redirecting from login, uid already in session')
        return redirect(url_for('home'))

    conn = dbi.connect()
    email = session['CAS_ATTRIBUTES']['cas:mail']
    # print('email: ',email)
    uid_dic = queries.check_user_registration(conn, email) 
    uid = uid_dic['uid']
    # print('uid: ',uid)
    
    # if the user is already registered, set cookie and redirect to home
    if uid: 
        # print('redirecting from after_login, user already registered')
        session['uid'] = uid
        flash('Welcome back, you are logged in.')
        return redirect(url_for('home'))
    # register if scott or a student
    elif email == 'scott.anderson@wellesley.edu' or session['CAS_ATTRIBUTES']['cas:isStudent'] == 'Y':
        # print('registering user and redirecting to homepage')
        flash('You are now registered with Agora!')
        uid_dic = queries.register_user(conn, email)
        uid = uid_dic['last_insert_id()']
        # print('new user uid: ', uid)
        session['uid'] = uid
        return redirect(url_for('home'))
    else: 
        flash('You must be a Wellesley College student to use Agora.')
        return redirect('http://cs.wellesley.edu:1950/login/')

@app.route('/logout/')
def logout():
    flash('You have been logged out.')
    # return redirect(url_for('cas.login'))
    return redirect('http://cs.wellesley.edu:1950/login/')

@app.route('/view/<postid>', methods=['GET','POST'])
#view individual posts
def view_post(postid):
    conn = dbi.connect()
    # if user clicks on a post
    if request.method == 'GET':
        #always include these in all posts
        user = queries.post_user(conn, postid)['username']
        text = queries.post_text(conn,postid)['text']
        time = queries.post_time(conn,postid)['time']

        #course variables
        try:
            course_code = queries.post_course_code(conn, postid)['code']
        except TypeError:
            course_code = None
        try:
            course_name = queries.post_course_name(conn,postid)['title']
        except TypeError:
            course_name = None
        try:
            course_rating = queries.post_course_rating(conn, postid)['course_rating']
        except TypeError:
            course_rating = None
        #professor variables
        try:
            prof_name = queries.post_prof_name(conn, postid)['name']
        except TypeError:
            prof_name = None
        try:
            prof_rating = queries.post_prof_rating(conn, postid)['prof_rating']
        except TypeError:
            prof_rating = None
        
        #if there is no professor 
        if prof_name == None:
            return render_template('view-post-course.html', action= url_for('view_post', postid=postid), 
            user=user, course_name=course_name, course_code=course_code, course_rating=course_rating, text=text, time=time)
        #if there is no course
        elif course_code == None:
            return render_template('view-post-prof.html', action= url_for('view_post', postid=postid), 
            user=user, prof_name=prof_name, prof_rating=prof_rating, text=text, time=time)
        #if there is a prof and a course
        else:
            return render_template('view-post-prof-course.html', action= url_for('view_post', postid=postid), 
            user=user, course_name=course_name, course_code=course_code, course_rating=course_rating, prof_name=prof_name, 
            prof_rating=prof_rating, text=text, time=time) 

@app.route('/comment/', methods=['GET', 'POST'])
def comment():
    if request.method == 'GET':
        conn = dbi.connect()
        ### TO DO: Check if user is logged in and get their user id
        # for now assign random user
        return render_template('comment-form.html', action= url_for('comment'))
    

        
@app.route('/upload/', methods=['GET','POST'])
def upload():
    conn = dbi.connect()
    uid = session.get('uid')
    professors = {}
    courses = {}
    departments = queries.find_depts(conn)

    if request.method == 'GET':
        # load form
        return render_template('post-form.html', title='Create a Post',
        professors = professors, courses = courses, departments = departments)
    else: # method == POST
        # retrieve information
        username = queries.username_from_uid(conn, uid)
        time = datetime.now()
        dept = request.form['dept']
        profid = request.form['pid']
        courseid = request.form['course']
        prof_rating = request.form['prof-rating']
        course_rating = request.form['course-rating']
        review_text = request.form['review-text']

        ### TO DO: add pdf table to database; get pdf from form and append to database
        pdf = request.files['pdf']
        print(type(pdf))

        # check if essential information is present
        if dept == "":
            flash('Please choose a department')
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

        # upload post
        if profid == '':
            postid = queries.add_course_post(conn, time, uid, courseid, course_rating, review_text, pdf)
        elif courseid == '':
            postid = queries.add_prof_post(conn, time, uid, profid, prof_rating, review_text, pdf)
        else:
            postid = queries.add_post(conn, time, uid, courseid, profid, prof_rating, course_rating, review_text, pdf)
        flash('Upload successful')
        # go to post page
        return redirect(url_for('view_post', postid=postid['last_insert_id()']))

@app.route('/update_upload_form')
def update_upload_form():
    conn = dbi.connect()

    # the value of the department dropdown (selected by the user)
    department = request.args.get('department')

    # get values for the second dropdown
    professors = queries.find_profs_indepartment(conn, department)

    # get values for the third
    courses = queries.find_courses_indepartment(conn, department)
    # create the values in the dropdown as a html string
    html_string1 = '<option value="">Choose One</option>'
    for professor in professors:
        html_string1 += '<option value="{}">{}</option>'.format(professor['pid'], professor['name'])

    html_string2 = '<option value="">Choose One</option>'
    for course in courses:
        html_string2 += '<option value="{}">{}:{}</option>'.format(course['courseid'], course['code'], course['title'])

    return jsonify(html_string1=html_string1, html_string2=html_string2)

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

@app.route('/course-section/<department>/<professor>/<course>')
def course_section(department, professor, course):
    #placeholder for now
    return redirect(url_for('home'))

@app.route('/change-username', methods=['POST'])
def change_username():
    #get uid
    uid = session.get('uid')
    #get new name
    new_name = helper.random_username()
    #check if name exist
    check = queries.check_username(new_name)
    #if not none, the name exists, try again until you get a free name
    while check != None:
        new_name = helper.random_username()
        check = queries.check_username(uid, new_name)
    queries.update_username(new_name)
    return redirect(url_for('home'))

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

#code unnecessary with current tagging system, needed if prof-course relation enforced
# @app.route('/update_professors')
# def update_professors():
#     conn = dbi.connect()

#     # the value of the course chosen
#     courseid = request.args.get('course')

#     # get values for the second dropdown
#     professors = queries.find_profs_incourse(conn, courseid)

#     # create the values in the dropdown as a html string
#     html_string1 = '<option value="0">All</option>'
#     for professor in professors:
#         html_string1 += '<option value="{}">{}</option>'.format(professor['pid'], professor['name'])

#     return jsonify(html_string1=html_string1)

# @app.route('/update_courses')
# def update_courses():
#     conn = dbi.connect()

#     # the value of the professor chosen
#     pid = request.args.get('professor')

#     # get values for the second dropdown
#     courses = queries.find_course_byprofessor(conn, pid)

#     # create the values in the dropdown as a html string
#     html_string2 = '<option value="0">All</option>'
#     for course in courses:
#         html_string2 += '<option value="{}">{}:{}</option>'.format(course['courseid'], course['code'], course['title'])

#     return jsonify(html_string2=html_string2)