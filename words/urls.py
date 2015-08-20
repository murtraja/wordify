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
        )