import random 


def random_username():
    '''returns the random username '''
    adjective = get_random_word('static/common-adjectives.txt')
    animal = get_random_word('static/animals.txt')
    return adjective + animal


def get_random_word(file_name): 
    '''Returns a random word chosen from the file,
    the word will start with capital letter''' 

    file = open(file_name) 
    word_list = [] 
    #creates a list of all the read words from the file
    for line in file: 
        line = line.strip()
        word_list.append(line) 

    rand_index = random.randint(0, len(word_list) - 1) 
    word = word_list[rand_index].lower()
    return word.capitalize()