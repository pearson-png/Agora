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