from django.conf.urls import patterns, include, url

from django.contrib import admin

from lobby.views import *
from game.views import *

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^index/$', index),
    url(r'^allot/$', allot),
    url(r'^hall/$', hall),
    url(r'^host/$', host_room),
    url(r'^room/$', room),
    url(r'^enter/$', enter_room),
    url(r'^leave/$', leave_room),
    url(r'^change/$', change_room),
    url(r'^query/$', query),
    url(r'^action/$', action),
    url(r'^start/$', game_start),
    url(r'^wait/$', wait_start),
    url(r'^turn/$', turn_to),
    url(r'^admin/', include(admin.site.urls)),
)
