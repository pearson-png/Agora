from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi

import random, os
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
app.config['CAS_AFTER_LOGOUT'] = 'my_login'

# upload files
app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 2*1024*1024 # 2 MB
ALLOWED_EXTENSIONS = {'pdf'}

# create dic for random usernames
usernames_dict = {}

# to do: relplace hardcoded port numbers w port variable

@app.route('/', methods=['GET','POST'])
def home():
    # look at uid in session specifically
    # check if logged in for all routes
    if not session.get('uid'):
        return redirect(url_for('my_login'))

    # uid = session.get('uid')
    conn = dbi.connect()
    if request.method == 'GET':
        #gets homepage with dropdown menu of all choices and recent posts
        departments = queries.find_depts(conn)
        professors = {}
        courses = {}
        posts = queries.get_recent_post_allinfo(conn)
        return render_template('home_page.html',page_title='Hello', 
        departments = departments, courses = courses, 
        professors = professors, posts = posts)
    if request.method == 'POST':
        return helper.postFilterForm(conn, request.form)

@app.route('/search/<department>/<query>', methods=['GET'])
def search(department, query):
    if not session.get('uid'):
        return redirect(url_for('my_login'))
    #search the course or professor with names that match the entered query
    conn = dbi.connect()
    course_list = queries.search_course(conn, department, query)
    professor_list = queries.search_prof(conn, department, query)
    if len(course_list) == 0 and len(professor_list) == 0:
        flash("No matching results found")
        return redirect(url_for('home'))
    return render_template('search.html', course_list=course_list, professor_list=professor_list)


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
        html_string1 += '<option value="{}">{}</option>'.format(\
            professor['pid'], professor['name'])

    html_string2 = '<option value="0">All</option>'
    for course in courses:
        html_string2 += '<option value="{}">{}:{}</option>'.format(\
            course['courseid'], course['code'], course['title'])

    return jsonify(html_string1=html_string1, html_string2=html_string2)

@app.route('/my_login/')
# change everywhere tp my_login
def my_login():
    if session.get('uid'):
        session['uid'] = session.get('uid')
        return redirect(url_for('home'))
    else:
        return render_template('login.html')

@app.route('/after_login/')
def after_login():
    # if uid already in session, can delete later but shows functionality
    if session.get('uid'): 
        flash('redirecting from login, uid already in session')
        return redirect(url_for('home'))

    conn = dbi.connect()
    email = session['CAS_ATTRIBUTES']['cas:mail']
    # print('email: ',email)
    try: 
        uid_dic = queries.check_user_registration(conn, email) 
        uid = uid_dic['uid']

    except TypeError:
        uid = None
    
    # print('uid: ',uid)
    
    # if the user is already registered, set cookie and redirect to home
    if uid: 
        # print('redirecting from after_login, user already registered')
        session['uid'] = uid
        flash('Welcome back, you are logged in.')
        return redirect(url_for('home'))
    # turn back on if scott isnt grading
    # elif email == 'sanderso@wellesley.edu' or session['CAS_ATTRIBUTES']\
    #     ['cas:isStudent'] == 'Y':
    #     # print('registering user and redirecting to homepage')
    #     flash('You are now registered with Agora!')
    #     uid_dic = queries.register_user(conn, email)
    #     uid = uid_dic['last_insert_id()']
    #     # print('new user uid: ', uid)
    #     session['uid'] = uid
    #     return redirect(url_for('home'))
    # else: 
    #     flash('You must be a Wellesley College student to use Agora.')
    #     return redirect(url_for('my_login'))
    else:
        flash('You are now registered with Agora!')
        uid_dic = queries.register_user(conn, email)
        uid = uid_dic['last_insert_id()']
        # print('new user uid: ', uid)
        session['uid'] = uid
        return redirect(url_for('home'))

@app.route('/my_logout/')
def my_logout():
    flash('You have been logged out.')
    session['uid'] = None
    return redirect(url_for('my_login'))


@app.route('/view/<postid>', methods=['GET'])
#view individual posts
def view_post(postid):
    conn = dbi.connect()
    #query 1 gets all post info, always include these in all posts
    postInfo = queries.get_post_info(conn, postid)
    user = postInfo['username']
    text = postInfo['text']
    time = postInfo['time']
    upvotes = postInfo['upvotes']
    downvotes = postInfo['downvotes']
    attachments = postInfo['attachments']

    #query 2, loads all comments for given post
    comments = queries.get_comments(conn,postid)

    #query 3, gets all course info
    courseInfo = queries.get_course_info(conn,postid)

    if courseInfo != None:
        course_code = courseInfo['code']
        course_name = courseInfo['title']
        course_rating = courseInfo['course_rating']
    else: 
        course_code = None
        course_name = None
        course_rating = None
    
    #query 4 gets all of the prof info 
    profInfo = queries.get_prof_info(conn,postid)
    
    if profInfo != None:
        prof_name = profInfo['name']
        prof_rating = profInfo['prof_rating']
    else:
        prof_name = None
        prof_rating = None
    
    #if there is no professor 
    if prof_name == None:
        return render_template('view-post-course.html', postid=postid, 
        user=user, course_name=course_name, 
        course_code=course_code, course_rating=course_rating, text=text,
        time=time, comments=comments, upvotes=upvotes, downvotes=downvotes,
        filepath=attachments)
    #if there is no course
    elif course_code == None:
        return render_template('view-post-prof.html', postid=postid, 
        user=user, prof_name=prof_name, prof_rating=prof_rating, text=text,
        time=time, comments=comments, upvotes=upvotes, downvotes=downvotes,
        filepath=attachments)
    #if there is a prof and a course
    else:
        return render_template('view-post-prof-course.html', postid=postid,
        user=user, course_name=course_name, course_code=course_code,
        course_rating=course_rating, prof_name=prof_name, 
        prof_rating=prof_rating, text=text, time=time, comments=comments, 
        upvotes=upvotes, downvotes=downvotes,filepath=attachments) 


@app.route('/vote-post/<postid>/<vote>', methods=['GET', 'POST'])
#do in the query to make thread safe, same with downvotes ( makes sure there's no duplicate id's check for this in query)
def post_vote(postid,vote):
    conn = dbi.connect()
    queries.update_post_votes(conn,postid,vote)
    return redirect(url_for('home'))


@app.route('/comment/<postid>', methods=['GET', 'POST'])
def comment(postid):
    if not session.get('uid'):
        return redirect(url_for('my_login'))
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('comment-form.html', postid=postid)

    else : # request.method == 'POST'
        #retrieve information
        uid = session.get('uid')
        print('uid in comment fxn: ',uid)
        upvotes = 0
        downvotes = 0
        username = queries.username_from_uid(conn, uid)['username']
        time = datetime.now()
        text = request.form['comment-text']

        # upload file
        f = request.files['pdf']
        # if a file was submitted and it is a PDF
        if f and helper.allowed_file(f.filename, ALLOWED_EXTENSIONS):
            try:
                user_filename = f.filename
                # make file name the uid plus the input file name
                filename = secure_filename('{}'.format(user_filename))
                print('filename: ',filename)
                queries.add_file(conn, uid, filename)
                print('file added to database')
                filename = queries.add_file(conn, uid, filename)
                filename = filename['filepath']
                pathname = os.path.join(app.config['UPLOADS'],filename)
                print('pathname: ',pathname)
                f.save(pathname)
                # print('file added')
            
            except Exception as err:
                flash('File upload failed {why}'.format(why=err))
                return render_template('comment-form.html', postid=postid)
        # if a file was submitted and it is not a PDF
        elif f and not helper.allowed_file(f.filename):
            flash('File attachment must be a PDF')
            return render_template('comment-form.html', postid=postid)
        else:
            filename = None

         # check if essential information is present (text)
        if text == "":
            flash('Please provide content for your comment.')
            return render_template('comment-form.html', postid=postid)
        # upload comment
        else:
            commentid = queries.add_comment(conn, postid, time, uid, text, 
            filename, upvotes, downvotes, username)
            flash('Comment upload successful')
            # go to post page
            return redirect(url_for('view_post', postid=postid))


@app.route('/vote-comment/<postid>/<commentid>/<vote>', methods=['GET', 'POST'])
#do in the query to make thread safe, same with downvotes ( makes sure there's no duplicate id's check for this in query)
def comment_vote(postid,commentid,vote):
    conn = dbi.connect()
    queries.update_comment_votes(conn,commentid,vote)
    return redirect(url_for('view_post', postid=postid))

        
@app.route('/upload/', methods=['GET','POST'])
def upload():
    if not session.get('uid'):
        return redirect(url_for('my_login'))
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
        username = queries.username_from_uid(conn, uid)['username']
        time = datetime.now()
        dept = request.form['dept']
        profid = request.form['pid']
        courseid = request.form['course']
        prof_rating = request.form['prof-rating']
        course_rating = request.form['course-rating']
        review_text = request.form['review-text']
        upvotes = 0
        downvotes = 0

        # upload file
        f = request.files['pdf']
        # if a file was submitted and it is a PDF
        if f and helper.allowed_file(f.filename, ALLOWED_EXTENSIONS):
            try:
                user_filename = f.filename
                # make file name the uid plus the input file name
                filename = secure_filename('{}'.format(user_filename))
                print('filename: ',filename)
                queries.add_file(conn, uid, filename)
                print('file added to database')
                filename = queries.add_file(conn, uid, filename)
                filename = filename['filepath']
                pathname = os.path.join(app.config['UPLOADS'],filename)
                print('pathname: ',pathname)
                f.save(pathname)
                # print('file added')
            
            except Exception as err:
                flash('File upload failed {why}'.format(why=err))
                return render_template('post-form.html', title='Create a Post',
                                        professors = professors, 
                                        courses = courses,
                                        departments = departments)
        # if a file was submitted and it is not a PDF
        elif f and not helper.allowed_file(f.filename):
            flash('File attachment must be a PDF')
            return render_template('post-form.html', title='Create a Post',
                                    professors = professors, courses = courses,
                                    departments = departments)
        else:
            filename = None

        # check if essential information is present
        if dept == "":
            flash('Please choose a department')
            return render_template('post-form.html', title='Create a Post',
            professors = professors, courses = courses, 
            departments = departments)
        if profid == "" and courseid == "":
            flash('Please enter a Professor and/or Course.')
            return render_template('post-form.html', title='Create a Post',
            professors = professors, courses = courses, 
            departments = departments)
        elif profid == "" and prof_rating != "":
            flash('Please provide a Professor to rate or remove the \
                    Professor Rating.')
            return render_template('post-form.html', title='Create a Post',
            professors = professors, courses = courses, 
            departments = departments)
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
            postid = queries.add_course_post(conn, time, uid, courseid, 
            course_rating, review_text, filename, username, upvotes, 
            downvotes)['last_insert_id()']
        elif courseid == '':
            postid = queries.add_prof_post(conn, time, uid, profid, prof_rating
            , review_text, filename, username, upvotes, 
            downvotes)['last_insert_id()']
        else:
            postid = queries.add_post(conn, time, uid, courseid, profid, 
            prof_rating, course_rating, review_text, filename, username, 
            upvotes, downvotes)['last_insert_id()']

        flash('Upload successful')
        # go to post page
        return redirect(url_for('view_post', postid=postid))

@app.route('/view-file/<path:filepath>')
def view_file(filepath):
    if not session.get('uid'):
        return redirect(url_for('my_login'))
    return send_from_directory(app.config['UPLOADS'], filepath)

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
        html_string1 += '<option value="{}">{}</option>'.format(
            professor['pid'], professor['name'])

    html_string2 = '<option value="">Choose One</option>'
    for course in courses:
        html_string2 += '<option value="{}">{}:{}</option>'.format(
            course['courseid'], course['code'], course['title'])

    return jsonify(html_string1=html_string1, html_string2=html_string2)

@app.route('/<department>')
def department(department):
    if not session.get('uid'):
        return redirect(url_for('my_login'))
    conn = dbi.connect()
    if request.method == 'GET':
        dept_name = queries.find_dept_name(conn, department)
        departments = queries.find_depts(conn)
        professors = {}
        courses = {}
        posts = queries.get_dept_post_allinfo(conn, department)
        return render_template('department.html',page_title='Department Page', 
        departments = departments, courses = courses, 
        professors = professors, posts = posts, 
        #returning NoneType but still works
        name=dept_name['name'])
    if request.method == 'POST':
        return helper.postFilterForm(conn, request.form)

@app.route('/professor/<department>/<professor>')
def professor(department, professor):
    if not session.get('uid'):
        return redirect(url_for('my_login'))
    conn = dbi.connect()
    if request.method == 'GET':
        name = queries.find_prof_name(conn,professor)
        departments = queries.find_depts(conn)
        professors = {}
        courses = {}
        rating = queries.find_prof_avgrating(conn, professor)
        posts = queries.get_prof_post_allinfo(conn, professor)
        return render_template('professor.html', 
        departments = departments, courses = courses, 
        professors = professors, posts = posts, avg_rating=rating,
        #returning NoneType but still works
        prof_name=name['name'])
    if request.method == 'POST':
        return helper.postFilterForm(conn, request.form)

@app.route('/course/<department>/<course>')
def course(department, course):
    if not session.get('uid'):
        return redirect(url_for('my_login'))
    conn = dbi.connect()
    if request.method == 'GET':
        course_info = queries.find_course_info(conn,course)
        departments = queries.find_depts(conn)
        professors = {}
        courses = {}
        rating = queries.find_course_avgrating(conn, course)
        posts = queries.get_course_post_allinfo(conn, course)
        return render_template('course.html', code=course_info['code'], course=
        course_info['title'], avg_rating=rating,
        departments = departments, courses = courses, 
        professors = professors, posts = posts)
    if request.method == 'POST':
        return helper.postFilterForm(conn, request.form)

@app.route('/course-section/<department>/<professor>/<course>')
def course_section(department, professor, course):
    if not session.get('uid'):
        return redirect(url_for('my_login'))
    conn = dbi.connect()
    if request.method == 'GET':
        course_info = queries.find_course_info(conn,course)
        prof_info = queries.find_prof_name(conn,professor)
        departments = queries.find_depts(conn)
        professors = {}
        courses = {}
        posts = queries.get_section_post_allinfo(conn, course, professor)
        return render_template('course-section.html', code=course_info['code'], 
        course=course_info['title'], departments = departments, 
        courses = courses, professors = professors, posts=posts, 
        prof=prof_info['name'])
    if request.method == 'POST':
        return helper.postFilterForm(conn, request.form)

@app.route('/change-username', methods=['GET','POST'])
def change_username():
    if not session.get('uid'):
        return redirect(url_for('my_login'))
    conn = dbi.connect()
    #get uid
    uid = session.get('uid')
    #get new name
    new_name = helper.random_username(usernames_dict)
    #check if name exist
    check = queries.check_username(conn, new_name)
    #if not none, the name exists, try again until you get a free name
    while check != None:
        new_name = helper.random_username(usernames_dict)
        check = queries.check_username(conn, new_name)
    queries.update_username(conn, uid, new_name)

    flash('Your new username is {}.'.format(new_name))
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

#code unnecessary with current tagging system, needed if prof-course relation
#  enforced
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
#         html_string1 += '<option value="{}">{}</option>'.format(
#           professor['pid'], professor['name'])

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
#         html_string2 += '<option value="{}">{}:{}</option>'.format(
#           course['courseid'], course['code'], course['title'])

#     return jsonify(html_string2=html_string2)