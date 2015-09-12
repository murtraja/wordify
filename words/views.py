from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, render_to_response
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import serializers
from datetime import datetime
from datetime import timedelta
import urllib2, hashlib

from words.forms import UserForm , UserProfileForm
from words.models import Word,GroupFinalResult,GroupResultTable,FinalResult,ResultTable,User

from django.views.decorators.csrf import csrf_exempt

from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage

from redis import StrictRedis

import json

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
def single_player(request):
    return render (request, 'words/single_player.html', {})


@login_required
@csrf_exempt
def start_single(request):
    totwords = request.POST.get('totwords', -1)
    totwords = int(totwords)
    if totwords == -1:
        #return error
        return HttpResponse('Error! total words not posted');
    if not request.session.get('wordpks'):
        wordpks = random.sample([x for x in range(1,31)], totwords)
        request.session['wordpks']= '-'.join([str(x) for x in wordpks])
        request.session['ci']= 0
        print ("now initializing:",request.session)
        obj=FinalResult.objects.filter(re_user=request.user).order_by('-session_id')[:1]
        print "ethe"
        #print "sessionid"+str(obj[0].session_id)
        if(not obj):
            obj=FinalResult(re_user=request.user,session_id=1,marks=0,starttime=datetime.now(),endtime=datetime.now()+timedelta(minutes=5))
            obj.save()
        else:
            obj1=FinalResult(re_user=request.user,session_id=(obj[0].session_id+1),starttime=datetime.now(),marks=0,endtime=datetime.now()+timedelta(minutes=5))
            obj1.save()   #current session
            #print "kela"
    return render(request, 'words/start.html/', {})

@csrf_exempt
def sanswer_post(request):
    print "in the start"
    response_dict = {'done':False, 'next':'404'}
    wordpks = request.session.get('wordpks')
    usr=request.user        #username
    #print "username "+usr.username
    if wordpks:
        wordpks = wordpks.split('-')
        print str(wordpks)
        ci = int(request.session.get('ci'))


        #print ("nextword:",nextword)

    if request.method== 'POST':
        post_dict = request.POST
        #print ("post_dict:",post_dict)
        #print("inputWord",request.POST['inputWord'])
        cindex1=str(wordpks[ci-1])
        print "cindex "+cindex1
        correct_word=str(Word.objects.get(pk=cindex1))
        print "correct_word "+str(correct_word)
        input_word=request.POST['inputWord']
        print "input_word "+input_word
        print "ci "+str(ci)
        if str(correct_word)==str(input_word):
            mark=1
            sc1=FinalResult.objects.filter(re_user=request.user).order_by('-session_id')[:1]
            sc=sc1[0]
            sc.marks+=1
            sc.save()
            print sc.marks
        else:
            mark=0
        print "marks"+str(mark)
        #new
        obj=FinalResult.objects.filter(re_user=request.user).order_by('-session_id')[:1]  #to find current session
        newobj1=ResultTable(re_user=usr,session_id=obj[0].session_id,correct_ans=correct_word,ans=input_word,marks=mark)
        newobj1.save()

        #newobj=TestResult(re_user=usr,cindex=cindex1,correct_ans=correct_word,ans=input_word,marks=mark)
       # newobj.save()
        if ci>=(len(wordpks)):
            response_dict['done']=True
            response_dict['next']=reverse('result_single')

            #print("received word:",request.POST['inputWord'])
            del request.session['ci']
            del request.session['wordpks']
            return JsonResponse(response_dict)
        nextword = wordpks[ci]          #cindex
        nextword = str(Word.objects.get(pk=nextword))        #correct_word
        request.session['ci']= ci+1
    else:
        #get request => first word!
        nextword = wordpks[ci]          #cindex
        nextword = str(Word.objects.get(pk=nextword))        #correct_word
        request.session['ci']= ci+1
        #response_dict['next']='/static/audio/w'+hashlib.sha1(nextword).hexdigest()+'.mp3'
        print ("serving get request for 1st word")

    response_dict['next']=get_url_from_word(nextword)
    print("now sending json as",response_dict)
    return JsonResponse(response_dict)

@login_required
def result_single(request):
    fr_obj=FinalResult.objects.filter(re_user = request.user).order_by('-session_id')
    print "sliced version:",fr_obj[:1]
    print "simply adding [0]:",fr_obj[0]
    fr_obj = fr_obj[0]
    rt_obj = ResultTable.objects.filter(session_id = fr_obj.session_id, re_user = request.user)
    print "rt obj",rt_obj
    response_dict = {'data':[]}
    for obj in rt_obj:
        response_dict['data'].append([obj.correct_ans, obj.ans, obj.marks])
    print "response_dict for single_player",response_dict
    # return JsonResponse(response_dict)
    return render_to_response('words/single_result.html',{'jsondata':json.dumps(response_dict)})


@login_required
def result_group(request):
    # groupname = request.session.get('groupname',False)
    # if not groupname:
    #     return HttpResponse('error! groupname not found')
    groupname = 'groupname3'
    gfr_objs = GroupFinalResult.objects.filter(groupname = groupname)
    # get all the entries having the grouname, probably need to sort it too, if there are multiple
    # entries with same group names!
    print "printing gfr:",gfr_objs
    grt_objs = [GroupResultTable.objects.filter(usertest = gfr_obj) for gfr_obj in gfr_objs]
    print "printing grt:",grt_objs
    response_dict = {'data':[]}
    for users in grt_objs:
        answer_dict = {'user':users[0].usertest.re_user.username, 'ans':[]}
        for answer in users:
            answer_dict['ans'].append( [answer.correct_ans,answer.ans, answer.marks])
        response_dict['data'].append(answer_dict)
        print "response_dict:",response_dict
    print ""
    print "printing response_dict for",request.user,":",response_dict
    #return JsonResponse(response_dict)
    return render(request, 'words/group_result.html', {'jsondata':json.dumps(response_dict)})

def test_audio(request):
    word = str(Word.objects.get(pk=random.randint(1,len(Word.objects.all()))))
    path = 'audio/w'+hashlib.sha1(word).hexdigest()+'.mp3' 
    #path='audio/test.mp3'
    return render(request, 'words/testaudio.html', {'src':path, 'wrd':word})

def test_publish(request):
    pref = settings.MY_PREFIX
    redis_publisher = RedisPublisher(facility = pref, broadcast = True)
    message = RedisMessage(json.dumps({'type':'test', 'message':'this is a test message from server to everyone!'}))
    redis_publisher.publish_message(message)
    if request.GET.get('facility', None):
        redis_publisher = RedisPublisher(facility = request.GET['facility'], broadcast = True)
        redis_publisher.publish_message(RedisMessage('this is a test message from server to group!'))
    return HttpResponse('OK')

@login_required
def group(request):
    print(str(request.user)+' requested the group url')
    # should i publish a message here stating that this user is connected?
    return render(request, 'words/group.html', {})

def ginfo(request):
    print(str(request.user)+' requested groupinfo')
    rd = StrictRedis()
    pref = settings.MY_PREFIX
    groupinfo = []
    response = {}
    if rd.exists(pref+":groups"):
        # there is atleast 1 group already created
        groupnames = rd.smembers(pref+":groups")
        # groupnames is a set
        for groupname in groupnames:
            groupdict = rd.hgetall(pref+":"+groupname+":hash")
            groupinfo.append(groupdict)
            #print groupdict
        # time to serialize!
        response['group_list'] = groupinfo
    response.update( {"success":True, "group_count":len(groupinfo)})
    #print response
    return JsonResponse(response)

@csrf_exempt
def ganswer_post(request):
    '''
    i am assuming that the above condition noofusers==totusers would have already initialized
    the wordpks in redis for the first time, so you get that and put it in the user session after updating it!
    remove the first pk from the wordpks and update wordpks in user session to wordpks[1:]
    continue till wordpks is empty which will signify that all the words have been given to user
    '''
    username = str(request.user)
    print "inside ganswer_post for user:"+username
    pref = settings.MY_PREFIX
    facility = request.POST.get('facility')
    prefg = pref+":"+facility
    response_dict = {'done':False}
    
    wordpks = request.session.get('wordpks', 0)
    print 'initial value of wordpks:',wordpks

    if wordpks == 0:
        # just adds wordpks,totwords to user session
        print "wordpks not in session!"
        rd = StrictRedis()
        d = rd.hgetall(prefg+":hash")
        # store this dictionary in the session first
        # there is no need to do that!
        # request.session['hash'] = d
        # print "stored the hash dictionary in session"
        # print "wordpks: ",request.session['hash']['wordpks']
        wordpks = d['wordpks']


        # our first word, there won't be any user input here!
        wordpks = wordpks.split('-')
        request.session['totwords'] = len(wordpks)
        print "wordpks:"+str(wordpks)
        print 'now removing',request.user,'from pref:groupname'
        print rd.keys(pref+"*")
        print 'cardinality changed from',rd.scard(prefg),'to',
        rd.srem(prefg, str(request.user))
        print rd.scard(prefg)
        if rd.scard(prefg) == 0:
            # delete this key and hash
            print "now deleting the group hash"
            rd.delete(prefg)
            rd.delete(prefg+":hash")
            print rd.keys(pref+"*")
    else:
        # get user_input and send message that user gave the answer
        print "wordpks in session"
        print "wordpks:"+wordpks
        #take and store the user input here
        msgword = "the user "+username+' entered the word '+request.POST.get('input_word')
        print msgword
        if not (wordpks == [] or wordpks == ['']):
            #print "adhicha word"
            correct_ans=request.session.get('prev_word').strip()
            ans=request.POST.get('input_word').strip()
            if(str(correct_ans)==str(ans)):
                print "correct"
                marks=1
            else:
                print "wrong"
                marks=0
            obj1=GroupFinalResult.objects.filter(re_user=request.user).order_by('-starttime')[:1]
            currentobj=obj1[0]
            #print str(currentobj.starttime)
            print str(request.session.get('prev_word'))
            print str(request.POST.get('input_word'))
            ans=request.POST.get('input_word')
            currentobj.marks+=marks
            currentobj.save()
            print str(currentobj.marks)
            obj2=GroupResultTable(usertest=currentobj,correct_ans=correct_ans,ans=ans,marks=marks)   #to store result of each word
            obj2.save()
            print "zala"+str(obj2.marks)

        # calculate the question no. for which this answer was received
        x = int(request.session['totwords'])
        wordpks = wordpks.split('-')
        print 'now splitting wordpks...'
        print wordpks
        lenwordpks = 0 if wordpks == [''] else len(wordpks)
        currentqno = x - lenwordpks
        # currentqno != 0 because lenwordpks < x always in this else block
        # and it is equal in the if block above this else block
        # let's publish this message, shall we?
        redis_publisher = RedisPublisher(facility = facility, broadcast = True)
        # TODO make this json for consistency
        msgword = username+", gave the answer for question no. "+str(currentqno);
        message = RedisMessage(msgword)
        redis_publisher.publish_message(message)

    if wordpks == [] or wordpks == ['']:
        print "wordpks is empty"
        # no more words to dispatch redirect to result page
        # delete the session variables here
        del request.session['wordpks']
        del request.session['totwords']
        # del request.session['hash']
        '''
            so the thing is that we should display the results only 
            if all the users have finished playing, otherwise, we won't
            have data to put in the charts. therefore, whenever a user reaches this
            block, we check:
                if there are more users yet to reach this block then
                    store this user's name somewhere
                else this user is the last to finish, then
                    inform to all the users that results are ready to be dispatched
        '''
        rd = StrictRedis()
        # remove this user from the set
        print "now removing",str(request.user),"from prefg:members"
        print 'cardinality changed from',rd.scard(prefg+":members"),'to',
        rd.srem(prefg+":members", str(request.user))
        print rd.scard(prefg+":members")
        if rd.scard(prefg+":members") == 0:
            # all the users have completed the competition, time to display the results!
            print 'all users done before'
            print rd.keys(pref+"*")
            print "all the users have finished the competition"
            rd.delete(prefg+":members");
            print rd.keys(pref+"*")
            redis_publisher = RedisPublisher(facility = facility, broadcast = True)
            redis_publisher.publish_message(RedisMessage("#end"))
        request.session['groupname'] = facility
        response_dict['done'] = True
        response_dict['next'] = reverse('result')
        return JsonResponse(response_dict)

    # dispatch the next word
    print "now changing wordpks from "+str(wordpks)+" to ",
    nextpk = wordpks[0]
    print wordpks[0]
    an=wordpks[0]
    wrd=Word.objects.get(pk=an)
    print "current word"
    print wrd.word          #correct words
    correct_ans=wrd.word
    request.session['prev_word']=correct_ans #to store current word
    ans=request.POST.get('input_word')
    print ans
    wordpks = wordpks[1:]
    print wordpks
    request.session['wordpks'] = '-'.join(wordpks)
    wordurl = get_url_from_word(str(Word.objects.get(pk=nextpk)))
    response_dict['next'] = wordurl
    return JsonResponse(response_dict)





'''
whenever a new group is created pref:groupname will contain a list of members
currently in that group, this will be a set

pref:groupname:hash totwords will contain the total no. of words

pref:groupname:hash totmembers will contain the total no. of members

pref:groupname:hash owner will contain the username who created this group

pref:groupname:hash curmembers will contain current count of members in the group

pref:groups will be a set containing all groups that are there VERY IMPORTANT

'''
@login_required
@csrf_exempt
def new_group(request):
    groupname = request.POST.get("groupname")
    totwords = request.POST.get("totwords")
    totmembers = request.POST.get('totmembers')
    pref = settings.MY_PREFIX
    prefg = pref+":"+groupname
    user = str(request.user)
    rd = StrictRedis()
    # the above statements are self explanatory

    exists = rd.exists(pref+":"+groupname)
    if exists:
        # return error, can't create the group with that name
        # don't do that, just add this user to the already existing group
        # if group size < totmembers
        d = rd.hgetall(prefg+":hash")
        response = {'facility':""}
        if int(d['totmembers'])>int(d['curmembers']):
            rd.hincrby(prefg+":hash", 'curmembers')
            #d = rd.hgetall(prefg+":hash")
            response['facility'] = groupname
            response['new_group_created'] = False
            rd.sadd(prefg, user)
            #now notify the others that this user joined the group!
            redis_publisher = RedisPublisher(facility = pref, broadcast = True)
            mydict = {"type":"new_join", 'who':user, 'name':groupname}
            
            msgstring = json.dumps(mydict)
            print "broadcast message:"+msgstring
            message = RedisMessage(msgstring)
            redis_publisher.publish_message(message)
            
            # now check if the competition is ready to start
            if int(d['totmembers'])-1 == int(d['curmembers']):
                start_competition(request,groupname)

        return JsonResponse(response)

    # so the group doesn't exist
    rd.sadd(prefg, user)
    # add this user to the set of all the users that are part of this group

    hashdict = {'totwords':totwords, 'totmembers':totmembers, "owner":user, "name":groupname, 'curmembers':1}
    # adding group name is redundant but it simplifies things a lot
    rd.hmset(prefg+":hash", hashdict)
    # using hash greatly simplifies the things(dict interconversion hgetall()), though i feel that the
    # naming convention used is horrible
    
    redis_publisher = RedisPublisher(facility = pref, broadcast = True)
    mydict = {"type":"new_group"}
    mydict.update(hashdict)
    msgstring = json.dumps(mydict)
    print msgstring
    message = RedisMessage(msgstring)
    redis_publisher.publish_message(message)
    # notify the others about this new group that was created

    rd.sadd(pref+":groups", groupname)
    return JsonResponse({'facility':groupname, 'new_group_created':True})

def start_competition(request,groupname):
    # prepare the game
    # now set the questions here!
    '''
    ok so the new idea is to delete the group entry
    so that the ginfo won't come to know about this 
    group, so that means every thing related to the
    group will be deleted, after storing it to the database
    so the set element in pref:groups need to be deleted
    then pref:groupname:hash needs to be deleted
    but pref:groupname:wordpks need to be added, with
    a expire timeout of say 5 seconds, though it is too much
    chuck that, how about setting the expire timeout here
    and then copy every property of hash ...
    actually only pref:groups entry has to be deleted because
    using this set, ginfo accesses the hash.
    lets set the time out here for the hash
    and also broadcast this to inform that a group was deleted
    maybe settings message.type == 'group_delete'
    '''
    print "starting the competition for "+groupname
    print 'the following keys are there'
    rd = StrictRedis()
    pref = settings.MY_PREFIX
    prefg = pref+":"+groupname
    d = rd.hgetall(prefg+":hash")
    print rd.keys(pref+'*')
    print "changing from ",d
    totwords = int(d['totwords'])
    wordpks = random.sample([x for x in range(1,31)], totwords)
    wordpks = '-'.join([str(x) for x in wordpks])
    rd.hset(prefg+":hash", 'wordpks', wordpks)
    print "to",rd.hgetall(prefg+":hash")
    redis_publisher = RedisPublisher(facility = groupname, broadcast = True)
    message = RedisMessage('#start')
    redis_publisher.publish_message(message)
    print "published the #start"
    # rd.expire(prefg+":hash", extime)         # get rid of the group details after extime seconds
    # rd.expire(pref+":"+groupname, extime)   # don't require the usernames in that group also
    '''
    don't do the expire here, do it in ganswer_post:
    whenever user requests the wordpks, it removes its username from pref:groupname. 
    so check if llen('pref:groupname) is one then remove both, hash and this set
    this way we will be sure that only delete when every user has transferred wordpks from redis to session
    '''
    rd.srem(pref+":groups", groupname)  # prevent this group from showing up in the ginfo
    # to be on the safer side, should i create a new key storing wordpks? prefg:wordpks?

    group_members = rd.smembers(prefg)
    rd.sadd(prefg+":members", *group_members)
    rd.sadd(prefg+":gmembers", *group_members)
    rd.expire(prefg+":gmembers", 500)
    # create a new key containing all the members of this group
    # in pref:groupname:members this key will be helpful in checking
    # how many users have completed the competition, on similar lines
    # pref:groupname key will be responsible in providing the condition
    # as to when the pref:groupname:hash need to be deleted!
    # also copying to gmembers so that i know whose results are to be delivered in result_group
    # but only for 5 minutes you can view your previous group results, restricted, right? i know
    # the idea is to make a generic view which returns all the information, pretty much like
    # the admin interface app but providing interactive charts rather than pure data to see
    print "copied the group_members",group_members
    redis_publisher = RedisPublisher(facility = pref, broadcast = True)
    delete_group_msg = json.dumps({'type':'group_busy', 'name':groupname})
    redis_publisher.publish_message(RedisMessage(delete_group_msg))
    sttime=datetime.now()
    usrs=rd.smembers(prefg)
    print "for",groupname,"members are",usrs
    for i in usrs:
        obj=GroupFinalResult(re_user=User.objects.get(username=i),groupname=groupname,marks=0,starttime=sttime,endtime=sttime)
        obj.save()

    print 'leaving start competition...'
    print rd.keys(pref+"*")

@login_required
@csrf_exempt
def gdelete(request):
    groupname = request.POST.get('name', 0);
    rd = StrictRedis()
    pref = settings.MY_PREFIX
    prefg = pref+":"+groupname
    user = str(request.user)
    print "received request for deleting",groupname,"from",user
    ismember = rd.sismember(pref+":groups",groupname)
    if not ismember:
        return JsonResponse({'done':False,'reason':'No such group name'});
    # now check whether the requesting user is the one who created the group
    d = rd.hgetall(prefg+":hash")
    if d['owner'] != user:
        return JsonResponse({'done':False, 'reason':'Only group owner can delete the group'})
    rd.srem(pref+":groups", groupname)
    rd.delete(prefg+":hash", pref+":"+groupname)
    rd.delete(pref+":"+groupname)
    redis_publisher = RedisPublisher(facility = pref, broadcast = True)
    redis_publisher.publish_message(RedisMessage(json.dumps({"type":"group_delete", "name":groupname})))
    return JsonResponse({'done':True})

def delete_all_keys(request):
    rd = StrictRedis()
    print "now deleting keys"
    pref = settings.MY_PREFIX
    mydict = rd.keys(pref+"*")
    mydict = mydict + rd.keys('ws:broadcast*')
    for k in mydict:
        resp  = rd.delete(k)
        print "deleted:",k
    return HttpResponse("check terminal to see what keys were deleted<br><a href = '"+reverse('group')+"'>go back</a>")