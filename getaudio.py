import urllib2
import os,sys
from words.models import Word
from django.conf import settings
import hashlib
import time
stpath = settings.STATIC_PATH+'/audio'

for i in range(1,len(Word.objects.all())+1):
    cword = Word.objects.get(pk=i)
    cword = str(cword)
    filename = 'w'+hashlib.sha1(cword).hexdigest()
    filepath = stpath+'/'+filename+'.mp3'
    print filepath
    if os.path.isfile(filepath):
        print 'the file is already present for word:', cword
        continue
    print 'file not present for word:',cword
    PATH = 'https://api.voicerss.org/?key=67e187e912934c98bd7d8012ebf26454&src='+cword+'&hl=en-gb&f=24khz_16bit_stereo'
    response = ''
    while True:
        print 'in the loop:',cword
        try:
            print 'trying to open url:',PATH
            response = urllib2.urlopen(PATH)
            print 'successful:', cword
            time.sleep(2)
            print 'successful sleep complete',cword
            break;
        except:
            print 'there was error:',cword
            time.sleep(2)
            print 'error sleep complete',cword
    print response
    audiocontents = response.read()
    newfile = open(filepath, 'wb')
    newfile.write(audiocontents)
    print 'written',newfile.tell(),'bytes'
    newfile.close()
    
# print html
# response = urllib2.urlopen(html);
# audiocontents = response.read()
# newfile.write(audiocontents)
# newfile.write(html)
# newfile.close()
