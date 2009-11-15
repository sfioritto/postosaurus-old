from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^lists/(?P<listname>.+)/links/$', 'webapp.postosaurus.views.links'),
    (r'^lists/(?P<listname>.+)/members/$', 'webapp.postosaurus.views.members'),
    (r'^lists/(?P<listname>.+)/archive/$', 'webapp.postosaurus.views.archive_overview'),
    (r'^lists/(?P<listname>.+)/archive/(?P<month>\d+)/(?P<day>\d+)/(?P<year>\d+)/$', 
     'webapp.postosaurus.views.archive_by_day'),
    (r'^lists/create/$', 'webapp.postosaurus.views.create_list'),
    (r'^users/(?P<useremail>.+)/', 'webapp.postosaurus.views.user_main'),
    (r'^outofspace/$', 'webapp.postosaurus.views.out_of_space'),
    (r'^thanks/$', 'webapp.postosaurus.views.list_created'),
)
