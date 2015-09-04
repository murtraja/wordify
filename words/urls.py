from django.conf.urls import patterns, url
from words import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^register/$', views.register, name = 'register'),
        url(r'^login/$', views.user_login, name = 'login'),
        url(r'^logout/$', views.user_logout, name = 'logout'),
        url(r'^start/$', views.start_session, name = 'startsession'),
        url(r'^nextword/$', views.start, name = 'start'),
        url(r'^result/$', views.result, name = 'result'),
        url(r'^test_audio/$', views.test_audio, name='test_audio'),
        url(r'^group/$', views.group, name = 'group'),
        url(r'^ganswer_post/$', views.ganswer_post, name = 'ganswer_post'),
        url(r'^gconnect_post/$', views.gconnect_post, name = 'gconnect_post'),
        url(r'^test_publish/$', views.test_publish, name = 'test_publish')
        )