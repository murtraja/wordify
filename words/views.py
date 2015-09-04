from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.core.urlresolvers import reverse

import urllib2, hashlib

from words.forms import UserForm , UserProfileForm
from words.models import Word

from django.views.decorators.csrf import csrf_exempt

from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage

import redis

import random

def get_url_from_word(word):
    print("now querying for word: "+word)
    goturl = settings.AUDIO_URL+'w'+hashlib.sha1(word).hexdigest()+'.mp3'
    #print ("|"+goturl+"|")
    return goturl
    
# Create your views here.
def index(request):
#     request.session.set_test_cookie()
    context_dict = {"words":'-'.join([x.__str__() for x in Word.objects.all()])}
    return render(request, 'words/index.html', context_dict)

def register(request):
    registration_status = False
    if request.method == 'POST':
        # time to process the data!
        print ("request.Post", request.POST)
        user_form = UserForm(data = request.POST)
        profile_form=UserProfileForm(data=request.POST)
        print (user_form)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            
            profile = profile_form.save(commit = False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
                
            profile.save()
            registration_status = True
        else:
            print (user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    return render(request,
                  'words/register.html',
                  {'user_form':user_form, 'profile_form':profile_form, 'registration_status':registration_status})
    
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print (username, password)
        user = authenticate(username = username, password= password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/words/')
            else:
                return HttpResponse("Your wordify account is disabled!")
        else:
            print("Invalid login credentials:", username, password)
            return HttpResponse("invalid login details suppplied. try again!")
    else:
        return render(request, 'words/login.html',{})
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/words/")

@login_required
def start_session(request):
    #let 5 words be given first!
    if not request.session.get('wordpks'):
        wordpks = random.sample([x for x in range(1,31)], 5)
        request.session['wordpks']= '-'.join([str(x) for x in wordpks])
        request.session['ci']= 0
        print ("now initializing:",request.session)
    return render(request, 'words/start.html/', {})
@csrf_exempt
def start(request):
    print "in the start"
    response_dict = {'done':False, 'next':'404'}
    wordpks = request.session.get('wordpks')
    if wordpks:
        wordpks = wordpks.split('-')
        
        ci = int(request.session.get('ci'))
        if ci>=len(wordpks):
            response_dict['done']=True
            response_dict['next']='/words/result'
            print("received word:",request.POST['inputWord'])
            del request.session['ci']
            del request.session['wordpks']
            return JsonResponse(response_dict)
        nextword = wordpks[ci]
        nextword = str(Word.objects.get(pk=nextword))
        request.session['ci']= ci+1
        print ("nextword:",nextword)
        response_dict['next']=get_url_from_word(nextword)
    if request.method== 'POST':
        post_dict = request.POST
        print ("post_dict:",post_dict)
        print("inputWord",request.POST['inputWord'])
    else:
        #get request => first word!
        print ("serving get request for 1st word")
    print("now sending json as",response_dict)
    return JsonResponse(response_dict)
def result(request):
    return HttpResponse("well done!")
def test_audio(request):
    word = str(Word.objects.get(pk=random.randint(1,len(Word.objects.all()))))
    path = 'audio/w'+hashlib.sha1(word).hexdigest()+'.mp3' 
    #path='audio/test.mp3'
    return render(request, 'words/testaudio.html', {'src':path, 'wrd':word})

@login_required
def group(request):
    print(str(request.user)+' requested the group url')
    # should i publish a message here stating that this user is connected?
    return render(request, 'words/group.html', {})

@csrf_exempt
def gconnect_post(request):
    group = 'spellbee'
    totusers = 2
    redis_publisher = RedisPublisher(facility = 'wordify', groups  = group)
    user = str(request.user)
    msg = user+" connected successfully!"
    print msg
    message = RedisMessage(msg);
    redis_publisher.publish_message(message)
    # increment the user connected count here!
    rd = redis.StrictRedis()
    noofusers = rd.rpush(group+":"+'users', user )
    if(noofusers == totusers):
        #now send a magic string which will change the UI of browser into gaming display
        message = RedisMessage('#start')
        redis_publisher.publish_message(message)
        # now set the questions here!
        totwords = 5
        wordpks = random.sample([x for x in range(1,31)], totwords)
        queststring = '-'.join([str(x) for x in wordpks])
        rd.set(group+":wordpks", queststring)
        rd.set(group+":totwords", totwords)
    return HttpResponse('OK')

@csrf_exempt
def ganswer_post(request):
    '''
    i am assuming that the above condition noofusers==totusers would have already initialized
    the wordpks in redis for the first time, so you get that and put it in the user session after updating it!
    remove the first pk from the wordpks and update wordpks in user session to wordpks[1:]
    continue till wordpks is empty which will signify that all the words have been given to user
    '''
    group = 'spellbee'
    username = str(request.user)
    print "inside ganswer_post for user:"+username
    response_dict = {'done':False}
    totwords = redis.StrictRedis().get(group+":totwords")
    wordpks = request.session.get('wordpks', 0)
    print 'initial value of wordpks:',wordpks
    rd = redis.StrictRedis()
    if wordpks == 0:
        print "wordpks not in session!"
        wordpks = rd.get(group+":wordpks")
        # our first word, there won't be any user input here!
        wordpks = wordpks.split('-')
        print "wordpks:"+str(wordpks)
    else:
        print "wordpks in session"
        print "wordpks:"+wordpks
        #take and store the user input here
        msgword = "the user "+username+' entered the word '+request.POST.get('input_word')
        print msgword
        # calculate the question no. for which this answer was received
        x = int(rd.get(group+":totwords"))
        wordpks = wordpks.split('-')
        print 'now splitting wordpks...'
        print wordpks
        lenwordpks = 0 if wordpks == [''] else len(wordpks)
        currentqno = x - lenwordpks
        # currentqno != 0 because lenwordpks < x always in this else block
        # and it is equal in the if block above this else block
        # let's publish this message, shall we?
        redis_publisher = RedisPublisher(facility = 'wordify', groups = group)
        msgword = username+", gave the answer for question no. "+str(currentqno);
        message = RedisMessage(msgword)
        redis_publisher.publish_message(message)

    if wordpks == [] or wordpks == ['']:
        print "wordpks is empty"
        # no more words to dispatch redirect to result page
        # delete the session variables here
        del request.session['wordpks']
        response_dict['done'] = True
        response_dict['next'] = reverse('result')
        return JsonResponse(response_dict)

    print "now changing wordpks from "+str(wordpks)+" to ",
    nextpk = wordpks[0]
    wordpks = wordpks[1:]
    print wordpks
    request.session['wordpks'] = '-'.join(wordpks)
    wordurl = get_url_from_word(str(Word.objects.get(pk=nextpk)))
    response_dict['next'] = wordurl
    return JsonResponse(response_dict)


def test_publish(request):
    redis_publisher = RedisPublisher(facility = 'wordify', groups = 'spellbee')
    message = RedisMessage('this is a test message from server!')
    redis_publisher.publish_message(message)
    return HttpResponse('OK')

    
