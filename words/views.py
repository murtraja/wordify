from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render

import urllib2

from words.forms import UserForm , UserProfileForm
from words.models import Word

import random

def get_url_from_word(word):
    page = urllib2.urlopen('http://tts-api.com/tts.mp3?q='+word+'&return_url=1')
    goturl = page.read()
    print ("|"+goturl+"|")
    return goturl
    
# Create your views here.
def index(request):
#     request.session.set_test_cookie()
    context_dict = {"words":'-'.join([x.__str__() for x in Word.objects.all()])}
    return render(request, 'words/index.html', context_dict)

def register(request):
    registration_status = False
    '''
    if request.session.test_cookie_worked():
        print("-----------Worked---------")
        request.session.delete_test_cookie()
    '''
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
            return HttpResponse("invalid login details suppplied. try again1")
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
def start(request):
    print "in the start"
    response_dict = {'done':False, 'next':'404'}
    if request.method== 'GET':
        wordpks = request.session.get('wordpks')
        if wordpks:
            wordpks = wordpks.split('-')
            
            ci = int(request.session.get('ci'))
            if ci>=len(wordpks):
                response_dict['done']=True
                response_dict['next']='/words/result'
                return JsonResponse(response_dict)
            nextword = wordpks[ci]
            nextword = str(Word.objects.get(pk=nextword))
            request.session['ci']= ci+1
            print nextword
            response_dict['next']=get_url_from_word(nextword)
    print("now sending json as",response_dict)
    return JsonResponse(response_dict)
def result(request):
    return HttpResponse("well done!")
    