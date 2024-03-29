import random 
import queries
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)

def random_username(dic):
    '''returns the random username '''
    if len(dic) == 0:
        dic['animal'] = read_txt('static/animals.txt')
        dic['adjective'] = read_txt('static/common-adjectives.txt')
    adjective = get_random_word(dic['adjective'])
    animal = get_random_word(dic['animal'])
    return str(adjective + animal)

def get_random_word(words): 
    '''Returns a random word chosen from the list,
    the word will start with capital letter''' 
    rand_index = random.randint(0, len(words) - 1) 
    word = words[rand_index].lower()
    return word.capitalize()

def read_txt(file_name):
    '''reads in text file of animals or adjectives'''
    file = open(file_name) 
    word_list = [] 
    #creates a list of all the read words from the file
    for line in file: 
        line = line.strip()
        word_list.append(line) 
    return word_list

def allowed_file(filename, extensions):
    '''Checks file extension allowed for upload'''
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in extensions


def postFilterForm(conn, requests):
    #redirects according to filter options to dept/prof/course route
    filters = requests
    dept = filters['department']
    prof = filters['professor']
    course = filters['course']
    search = filters['search']
    ##options here
    if dept == "0":
        if search != 'None':
            return redirect(url_for('search', department=dept, 
            query=search))
        #if no dept chosen, and no search entered, reload the homepage no 
        # matter other fields
        departments = queries.find_depts(conn)
        professors = {}
        courses = {}
        posts = queries.get_recent_post_allinfo(conn)
        flash("Please choose a department or fill in the search box")
        return render_template('home_page.html',title='Hello', 
        departments = departments, courses = courses, 
        professors = professors, posts = posts)
    elif prof == "0" and course == "0":
        if search != 'None':
            return redirect(url_for('search', department=dept, 
            query=search))
        #if only department chosen, direct to dept page
        return redirect(url_for('department', department=dept))
    elif course == "0" and prof != "0":
        #if only prof chosen, direct to prof page
        return redirect(url_for('professor', department=dept, 
        professor=prof))
    elif course != "0" and prof == "0":
        #if only course chosen, direct to course page
        return redirect(url_for('course', department=dept, course=course))
    else:
        #if all three were chosen, give specific prof and course page
        return redirect(url_for('course_section', department=dept,
        professor=prof, course=course))