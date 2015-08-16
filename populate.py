myfile = open('mywords.txt')
mystr = myfile.read()
mywords = mystr.split(' ')
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordify.settings')

import django
django.setup()

from words.models import Word


def populate():
    for x in mywords:
        add_word(x)
    # Print out what we have added to the user.

def add_word(word):
    wordd, added = Word.objects.get_or_create(word=word)
    if added:
        print (wordd, "was successfully added")
    else:
        print(wordd, "already exists.")

# Start execution here!
if __name__ == '__main__':
    print "Starting words population script..."
    populate()