from django.conf.urls import patterns, url
from words import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^register/$', views.register, name = 'register'),
        url(r'^login/$', views.user_login, name = 'login'),
        url(r'^logout/$', views.user_logout, name = 'logout'),
        # above urls are self-explanatory

        url(r'^single_player/$', views.single_player, name = 'single_player'),
        # to get the total words in practice session, can be extended to even select the data set

        url(r'^start_single/$', views.start_single, name = 'start_single'),
        # to generate the random words based on input received from single_player, i.e. set up the game parameters

        url(r'^sanswer_post/$', views.sanswer_post, name = 'sanswer_post'),
        # used to get the next word in the practice session and post the user input to database =AJAX=

        url(r'^result/$', views.result, name = 'result'),
        # to display results 

        url(r'^test_audio/$', views.test_audio, name='test_audio'),
        # for testing purposes only

        url(r'^new_group/$', views.new_group, name = 'new_group'),
        # create a new group or join a user to an existing group =AJAX=
        
        url(r'^ginfo/$', views.ginfo, name = 'ginfo'),
        # returns a JSON string which contains all the group information =AJAX=
        
        url(r'^group/$', views.group, name = 'group'),
        # brings up the group page, contains group joining/creation and gameplay elements

        url(r'^ganswer_post/$', views.ganswer_post, name = 'ganswer_post'),
        # gets the next word and posts the user input in the group gameplay

        url(r'^gdelete/$', views.gdelete, name = 'gdelete'),
        # deletes the posted group name =AJAX=

        url(r'^test_publish/$', views.test_publish, name = 'test_publish'),
        # for debugging purposes only

        url(r'^delete_all_keys/$', views.delete_all_keys, name = 'delete_all_keys')
        # very dangerous view, essentially deletes every key that was created except session keys 
        )