from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^(?P<orgname>[a-zA-Z0-9]+)/$', 'webapp.postosaurus.views.org.main'),
    (r'^(?P<orgname>.+)/links/$', 'webapp.postosaurus.views.org.links'),
    (r'^(?P<orgname>.+)/files/$', 'webapp.postosaurus.views.org.files'),
    (r'^(?P<orgname>.+)/members/$', 'webapp.postosaurus.views.org.members'),
    (r'^(?P<orgname>.+)/tasks/$', 'webapp.postosaurus.views.org.tasks'),
    (r'^(?P<orgname>.+)/lists/(?P<listname>.+)/members/$', 'webapp.postosaurus.views.list.members'),
    (r'^(?P<orgname>.+)/lists/(?P<listname>.+)/archive/$', 'webapp.postosaurus.views.list.archive_overview'),
    (r'^(?P<orgname>.+)/lists/(?P<listname>.+)/archive/(?P<month>\d+)/(?P<day>\d+)/(?P<year>\d+)/$', 
     'webapp.postosaurus.views.list.archive_by_day'),
)
