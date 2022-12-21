import random 


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
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in extensions